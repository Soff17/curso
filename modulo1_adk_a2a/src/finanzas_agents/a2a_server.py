"""Expone el especialista como servidor A2A y el supervisor lo consume por red.

Terminal 1:  uvicorn finanzas_agents.a2a_server:a2a_app --port 8001
Terminal 2:  adk web   (usar supervisor_remoto)

Imports verificados con google-adk 2.11.0 (RemoteA2aAgent es experimental; ver parámetro use_legacy).
"""
from google.adk.a2a.utils.agent_to_a2a import to_a2a   # verificado: google-adk 2.11.0
from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent   # verificado: google-adk 2.11.0

from shared.config import MODEL_NAME

from .agent import presupuestos_agent, tesoreria_agent

# --- Servidor (agente worker) ---
a2a_app = to_a2a(presupuestos_agent, port=8001)

# --- Cliente (supervisor que delega por A2A) ---
presupuestos_remoto = RemoteA2aAgent(
    name="especialista_presupuestos_remoto",
    description="Especialista de presupuestos expuesto vía A2A.",
    agent_card="http://localhost:8001/.well-known/agent-card.json",
)

supervisor_remoto = Agent(
    name="supervisor_finanzas_remoto",
    model=MODEL_NAME,
    instruction="Delega consultas de presupuesto al especialista remoto y consolida la respuesta.",
    sub_agents=[presupuestos_remoto],
)


# --- Segundo especialista como servidor A2A (reto opcional 5.4) ---
# Terminal 3:  uvicorn finanzas_agents.a2a_server:a2a_app_tesoreria --port 8002
a2a_app_tesoreria = to_a2a(tesoreria_agent, port=8002)

# --- Router: un supervisor que enruta por red a DOS especialistas remotos ---
# Un agente solo puede tener UN padre: por eso son instancias nuevas, distintas de presupuestos_remoto.
presupuestos_rem = RemoteA2aAgent(
    name="especialista_presupuestos",
    description="Presupuesto vs ejecutado por división y trimestre.",
    agent_card="http://localhost:8001/.well-known/agent-card.json",
)
tesoreria_rem = RemoteA2aAgent(
    name="especialista_tesoreria",
    description="Flujo de caja, liquidez y pagos.",
    agent_card="http://localhost:8002/.well-known/agent-card.json",
)

supervisor_router = Agent(
    name="supervisor_router",
    model=MODEL_NAME,
    description="Supervisor que enruta por red a dos especialistas remotos.",
    instruction=("Eres el Supervisor de Finanzas. Presupuesto/ejecución -> especialista_presupuestos; "
                 "liquidez/caja/pagos -> especialista_tesoreria. Delega siempre en un especialista."),
    sub_agents=[presupuestos_rem, tesoreria_rem],
)
