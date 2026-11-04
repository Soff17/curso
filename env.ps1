# Uso:  . .\env.ps1      (con el punto inicial, en la raíz del proyecto)
# Configura PYTHONPATH para ejecutar cualquier módulo desde la terminal.
$root = $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = (@("", "modulo1_adk_a2a/src", "modulo2_rag_reranking/src", "modulo3_sql_bigquery/src",
  "modulo4_ml_multimodal_bi", "modulo4_ml_multimodal_bi/src", "modulo5_agentops/src", "capstone/src") |
  ForEach-Object { Join-Path $root $_ }) -join ";"
Write-Host "PYTHONPATH listo para $root"
