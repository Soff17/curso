"""Búsqueda en las políticas internas para el agente híbrido: la misma que el Módulo 2, con su misma fuente.

Fuente (variable `AUDITOR_FUENTE`, la misma del Módulo 2):
  politicas   (por defecto) las políticas en markdown, un chunk por artículo; es la herramienta del Módulo 2.
  rag_engine  las políticas en PDF dentro de RAG Engine (el corpus que crea `preparar_corpus.py` del Módulo 2 o
              `preparar_rag.py` de este módulo). Necesita AGENTS_MODE=cloud y RAG_CORPUS_POLITICAS.
"""
import os
from functools import lru_cache

from rag.auditor import buscar_politicas as _politicas_markdown
from rag.auditor import evidence
from shared.config import RETRIEVE_K, is_cloud

UMBRAL_POLITICAS = float(os.getenv("UMBRAL_AUDITOR") or 0.14)       # calibrado con la Ranking API en el Módulo 2


@lru_cache(maxsize=1)
def _rag_engine():
    if not is_cloud():
        raise RuntimeError("AUDITOR_FUENTE=rag_engine necesita AGENTS_MODE=cloud (y un corpus ya importado).")
    from rag.ragengine import RagEngineProject
    from rag.retrieval import RagEngineRetriever, VertexRanker, ranking_config
    proyecto = RagEngineProject(os.environ["GOOGLE_CLOUD_PROJECT"])
    return RagEngineRetriever(proyecto, os.environ["RAG_CORPUS_POLITICAS"]), VertexRanker(ranking_config())


def buscar_politicas(consulta: str) -> dict:
    """Busca en las políticas internas los 3 artículos más relevantes para la consulta.

    Args:
        consulta: la norma o el hecho que se quiere encontrar (por ejemplo, «exceso presupuestal en consultoría»).

    Returns:
        dict con 'citations' (id, cita, score, texto). Lista vacía si nada supera el umbral:
        en ese caso NO se debe afirmar lo que dice la política.
    """
    if os.getenv("AUDITOR_FUENTE", "politicas").lower() == "rag_engine":
        retriever, reranker = _rag_engine()
        return evidence(consulta, retriever.search(consulta, RETRIEVE_K), reranker, UMBRAL_POLITICAS)
    return _politicas_markdown(consulta)
