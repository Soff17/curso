# Plan del instructor – 6 semanas

Formato semanal: **Sesión teórico-práctica 2 h** (grupo completo, 30 personas) + **Tutoría / Code Review 2 h** (por células; sugiero 5 bloques de ~25 min o 2 turnos de 2 h con 2-3 células).

## Semana 1 – ADK Code-First y A2A

**Sesión (2 h)**
| Min | Actividad |
|---|---|
| 0-15 | Bienvenida, formación de células, roles (líder técnico, datos, QA, relator, etc.) |
| 15-40 | Arquitectura: Agent Engine, Memory Bank, Model Garden, de Low-Code a Code-First |
| 40-60 | Setup: venv, `google-adk`, `adk web`, autenticación |
| 60-90 | Primer agente (`modulo1/src/finanzas_agents/base_agent.py`) + herramientas tipadas |
| 90-115 | A2A: patrón Supervisor/Router-Worker, hand-off jerárquico, Pydantic como contrato |
| 115-120 | Cierre y asignación del lab |

**Tutoría (2 h):** cada célula construye Supervisor + Especialista en Presupuestos, con estado de sesión. Code review: contratos Pydantic, nombres/descripciones de agentes (el router depende de ellos).
**Entregable:** ver "El lab: qué se entrega" en `modulo1_adk_a2a/SESION_PRACTICA.md`.

## Semana 2 – RAG financiero y Reranking

**Sesión:** chunking semántico en documentos contables (30 min) → embeddings/Vector Search (20) → two-stage retrieval K=20→N=3 y thresholding (40) → demo del Auditor de Políticas (30).
**Tutoría:** la célula ingesta `data/politicas/*.md`, construye el auditor y valida con 6 casos de gasto (`data/casos_gasto.json`).
**Trampa pedagógica:** mostrar con y sin rerank el mismo caso y comparar la cita devuelta.

## Semana 3 – Text-to-SQL con RAG de metadata + híbrido

**Sesión:** problema del esquema grande (15) → RAG del catálogo de datos (30) → guardrails SQL (read-only, timeout, LIMIT) (30) → BigQuery/BQML (25) → híbrido RAG+SQL (20).
**Tutoría:** conectar SQLite (o SQL Server real), generar consulta y contrastar contra presupuesto del informe.
**Discusión clave:** por qué el LLM nunca debe tener credenciales de escritura.

## Semana 4 – ML interno, multimodalidad y BI

**Sesión:** Function Calling hacia FastAPI/Vertex Prediction (30) → Gemini Vision sobre dashboards (30) → Tableau REST API (30) → A2A con agente de ML (30).
**Tutoría:** diagnóstico integrado forecast + gráfica + comentarios.
**Prerrequisito:** `ml_service` levantado (`uvicorn`) y capturas de ejemplo en `modulo4/.../samples`.

## Semana 5 – AgentOps, evaluación y gobernanza

**Sesión:** métricas RAG (Faithfulness, Answer Relevance, Context Recall) (35) → evaluación A2A (20) → trazabilidad/costos (25) → IAM/DLP/VPC-SC (25) → CI/CD (15).
**Tutoría:** pipeline que bloquea el deploy si Faithfulness < umbral (`modulo5/ci/cloudbuild.yaml`).

## Semana 6 – Capstone & Demo Day

**Sesión (2 h) – ensayo y ajustes:** checklist de integración, pruebas de la pregunta oficial.
**Tutoría (2 h) – Demo Day:** 5 células × ~15 min presentación + 8 min preguntas; evaluación con la rúbrica.

## Materiales a preparar por semana

- Diapositivas (outline en `SESION_TEORICA.md` de los módulos 1, 2 y 3 y en el `GUIA_INSTRUCTOR.md` de los módulos 4-5; se pueden convertir a PPTX).
- Notebook de ejercicios base (equivalente a los scripts de `src/`).
- Repositorio por célula (plantilla = esta carpeta).
