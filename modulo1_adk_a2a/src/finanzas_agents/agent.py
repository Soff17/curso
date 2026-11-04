"""Agentes del Módulo 1 (ADK Code-First). `adk web` / `adk run` buscan `root_agent` en este paquete.

Es el mismo árbol que se construye paso a paso en el notebook (Partes 2, 3 y 7):

    supervisor_finanzas  (root_agent)
     ├── especialista_presupuestos   → herramienta consultar_presupuesto
     └── especialista_tesoreria      → sin herramientas (ver su instrucción)

Dos formas de delegar:
  1) sub_agents  → hand-off jerárquico dentro del mismo proceso (transfer_to_agent).
  2) A2A remoto  → el especialista de presupuestos también se expone por red: ver a2a_server.py.

Para ampliarlo en los módulos siguientes: agrega herramientas al especialista que corresponda, o crea otro
especialista y añádelo a `sub_agents` del supervisor. Recuerda: un agente solo puede tener UN padre.
"""
from google.adk.agents import Agent   # verificado: google-adk 2.11.0

from shared.config import MODEL_NAME

from .tools import consultar_presupuesto

presupuestos_agent = Agent(
    name="especialista_presupuestos",
    model=MODEL_NAME,
    description=("Especialista en presupuestos: consulta presupuesto vs ejecutado por "
                 "división, trimestre y categoría, y calcula desviaciones."),
    instruction=(
        "Eres un analista de presupuestos. Usa SIEMPRE la herramienta consultar_presupuesto; "
        "nunca inventes cifras. Responde con totales, desviación % y las 2 categorías con "
        "mayor exceso. Si falta división o trimestre, pídelos. "
        "Reporta las cifras EXACTAMENTE como las devuelve la herramienta: mismas unidades, "
        "sin multiplicarlas, convertirlas ni redondearlas."
    ),
    tools=[consultar_presupuesto],
)

tesoreria_agent = Agent(
    name="especialista_tesoreria",
    model=MODEL_NAME,
    description="Flujo de caja, liquidez y pagos.",
    instruction=(
        "Eres el especialista de Tesorería (flujo de caja, liquidez y pagos). "
        "No tienes herramientas ni acceso a datos de la empresa: no des cifras ni inventes datos; "
        "si te piden un dato, explica qué información necesitarías. "
        "Si te preguntan por presupuesto o ejecución, devuelve el control."
    ),
)

root_agent = Agent(
    name="supervisor_finanzas",
    model=MODEL_NAME,
    description="Orquestador financiero que delega a especialistas.",
    instruction=(
        "Eres el Supervisor de Finanzas. Analiza la solicitud y delega:\n"
        "- Preguntas de presupuesto/ejecución -> especialista_presupuestos.\n"
        "- Preguntas de liquidez/caja/pagos -> especialista_tesoreria.\n"
        "Conserva el contexto de la conversación (división y trimestre ya mencionados) "
        "para preguntas de seguimiento. Resume la respuesta final con cifras exactas."
    ),
    sub_agents=[presupuestos_agent, tesoreria_agent],
)
