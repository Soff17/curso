"""Agente Financiero del Capstone: Supervisor A2A + 3 subagentes (RAG+Rerank, SQL, ML&BI).

`adk web capstone/src` o despliegue con `adk deploy agent_engine capstone/src/capstone_agent`.
"""
from google.adk.agents import Agent   # verificado: google-adk 2.11.0
from google.adk.tools.agent_tool import AgentTool   # verificado: google-adk 2.11.0

from bi_agents.agent import build_ml_bi_agent
from rag.auditor import build_auditor_agent
from shared.config import MODEL_NAME
from sqlagent.agent import build_sql_agent

auditor = build_auditor_agent()
sql_agent = build_sql_agent()
ml_bi = build_ml_bi_agent()

root_agent = Agent(
    name="supervisor_financiero",
    model=MODEL_NAME,
    description="Orquestador del análisis financiero multiagente.",
    instruction=(
        "Eres el Supervisor Financiero. Para preguntas de desviación presupuestal y riesgo:\n"
        "1) auditor_politicas: ¿el exceso estaba permitido? (top-3 artículos tras rerank)\n"
        "2) agente_sql: desgloses exactos por categoría/trimestre\n"
        "3) agente_ml_bi: probabilidad de mora y validación visual en Tableau\n"
        "Informe ejecutivo: cada afirmación numérica o normativa lleva una referencia [R#] a su "
        "fuente (consulta SQL, artículo, modelo). Si una fuente falla o no hay evidencia, dilo; "
        "NUNCA completes con conocimiento propio. Estructura: Hallazgos, ¿Permitido?, Riesgo, Referencias."
    ),
    tools=[AgentTool(agent=auditor), AgentTool(agent=sql_agent), AgentTool(agent=ml_bi)],
)
