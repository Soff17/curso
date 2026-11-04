"""Pruebas que requieren google-adk instalado (se omiten si no está). No llaman a ningún modelo."""
import pytest

pytest.importorskip("google.adk")

from google.adk.cli.utils.agent_loader import AgentLoader  # noqa: E402
from google.adk.agents import LoopAgent, ParallelAgent, SequentialAgent  # noqa: E402

from shared.config import ROOT  # noqa: E402


def test_adk_descubre_el_paquete_y_su_root_agent():
    loader = AgentLoader(str(ROOT / "modulo1_adk_a2a" / "src"))
    assert "finanzas_agents" in loader.list_agents()
    assert loader.load_agent("finanzas_agents").name == "supervisor_finanzas"


def test_supervisor_tiene_los_dos_especialistas():
    from finanzas_agents.agent import root_agent
    assert [a.name for a in root_agent.sub_agents] == ["especialista_presupuestos", "especialista_tesoreria"]


def test_workflows_construyen_con_output_key():
    from finanzas_agents import workflows as w
    assert isinstance(w.pipeline_secuencial, SequentialAgent)
    assert isinstance(w.comparador, ParallelAgent)
    assert isinstance(w.refinador, LoopAgent) and w.refinador.max_iterations == 3
    assert w.analista.output_key == "analisis_presupuesto"


def test_agent_card_a2a_publicada():
    from fastapi.testclient import TestClient
    from finanzas_agents.a2a_server import a2a_app
    with TestClient(a2a_app) as c:  # with: arranca el lifespan que registra las rutas
        r = c.get("/.well-known/agent-card.json")
    assert r.status_code == 200 and r.json()["name"] == "especialista_presupuestos"


def test_router_tiene_dos_especialistas_remotos():
    from finanzas_agents.a2a_server import supervisor_router
    assert [a.name for a in supervisor_router.sub_agents] == ["especialista_presupuestos", "especialista_tesoreria"]


def test_agent_card_tesoreria_publicada():
    from fastapi.testclient import TestClient
    from finanzas_agents.a2a_server import a2a_app_tesoreria
    with TestClient(a2a_app_tesoreria) as c:
        r = c.get("/.well-known/agent-card.json")
    assert r.status_code == 200 and r.json()["name"] == "especialista_tesoreria"
