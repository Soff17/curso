"""Helper didáctico: ejecuta un agente con Runner y muestra los EVENTOS (herramientas, transferencias, respuesta)."""
from google.adk.runners import InMemoryRunner
from google.genai import types

_runners: dict[int, InMemoryRunner] = {}   # clave = id(agente): si reconstruyes el agente, se crea otro runner
APP, USER = "modulo1", "alumno"


async def preguntar(agent, texto: str, session_id: str = "s1", verbose: bool = True) -> str | None:
    """Envía `texto` al agente en la sesión `session_id` (misma sesión = misma conversación/estado).

    - `verbose=True` (por defecto): imprime los eventos y la respuesta, y devuelve `None`
      (así Jupyter no vuelve a mostrar la respuesta duplicada debajo de la celda).
    - `verbose=False`: no imprime nada y **devuelve el texto** de la respuesta (útil para guardarlo o comprobarlo).
    """
    runner = _runners.setdefault(id(agent), InMemoryRunner(agent=agent, app_name=APP))
    if not await runner.session_service.get_session(app_name=APP, user_id=USER, session_id=session_id):
        await runner.session_service.create_session(app_name=APP, user_id=USER, session_id=session_id)
    if verbose:
        print(f"👤 {texto}")
    final = ""
    msg = types.Content(role="user", parts=[types.Part(text=texto)])
    async for ev in runner.run_async(user_id=USER, session_id=session_id, new_message=msg):
        for p in (ev.content.parts if ev.content and ev.content.parts else []):
            if verbose and p.function_call:
                print(f"   🔧 [{ev.author}] llama {p.function_call.name}({dict(p.function_call.args or {})})")
            if verbose and p.function_response:
                r = str(p.function_response.response)
                print(f"   📥 [{ev.author}] resultado de {p.function_response.name}: {r[:110]}{'…' if len(r) > 110 else ''}")
        if ev.is_final_response() and ev.content and ev.content.parts:
            nuevo = "".join(p.text or "" for p in ev.content.parts)
            if verbose and nuevo != final:   # A2A remoto puede emitir la misma respuesta dos veces
                print(f"🤖 [{ev.author}] {nuevo}")
            final = nuevo
    return None if verbose else final


async def estado(agent, session_id: str = "s1") -> dict:
    """Devuelve el estado (state) guardado en la sesión: aquí aparecen los output_key."""
    runner = _runners[id(agent)]
    s = await runner.session_service.get_session(app_name=APP, user_id=USER, session_id=session_id)
    return dict(s.state) if s else {}
