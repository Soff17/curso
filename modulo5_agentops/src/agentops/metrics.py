"""Métricas de evaluación RAG y A2A.

Cloud: usar Vertex AI Evaluation (Gen AI Evaluation Service) con métricas model-based (groundedness/fulfillment/etc.).
Offline: métricas léxicas deterministas con la MISMA interfaz, para poder correr el gate de CI sin llamadas a LLM.
"""
import re
import unicodedata
from dataclasses import dataclass


def _norm_tokens(t: str) -> set[str]:
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return {w[:6] for w in re.findall(r"[a-z0-9]+", t) if len(w) > 2}


def _sentences(t: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", t) if len(s.strip()) > 15]


def faithfulness(answer: str, contexts: list[str], support_thr: float = 0.6) -> float:
    """Fracción de oraciones de la respuesta cuyos términos están soportados por el contexto."""
    ctx = set().union(*(_norm_tokens(c) for c in contexts)) if contexts else set()
    sents = _sentences(answer)
    if not sents:
        return 0.0
    ok = 0
    for s in sents:
        toks = _norm_tokens(s)
        if toks and len(toks & ctx) / len(toks) >= support_thr:
            ok += 1
    return round(ok / len(sents), 4)


def answer_relevance(question: str, answer: str) -> float:
    q, a = _norm_tokens(question), _norm_tokens(answer)
    return round(len(q & a) / len(q), 4) if q else 0.0


def context_recall(retrieved_ids: list[str], gold_ids: list[str]) -> float:
    if not gold_ids:
        return 1.0
    return round(len(set(retrieved_ids) & set(gold_ids)) / len(set(gold_ids)), 4)


@dataclass
class A2ATrace:
    esperado: str      # agente que debía atender
    real: str          # agente que atendió
    exito: bool        # la delegación terminó con respuesta válida


def delegation_metrics(traces: list[A2ATrace]) -> dict:
    n = len(traces) or 1
    return {"tasa_exito_delegacion": round(sum(t.exito for t in traces) / n, 4),
            "precision_ruta": round(sum(t.esperado == t.real for t in traces) / n, 4)}
