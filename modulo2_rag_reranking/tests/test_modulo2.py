import json

import pytest

from rag.auditor import buscar_politicas
from rag.chunking import load_corpus
from rag.retrieval import LexicalReranker, TfidfRetriever, two_stage_retrieve
from shared.config import DATA_DIR, POLICIES_DIR


def test_chunking_por_articulo():
    chunks = load_corpus(POLICIES_DIR)
    assert len(chunks) >= 18
    assert all(c.article and "–" in c.text.splitlines()[0] for c in chunks)
    assert any(c.id == "POL-VIA-2026#1.3" for c in chunks)


def test_devuelve_a_lo_mas_tres():
    r = buscar_politicas("viaje internacional sin autorización previa")
    assert 0 < len(r["citations"]) <= 3


def test_umbral_descarta_ruido():
    chunks = load_corpus(POLICIES_DIR)
    hits = two_stage_retrieve("xyzzy qwerty plugh", TfidfRetriever(chunks), LexicalReranker())
    assert hits == []


CASOS = json.loads((DATA_DIR / "casos_gasto.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("caso", CASOS, ids=lambda c: c["id"])
def test_recall_articulo_esperado_en_top3(caso):
    arts = {c["chunk_id"].split("#")[1].split(".")[0] + "." + c["chunk_id"].split("#")[1].split(".")[1]
            for c in buscar_politicas(caso["descripcion"])["citations"]}
    assert set(caso["articulos_esperados"]) & arts, (caso["id"], arts)
