# Glosario de nombres: Vertex AI → Gemini Enterprise Agent Platform

Fuente oficial: https://docs.cloud.google.com/gemini-enterprise-agent-platform/vertex-ai-name-changes (renombrado anunciado en Cloud Next, abril 2026). Úsalo para hablar con los alumnos: ellos verán los nombres nuevos en la consola, pero muchos tutoriales viejos usan los anteriores.

| Nombre anterior | Nombre actual | Dónde sale en el programa |
|---|---|---|
| Vertex AI / Vertex AI Platform | Gemini Enterprise Agent Platform (en consola: "Plataforma de agentes") | Todos |
| Vertex AI Agent Engine | **Agent Runtime** | M1, M5 (despliegue) |
| Agent Engine Memory Bank / Sessions | Memory Bank / Sessions de Gemini Enterprise Agent Platform | M1 |
| Vertex AI Model Garden | Model Garden (Gemini Enterprise Agent Platform) | M1 |
| Vertex AI Vector Search | Vector Search on Gemini Enterprise Agent Platform | M2 |
| Vertex AI Vector Search 2.0 | Agent Retrieval | M2 |
| Vertex AI Search | Agent Search | M2 |
| RAG Engine | RAG Engine (sin cambio) | M2 |
| Vertex AI Endpoints / Online Inference | Gemini Enterprise Agent Platform Endpoints / Online Inference | M4 ("Vertex AI Prediction") |
| Gen AI evaluation service / Model Evaluation | **Gemini Enterprise Agent Platform Evals** / Model Evaluation | M5 |
| Vertex AI Pipelines / Notebooks / Workbench | Agent Platform Pipelines / Notebooks / Workbench | opcional |
| Vertex AI Studio | Agent Studio | M1 (low-code, para contrastar) |

## Identificadores técnicos (confirmados en la documentación)
- API: se sigue habilitando como **`aiplatform.googleapis.com`** (la documentación de ADK la llama "Agent Platform API"). Rol: `roles/aiplatform.user` ("Agent Platform User").
- SDK: la documentación de Model Garden sigue usando el **SDK `vertexai`** (`vertexai.init(...)`, `model_garden.OpenModel(...)`) y los comandos **`gcloud ai model-garden models ...`** y `gcloud ai endpoints ...`.
- Variable de entorno de ADK: **`GOOGLE_GENAI_USE_ENTERPRISE=TRUE`** (antes `GOOGLE_GENAI_USE_VERTEXAI`; equivalentes; si tu ADK es antiguo usa la vieja). Alternativa rápida: `GOOGLE_API_KEY`.
- CLI de despliegue de ADK: el subcomando conserva el nombre **`adk deploy agent_engine`** (también `cloud_run`, `gke`, `docker`).
- Modelos: los ejemplos de ADK usan el alias `gemini-flash-latest`, pero **en Agent Platform (modo corporativo) ese alias dio 404** en el proyecto de prueba. Funcionó `gemini-2.5-flash` (global y us-central1), y también `gemini-3.5-flash`, `3.6-flash`, `3.7-flash`, `3.8-flash` y `3.1-flash-lite` (global). El alias sí aplica a claves de AI Studio. Para listar lo que tiene tu proyecto: `genai.Client(vertexai=True, project=..., location='global').models.list()`.
Release notes: https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes

## Desplegar un modelo desde Model Garden (por si lo muestras)
Documentación: sección "Implementa un modelo abierto". Consola: Model Garden → tarjeta del modelo → **Implementar** → nombres de modelo/endpoint, ubicación, tipo de máquina → **Implementar**. CLI:
```
gcloud ai model-garden models list
gcloud ai model-garden models list-deployment-config --model=MODEL_ID
gcloud ai model-garden models deploy --model=MODEL_ID [--machine-type=... --accelerator-type=... --asynchronous]
gcloud ai endpoints list --list-model-garden-endpoints-only --region=LOCATION
```
Requiere cuota de aceleradores (p. ej. NVIDIA_L4) y aceptar el EULA. Los modelos de Gemini no se "despliegan": se consumen por API (MaaS). Desplegar un modelo abierto (Gemma) **cuesta** mientras el endpoint esté activo: elimínalo después de la demo.

## ADK / A2A (docs: https://adk.dev)
- Instalación para A2A: `pip install "google-adk[a2a]"` (ya está en `requirements.txt`).
- `to_a2a(root_agent)` genera la agent card automáticamente; el servidor debe usar un puerto distinto al del agente consumidor.
- `RemoteA2aAgent` (import `google.adk.agents.remote_a2a_agent`) está documentado como **experimental**; la guía de consumo menciona un parámetro `use_legacy=False` para la integración nueva. Revisa la firma en la versión que instales.
- Los modelos de la consola ya incluyen Gemini 3.x: toma el ID exacto desde la tarjeta del modelo en Model Garden y ponlo en `MODEL_NAME`.
