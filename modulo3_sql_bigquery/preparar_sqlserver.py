"""Prepara un SQL Server para el Módulo 3: crea la base `finanzas`, carga las 22 tablas y crea un login de SOLO LECTURA
por célula. Lo corre quien administra el servidor (el instructor), una vez.

    python modulo3_sql_bigquery/preparar_sqlserver.py --dry-run    # muestra el plan; no se conecta a nada
    python modulo3_sql_bigquery/preparar_sqlserver.py              # 💸 crea la base, carga las tablas y crea los logins
    python modulo3_sql_bigquery/preparar_sqlserver.py --limpiar    # borra la base y los logins

Se conecta con la cuenta administradora, por el puerto local que abre el Cloud SQL Auth Proxy (127.0.0.1:1433):
    MSSQL_ADMIN_PASSWORD=<la clave de la cuenta sqlserver>   (obligatoria)
    MSSQL_ADMIN_USER=sqlserver   MSSQL_HOST=127.0.0.1   MSSQL_PORT=1433   (opcionales)
Los alumnos NUNCA reciben la cuenta administradora: reciben `MSSQL_URL` de su login `celdaN_ro`, que tiene solo el rol
`db_datareader`. Esa es la barrera real; los guardrails del agente son la segunda. Las claves se generan al azar y se
imprimen una sola vez al terminar: cópialas y no las compartas por canales abiertos.
Requisitos: `pip install sqlalchemy pyodbc` y el ODBC Driver 18 for SQL Server.
"""
import argparse
import csv
import os
import secrets
import string
from urllib.parse import quote

from sqlagent.dwh import leer_tablas

BASE = "finanzas"
TIPOS = {"TEXT": "NVARCHAR(200)", "INTEGER": "INT", "REAL": "FLOAT"}
DRIVER = "ODBC+Driver+18+for+SQL+Server"


def ddl_tabla(nombre: str, cols: list[tuple[str, str]]) -> str:
    cuerpo = ", ".join(f"[{c}] {TIPOS[t]}" for c, t in cols)
    return f"DROP TABLE IF EXISTS dbo.[{nombre}]; CREATE TABLE dbo.[{nombre}] ({cuerpo})"


def convertir(valor: str, tipo: str):
    if tipo == "INTEGER":
        return int(valor)
    if tipo == "REAL":
        return float(valor)
    return valor


def clave_nueva() -> str:
    """16 caracteres al azar más mayúscula, minúscula, número y símbolo (la política de contraseñas de SQL Server)."""
    base = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    return f"{base}aA1!"


def nombres_celdas(n: int) -> list[str]:
    return [f"celda{i}_ro" for i in range(1, n + 1)]


def sentencias_logins(usuario: str, clave: str) -> tuple[list[str], list[str]]:
    """(en master, en la base): crear el login y darle solo lectura. Reemplaza uno anterior con el mismo nombre."""
    master = [f"IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'{usuario}') DROP LOGIN [{usuario}]",
              f"CREATE LOGIN [{usuario}] WITH PASSWORD = N'{clave}', CHECK_EXPIRATION = OFF"]
    base = [f"IF EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'{usuario}') DROP USER [{usuario}]",
            f"CREATE USER [{usuario}] FOR LOGIN [{usuario}]",
            f"ALTER ROLE db_datareader ADD MEMBER [{usuario}]"]
    return master, base


def url(usuario: str, clave: str, host: str, puerto: str, base: str) -> str:
    # TrustServerCertificate: el ODBC Driver 18 cifra siempre; el certificado de 127.0.0.1 no es de confianza.
    return (f"mssql+pyodbc://{quote(usuario, safe='')}:{quote(clave, safe='')}@{host}:{puerto}/{base}"
            f"?driver={DRIVER}&TrustServerCertificate=yes")


def _engine(database: str):
    from sqlalchemy import create_engine           # pip install sqlalchemy pyodbc
    u = url(os.getenv("MSSQL_ADMIN_USER", "sqlserver"), os.environ["MSSQL_ADMIN_PASSWORD"],
            os.getenv("MSSQL_HOST", "127.0.0.1"), os.getenv("MSSQL_PORT", "1433"), database)
    return create_engine(u, fast_executemany=True, connect_args={"timeout": 30})


def main(argv: list[str] | None = None, engine_factory=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="muestra el plan sin conectarse")
    ap.add_argument("--limpiar", action="store_true", help="borra la base y los logins de las células")
    ap.add_argument("--celdas", type=int, default=5, help="cuántos logins de solo lectura crear (por defecto 5)")
    args = ap.parse_args(argv)
    tablas, celdas = leer_tablas(), nombres_celdas(args.celdas)
    faltan = [str(p) for _, p, _ in tablas if not p.exists()]
    if faltan:
        print("Faltan CSV (genera los datos con `python data/seed_data.py`):", *faltan[:3], sep="\n  ")
        return 1

    if args.dry_run:
        print(f"Base: {BASE} · {len(tablas)} tablas · logins de solo lectura: {', '.join(celdas)}\n")
        print("1. CREATE DATABASE finanzas (si no existe)")
        print(f"2. Crear y cargar {len(tablas)} tablas, por ejemplo:\n   {ddl_tabla(*tablas[0][::2])}")
        for u in celdas[:1]:
            m, b = sentencias_logins(u, "<clave al azar>")
            print("3. Por cada célula:\n   " + "\n   ".join(m + b))
        print("\nNo se conectó a nada.")
        return 0
    if not os.getenv("MSSQL_ADMIN_PASSWORD") and engine_factory is None:
        print("Falta MSSQL_ADMIN_PASSWORD (la clave de la cuenta administradora, la de `--root-password`).")
        return 1

    fabrica = engine_factory or _engine
    host, puerto = os.getenv("MSSQL_HOST", "127.0.0.1"), os.getenv("MSSQL_PORT", "1433")
    master = fabrica("master")
    with master.connect().execution_options(isolation_level="AUTOCOMMIT") as c:
        if args.limpiar:
            c.exec_driver_sql(f"IF DB_ID(N'{BASE}') IS NOT NULL ALTER DATABASE [{BASE}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
            c.exec_driver_sql(f"DROP DATABASE IF EXISTS [{BASE}]")
            for u in celdas:
                c.exec_driver_sql(f"IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'{u}') DROP LOGIN [{u}]")
            print(f"Borrada la base {BASE} y los logins {', '.join(celdas)}.")
            return 0
        c.exec_driver_sql(f"IF DB_ID(N'{BASE}') IS NULL CREATE DATABASE [{BASE}]")
    print(f"Base {BASE} lista.")

    db = fabrica(BASE)
    with db.connect().execution_options(isolation_level="AUTOCOMMIT") as c:
        for nombre, ruta, cols in tablas:
            for sentencia in ddl_tabla(nombre, cols).split("; "):
                c.exec_driver_sql(sentencia)
            with open(ruta, newline="", encoding="utf-8") as f:
                lector = csv.reader(f)
                next(lector)                                                  # encabezado
                filas = [tuple(convertir(v, t) for v, (_, t) in zip(r, cols)) for r in lector]
            c.exec_driver_sql(f"INSERT INTO dbo.[{nombre}] VALUES ({','.join('?' * len(cols))})", filas)
            print(f"  {nombre}: {len(filas)} filas")
        claves = {u: clave_nueva() for u in celdas}
        for u, clave in claves.items():
            m, b = sentencias_logins(u, clave)
            with master.connect().execution_options(isolation_level="AUTOCOMMIT") as cm:
                for s in m:
                    cm.exec_driver_sql(s)
            for s in b:
                c.exec_driver_sql(s)
    print("\nLogins de SOLO LECTURA (una línea `MSSQL_URL=` para el .env de cada célula; se muestran una sola vez):")
    for u, clave in claves.items():
        print(f"  # {u}\n  MSSQL_URL={url(u, clave, host, puerto, BASE)}")
    print("\nY en el .env de cada alumno: AGENTS_MODE=cloud, SQL_BACKEND=sqlserver")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
