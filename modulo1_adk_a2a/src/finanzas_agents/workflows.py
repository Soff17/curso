"""Los 3 tipos de agentes de flujo de trabajo de ADK (heredan de BaseAgent) + paso de información con output_key.

- SequentialAgent: ejecuta sub-agentes en orden.
- ParallelAgent:   ejecuta sub-agentes a la vez.
- LoopAgent:       repite sub-agentes hasta max_iterations (o hasta que uno escale). No usa modelo ni instrucciones.
Verificado con google-adk 2.11.0.
"""
from google.adk.agents import Agent, LoopAgent, ParallelAgent, SequentialAgent

from shared.config import MODEL_NAME

from .tools import consultar_presupuesto

# output_key: la respuesta final del agente se guarda en el estado de la sesión bajo esa clave;
# el siguiente agente la lee con {clave} en su instrucción.
analista = Agent(
    name="analista_presupuesto",
    model=MODEL_NAME,
    description="Consulta presupuesto vs ejecutado y resume la desviación.",
    instruction=(
        "Usa consultar_presupuesto para la división y trimestre pedidos. Resume totales y desviación %. "
        "Reporta las cifras EXACTAMENTE como las devuelve la herramienta: mismas unidades, "
        "sin multiplicarlas, convertirlas ni redondearlas."
    ),
    tools=[consultar_presupuesto],
    output_key="analisis_presupuesto",
)

redactor = Agent(
    name="redactor_ejecutivo",
    model=MODEL_NAME,
    description="Redacta resúmenes ejecutivos.",
    instruction=(
        "Redacta un resumen ejecutivo de 3 líneas basado SOLO en este análisis: {analisis_presupuesto}. "
        "Copia las cifras tal cual aparecen en el análisis, sin cambiar sus unidades."
    ),
    output_key="resumen_ejecutivo",
)

# 1) Secuencial: analista -> redactor
pipeline_secuencial = SequentialAgent(name="pipeline_presupuesto", sub_agents=[analista, redactor])

# 2) Paralelo: dos analistas independientes (cada uno con su propia clave de salida)
analista_a = analista.clone(update={"name": "analista_a", "output_key": "analisis_a"})
analista_b = analista.clone(update={"name": "analista_b", "output_key": "analisis_b"})
comparador = ParallelAgent(name="comparador_paralelo", sub_agents=[analista_a, analista_b])

# 3) Bucle: refinar hasta 3 iteraciones (sin modelo, sin descripción/instrucción propias)
revisor = Agent(
    name="revisor",
    model=MODEL_NAME,
    description="Revisa y mejora el resumen.",
    instruction="Mejora la claridad de: {resumen_ejecutivo}. Mantén las cifras exactas.",
    output_key="resumen_ejecutivo",
)
refinador = LoopAgent(name="refinador", sub_agents=[revisor], max_iterations=3)
