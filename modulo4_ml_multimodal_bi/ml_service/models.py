"""Modelos 'internos' simulados del equipo de BI (sustituyen a los reales del cliente).

Son deliberadamente simples: el foco del módulo es CÓMO el agente los consume, no el modelo.
"""
import math
from statistics import mean, pstdev


def forecast(series: list[float], horizon: int = 3) -> dict:
    """Tendencia lineal por mínimos cuadrados + banda ±1.64σ de residuales."""
    n = len(series)
    if n < 3:
        raise ValueError("Se requieren al menos 3 observaciones")
    xs = list(range(n))
    mx, my = mean(xs), mean(series)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, series)) / sum((x - mx) ** 2 for x in xs)
    icpt = my - slope * mx
    resid = [y - (icpt + slope * x) for x, y in zip(xs, series)]
    sd = pstdev(resid)
    pts = []
    for h in range(1, horizon + 1):
        yhat = icpt + slope * (n - 1 + h)
        pts.append({"paso": h, "pronostico": round(yhat, 2),
                    "lo": round(yhat - 1.64 * sd, 2), "hi": round(yhat + 1.64 * sd, 2)})
    return {"modelo": "tendencia_lineal_v1", "pendiente": round(slope, 2), "puntos": pts}


def prob_mora(pct_cartera_mora: float, dias_vencido_prom: float, monto_expuesto: float) -> dict:
    """Regresión logística con coeficientes fijos (credit scoring de juguete)."""
    z = -3.0 + 4.0 * pct_cartera_mora + 0.02 * dias_vencido_prom + 0.000002 * monto_expuesto
    p = 1 / (1 + math.exp(-z))
    banda = "ALTO" if p >= 0.6 else "MEDIO" if p >= 0.3 else "BAJO"
    return {"modelo": "credit_scoring_v1", "probabilidad_mora": round(p, 4), "riesgo": banda}


def detect_anomalies(values: list[float], z_thr: float = 2.0) -> dict:
    mu, sd = mean(values), pstdev(values) or 1.0
    out = [{"indice": i, "valor": v, "z": round((v - mu) / sd, 2)}
           for i, v in enumerate(values) if abs((v - mu) / sd) >= z_thr]
    return {"modelo": "zscore_v1", "anomalias": out}
