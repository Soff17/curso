# IAM de mínimo privilegio – plantilla

| Service Account | Rol | Para qué |
|---|---|---|
| `sa-agente-runtime` | `roles/aiplatform.user` (la doc de ADK lo llama "Agent Platform User") | Llamar a Gemini / Agent Runtime |
| | `roles/bigquery.dataViewer` (dataset `finanzas`) + `roles/bigquery.jobUser` | Consultas SQL solo lectura |
| | `roles/discoveryengine.viewer` | Ranking API |
| | `roles/secretmanager.secretAccessor` (solo secretos del agente) | PAT Tableau, cadena SQL Server |
| | `roles/cloudtrace.agent`, `roles/logging.logWriter` | Observabilidad |
| `sa-cicd` | `roles/cloudbuild.builds.builder`, `roles/artifactregistry.writer`, `roles/aiplatform.admin` (acotado al proyecto de despliegue) | Pipeline |
| `sa-dlp` | `roles/dlp.user` | Enmascaramiento |

## Reglas
- Nada de `roles/owner` / `editor` en cuentas de agentes.
- SQL Server: login dedicado con `db_datareader`, `DENY` explícito sobre tablas sensibles.
- **VPC Service Controls:** perímetro con `aiplatform`, `bigquery`, `storage`, `dlp`; ingress solo desde la red del cliente; probar con `dry-run` antes de forzar.
- Secretos en Secret Manager, nunca en `.env` versionado.
- Auditoría: habilitar Data Access logs para Agent Platform (aiplatform) y BigQuery.
