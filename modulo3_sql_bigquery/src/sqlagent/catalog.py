"""RAG de metadata: recupera solo las tablas relevantes antes de pedirle SQL al LLM.

Cada tabla del catálogo es un fragmento: su descripción de negocio y sus columnas con la suya.
Con 22 tablas, mandarlas todas al prompt sería caro y confuso; aquí se traen K candidatas y se
reordenan para quedarse con N.
"""
import sqlite3
from functools import lru_cache

from rag.chunking import Chunk
from rag.retrieval import LexicalReranker, TfidfRetriever, two_stage_retrieve

import os

from shared.config import DB_PATH, is_cloud

K_CATALOGO = 8          # candidatas de la primera etapa (el catálogo tiene 22 tablas)
# Calibrado con `probar_catalogo.py` (2026-11-03) sobre 11 preguntas del catálogo y 3 fuera de él:
#   Ranking API: lo irrelevante llega a 0.024 y la tabla correcta baja hasta 0.174 -> punto medio 0.099.
#   Reranker léxico (offline): irrelevante hasta 0.085, correcta desde 0.109 -> punto medio 0.097.
# Con 0.10 pasan las dos. La muestra de preguntas irrelevantes es pequeña (3): se RECALIBRA si cambia el catálogo.
UMBRAL = float(os.getenv("UMBRAL_CATALOGO") or 0.10)


@lru_cache(maxsize=1)
def _chunks() -> list[Chunk]:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    rows = con.execute("SELECT tabla, columna, tipo, descripcion FROM catalogo_datos").fetchall()
    try:
        tablas = dict(con.execute("SELECT tabla, descripcion FROM catalogo_tablas").fetchall())
    except sqlite3.OperationalError:          # catálogo antiguo, sin descripciones de tabla
        tablas = {}
    con.close()
    by_table: dict[str, list[tuple]] = {}
    for t, c, ty, d in rows:
        by_table.setdefault(t, []).append((c, ty, d))
    out = []
    for t, cols in by_table.items():
        cabecera = f"Tabla {t}: {tablas[t]}" if t in tablas else f"Tabla {t}"
        text = cabecera + "\n" + "\n".join(f"- {c} ({ty}): {d}" for c, ty, d in cols)
        out.append(Chunk(id=f"tabla#{t}", doc="catalogo", article=t, title=t, text=text, source="catalogo_datos"))
    return out


@lru_cache(maxsize=1)
def _pipeline():
    """offline: TF-IDF + reranker léxico (cuentan palabras). cloud: embeddings de Vertex + Ranking API,
    como el auditor del Módulo 2 (comparan significado). La rama cloud se probó solo con simulados."""
    ch = _chunks()
    if is_cloud():
        from rag.retrieval import VertexEmbeddingRetriever, VertexRanker, ranking_config
        return VertexEmbeddingRetriever(ch), VertexRanker(ranking_config())
    return TfidfRetriever(ch), LexicalReranker()


def buscar_esquema(pregunta: str, max_tablas: int = 3) -> dict:
    """Devuelve las tablas/columnas relevantes del catálogo para generar SQL.

    Args:
        pregunta: la pregunta de negocio en lenguaje natural.
        max_tablas: máximo de tablas a devolver.
    """
    r, rr = _pipeline()
    hits = two_stage_retrieve(pregunta, r, rr, k=K_CATALOGO, n=max_tablas, threshold=UMBRAL)
    return {"tablas": [{"tabla": h.chunk.title, "score": h.score, "esquema": h.chunk.text} for h in hits]}
