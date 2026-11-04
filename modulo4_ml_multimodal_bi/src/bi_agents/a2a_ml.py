"""Agente ML expuesto por A2A (puerto 8002) y consumido por el agente BI.

Terminal 1: uvicorn bi_agents.a2a_ml:a2a_app --port 8002
Terminal 2: adk web modulo4_ml_multimodal_bi/src   (agente: bi_orquestador)
Imports verificados con google-adk 2.11.0.
"""
from google.adk.a2a.utils.agent_to_a2a import to_a2a   # verificado: google-adk 2.11.0
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent   # verificado: google-adk 2.11.0

from shared.config import MODEL_NAME

from .agent import build_ml_bi_agent, diagnosticar_division

ml_agent = build_ml_bi_agent()
a2a_app = to_a2a(ml_agent, port=8002)

ml_remoto = RemoteA2aAgent(
    name="agente_forecast_remoto",
    description="Agente con modelos internos de forecasting, mora y anomalías (A2A).",
    agent_card="http://localhost:8002/.well-known/agent-card.json",
)

bi_orquestador = Agent(
    name="bi_orquestador",
    model=MODEL_NAME,
    instruction=("Para pronósticos y riesgo delega al agente_forecast_remoto por A2A. Después usa "
                 "diagnosticar_division para ver la gráfica y concluye si confirma o contradice al modelo."),
    sub_agents=[ml_remoto],
    tools=[diagnosticar_division],
)
