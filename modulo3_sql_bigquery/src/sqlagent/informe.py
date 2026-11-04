"""Búsqueda en el informe de presupuesto (texto no estructurado) para el agente híbrido.

El agente necesita DOS cosas distintas y por eso hay dos herramientas:
  - `ejecutar_sql`   -> las cifras de la base (determinísticas).
  - `buscar_informe` -> lo que dice el informe (la cifra y su cita), recuperado con RAG + reranking.
Y una tercera, `contrastar_cifras`, que las compara con una regla fija en código: el modelo no calcula.

Fuente (variable `INFORME_FUENTE`):
  markdown    (por defecto) el informe en markdown, una sección por fragmento. offline: TF-IDF + reranker léxico;
              cloud: embeddings de Vertex + Ranking API.
  rag_engine  el PDF del informe ya importado en RAG Engine (necesita AGENTS_MODE=cloud y RAG_CORPUS_INFORMES).
"""
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from rag.auditor import evidence
from rag.chunking import Chunk
from rag.retrieval import LexicalReranker, TfidfRetriever

from shared.config import DATA_DIR, RETRIEVE_K, is_cloud

INFORMES_DIR = DATA_DIR / "informes"
SECCION_RE = re.compile(r"^##\s+(\d+)\.\s+(.+)$", re.M)
# Calibrado con `probar_informe.py` (2026-11-03, 6 preguntas del informe y 4 fuera de él), con la Ranking API:
#   informe en markdown:      irrelevante hasta 0.032, relevante desde 0.708
#   informe en RAG Engine/PDF: irrelevante hasta 0.019, relevante desde 0.201 (una pregunta vaga: «para qué sirve»)
# Con 0.10 pasan las dos, con margen sobre lo irrelevante y sin dejar fuera la pregunta vaga (con 0.20 se quedaba a una
# milésima). A este agente le sale más caro decir «no lo encontré» por error que traer un fragmento de más.
# Reranker léxico (offline): irrelevante 0.000, correcta desde 0.136 -> se deja 0.05.
UMBRAL_INFORME = float(os.getenv("UMBRAL_INFORME") or (0.10 if is_cloud() else 0.05))


@dataclass(frozen=True)
class SeccionInforme(Chunk):
    """Una sección del informe. La cita es la sección: «Informe …, sección 2 (Presupuesto aprobado …)»."""

    @property
    def citation(self) -> str:
        return f"{self.doc}, sección {self.article} ({self.title})"


def cargar_secciones(path: Path) -> list[SeccionInforme]:
    raw = path.read_text(encoding="utf-8")
    doc = raw.splitlines()[0].lstrip("# ").strip()
    marcas = list(SECCION_RE.finditer(raw))
    out = []
    for i, m in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(raw)
        cuerpo = raw[m.end():fin].strip()
        out.append(SeccionInforme(f"{path.stem}#{m.group(1)}", doc, m.group(1), m.group(2).strip(),
                                  f"{doc} – sección {m.group(1)} – {m.group(2).strip()}\n{cuerpo}", str(path)))
    return out


@lru_cache(maxsize=1)
def _markdown():
    secciones = [s for p in sorted(INFORMES_DIR.glob("*.md")) for s in cargar_secciones(p)]
    if is_cloud():
        from rag.retrieval import VertexEmbeddingRetriever, VertexRanker, ranking_config
        return VertexEmbeddingRetriever(secciones), VertexRanker(ranking_config())
    return TfidfRetriever(secciones), LexicalReranker()


@lru_cache(maxsize=1)
def _rag_engine():
    if not is_cloud():
        raise RuntimeError("INFORME_FUENTE=rag_engine necesita AGENTS_MODE=cloud (y el PDF ya importado).")
    from rag.ragengine import RagEngineProject
    from rag.retrieval import RagEngineRetriever, VertexRanker, ranking_config
    proyecto = RagEngineProject(os.environ["GOOGLE_CLOUD_PROJECT"])
    return RagEngineRetriever(proyecto, os.environ["RAG_CORPUS_INFORMES"]), VertexRanker(ranking_config())


def buscar_informe(consulta: str) -> dict:
    """Busca en el informe de presupuesto los 3 fragmentos más relevantes para la consulta.

    Args:
        consulta: la cifra o el hecho que se quiere encontrar en el informe (por ejemplo,
            «presupuesto aprobado de Consultoría de la división Norte en el 3T 2026»).

    Returns:
        dict con 'citations' (id, cita, score, texto). Las cifras del informe se leen del 'texto' de las
        citas, y el informe dice en qué unidad vienen (USD o miles de USD). Lista vacía si nada supera
        el umbral: entonces NO se debe inventar una cifra del informe.
    """
    retriever, reranker = _rag_engine() if os.getenv("INFORME_FUENTE", "markdown").lower() == "rag_engine" else _markdown()
    # max_chars alto: el informe cabe en un solo fragmento y el tope de 1,200 caracteres del Módulo 2 le cortaba el final
    # (justo la frase de que el exceso no tiene la aprobación del Comité).
    return evidence(consulta, retriever.search(consulta, RETRIEVE_K), reranker, UMBRAL_INFORME, max_chars=4000)
