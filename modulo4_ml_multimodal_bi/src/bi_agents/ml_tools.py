"""Function Calling hacia los modelos internos. Cloud: HTTP al servicio; offline: llamada en proceso."""
import os
import sqlite3

from shared.config import DB_PATH, is_cloud


def _call(path: str, payload: dict) -> dict:
    if is_cloud():
        import httpx
        r = httpx.post(os.environ["ML_SERVICE_URL"] + path, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()
    from ml_service import models
    if path == "/forecast":
        return models.forecast(payload["serie"], payload["horizonte"])
    if path == "/credit-score":
        return models.prob_mora(**payload)
    if path == "/anomalies":
        return models.detect_anomalies(payload["valores"])
    raise ValueError(path)


def serie_gasto_mensual(division: str) -> list[float]:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    rows = con.execute("SELECT substr(fecha,1,7) m, SUM(monto) FROM gastos WHERE division=? GROUP BY m ORDER BY m",
                       (division,)).fetchall()
    con.close()
    return [round(v, 2) for _, v in rows]


def pronosticar_gasto(division: str, horizonte: int = 3) -> dict:
    """Pronostica el gasto mensual de una división con el modelo interno de forecasting.

    Args:
        division: Norte, Sur, Centro u Occidente.
        horizonte: meses a pronosticar (1-12).
    """
    serie = serie_gasto_mensual(division)
    if len(serie) < 3:
        return {"status": "error", "message": "serie insuficiente"}
    return {"status": "ok", "division": division, "historico": serie,
            **_call("/forecast", {"serie": serie, "horizonte": horizonte})}


def estimar_probabilidad_mora(division: str, trimestre: str = "2026-Q3") -> dict:
    """Estima la probabilidad de mora de la cartera de una división con el modelo de credit scoring.

    Args:
        division: Norte, Sur, Centro u Occidente.
        trimestre: trimestre de corte AAAA-Qn.
    """
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    n, mora, dias, monto = con.execute(
        "SELECT COUNT(*), SUM(estado='en_mora'), AVG(dias_vencido), SUM(monto) "
        "FROM cuentas_por_cobrar WHERE division=? AND trimestre=?", (division, trimestre)).fetchone()
    con.close()
    if not n:
        return {"status": "error", "message": "sin cartera"}
    res = _call("/credit-score", {"pct_cartera_mora": mora / n, "dias_vencido_prom": dias,
                                  "monto_expuesto": monto})
    return {"status": "ok", "division": division, "pct_cartera_mora": round(mora / n, 3), **res}


def detectar_anomalias_gasto(division: str) -> dict:
    """Detecta meses anómalos en el gasto de una división."""
    return {"status": "ok", **_call("/anomalies", {"valores": serie_gasto_mensual(division)})}
