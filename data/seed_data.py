"""Genera data/finanzas.db (SQLite) y CSV sintéticos. Reproducible (semilla fija).

Historia embebida: la división Norte excede su presupuesto operacional en Q3-2026
por viáticos y consultoría externa; además tiene cartera vencida creciente.
"""
import csv
import random
import sqlite3
from pathlib import Path

DATA = Path(__file__).parent
DB = DATA / "finanzas.db"
random.seed(42)

DIVISIONES = ["Norte", "Sur", "Centro", "Occidente"]
CATEGORIAS = ["Viaticos", "Consultoria", "Tecnologia", "Marketing", "Servicios"]
TRIMESTRES = ["2026-Q1", "2026-Q2", "2026-Q3"]

SCHEMA = """
DROP TABLE IF EXISTS presupuesto;
DROP TABLE IF EXISTS gastos;
DROP TABLE IF EXISTS cuentas_por_cobrar;
DROP TABLE IF EXISTS catalogo_datos;
CREATE TABLE presupuesto (
  division TEXT, trimestre TEXT, categoria TEXT, presupuestado REAL, ejecutado REAL);
CREATE TABLE gastos (
  id INTEGER PRIMARY KEY, division TEXT, fecha TEXT, trimestre TEXT, categoria TEXT,
  monto REAL, proveedor TEXT, descripcion TEXT);
CREATE TABLE cuentas_por_cobrar (
  cliente TEXT, division TEXT, monto REAL, dias_vencido INTEGER, estado TEXT, trimestre TEXT);
CREATE TABLE catalogo_datos (
  tabla TEXT, columna TEXT, tipo TEXT, descripcion TEXT);
"""

CATALOGO = [
    ("presupuesto", "division", "TEXT", "Division de negocio: Norte, Sur, Centro, Occidente"),
    ("presupuesto", "trimestre", "TEXT", "Trimestre fiscal formato AAAA-Qn, por ejemplo 2026-Q3"),
    ("presupuesto", "categoria", "TEXT", "Categoria de gasto operacional. Valores exactos, sin acentos: Viaticos, Consultoria, Tecnologia, Marketing, Servicios"),
    ("presupuesto", "presupuestado", "REAL", "Monto presupuestado asignado en la categoria"),
    ("presupuesto", "ejecutado", "REAL", "Monto realmente ejecutado; si es mayor que presupuestado hay exceso"),
    ("gastos", "id", "INTEGER", "Identificador del gasto"),
    ("gastos", "division", "TEXT", "Division que realizo el gasto: Norte, Sur, Centro, Occidente"),
    ("gastos", "fecha", "TEXT", "Fecha del gasto AAAA-MM-DD"),
    ("gastos", "trimestre", "TEXT", "Trimestre fiscal del gasto, formato AAAA-Qn, por ejemplo 2026-Q3"),
    ("gastos", "categoria", "TEXT", "Categoria del gasto. Valores exactos, sin acentos: Viaticos, Consultoria, Tecnologia, Marketing, Servicios"),
    ("gastos", "monto", "REAL", "Importe del gasto en USD"),
    ("gastos", "proveedor", "TEXT", "Proveedor o beneficiario"),
    ("gastos", "descripcion", "TEXT", "Descripcion libre del gasto"),
    ("cuentas_por_cobrar", "cliente", "TEXT", "Cliente deudor"),
    ("cuentas_por_cobrar", "division", "TEXT", "Division propietaria de la cuenta: Norte, Sur, Centro, Occidente"),
    ("cuentas_por_cobrar", "monto", "REAL", "Monto pendiente de cobro"),
    ("cuentas_por_cobrar", "dias_vencido", "INTEGER", "Dias de atraso; 0 si esta al corriente"),
    ("cuentas_por_cobrar", "estado", "TEXT", "vigente, vencida o en_mora"),
    ("cuentas_por_cobrar", "trimestre", "TEXT", "Trimestre de corte"),
]


def build() -> None:
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO catalogo_datos VALUES (?,?,?,?)", CATALOGO)

    presupuesto, gastos = [], []
    gid = 1
    for d in DIVISIONES:
        for q in TRIMESTRES:
            for c in CATEGORIAS:
                base = random.randint(40, 90) * 1000
                factor = random.uniform(0.85, 1.02)
                if d == "Norte" and q == "2026-Q3":
                    factor = {"Viaticos": 1.45, "Consultoria": 1.60}.get(c, 1.05)
                ejec = round(base * factor, 2)
                presupuesto.append((d, q, c, float(base), ejec))
                # repartir ejecutado en 4 gastos
                parts = [random.random() for _ in range(4)]
                s = sum(parts)
                for i, p in enumerate(parts):
                    month = (int(q[-1]) - 1) * 3 + 1 + i % 3
                    gastos.append((gid, d, f"2026-{month:02d}-{random.randint(1, 28):02d}", q, c,
                                   round(ejec * p / s, 2), f"Proveedor-{random.randint(1, 20)}",
                                   f"{c} {d} {q} #{i + 1}"))
                    gid += 1
    con.executemany("INSERT INTO presupuesto VALUES (?,?,?,?,?)", presupuesto)
    con.executemany("INSERT INTO gastos VALUES (?,?,?,?,?,?,?,?)", gastos)

    cxc = []
    for d in DIVISIONES:
        for i in range(12):
            mora = d == "Norte" and random.random() < 0.55
            dias = random.randint(35, 120) if mora else random.choice([0, 0, 0, 5, 15])
            estado = "en_mora" if dias > 30 else ("vencida" if dias > 0 else "vigente")
            cxc.append((f"Cliente-{d[0]}{i + 1}", d, random.randint(10, 200) * 1000, dias, estado, "2026-Q3"))
    con.executemany("INSERT INTO cuentas_por_cobrar VALUES (?,?,?,?,?,?)", cxc)
    con.commit()

    for name, cols, rows in [
        ("presupuesto", ["division", "trimestre", "categoria", "presupuestado", "ejecutado"], presupuesto),
        ("gastos", ["id", "division", "fecha", "trimestre", "categoria", "monto", "proveedor", "descripcion"], gastos),
        ("cuentas_por_cobrar", ["cliente", "division", "monto", "dias_vencido", "estado", "trimestre"], cxc),
    ]:
        with open(DATA / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)

    # Módulo 3: 19 tablas más y su catálogo (tablas y columnas). No altera las tres de arriba.
    from seed_dwh import build_dwh
    n = build_dwh(con, DATA / "dwh")
    print(f"Catálogo del Módulo 3: {n} tablas")
    con.close()
    print(f"OK: {DB}")


if __name__ == "__main__":
    build()
