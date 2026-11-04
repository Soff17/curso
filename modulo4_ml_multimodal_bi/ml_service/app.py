"""Microservicio FastAPI (stand-in de un endpoint de Vertex AI Prediction).

Arranque:  uvicorn ml_service.app:app --port 8080   (desde modulo4_ml_multimodal_bi/)
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field

from . import models

app = FastAPI(title="BI ML Service", version="1.0")


class ForecastIn(BaseModel):
    serie: list[float] = Field(min_length=3)
    horizonte: int = Field(default=3, ge=1, le=12)


class MoraIn(BaseModel):
    pct_cartera_mora: float = Field(ge=0, le=1)
    dias_vencido_prom: float = Field(ge=0)
    monto_expuesto: float = Field(ge=0)


class AnomIn(BaseModel):
    valores: list[float] = Field(min_length=3)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/forecast")
def forecast(body: ForecastIn):
    return models.forecast(body.serie, body.horizonte)


@app.post("/credit-score")
def credit(body: MoraIn):
    return models.prob_mora(**body.model_dump())


@app.post("/anomalies")
def anomalies(body: AnomIn):
    return models.detect_anomalies(body.valores)
