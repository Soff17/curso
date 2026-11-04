# Genera datos, corre tests y muestra el informe del Capstone (modo offline).
$root = $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = (@("", "modulo2_rag_reranking/src", "modulo3_sql_bigquery/src", "modulo4_ml_multimodal_bi",
  "modulo4_ml_multimodal_bi/src", "modulo5_agentops/src", "capstone/src") | ForEach-Object { Join-Path $root $_ }) -join ";"
python "$root/data/seed_data.py"
python -m pytest "$root" -q
python -m capstone_agent.report
