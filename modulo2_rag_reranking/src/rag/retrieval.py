"""Etapa 1 (recuperación vectorial K=20) y Etapa 2 (reranking N=3) con sustitutos offline."""
import math
import os
import re
import unicodedata
from dataclasses import dataclass
from typing import Protocol

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from shared.config import EMBEDDING_MODEL, RELEVANCE_THRESHOLD, RERANK_N, RETRIEVE_K

from .chunking import Chunk, chunk_articles, to_chunk_doc


@dataclass
class Scored:
    chunk: Chunk
    score: float


class Retriever(Protocol):
    def search(self, query: str, k: int) -> list[Scored]: ...


class Reranker(Protocol):
    def rerank(self, query: str, candidates: list[Scored], n: int) -> list[Scored]: ...


# ---------- Etapa 1 ----------
class TfidfRetriever:
    """Sustituto offline del Vector Search (misma interfaz que VertexEmbeddingRetriever)."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.vec = TfidfVectorizer(strip_accents="unicode", lowercase=True, ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vec.fit_transform([c.text for c in chunks])

    def search(self, query: str, k: int = RETRIEVE_K) -> list[Scored]:
        q = self.vec.transform([query])
        sims = (self.matrix @ q.T).toarray().ravel()
        idx = np.argsort(-sims)[:k]
        return [Scored(self.chunks[i], float(sims[i])) for i in idx]


class VertexEmbeddingRetriever:
    """Embeddings de Vertex AI + coseno en memoria. Para producción: Vertex AI Vector Search."""

    def __init__(self, chunks: list[Chunk]):
        from google import genai  # VERIFICAR: google-genai
        self.client = genai.Client()
        self.chunks = chunks
        self.matrix = self._embed([c.text for c in chunks], "RETRIEVAL_DOCUMENT")

    def _embed(self, texts: list[str], task: str) -> np.ndarray:
        from google.genai import types
        res = self.client.models.embed_content(
            model=EMBEDDING_MODEL, contents=texts,
            config=types.EmbedContentConfig(task_type=task))
        m = np.array([e.values for e in res.embeddings], dtype=float)
        return m / np.linalg.norm(m, axis=1, keepdims=True)

    def search(self, query: str, k: int = RETRIEVE_K) -> list[Scored]:
        q = self._embed([query], "RETRIEVAL_QUERY")[0]
        sims = self.matrix @ q
        idx = np.argsort(-sims)[:k]
        return [Scored(self.chunks[i], float(sims[i])) for i in idx]


# ---------- Etapa 2 ----------
_STOP = set("de la el en y a los las del un una por con para que se al su sus o es lo como mas pero si no ya sin sobre entre".split())


def _tokens(text: str) -> list[str]:
    t = unicodedata.normalize("NFKD", text.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return [w[:6] for w in re.findall(r"[a-z0-9]+", t) if w not in _STOP and len(w) > 2]


class LexicalReranker:
    """Sustituto offline de un cross-encoder: puntúa la consulta CONTRA cada candidato por separado
    (cobertura de términos ponderada por rareza dentro del conjunto candidato + bonus por bigramas)."""

    def rerank(self, query: str, candidates: list[Scored], n: int = RERANK_N) -> list[Scored]:
        qt = _tokens(query)
        if not qt or not candidates:
            return []
        docs = [set(_tokens(c.chunk.text)) for c in candidates]
        df = {t: sum(t in d for d in docs) for t in set(qt)}
        N = len(docs)
        w = {t: math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5)) for t in set(qt)}
        total = sum(w[t] for t in set(qt)) or 1.0
        qbi = {(a, b) for a, b in zip(qt, qt[1:])}
        out = []
        for c, d in zip(candidates, docs):
            cov = sum(w[t] for t in set(qt) if t in d) / total
            dt = _tokens(c.chunk.text)
            bi = len(qbi & set(zip(dt, dt[1:]))) / (len(qbi) or 1)
            out.append(Scored(c.chunk, round(0.85 * cov + 0.15 * bi, 4)))
        out.sort(key=lambda s: -s.score)
        return out[:n]


class VertexRanker:
    """Vertex AI Ranking API (Discovery Engine). Cloud."""

    def __init__(self, ranking_config: str, model: str = "semantic-ranker-default@latest"):
        from google.cloud import discoveryengine_v1 as de  # VERIFICAR
        self.de, self.cfg, self.model = de, ranking_config, model
        self.client = de.RankServiceClient()

    def rerank(self, query: str, candidates: list[Scored], n: int = RERANK_N) -> list[Scored]:
        recs = [self.de.RankingRecord(id=str(i), title=c.chunk.title, content=c.chunk.text)
                for i, c in enumerate(candidates)]
        req = self.de.RankRequest(ranking_config=self.cfg, model=self.model, query=query,
                                  records=recs, top_n=n)
        res = self.client.rank(request=req)
        return [Scored(candidates[int(r.id)].chunk, float(r.score)) for r in res.records]


def ranking_config() -> str:
    """RANKING_CONFIG del .env; si falta o conserva el valor de ejemplo («tu-proyecto»), se deriva del proyecto."""
    cfg = os.getenv("RANKING_CONFIG", "")
    if cfg and "tu-proyecto" not in cfg:
        return cfg
    proyecto = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    if not proyecto or proyecto == "tu-proyecto":
        raise RuntimeError("Falta GOOGLE_CLOUD_PROJECT (o RANKING_CONFIG) en tu .env.")
    return f"projects/{proyecto}/locations/global/rankingConfigs/default_ranking_config"


# ---------- Pipeline ----------
def two_stage_retrieve(query: str, retriever: Retriever, reranker: Reranker,
                       k: int = RETRIEVE_K, n: int = RERANK_N,
                       threshold: float = RELEVANCE_THRESHOLD) -> list[Scored]:
    """K candidatos -> rerank -> top-N -> descarta los que no superan el umbral (score thresholding)."""
    candidates = retriever.search(query, k)
    top = reranker.rerank(query, candidates, n)
    return [s for s in top if s.score >= threshold]


# ---------- Varias fuentes: cuota por fuente ----------
def select_with_quotas(query: str, sources: dict[str, list[Scored]], reranker: Reranker,
                       threshold: float, quotas: dict[str, int], n: int = RERANK_N) -> list[Scored]:
    """Mezcla candidatos de varias fuentes con UNA sola llamada al reranker y reserva lugar a cada fuente.

    Si se reordena todo junto, los fragmentos largos de una fuente pueden quedarse con los N lugares y la otra
    fuente nunca llega al agente. Aquí se recorre la lista ya ordenada y se toma, en orden, hasta `quotas[fuente]`
    fragmentos de cada fuente (siempre que superen el umbral), con un máximo total de `n`.
    La suma de las cuotas debería ser `n` (p. ej. 2 políticas + 1 reporte = 3).
    """
    todos = [h for cands in sources.values() for h in cands]
    if not todos:
        return []
    origen = {id(h.chunk): nombre for nombre, cands in sources.items() for h in cands}
    ordenados = reranker.rerank(query, todos, len(todos))
    usados = {nombre: 0 for nombre in sources}
    elegidos: list[Scored] = []
    for h in ordenados:
        nombre = origen[id(h.chunk)]
        if h.score >= threshold and usados[nombre] < quotas.get(nombre, 0) and len(elegidos) < n:
            elegidos.append(h)
            usados[nombre] += 1
    return elegidos


# ---------- Calibración y evaluación ----------
def calibrate_threshold(retrieve, reranker: Reranker, covered: list[str], outside: list[str]) -> tuple[float, dict]:
    """Umbral = punto medio del hueco entre el MEJOR puntaje de las consultas fuera del corpus (máximo) y el mejor
    puntaje de las cubiertas (mínimo). Si los grupos se solapan, usa el mínimo de las cubiertas y avisa.
    `retrieve(consulta) -> list[Scored]`. Los puntajes de cada fuente/reranker NO son comparables: recalibra al cambiar."""
    def mejor(q: str) -> float:
        top = reranker.rerank(q, retrieve(q), 1)
        return top[0].score if top else 0.0
    relevantes = [mejor(q) for q in covered]
    irrelevantes = [mejor(q) for q in outside]
    a, b = max(irrelevantes), min(relevantes)
    hay_hueco = a < b
    umbral = round((a + b) / 2, 2) if hay_hueco else round(b, 2)
    return umbral, {"max_irrelevantes": a, "min_relevantes": b, "hay_hueco": hay_hueco,
                    "relevantes": relevantes, "irrelevantes": irrelevantes}


def hit_at_n(retrieve, reranker: Reranker, cases: list[dict], n: int = RERANK_N) -> tuple[int, int]:
    """Hit@N sin y con reranking: un caso acierta si ALGÚN artículo esperado está en los N fragmentos."""
    ok1 = ok2 = 0
    for c in cases:
        esperado = set(c["articulos_esperados"])
        cand = retrieve(c["descripcion"])
        a1 = {a for h in cand[:n] for a in chunk_articles(h.chunk)}
        a2 = {a for h in reranker.rerank(c["descripcion"], cand, n) for a in chunk_articles(h.chunk)}
        ok1 += bool(a1 & esperado)
        ok2 += bool(a2 & esperado)
    return ok1, ok2


# ---------- Etapa 1 sobre un corpus de RAG Engine (Vector Search administrado) ----------
class RagEngineRetriever:
    """Etapa 1 contra un corpus de RAG Engine. Cada fragmento se convierte en un `ChunkDoc` (documento, artículos y
    cita reconstruidos del texto). `project` es un `rag.ragengine.RagEngineProject` (o cualquier objeto con
    `retrieve(corpus, query, k) -> list` de contextos con `.text` y `.source_uri`)."""

    def __init__(self, project, corpus: str):
        self.project, self.corpus = project, corpus

    def search(self, query: str, k: int = RETRIEVE_K) -> list[Scored]:
        vistos: set[str] = set()
        salida: list[Scored] = []
        for i, c in enumerate(self.project.retrieve(self.corpus, query, k)):
            clave = " ".join((getattr(c, "text", "") or "").split())
            if clave and clave not in vistos:
                vistos.add(clave)
                salida.append(Scored(to_chunk_doc(c.text, getattr(c, "source_uri", "") or "", i), 0.0))
        return salida
