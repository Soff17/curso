"""Pruebas de la ESTRUCTURA del proyecto de agentes. No llaman a ningún modelo.

Comprueban lo que se rompe con más frecuencia al ampliar el proyecto: nombres inválidos o repetidos,
agentes sin descripción/instrucción, un supervisor que no menciona a sus especialistas y llaves de
`output_key` que no coinciden con las que usa el siguiente agente.
"""
import pytest

pytest.importorskip("google.adk")

from finanzas_agents import workflows as w  # noqa: E402
from finanzas_agents.agent import presupuestos_agent, root_agent, tesoreria_agent  # noqa: E402


def _arbol():
    return [root_agent, *root_agent.sub_agents]


def test_nombres_validos_y_unicos():
    nombres = [a.name for a in _arbol()]
    assert all(n.isidentifier() for n in nombres), nombres        # sin espacios ni tildes
    assert len(nombres) == len(set(nombres)), nombres


def test_cada_agente_tiene_description_e_instruction():
    for a in _arbol():
        assert (a.description or "").strip(), f"{a.name} sin description"
        assert (a.instruction or "").strip(), f"{a.name} sin instruction"


def test_cada_especialista_cuelga_del_supervisor():
    # Un agente solo puede tener UN padre: si falla, alguien lo reutilizó sin clone().
    assert all(a.parent_agent is not None and a.parent_agent.name == root_agent.name
               for a in root_agent.sub_agents)


def test_supervisor_menciona_a_sus_especialistas_en_la_instruccion():
    for a in root_agent.sub_agents:
        assert a.name in root_agent.instruction, f"la instrucción del supervisor no menciona a {a.name}"


def test_presupuestos_tiene_la_herramienta():
    assert [t.__name__ for t in presupuestos_agent.tools] == ["consultar_presupuesto"]


def test_tesoreria_no_tiene_herramientas():
    assert not tesoreria_agent.tools


def test_workflows_enlazan_las_llaves_de_estado():
    # La llave que guarda el analista debe ser la que lee el redactor con {llave}.
    assert "{" + w.analista.output_key + "}" in w.redactor.instruction
