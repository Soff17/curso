# Guía del instructor – Módulo 5 (Semana 5)

## Mensajes clave
1. Sin evaluación automática no hay agentes en producción financiera. La evaluación es el "unit test" del comportamiento.
2. Evaluar **retrieval** (Context Recall) y **generación** (Faithfulness, Relevance) por separado para saber dónde está el fallo.
3. Trazabilidad = poder reconstruir por qué un agente dijo X: spans A2A, citas, versión del modelo y del corpus.
4. Gobernanza no es un anexo: IAM mínimo, DLP antes de loguear, perímetro VPC-SC.

## Estructura (2 h)
| Min | Tema | Material |
|---|---|---|
| 0-35 | Métricas RAG | `metrics.py` (demo: respuesta fiel vs inventada) |
| 35-55 | Evaluación A2A | `delegation_metrics` |
| 55-80 | Cloud Trace / Logging / costos | `governance.Tracer`, `token_cost` |
| 80-105 | IAM, DLP, VPC-SC | `ci/iam_least_privilege.md`, `mask_pii` |
| 105-120 | CI/CD y gate | `ci/cloudbuild.yaml`, `eval_gate.py` |

## Demo clave
Ejecutar `python -m agentops.eval_gate --threshold 0.85` (exit 0); modificar `offline_agent` para inventar texto; ejecutar de nuevo (exit 1). Mostrar el JSON del reporte.

## Advertencias honestas
- Las métricas offline son aproximaciones léxicas, útiles como gate barato y determinista; no reemplazan una evaluación model-based.
- `PRICE_PER_M` son valores de ejemplo: actualizar con la tarifa vigente.
- `adk deploy agent_engine` existe en ADK 2.11 (también `cloud_run`, `gke`, `docker`), pero **no se ejecutó un despliegue real**. `agents-cli` (`google-agents-cli`) también existe y lo usa un agente de código; confirma con el cliente cuál prefieren.
