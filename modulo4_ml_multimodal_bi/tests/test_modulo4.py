import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from bi_agents.agent import diagnosticar_division
from bi_agents.ml_tools import estimar_probabilidad_mora, pronosticar_gasto
from bi_agents.tableau_client import obtener_vista_tableau
from ml_service.app import app
from ml_service.models import detect_anomalies, forecast


def test_forecast_lineal_exacto():
    r = forecast([10, 20, 30, 40], 2)
    assert [p["pronostico"] for p in r["puntos"]] == [50.0, 60.0]


def test_forecast_requiere_datos():
    with pytest.raises(ValueError):
        forecast([1, 2])


def test_anomalias():
    assert detect_anomalies([10, 11, 10, 12, 10, 11, 100])["anomalias"][0]["indice"] == 6


def test_api_valida_payload():
    c = TestClient(app)
    assert c.post("/forecast", json={"serie": [1, 2]}).status_code == 422
    assert c.post("/credit-score", json={"pct_cartera_mora": 2, "dias_vencido_prom": 1, "monto_expuesto": 1}).status_code == 422
    assert c.post("/forecast", json={"serie": [1, 2, 3], "horizonte": 1}).json()["puntos"][0]["pronostico"] == 4.0


def test_mora_norte_mayor_que_sur():
    n, s = estimar_probabilidad_mora("Norte"), estimar_probabilidad_mora("Sur")
    assert n["probabilidad_mora"] > s["probabilidad_mora"]
    assert n["riesgo"] in {"MEDIO", "ALTO"}


def test_vista_stub_es_png():
    v = obtener_vista_tableau("Finanzas", "GastoMensual", "Norte")
    assert v["png"].startswith(b"\x89PNG")


def test_diagnostico_integrado():
    d = diagnosticar_division("Norte")
    assert d["status"] == "ok" and len(d["forecast"]) == 3 and d["lectura_visual"]
