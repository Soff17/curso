import json

from agentops.eval_gate import main, offline_agent, run_eval
from agentops.governance import Tracer, audit_record, mask_pii, token_cost
from agentops.metrics import (A2ATrace, answer_relevance, context_recall, delegation_metrics,
                              faithfulness)


def test_faithfulness_detecta_alucinacion():
    ctx = ["El límite de viáticos es de USD 150 por día en viajes nacionales."]
    fiel = "El límite de viáticos es de USD 150 por día en viajes nacionales."
    inventado = "El Director aprobó un bono extraordinario para todos los empleados del sur."
    assert faithfulness(fiel, ctx) == 1.0
    assert faithfulness(inventado, ctx) == 0.0


def test_metricas_basicas():
    assert context_recall(["a", "b"], ["a", "c"]) == 0.5
    assert 0 < answer_relevance("viaje internacional", "el viaje internacional requiere autorización") <= 1


def test_delegacion():
    m = delegation_metrics([A2ATrace("sql", "sql", True), A2ATrace("rag", "sql", False)])
    assert m == {"tasa_exito_delegacion": 0.5, "precision_ruta": 0.5}


def test_gate_autoriza_agente_fiel(tmp_path):
    assert main(["--threshold", "0.85", "--report", str(tmp_path / "r.json")]) == 0
    assert json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))["autorizado"] is True


def test_gate_bloquea_agente_que_alucina(monkeypatch, tmp_path):
    def malo(q):
        r = offline_agent(q)
        r["answer"] = "La empresa otorgó un bono secreto a los directores en el extranjero este mes."
        return r
    rep = run_eval(malo)
    assert rep["promedio"]["faithfulness"] < 0.85
    monkeypatch.setattr("agentops.eval_gate.offline_agent", malo)
    monkeypatch.setattr("agentops.eval_gate.run_eval", lambda f=malo: run_eval(malo))
    assert main(["--threshold", "0.85", "--report", str(tmp_path / "r.json")]) == 1


def test_dlp_enmascara():
    t = mask_pii("Escríbeme a ana@empresa.com, tarjeta 4111 1111 1111 1111, CLABE 012345678901234567")
    assert "ana@" not in t and "4111" not in t and "0123456789" not in t


def test_audit_record_enmascara():
    r = audit_record("sql", "mi correo es x@y.com", "ok", ["POL-VIA-2026#1.3"])
    assert "x@y.com" not in json.dumps(r)


def test_tracer_y_costo():
    tr = Tracer()
    with tr.span("a2a.delegate", **{"from": "supervisor", "to": "sql"}):
        pass
    assert tr.a2a_hops() == [("supervisor", "sql")]
    assert token_cost(1_000_000, 0) == 0.30
