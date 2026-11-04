# Análisis del cronograma

## Resumen

- **Audiencia:** Equipo de BI, 30 personas en 5 células de 6.
- **Duración:** 6 semanas × 4 h = 24 h. Cada semana: 2 h sesión teórico-práctica + 2 h tutoría/code review.
- **Hilo conductor:** un agente financiero que crece módulo a módulo hasta el Capstone ("¿Por qué la división Norte excedió su presupuesto operacional en Q3 y cuál es el riesgo de impago proyectado?").

| Sem | Módulo | Entregable del PDF | Carpeta |
|---|---|---|---|
| 1 | Code-First ADK + A2A | 2 agentes Python: Supervisor de Finanzas → Especialista en Presupuestos, manteniendo estado | `modulo1_adk_a2a` |
| 2 | RAG financiero + Reranking | Agente Auditor de Políticas: K=20 → rerank → N=3, justifica aprobación/rechazo de gasto | `modulo2_rag_reranking` |
| 3 | SQL Server/BigQuery + RAG estructurado | Agente que rerankea catálogo, genera/ejecuta SQL y contrasta con presupuesto del informe RAG | `modulo3_sql_bigquery` |
| 4 | ML interno + Multimodal + BI | Agente que invoca (A2A) modelo de forecasting, extrae gráfica de Tableau y diagnostica | `modulo4_ml_multimodal_bi` |
| 5 | AgentOps, evaluación, gobernanza | Pipeline CI/CD con gate de Faithfulness antes de desplegar en Agent Engine | `modulo5_agentops` |
| 6 | Capstone & Demo Day | Presentación y evaluación del Agente Financiero de cada célula | `capstone` |

## Observaciones sobre el cronograma

1. **Carga alta por módulo.** Módulo 4 junta ML por Function Calling, Gemini Vision y dos APIs de BI en 4 h. Recomiendo repartir: 2 h teoría = ML + Vision; tutoría = Tableau API.
2. **Semana 3 y 4 aparecen en una sola fila del PDF**, pero son dos módulos de 4 h cada uno (semanas distintas).
3. **"Data Studio"** hoy se llama **Looker Studio**. No tiene un "SDK" equivalente a Tableau REST; la integración programática es vía Looker Studio Linking API / conectores / BigQuery como fuente. Hay que aclarar con el cliente qué se espera. En el material trato Tableau como integración principal y Looker Studio como captura de pantalla + fuente BigQuery.
4. **`google-agents-cli`** (Módulo 5) **sí existe** (comando `agents-cli`; instalación `uvx google-agents-cli setup`). Está pensada para que un agente de código (Claude Code, Antigravity, Codex) cree, evalúe y despliegue agentes ADK; requiere Python 3.11+, `uv`, Node.js y, para desplegar, gcloud y Terraform. Los subcomandos de despliegue/evaluación no los documenta adk.dev como CLI (se piden por prompt al agente de código). El material usa `adk deploy agent_engine` / `adk eval` (verificados en la CLI de ADK 2.11) y menciona agents-cli como alternativa. Confirma con el cliente cuál usan.
5. **Reranking:** el PDF cita Ranking API, Cohere Rerank y BGE-Reranker. Se implementa Vertex AI Ranking API (cloud) y un reranker léxico/cross-encoder local (offline). K=20 y N=3 son parámetros fijos del entregable.
6. **A2A:** en ADK existe tanto sub-agentes locales (`sub_agents`, transferencia dentro del mismo proceso) como el protocolo A2A real (servidor HTTP + `RemoteA2aAgent`). El módulo 1 enseña ambos: primero hand-off local, luego A2A por red.
7. **SQL Server desde GCP** requiere conectividad (VPN/Cloud SQL for SQL Server/Private Service Connect). Es el mayor riesgo logístico; se provee SQLite como sustituto y el conector real aislado.
8. **Evaluación del Capstone:** el PDF no define criterios. Propongo rúbrica en `02-rubricas.md`.

## Riesgos y mitigación

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Cuotas / permisos GCP para 30 personas | Bloquea labs | Proyecto por célula (5), cuotas pre-solicitadas, `03-setup-gcp.md` |
| Sin acceso a SQL Server/Tableau reales | Bloquea M3/M4 | Modo offline con SQLite y stubs de Tableau |
| Cambios de API en ADK/Vertex | Código roto | Fijar versiones en `requirements.txt` tras validar; smoke test previo |
| Diferencias de nivel Python entre alumnos | Ritmo desigual | Parejas por célula; ejercicios base en notebook; tutoría por célula |
| Datos sensibles reales | Cumplimiento | Solo datos sintéticos; DLP en M5 |

## Preguntas abiertas para el cliente

1. ¿Proyecto GCP y región ya definidos? ¿Habilitada Agent Engine en esa región?
2. ¿SQL Server on-prem o Cloud SQL? ¿Hay red privada hacia GCP?
3. ¿Tableau Server/Cloud? ¿Se pueden crear Personal Access Tokens?
4. ¿Qué modelos ML internos existen realmente (credit scoring, forecasting, anomalías) y cómo se exponen?
5. ¿El idioma de la sesión y del material es español (asumido)?
6. ¿Evaluación formal / certificación al final?
