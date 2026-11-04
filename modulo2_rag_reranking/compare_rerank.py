"""Compara Recall@3 de la etapa 1 sola vs etapa 1 (K=20) + reranking (N=3). Uso: python modulo2_rag_reranking/compare_rerank.py"""
import json

from rag.chunking import load_corpus
from rag.retrieval import LexicalReranker, TfidfRetriever
from shared.config import DATA_DIR, POLICIES_DIR, RERANK_N, RETRIEVE_K


def art(chunk_id: str) -> str:
    return ".".join(chunk_id.split("#")[1].split(".")[:2])


chunks = load_corpus(POLICIES_DIR)
ret, rr = TfidfRetriever(chunks), LexicalReranker()
casos = json.loads((DATA_DIR / "casos_gasto.json").read_text(encoding="utf-8"))
hit1 = hit2 = 0
print(f"{'caso':5} {'esperado':10} {'solo etapa 1 (top3)':32} {'con rerank (top3)':32}")
for c in casos:
    cand = ret.search(c["descripcion"], RETRIEVE_K)
    s1 = [art(x.chunk.id) for x in cand[:RERANK_N]]
    s2 = [art(x.chunk.id) for x in rr.rerank(c["descripcion"], cand, RERANK_N)]
    ok1 = bool(set(s1) & set(c["articulos_esperados"]))
    ok2 = bool(set(s2) & set(c["articulos_esperados"]))
    hit1, hit2 = hit1 + ok1, hit2 + ok2
    print(f"{c['id']:5} {','.join(c['articulos_esperados']):10} {str(s1) + (' ok' if ok1 else ' X'):32} {str(s2) + (' ok' if ok2 else ' X'):32}")
n = len(casos)
print(f"\nHit@3 sin rerank: {hit1}/{n}   con rerank: {hit2}/{n}")
