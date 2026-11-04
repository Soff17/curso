"""Paquete para `adk web`: el agente híbrido del Módulo 3 (RAG de metadata + SQL + informe + política).

    agente_sql  (root_agent)
     ├── buscar_esquema      RAG de metadata + reranking: elige las tablas del catálogo
     ├── ejecutar_sql        guardrails + conector (SQLite, SQL Server o BigQuery según SQL_BACKEND)
     ├── buscar_informe      RAG sobre el informe de presupuesto (con cita)
     ├── contrastar_cifras   compara SQL contra informe con una regla fija
     └── buscar_politicas    RAG sobre las políticas internas (Módulo 2)

    adk web --port 8501 modulo3_sql_bigquery/src      # y elige «sql_app»
"""
from sqlagent.agent import build_sql_agent

root_agent = build_sql_agent()
