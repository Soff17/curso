"""Comprueba tu BigQuery con el conector del módulo (💸 centavos; BigQuery cobra mínimo 10 MiB por tabla consultada).

    . .\\env.ps1
    python modulo3_sql_bigquery/verificar_bigquery.py

Necesita en el .env: AGENTS_MODE=cloud, SQL_BACKEND=bigquery, BQ_DATASET=<tu dataset> (lo imprime preparar_bigquery.py).
Hace cuatro cosas, de la más barata a la más cara, y para si algo falla:
  1. lista las tablas y los modelos del dataset,
  2. calcula cuántos bytes procesaría una consulta (dry run: no cobra),
  3. ejecuta esa consulta por el camino del agente (guardrails + tope de bytes),
  4. intenta una consulta peligrosa, que debe quedar bloqueada ANTES de llegar a BigQuery.
"""
from sqlagent.agent import ejecutar_sql
from sqlagent.connectors import BigQueryConnector, get_connector

CONSULTA = ("SELECT division, ROUND(SUM(ejecutado) - SUM(presupuestado), 2) AS exceso FROM presupuesto "
            "WHERE trimestre = '2026-Q3' AND categoria = 'Consultoria' GROUP BY division ORDER BY exceso DESC")


def main() -> int:
    con = get_connector()
    if not isinstance(con, BigQueryConnector):
        print(f"El conector activo es {type(con).__name__}, no BigQuery. Revisa SQL_BACKEND=bigquery y AGENTS_MODE=cloud en el .env.")
        return 1
    print(f"1. Dataset {con.client.project}.{con.dataset}")
    tablas = sorted(con.tables())
    print(f"   {len(tablas)} tablas y modelos: {', '.join(tablas[:6])}{' …' if len(tablas) > 6 else ''}")
    if len(tablas) < 22:
        print("   ⚠️ Se esperaban 22 tablas: ¿corriste preparar_bigquery.py?")
    print(f"2. Dry run: la consulta procesaría {con.dry_run_bytes(CONSULTA):,} bytes (tope: {con.max_bytes:,})")
    r = ejecutar_sql(CONSULTA)
    print(f"3. ejecutar_sql -> {r['status']}")
    for fila in r.get("rows", []):
        print("   ", fila)
    print("   SQL que se ejecutó:", r.get("sql"))
    print("   (Debe salir Norte arriba, con un exceso de 46800.0)")
    b = ejecutar_sql("DELETE FROM gastos WHERE division = 'Norte'")
    print(f"4. Consulta peligrosa -> {b['status']}: {b.get('message')}")
    ok = r["status"] == "ok" and b["status"] == "bloqueado"
    if "forecast_gasto" in tablas:
        p = ejecutar_sql("SELECT division, forecast_timestamp, ROUND(forecast_value, 2) AS pronostico "
                         "FROM ML.FORECAST(MODEL forecast_gasto, STRUCT(3 AS horizon)) ORDER BY division, forecast_timestamp")
        print(f"5. BigQuery ML (ML.FORECAST, 3 periodos) -> {p['status']}: {p.get('message') or str(p['n']) + ' filas (4 divisiones x 3)'}")
        for fila in p.get("rows", [])[:3]:
            print("   ", fila)
        print("   (Los periodos deben ser MESES: 1 de octubre, 1 de noviembre y 1 de diciembre de 2026. "
              "Si salen cada 3 días, el modelo es el anterior: corre `preparar_bigquery.py --modelo` otra vez)")
        ok = ok and p["status"] == "ok"
    else:
        print("5. (Sin modelo: corre `preparar_bigquery.py --modelo` si quieres probar BigQuery ML)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
