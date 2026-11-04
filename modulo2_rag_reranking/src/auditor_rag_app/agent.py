"""Paquete para `adk web`: el Agente Auditor de Políticas Financieras del Módulo 2 (RAG + reranking + umbral).

    auditor_politicas  (root_agent)
     └── herramienta de búsqueda → etapa 1 (K=20) → reranking (N=3) → umbral → citas → AuditDecision

Es el mismo auditor que se construye en el notebook. Lo único que cambia entre fuentes es DE DÓNDE SALEN LOS
CANDIDATOS; el reranker, el umbral, la instrucción y la salida estructurada son los mismos.

Fuente de los documentos (variable `AUDITOR_FUENTE`):

  politicas   (por defecto)  Las políticas en markdown, un chunk por artículo (citas exactas).
                             AGENTS_MODE=cloud → embeddings de Vertex + Ranking API; offline → TF-IDF + reranker léxico.
  rag_engine                 Las políticas en PDF, ya importadas en RAG Engine (Vector Search administrado).
                             Necesita AGENTS_MODE=cloud y RAG_CORPUS_POLITICAS (nombre de recurso del corpus).
                             El corpus se crea con `preparar_corpus.py`.
                             EXTENSIÓN OPCIONAL (no es parte del entregable): si defines también RAG_CORPUS_REPORTES
                             (corpus del reporte 10-Q), se busca en las dos fuentes con cuota por fuente
                             (2 políticas + 1 reporte).

Umbral: `UMBRAL_AUDITOR` si lo defines. Si no: 0.14 en cloud (calibrado con la Ranking API sobre este corpus) y, en
offline, se CALIBRA SOLO al arrancar con los 6 casos y tres consultas fuera del corpus (el 0.05 por defecto del
reranker léxico deja pasar el caso del yate). El umbral se RECALIBRA cuando cambia el corpus o el reranker.
"""
import json
import os

from rag.auditor import _pipeline, build_auditor, citations_dict, evidence, make_tool
from rag.retrieval import RagEngineRetriever, calibrate_threshold, select_with_quotas
from shared.config import DATA_DIR, RERANK_N, RETRIEVE_K, is_cloud

FUENTE = os.getenv("AUDITOR_FUENTE", "politicas").lower()
CUOTAS = {"políticas": 2, "reporte": 1}          # 2 + 1 = N
FUERA_DEL_CORPUS = ["Compra de un yate para la dirección", "Receta de paella valenciana para ocho personas",
                    "xyzzy qwerty plugh"]


def _umbral(retriever=None, reranker=None) -> float:
    """UMBRAL_AUDITOR si está definido; 0.14 en cloud (calibrado); en offline se calibra con los 6 casos."""
    if os.getenv("UMBRAL_AUDITOR"):
        return float(os.environ["UMBRAL_AUDITOR"])
    if is_cloud() or retriever is None:
        return 0.14
    casos = json.loads((DATA_DIR / "casos_gasto.json").read_text(encoding="utf-8"))
    umbral, _ = calibrate_threshold(lambda q: retriever.search(q, RETRIEVE_K), reranker,
                                    [c["descripcion"] for c in casos], FUERA_DEL_CORPUS)
    return umbral


def _politicas():
    retriever, reranker = _pipeline()
    umbral = _umbral(retriever, reranker)

    def resolver(consulta: str) -> dict:
        return evidence(consulta, retriever.search(consulta, RETRIEVE_K), reranker, umbral)
    return resolver, "buscar_politicas", "en las políticas internas (un chunk por artículo)", ""


def _rag_engine():
    if not is_cloud():
        raise RuntimeError("AUDITOR_FUENTE=rag_engine necesita AGENTS_MODE=cloud (y un corpus ya importado).")
    from rag.ragengine import RagEngineProject
    from rag.retrieval import VertexRanker, ranking_config
    proyecto = RagEngineProject(os.environ["GOOGLE_CLOUD_PROJECT"])
    reranker = VertexRanker(ranking_config())
    politicas = RagEngineRetriever(proyecto, os.environ["RAG_CORPUS_POLITICAS"])
    umbral = _umbral()
    corpus_reportes = os.getenv("RAG_CORPUS_REPORTES")
    if not corpus_reportes:
        def resolver(consulta: str) -> dict:
            return evidence(consulta, politicas.search(consulta, RETRIEVE_K), reranker, umbral)
        return resolver, "buscar_politicas", "en las políticas internas (PDFs en RAG Engine)", ""
    reportes = RagEngineRetriever(proyecto, corpus_reportes)

    def resolver(consulta: str) -> dict:
        fuentes = {"políticas": politicas.search(consulta, RETRIEVE_K), "reporte": reportes.search(consulta, RETRIEVE_K)}
        return citations_dict(consulta, select_with_quotas(consulta, fuentes, reranker, umbral, CUOTAS, RERANK_N))
    extra = (" Las fuentes pueden ser artículos de política o fragmentos del reporte 10-Q en PDF: cita cada una con el "
             "nombre exacto que devuelve la herramienta (por ejemplo «10-Q 3T 2026 (PDF), fragmento 2 (Item 1 – Estados "
             "financieros)»). Si una cifra del reporte contradice la política, dilo en la justificación.")
    return (resolver, "buscar_politicas_y_reporte",
            "entre las políticas internas (PDFs) y el reporte trimestral 10-Q (PDF) en RAG Engine", extra)


if FUENTE == "rag_engine":
    _resolver, _nombre, _que, _extra = _rag_engine()
elif FUENTE == "politicas":
    _resolver, _nombre, _que, _extra = _politicas()
else:
    raise RuntimeError(f"AUDITOR_FUENTE desconocida: {FUENTE!r}. Usa 'politicas' o 'rag_engine'.")

root_agent = build_auditor(make_tool(_nombre, _resolver, _que), "auditor_politicas", _extra)
