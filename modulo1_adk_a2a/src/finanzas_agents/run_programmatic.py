"""Invocar el agente por código (sin `adk run`/`adk web`): hay que proporcionar servicios y un Runner.

- SessionService: guarda la conversación (en memoria: se pierde al cerrar; en producción, base de datos).
- ArtifactService: guarda salidas/archivos que otros agentes pueden recuperar.
- Runner: toma el mensaje, reúne los servicios e invoca al agente raíz; emite EVENTOS de forma asíncrona.

Uso (requiere credenciales de Gemini):  python -m finanzas_agents.run_programmatic
Verificado con google-adk 2.11.0 (la construcción; la ejecución requiere modelo).
"""
import asyncio

from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent

APP, USER, SESSION = "finanzas_app", "analista1", "s1"


async def ask(runner: Runner, text: str) -> str:
    msg = types.Content(role="user", parts=[types.Part(text=text)])
    final = ""
    async for event in runner.run_async(user_id=USER, session_id=SESSION, new_message=msg):
        # Cada acción (llamada a herramienta, transferencia, respuesta) es un evento.
        if event.is_final_response() and event.content and event.content.parts:
            final = event.content.parts[0].text
    return final


async def main() -> None:
    session_service = InMemorySessionService()
    runner = Runner(app_name=APP, agent=root_agent, session_service=session_service,
                    artifact_service=InMemoryArtifactService())
    await session_service.create_session(app_name=APP, user_id=USER, session_id=SESSION)
    print(await ask(runner, "¿Cómo va la división Norte en 2026-Q3?"))
    print(await ask(runner, "¿Y en 2026-Q2?"))  # misma sesión -> conserva contexto


if __name__ == "__main__":
    asyncio.run(main())
