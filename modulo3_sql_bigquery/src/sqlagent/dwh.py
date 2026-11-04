"""El almacén de datos de ejemplo (22 tablas): de dónde salen sus esquemas y sus CSV.

Lo comparten los scripts que cargan los datos a BigQuery y a SQL Server, para que las dos bases queden iguales.
"""
import sqlite3
from pathlib import Path

from shared.config import DATA_DIR, DB_PATH

ORIGINALES = {"presupuesto", "gastos", "cuentas_por_cobrar"}      # sus CSV están en data/; el resto en data/dwh/


def leer_tablas() -> list[tuple[str, Path, list[tuple[str, str]]]]:
    """(tabla, ruta del CSV, [(columna, tipo de SQLite: TEXT | INTEGER | REAL)]) según el catálogo."""
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    filas = con.execute("SELECT tabla, columna, tipo FROM catalogo_datos ORDER BY rowid").fetchall()
    con.close()
    por_tabla: dict[str, list[tuple[str, str]]] = {}
    for tabla, col, tipo in filas:
        por_tabla.setdefault(tabla, []).append((col, tipo))
    return [(t, (DATA_DIR if t in ORIGINALES else DATA_DIR / "dwh") / f"{t}.csv", cols) for t, cols in por_tabla.items()]
