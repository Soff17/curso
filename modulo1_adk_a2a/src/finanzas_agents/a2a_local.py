"""Simulación A2A en proceso, SIN LLM ni GCP, para enseñar el protocolo y probar offline.

Muestra: handshake (agent card), envelope tipado, traspaso de contexto de sesión,
delegación y estado persistente entre turnos.
"""
import re
from dataclasses import dataclass, field

from .contracts import A2AEnvelope, BudgetRequest
from .tools import get_budget


@dataclass
class AgentCard:
    name: str
    skills: list[str]


class BudgetWorker:
    card = AgentCard(name="especialista_presupuestos", skills=["presupuesto"])

    def handle(self, env: A2AEnvelope) -> A2AEnvelope:
        req = BudgetRequest(**env.payload)  # contrato estricto: lanza ValidationError si no cumple
        resp = get_budget(req)
        return A2AEnvelope(session_id=env.session_id, sender=self.card.name, receiver=env.sender,
                           intent="presupuesto.respuesta", payload=resp.model_dump(),
                           context=env.context)


@dataclass
class Supervisor:
    workers: dict[str, BudgetWorker]
    sessions: dict[str, dict] = field(default_factory=dict)

    def handshake(self, worker_name: str) -> AgentCard:
        return self.workers[worker_name].card

    def ask(self, session_id: str, text: str) -> str:
        state = self.sessions.setdefault(session_id, {})  # estado de la conversación
        m = re.search(r"(Norte|Sur|Centro|Occidente)", text, re.I)
        q = re.search(r"(\d{4})?\s*-?\s*Q([1-4])", text, re.I)
        if m:
            state["division"] = m.group(1).capitalize()
        if q:
            state["trimestre"] = f"{q.group(1) or state.get('anio', '2026')}-Q{q.group(2)}"
            state["anio"] = state["trimestre"][:4]
        if "division" not in state or "trimestre" not in state:
            return "Necesito división y trimestre."
        env = A2AEnvelope(session_id=session_id, sender="supervisor_finanzas",
                          receiver="especialista_presupuestos", intent="presupuesto.consulta",
                          payload={"division": state["division"], "trimestre": state["trimestre"]},
                          context=dict(state))
        reply = self.workers["especialista_presupuestos"].handle(env)
        p = reply.payload
        state["ultima_desviacion"] = p["desviacion_pct"]
        return (f"{p['division']} {p['trimestre']}: presupuestado {p['total_presupuestado']:,.0f}, "
                f"ejecutado {p['total_ejecutado']:,.0f} ({p['desviacion_pct']:+.1f}%).")
