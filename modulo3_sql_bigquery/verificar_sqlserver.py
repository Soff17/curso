"""Comprueba tu SQL Server con el conector del módulo, usando el login de SOLO LECTURA (💸 sin costo extra: es tu instancia).

    . .\\env.ps1
    python modulo3_sql_bigquery/verificar_sqlserver.py

Necesita en el .env: AGENTS_MODE=cloud, SQL_BACKEND=sqlserver y MSSQL_URL=<la línea de tu célula>, con el Cloud SQL
Auth Proxy corriendo en otra terminal (escucha en 127.0.0.1:1433).
Hace cinco comprobaciones y dice cuál falló:
  1. conecta y lista las tablas (deben ser 22),
  2. ejecuta una consulta por el camino del agente (el guardrail pone `TOP`, no `LIMIT`),
  3. un DELETE por el camino del agente: lo bloquea el guardrail,
  4. un DELETE que NO toca filas, directo a la base: lo debe rechazar SQL Server por permisos (la barrera real),
  5. una consulta que tarda más que el tiempo permitido: debe cortarse sola.
"""
import time

from sqlagent.agent import ejecutar_sql
from sqlagent.connectors import SqlServerConnector, get_connector

CONSULTA = ("SELECT division, ROUND(SUM(ejecutado) - SUM(presupuestado), 2) AS exceso FROM presupuesto "
            "WHERE trimestre = '2026-Q3' AND categoria = 'Consultoria' GROUP BY division ORDER BY exceso DESC")


def main() -> int:
    con = get_connector()
    if not isinstance(con, SqlServerConnector):
        print(f"El conector activo es {type(con).__name__}. Revisa SQL_BACKEND=sqlserver y AGENTS_MODE=cloud en el .env.")
        return 1
    fallos = []
    tablas = sorted(con.tables())
    print(f"1. Conectado. {len(tablas)} tablas: {', '.join(tablas[:6])}{' …' if len(tablas) > 6 else ''}")
    if len(tablas) != 22:
        fallos.append("se esperaban 22 tablas")

    r = ejecutar_sql(CONSULTA)
    print(f"2. ejecutar_sql -> {r['status']}\n   SQL que se ejecutó: {r.get('sql') or r.get('message')}")
    for fila in r.get("rows", []):
        print("   ", fila)
    if r["status"] != "ok" or "TOP" not in (r.get("sql") or ""):
        fallos.append("la consulta no salió bien o no usó TOP")

    b = ejecutar_sql("DELETE FROM gastos WHERE division = 'Norte'")
    print(f"3. DELETE por el agente -> {b['status']}: {b.get('message')}")
    if b["status"] != "bloqueado":
        fallos.append("el guardrail no bloqueó el DELETE")

    try:
        with con.engine.connect() as c:
            c.exec_driver_sql("DELETE FROM dbo.gastos WHERE 1 = 0")   # no borra nada ni aunque tuviera permiso
            c.rollback()
        print("4. ⚠️ SQL Server ACEPTÓ el DELETE: este login puede escribir. Revisa que solo tenga db_datareader.")
        fallos.append("el login puede escribir")
    except Exception as e:                                           # noqa: BLE001
        print(f"4. DELETE directo -> rechazado por SQL Server ({type(e).__name__}): {str(e).splitlines()[0][:110]}")

    corto = SqlServerConnector(query_timeout_s=2)
    t0 = time.time()
    try:
        with corto.engine.connect() as c:
            c.exec_driver_sql("WAITFOR DELAY '00:00:08'")
        print("5. ⚠️ La consulta de 8 s NO se cortó con un límite de 2 s.")
        fallos.append("el tiempo máximo por consulta no funcionó")
    except Exception as e:                                           # noqa: BLE001
        print(f"5. Consulta lenta -> cortada a los {time.time() - t0:.1f} s ({type(e).__name__}): {str(e).splitlines()[0][:100]}")

    print("\n✅ Todo bien." if not fallos else "\n❌ Falló: " + "; ".join(fallos))
    return 0 if not fallos else 1


if __name__ == "__main__":
    raise SystemExit(main())
