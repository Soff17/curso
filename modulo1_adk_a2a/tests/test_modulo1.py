import pytest
from pydantic import ValidationError

from finanzas_agents.a2a_local import BudgetWorker, Supervisor
from finanzas_agents.contracts import BudgetRequest
from finanzas_agents.tools import consultar_presupuesto


def test_contrato_rechaza_division_invalida():
    with pytest.raises(ValidationError):
        BudgetRequest(division="Marte", trimestre="2026-Q3")


def test_contrato_rechaza_trimestre_invalido():
    with pytest.raises(ValidationError):
        BudgetRequest(division="Norte", trimestre="Q3-2026")


def test_tool_norte_q3_excede():
    r = consultar_presupuesto("Norte", "2026-Q3")
    assert r["status"] == "ok" and r["desviacion_pct"] > 15


def test_tool_error_estructurado():
    assert consultar_presupuesto("Norte", "1999-Q1")["status"] == "error"


def test_a2a_mantiene_estado_entre_turnos():
    sup = Supervisor(workers={"especialista_presupuestos": BudgetWorker()})
    assert sup.handshake("especialista_presupuestos").skills == ["presupuesto"]
    a = sup.ask("s1", "¿Cómo va la división Norte en Q3?")
    assert "Norte 2026-Q3" in a
    b = sup.ask("s1", "¿Y en Q2?")  # reutiliza la división del turno anterior
    assert "Norte 2026-Q2" in b
    assert sup.sessions["s1"]["division"] == "Norte"
