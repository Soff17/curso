# Checklist de preparación (hacer 1 semana antes)

## GCP
- [ ] Proyecto por célula (5) o uno compartido con service accounts por célula.
- [ ] APIs: `aiplatform.googleapis.com`, `bigquery.googleapis.com`, `discoveryengine.googleapis.com` (Ranking API), `dlp.googleapis.com`, `cloudtrace.googleapis.com`, `logging.googleapis.com`, `cloudbuild.googleapis.com`, `artifactregistry.googleapis.com`.
- [ ] Roles mínimos alumnos: `roles/aiplatform.user`, `roles/bigquery.dataViewer` + `jobUser`, `roles/logging.viewer`.
- [ ] Cuotas de Gemini y Embeddings suficientes para 30 usuarios simultáneos.
- [ ] Región con Agent Engine disponible (validar en documentación vigente).

## Local
- [ ] Python 3.11+; Windows: Microsoft ODBC Driver 18 para SQL Server si se usará SQL Server real.
- [ ] `gcloud auth application-default login`
- [ ] `pip install -r requirements.txt` y `pytest` en verde.

## Validación de versiones (obligatoria)
Antes de la sesión 1, ejecutar y anotar versiones:
```
pip show google-adk google-genai google-cloud-aiplatform
python -c "from google.adk.agents import Agent; print('ok')"
python -c "from google.adk.agents.remote_a2a_agent import RemoteA2aAgent; print('a2a ok')"
```
Si un import falla, ajustar el módulo correspondiente (los imports de ADK/A2A ya están verificados con google-adk 2.11.0; quedan marcados `# VERIFICAR` solo los de Ranking API, Tableau, DLP, ODBC y google-genai).

## Tableau
- [ ] Personal Access Token por célula, permiso de lectura sobre un libro de ejemplo.
- [ ] Si no hay Tableau: usar `modulo4_ml_multimodal_bi/src/bi_agents/tableau_client.py` en modo `stub`.

## Datos
- [ ] `python data/seed_data.py` genera `data/finanzas.db` (SQLite). Para BigQuery, cargar los CSV de `data/` a un dataset `finanzas`.
