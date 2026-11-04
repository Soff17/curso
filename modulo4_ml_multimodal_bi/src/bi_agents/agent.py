"""Agente ML & BI: forecast (modelo interno) + gráfica de Tableau (visión) -> diagnóstico integrado."""
from shared.config import MODEL_NAME

from .ml_tools import detectar_anomalias_gasto, estimar_probabilidad_mora, pronosticar_gasto
from .tableau_client import obtener_vista_tableau
from .vision import analizar_grafica


def diagnosticar_division(division: str, workbook: str = "Finanzas", vista: str = "GastoMensual") -> dict:
    """Diagnóstico integrado: pronóstico ML + lectura visual de la gráfica de Tableau.

    Args:
        division: Norte, Sur, Centro u Occidente.
        workbook: libro de Tableau.
        vista: vista de Tableau con la tendencia.
    """
    fc = pronosticar_gasto(division, 3)
    view = obtener_vista_tableau(workbook, vista, division)
    if fc["status"] != "ok" or view["status"] != "ok":
        return {"status": "error", "forecast": fc, "vista": {k: v for k, v in view.items() if k != "png"}}
    lectura = analizar_grafica(view["png"], f"Division {division}.", view.get("serie"))
    ultimo = fc["historico"][-1]
    siguiente = fc["puntos"][0]["pronostico"]
    return {"status": "ok", "division": division, "forecast": fc["puntos"],
            "lectura_visual": lectura, "fuente_grafica": view["fuente"],
            "consistencia": "coherente" if (siguiente >= ultimo) == (fc["pendiente"] > 0) else "revisar"}


def build_ml_bi_agent():
    from google.adk.agents import Agent   # verificado: google-adk 2.11.0
    return Agent(
        name="agente_ml_bi",
        model=MODEL_NAME,
        description="Invoca modelos internos de ML (forecast, mora, anomalías) y valida visualmente en Tableau.",
        instruction=("Usa diagnosticar_division para forecast+gráfica y estimar_probabilidad_mora para riesgo. "
                     "Reporta cifras exactas del modelo, indica el nombre/versión del modelo y si la gráfica "
                     "confirma o contradice el resultado. No inventes valores."),
        tools=[diagnosticar_division, estimar_probabilidad_mora, detectar_anomalias_gasto],
    )
