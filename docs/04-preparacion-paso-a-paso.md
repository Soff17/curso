# Paso 0 – Preparación previa (hazla una vez, antes del Módulo 1)

Todos los comandos son para **PowerShell** en `C:\Users\Sofia Donlucas\Documents\Visual\GeminiAgentsBI`.

## 0.1 Entorno local
```powershell
cd "C:\Users\Sofia Donlucas\Documents\Visual\GeminiAgentsBI"
python --version                       # necesitas 3.11+
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt        # puede tardar varios minutos
. .\env.ps1                            # (punto + espacio) configura PYTHONPATH
python data\seed_data.py               # esperado: "OK: ...finanzas.db"
python -m pytest -q                    # esperado: 61 passed
```
Si `pyodbc` falla al instalar, quítalo de `requirements.txt` por ahora (solo se usa con SQL Server real).

## 0.2 Google Cloud
```powershell
gcloud --version
gcloud auth login
gcloud auth application-default login
gcloud config set project TU_PROYECTO
gcloud services enable aiplatform.googleapis.com bigquery.googleapis.com discoveryengine.googleapis.com `
  dlp.googleapis.com cloudtrace.googleapis.com logging.googleapis.com cloudbuild.googleapis.com `
  artifactregistry.googleapis.com
```
Copia `.env.example` a `.env`, pon tu proyecto y deja `AGENTS_MODE=offline` hasta que cada paso cloud funcione.

> Nombres: Vertex AI = Gemini Enterprise Agent Platform; Agent Engine = Agent Runtime. Ver `05-nombres-actuales.md`. La API se sigue habilitando como `aiplatform.googleapis.com` ("Agent Platform API", confirmado en la documentación de ADK).

## 0.3 Prueba de humo de ADK (si falla, resuélvelo hoy)
```powershell
pip show google-adk                    # anota la versión
python -c "from google.adk.agents import Agent; print('adk ok')"
python -c "from google.adk.agents.remote_a2a_agent import RemoteA2aAgent; print('a2a cliente ok')"
python -c "from google.adk.a2a.utils.agent_to_a2a import to_a2a; print('a2a servidor ok')"
python -c "from google.adk.tools.agent_tool import AgentTool; print('agenttool ok')"
```
Estos 4 imports están verificados con **google-adk 2.11.0** (`pip install "google-adk[a2a]"`). Si con otra versión alguno falla, consulta https://adk.dev y corrige el import en el archivo correspondiente. Anota el cambio: tus alumnos lo necesitarán.

## 0.4 Prueba de humo de Gemini
```powershell
$env:GOOGLE_GENAI_USE_ENTERPRISE="TRUE"   # antes GOOGLE_GENAI_USE_VERTEXAI (si tu ADK es antiguo, usa el nombre viejo)
$env:GOOGLE_CLOUD_PROJECT="TU_PROYECTO"; $env:GOOGLE_CLOUD_LOCATION="us-central1"
# Alternativa rápida sin Google Cloud: $env:GOOGLE_API_KEY="..." (clave de AI Studio) y no definir la variable ENTERPRISE
python -c "from google import genai; c=genai.Client(); print(c.models.generate_content(model='gemini-2.5-flash', contents='Di hola en una palabra').text)"
```

## 0.5 Cómo usar las guías
**Módulo 1:** usa `modulo1_adk_a2a/SESION_TEORICA.md` (sección 4, ensayo previo de las demos) y `SESION_PRACTICA.md`. **Módulo 2:** igual, en `modulo2_rag_reranking/` (`SESION_TEORICA.md`, `SESION_PRACTICA.md`, `COMANDOS.md`). **Módulo 3:** igual, en `modulo3_sql_bigquery/` (`SESION_TEORICA.md` y `SESION_PRACTICA.md`; `COMANDOS.md` está pendiente). **Módulos 4-5:** cada uno tiene `PASO_A_PASO.md`. Hazlas en orden; cada paso indica **Qué haces → Qué debes ver → Qué explicar a los alumnos**. Al final de cada una hay un checklist "Listo para dar clase".
