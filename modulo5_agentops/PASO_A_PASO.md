# Módulo 5 – Paso a paso (AgentOps, evaluación y gobernanza)

Terminal en la raíz, `.venv` activo, `. .\env.ps1`.

---
## Contenido 1 – Métricas de calidad para RAG
```powershell
python -c "
from agentops.metrics import faithfulness, answer_relevance, context_recall
ctx=['El límite de viáticos es de USD 150 por día en viajes nacionales.']
print('fiel     ', faithfulness('El límite de viáticos es de USD 150 por día en viajes nacionales.', ctx))
print('inventado', faithfulness('El Director aprobó un bono extraordinario para todos los empleados del sur.', ctx))
print('recall   ', context_recall(['1.3','3.2'], ['1.3']))
print('relevance', answer_relevance('viaje internacional sin autorización','El viaje internacional requiere autorización previa'))"
```
**Debes ver:** 1.0, 0.0, 1.0, 0.75. **Explica:** Faithfulness = ¿la respuesta se sostiene en el contexto?; Answer Relevance = ¿responde la pregunta?; Context Recall = ¿el retrieval trajo lo necesario? (así sabes si falla el retrieval o la generación).
Evaluación del conjunto:
```powershell
python -c "
from agentops.eval_gate import run_eval; import json; print(json.dumps(run_eval()['promedio'], indent=1))"
```
**Debes ver:** faithfulness 1.0, answer_relevance ≈ 0.63, context_recall ≈ 0.92.
**Agent Platform Evals (antes Gen AI evaluation service / Vertex AI Evaluation), cloud:** en un notebook, busca en la documentación vigente el SDK de evaluación (antes `from vertexai.evaluation import EvalTask, PointwiseMetric`; el módulo puede haber cambiado) con un dataset (`prompt`, `response`, `context`) y métricas model-based (groundedness / fulfillment). Corre la misma tabla y compara con la versión léxica: es buen material de discusión (son aproximaciones).

## Contenido 2 – Evaluación de interacciones A2A
```powershell
python -c "
from agentops.metrics import A2ATrace, delegation_metrics
print(delegation_metrics([A2ATrace('sql','sql',True), A2ATrace('rag','sql',False), A2ATrace('ml','ml',True)]))"
```
**Debes ver:** `tasa_exito_delegacion` 0.6667, `precision_ruta` 0.6667. **Ejercicio:** arma 10 preguntas con el agente esperado y registra los `A2ATrace` reales leyendo el Trace de ADK.

## Contenido 3 – Observabilidad, trazas y costos
1. Tracer didáctico:
```powershell
python -c "
from agentops.governance import Tracer, token_cost
t=Tracer()
with t.span('a2a.delegate', **{'from':'supervisor','to':'agente_sql'}): pass
print(t.a2a_hops(), t.spans[0].ms, 'ms'); print(token_cost(120000, 8000))"
```
2. Cloud Trace y Logging reales: habilita APIs (`cloudtrace`, `logging`); ADK emite spans OpenTelemetry; al desplegar en Agent Engine activa el tracing (flag/opción de despliegue — validar en tu versión) y abre *Cloud Trace → Trace explorer*. **Debes ver** spans por llamada de agente/herramienta/LLM.
3. Auditoría: en *Logs Explorer* filtra por `resource.type="aiplatform.googleapis.com/ReasoningEngine"` (validar el tipo de recurso) y revisa entradas. Usa `audit_record(...)` para escribir registros estructurados con PII enmascarada.
4. Costo: actualiza `PRICE_PER_M` con la tarifa vigente y calcula tokens reales de la respuesta (`usage_metadata`).

## Contenido 4 – Seguridad y gobernanza financiera
1. DLP:
```powershell
python -c "
from agentops.governance import mask_pii
print(mask_pii('Escríbeme a ana@empresa.com, tarjeta 4111 1111 1111 1111, CLABE 012345678901234567'))"
```
**Debes ver:** `[EMAIL]`, `[TARJETA]`, `[CLABE...]`. Con `AGENTS_MODE=cloud` usa Cloud DLP (`dlp_mask`); prueba con `gcloud services enable dlp.googleapis.com`.
2. IAM mínimo: sigue `ci/iam_least_privilege.md`. Comandos ejemplo:
```powershell
gcloud iam service-accounts create sa-agente-runtime
gcloud projects add-iam-policy-binding TU_PROYECTO --member="serviceAccount:sa-agente-runtime@TU_PROYECTO.iam.gserviceaccount.com" --role="roles/aiplatform.user"
```
3. VPC Service Controls: muestra en consola *Security → VPC Service Controls* y crea un perímetro en **modo dry-run** con `aiplatform`, `bigquery`, `dlp`. **Explica** exfiltración y por qué dry-run primero. (Requiere permisos de organización: si no los tienes, muéstralo con capturas.)

## Contenido 4b – Gobernanza en la plataforma (de tus notas; demostración en consola/slides)
Una vez desplegado el agente, la gobernanza da "seguridad y control para confiarle tareas reales". Recorre estos controles (ubica cada uno en la consola y anota su nombre actual):
- **Identidad del agente:** al desplegar en Agent Runtime cada agente obtiene su propio principal IAM → sabes *qué agente* hizo *qué acción*.
- **Agent Registry:** cataloga automáticamente los agentes desplegados y los servidores MCP (propios y de terceros); se pueden registrar agentes A2A.
- **Políticas de acceso (IAM):** qué agentes pueden usar qué herramientas y a qué otros agentes llamar (políticas sobre herramientas y sobre el registro).
- **Protección de datos sensibles en entradas/salidas:** plantillas de protección de modelos y datos (probablemente *Model Armor*: verifícalo en la consola) junto con DLP.
- **Agent Gateway:** punto único de entrada/salida que audita y aplica políticas (tus notas dicen "API Gateway"; la documentación de escalado lo nombra **Agent Gateway**).
- **Detección de anomalías:** un LLM como evaluador observa patrones de razonamiento y marca comportamientos raros o estancados.
- **Observabilidad:** trazas automáticas de por qué el agente decidió algo y qué herramientas llamó (Cloud Trace; en `adk deploy` usa `--trace_to_cloud`); **topología de agentes** para ver gráficamente sistemas multiagente/MCP.
**Explica:** los agentes no son 100 % deterministas → se necesita visibilidad, identidad y control, no solo pruebas.

## Contenido 4c – Evaluación, simulación y optimización (de tus notas)
- Las pruebas unitarias clásicas no bastan con IA generativa (no determinista): se usa **evaluación de agentes** (interacciones de varios pasos).
- **Simulación de agentes:** genera miles de interacciones de muestra para probar antes de producción (no escribir casos a mano).
- **Optimizador:** refina las instrucciones a partir de señales de fallo; puede cerrar un bucle de retroalimentación continuo.
- En código: `adk eval <paquete_del_agente> <eval_set>` existe en la CLI de ADK 2.11 (verifica el formato del eval set en https://adk.dev, sección Evaluate). Lo nuestro (`eval_gate.py`) es el gate barato y determinista; esto sería la versión model-based.

## Contenido 5 – CI/CD para agentes
1. Gate local:
```powershell
python -m agentops.eval_gate --threshold 0.85 --report eval_report.json ; $LASTEXITCODE   # 0
```
Abre `eval_report.json` (`autorizado: true`).
2. Rompe el agente a propósito: en `eval_gate.py`, dentro de `offline_agent`, cambia `"answer"` por una frase inventada (p. ej. "La empresa otorgó un bono secreto a los directores en el extranjero este mes.") y repite → **exit code 1, BLOQUEADO**. Revierte el cambio.
3. Pipeline en la nube:
```powershell
gcloud artifacts repositories create agentes-bi --repository-format=docker --location=us-central1
gcloud builds submit --config modulo5_agentops/ci/cloudbuild.yaml --substitutions=_REGION=us-central1,_THRESHOLD=0.85 .
```
Necesitas un `Dockerfile` en la raíz (un `FROM python:3.11-slim`, `COPY . .`, `pip install -r requirements.txt` basta para la demo). **Debes ver** los pasos: install → unit-tests → eval-faithfulness-gate → build → push → deploy. Con el agente roto, el pipeline **se detiene en el gate** y no despliega.
> `adk deploy agent_engine` existe en google-adk 2.11 (verificado con `--help`; también `cloud_run`, `gke`, `docker`). **No se ha ejecutado un despliegue real**: haz uno de prueba. El despliegue empaqueta la carpeta del agente; como el capstone importa `shared/`, `rag/`, `sqlagent/`, `bi_agents/` y `data/`, inclúyelos con `--extra_packages` o reorganiza el agente como paquete autocontenido.
> `agents-cli` (`google-agents-cli`, el que cita el PDF) **sí existe**: `uvx google-agents-cli setup`; lo opera un agente de código (Claude Code, Antigravity, Codex) y requiere Python 3.11+, `uv`, Node.js (y gcloud + Terraform para desplegar). Confirma con el cliente cuál herramienta usan.

---
## Entregable práctico – Pipeline con gate de Faithfulness
- [ ] `python -m pytest modulo5_agentops -q` → 8 passed.
- [ ] Gate verde (exit 0) con el agente correcto y rojo (exit 1) con el agente que alucina.
- [ ] `cloudbuild.yaml` ejecutado: un build autorizado y uno bloqueado (capturas para la clase).
- [ ] Trazas A2A visibles y registros con PII enmascarada.

## Listo para dar clase si…
Puedes ejecutar en vivo el gate verde/rojo, explicar qué mide cada métrica y qué limitación tienen las métricas léxicas.
