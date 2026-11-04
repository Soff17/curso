"""Agente Auditor de Políticas Financieras: RAG + Reranking -> decisión justificada con citas."""
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel

from shared.config import POLICIES_DIR, RERANK_N, is_cloud, MODEL_NAME

from .chunking import load_corpus
from .retrieval import (LexicalReranker, TfidfRetriever, VertexEmbeddingRetriever, VertexRanker,
                        ranking_config, two_stage_retrieve)


class Citation(BaseModel):
    chunk_id: str
    citation: str
    score: float
    text: str


class AuditEvidence(BaseModel):
    query: str
    citations: list[Citation]


@lru_cache(maxsize=1)
def _pipeline():
    chunks = load_corpus(POLICIES_DIR)
    if is_cloud():
        return VertexEmbeddingRetriever(chunks), VertexRanker(ranking_config())
    return TfidfRetriever(chunks), LexicalReranker()


def buscar_politicas(consulta: str) -> dict:
    """Busca en las políticas internas los 3 artículos más relevantes para la consulta.

    Args:
        consulta: descripción del gasto o pregunta normativa.

    Returns:
        dict con 'citations' (id, cita, score, texto). Lista vacía si nada supera el umbral:
        en ese caso NO se debe aprobar ni rechazar, solo escalar.
    """
    retriever, reranker = _pipeline()
    hits = two_stage_retrieve(consulta, retriever, reranker)
    ev = AuditEvidence(query=consulta, citations=[
        Citation(chunk_id=h.chunk.id, citation=h.chunk.citation, score=h.score, text=h.chunk.text)
        for h in hits])
    return ev.model_dump()


class AuditDecision(BaseModel):
    decision: Literal["APROBADO", "RECHAZADO", "ESCALAR"]
    justificacion: str
    articulos_citados: list[str]


INSTRUCTION = (
    "Eres auditor de políticas financieras. Para cada gasto: 1) llama {herramienta}; 2) decide APROBADO o "
    "RECHAZADO solo con los fragmentos devueltos; 3) cita cada fuente con el nombre exacto que devuelve la "
    "herramienta (por ejemplo «POL-VIA-2026, Art. 1.3 (Autorización previa)»). Si la lista de citas está vacía, "
    "o los fragmentos devueltos no aplican al gasto, responde ESCALAR. Nunca uses conocimiento externo ni "
    "inventes artículos ni cifras.")


# ---------- Piezas reutilizables: lo único que cambia entre fuentes es «de dónde salen los candidatos» ----------
def evidence(query: str, candidates: list, reranker, threshold: float, n: int = RERANK_N,
             max_chars: int = 1200) -> dict:
    """Etapa 2 y umbral: de los candidatos de CUALQUIER fuente a las citas que ve el agente.
    Lista vacía = nada superó el umbral = el agente debe responder ESCALAR."""
    hits = [h for h in reranker.rerank(query, candidates, n) if h.score >= threshold]
    return citations_dict(query, hits, max_chars)


def citations_dict(query: str, hits: list, max_chars: int = 1200) -> dict:
    return AuditEvidence(query=query, citations=[
        Citation(chunk_id=h.chunk.id, citation=h.chunk.citation, score=h.score, text=h.chunk.text[:max_chars])
        for h in hits]).model_dump()


def make_tool(name: str, resolver, what: str):
    """Fabrica la herramienta del agente. `resolver(consulta) -> dict` devuelve las citas; se evalúa al llamar,
    así recoge un umbral recalibrado. El docstring es lo que lee el modelo para decidir cuándo usarla."""
    def herramienta(consulta: str) -> dict:
        return resolver(consulta)
    herramienta.__name__ = herramienta.__qualname__ = name
    herramienta.__doc__ = (f"Busca {what} los 3 fragmentos más relevantes para la consulta.\n\n"
                           "    Args:\n        consulta: descripción del gasto o pregunta normativa.\n\n"
                           "    Returns:\n        dict con 'citations' (id, cita, score, texto). Lista vacía si nada supera el umbral:\n"
                           "        en ese caso NO se debe aprobar ni rechazar, solo escalar.\n    ")
    return herramienta


def build_auditor(tool, name: str = "auditor_politicas", extra: str = ""):
    """El auditor: misma instrucción y mismo AuditDecision con cualquier herramienta de búsqueda."""
    from google.adk.agents import Agent   # verificado: google-adk 2.11.0
    return Agent(
        name=name,
        model=MODEL_NAME,
        description="Audita gastos contra políticas internas citando fuentes exactas.",
        instruction=INSTRUCTION.format(herramienta=tool.__name__) + extra,
        tools=[tool],
        output_schema=AuditDecision,
    )


def build_auditor_agent():
    """Auditor con las políticas en markdown (un chunk por artículo). Lo usan el capstone y el Módulo 3."""
    return build_auditor(buscar_politicas)
