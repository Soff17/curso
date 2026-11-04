"""Prepara BigQuery para el Módulo 3: crea TU dataset y carga las 22 tablas del almacén de datos (CSV).

    python modulo3_sql_bigquery/preparar_bigquery.py --dry-run     # muestra el plan; no llama a ningún servicio
    python modulo3_sql_bigquery/preparar_bigquery.py               # 💸 crea el dataset y carga las tablas
    python modulo3_sql_bigquery/preparar_bigquery.py --modelo      # 💸 además entrena el modelo de pronóstico (BigQuery ML)
    python modulo3_sql_bigquery/preparar_bigquery.py --variables   # vuelve a imprimir las variables del .env
    python modulo3_sql_bigquery/preparar_bigquery.py --limpiar     # 💸 BORRA tu dataset con todo lo que contiene

Cada persona tiene su propio dataset (`finanzas_<tu usuario>`), así que nadie pisa a nadie. El dataset se crea en la
ubicación `BQ_LOCATION` (por defecto US); una vez creado, su ubicación no se puede cambiar.
Requisitos: la API de BigQuery y tus credenciales (`gcloud auth application-default login`).
Los esquemas salen del catálogo (`catalogo_datos`): TEXT -> STRING, INTEGER -> INT64, REAL -> FLOAT64. Las fechas
quedan como texto AAAA-MM-DD; para BigQuery ML se convierten con DATE(fecha) dentro de la consulta.
"""
import argparse
import getpass
import os
import re
from pathlib import Path

from sqlagent.connectors import BQML_EXAMPLE
from sqlagent.dwh import leer_tablas

TIPOS = {"TEXT": "STRING", "INTEGER": "INT64", "REAL": "FLOAT64"}


def nombres() -> dict:
    usuario = re.sub(r"[^a-z0-9]", "", getpass.getuser().lower())[:12] or "alumno"
    return {"usuario": usuario, "dataset": f"finanzas_{usuario}", "location": os.getenv("BQ_LOCATION", "US")}


def tablas_a_cargar() -> list[tuple[str, Path, list[tuple[str, str]]]]:
    """(tabla, ruta del CSV, [(columna, tipo de BigQuery)]) para las 22 tablas, según el catálogo."""
    return [(t, ruta, [(c, TIPOS[tp]) for c, tp in cols]) for t, ruta, cols in leer_tablas()]


def imprimir_variables(n: dict) -> None:
    print("AGENTS_MODE=cloud\nSQL_BACKEND=bigquery")
    print(f"BQ_DATASET={n['dataset']}\nBQ_LOCATION={n['location']}")


def main(argv: list[str] | None = None, client_factory=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="muestra el plan sin llamar a ningún servicio")
    ap.add_argument("--modelo", action="store_true", help="además entrena el modelo de pronóstico (BigQuery ML)")
    ap.add_argument("--variables", action="store_true", help="imprime las variables del .env")
    ap.add_argument("--limpiar", action="store_true", help="borra tu dataset y todo lo que contiene")
    args = ap.parse_args(argv)

    n = nombres()
    proyecto = os.getenv("GOOGLE_CLOUD_PROJECT", "tu-proyecto")
    tablas = tablas_a_cargar()
    faltan = [str(p) for _, p, _ in tablas if not p.exists()]
    if faltan:
        print("Faltan CSV (genera los datos con `python data/seed_data.py`):", *faltan[:3], sep="\n  ")
        return 1

    if args.dry_run or args.variables:
        if args.dry_run:
            print(f"Proyecto: {proyecto} · dataset: {proyecto}.{n['dataset']} · ubicación: {n['location']}")
            print(f"1. Crear el dataset (si no existe)\n2. Cargar {len(tablas)} tablas desde CSV:")
            for t, p, cols in tablas:
                print(f"   - {t}: {len(cols)} columnas ({p.name})")
            if args.modelo:
                print("3. Entrenar el modelo `forecast_gasto` (ARIMA_PLUS) con BigQuery ML")
            print("\nNo se llamó a ningún servicio.")
        imprimir_variables(n)
        return 0

    from google.cloud import bigquery
    cliente = (client_factory or (lambda: bigquery.Client(project=proyecto if proyecto != "tu-proyecto" else None,
                                                          location=n["location"])))()
    ref = f"{cliente.project}.{n['dataset']}"

    if args.limpiar:
        cliente.delete_dataset(ref, delete_contents=True, not_found_ok=True)
        print(f"Borrado el dataset {ref} (con todo su contenido).")
        return 0

    ds = bigquery.Dataset(ref)
    ds.location = n["location"]
    cliente.create_dataset(ds, exists_ok=True)
    print(f"Dataset {ref} listo ({n['location']}).")
    for t, ruta, cols in tablas:
        cfg = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.CSV, skip_leading_rows=1,
                                     schema=[bigquery.SchemaField(c, tp) for c, tp in cols],
                                     write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
        with open(ruta, "rb") as f:
            job = cliente.load_table_from_file(f, f"{ref}.{t}", job_config=cfg)
        job.result()
        print(f"  {t}: {cliente.get_table(f'{ref}.{t}').num_rows} filas")
    if args.modelo:
        sql = BQML_EXAMPLE.split(";")[0].replace("`finanzas.", f"`{ref}.")
        cliente.query(sql, job_config=bigquery.QueryJobConfig(default_dataset=ref)).result()
        print(f"Modelo {ref}.forecast_gasto entrenado.")
    print("\nCopia estas líneas a tu .env y reinicia lo que lo lea:")
    imprimir_variables(n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
