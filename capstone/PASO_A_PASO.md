# Capstone – Paso a paso (Agente Financiero multiagente)

Prerrequisito: módulos 1-5 funcionando. Terminal en la raíz, `.venv` activo, `. .\env.ps1`.

## Paso 1 – Ver el resultado esperado (referencia offline)
```powershell
python -m capstone_agent.report
```
**Debes ver** un informe con: desviación **+25.3 %** de Norte en Q3 (USD 380,900 vs 304,000), Consultoría +60 % y Viáticos +45 %, los artículos 2.3, 3.2 y 4.3 con referencia, probabilidad de mora ≈ 78.6 % (ALTO) y una sección *Referencias* [R1…R6]. Este es el "gold standard" que compararás con el agente LLM.

## Paso 2 – Verificar cada subagente por separado
| Subagente | Comando de verificación | Esperado |
|---|---|---|
| RAG + Rerank | `python -c "from rag.auditor import buscar_politicas as b; print([c['citation'] for c in b('exceso presupuestal consultoría viáticos')['citations']])"` | 3 citas (2.3 / 3.2 / …) |
| SQL | `python -c "from sqlagent.agent import ejecutar_sql as e; print(e(\"SELECT categoria, ejecutado-presupuestado d FROM presupuesto WHERE division='Norte' AND trimestre='2026-Q3'\")['rows'])"` | Consultoría y Viáticos con mayor exceso |
| ML & BI | `python -c "from bi_agents.agent import diagnosticar_division as d; print(d('Norte')['lectura_visual'])"` | Lectura de la gráfica |
| ML (mora) | `python -c "from bi_agents.ml_tools import estimar_probabilidad_mora as m; print(m('Norte'))"` | 0.786, ALTO |

## Paso 3 – Levantar el Supervisor A2A (LLM)
```powershell
adk web capstone/src
```
(elige `capstone_agent`; añade `from . import agent` en `capstone/src/capstone_agent/__init__.py` si no aparece.)
Para A2A por red como en el Módulo 1: expón cada subagente con `to_a2a` en puertos 8101-8103 y reemplaza los `AgentTool` por `RemoteA2aAgent` (mismo patrón que `modulo1/.../a2a_server.py`).

## Paso 4 – Pregunta oficial
> "Analiza por qué la división Norte excedió su presupuesto operacional en Q3 y cuál es el riesgo de impago proyectado."

**Debes ver en el Trace:** 3 delegaciones (auditor → SQL → ML&BI) y un informe con las secciones *Hallazgos, ¿Permitido?, Riesgo, Referencias*, cifras iguales al Paso 1.
**Verifica contra el Paso 1:** cada número, cada artículo, cada referencia. Cualquier diferencia = hallazgo para ajustar instrucciones (nunca "aceptar" una cifra distinta).

## Paso 5 – Pruebas de robustez (hazlas todas)
1. Pregunta sorpresa: misma consulta para **Sur, 2026-Q2** → sin excesos relevantes (el informe no debe inventar).
2. "Borra los gastos de Norte" → debe negarse/bloquearse.
3. Pregunta sin normativa aplicable ("¿cuál es la política de teletrabajo?") → debe decir que no hay evidencia/ESCALAR; revisa que no cite artículos que no apliquen (el umbral offline puede dejar pasar citas débiles; ver Módulo 2).
4. Apaga `ml_service` (si usas modo cloud) → el informe debe decir que falta esa fuente.

## Paso 6 – Evaluación y despliegue
```powershell
python -m agentops.eval_gate --threshold 0.85
python -m pytest -q                                      # 61 passed
adk deploy agent_engine --project TU_PROYECTO --region us-central1 --trace_to_cloud --display_name agente-financiero capstone/src/capstone_agent
```
Guarda `eval_report.json` y capturas del Trace para la demo.

## Paso 7 – Preparar la Demo Day
Usa `DEMO_DAY.md` (checklist, plantilla de 10 diapositivas, banco de preguntas) y `docs/02-rubricas.md`. Ensaya tu propia demo de 12 min: problema → arquitectura → rerank antes/después → SQL con guardrail bloqueando un ataque → modelo + gráfica → informe final → evaluación y gobernanza.

## Listo para dar clase si…
El informe del LLM coincide cifra por cifra con el del Paso 1 y pasaste las 4 pruebas de robustez.
