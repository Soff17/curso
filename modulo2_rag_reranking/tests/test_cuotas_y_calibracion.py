"""Varias fuentes (cuota por fuente), calibración del umbral y Hit@3. Todo offline."""
import json

from rag.chunking import Chunk, load_corpus
from rag.retrieval import LexicalReranker, Scored, TfidfRetriever, calibrate_threshold, hit_at_n, select_with_quotas
from shared.config import DATA_DIR, POLICIES_DIR

CASOS = json.loads((DATA_DIR / "casos_gasto.json").read_text(encoding="utf-8"))


class RerankerFijo:
    """Reranker simulado con puntajes dados por id; cuenta cuántas veces se le llama."""
    def __init__(self, puntajes: dict[str, float]):
        self.puntajes, self.llamadas = puntajes, 0

    def rerank(self, query, candidates, n):
        self.llamadas += 1
        out = [Scored(c.chunk, self.puntajes[c.chunk.id]) for c in candidates]
        out.sort(key=lambda s: -s.score)
        return out[:n]


def _chunk(i: str) -> Scored:
    return Scored(Chunk(i, "D", i, i, i, "s"), 0.0)


FUENTES = {"políticas": [_chunk("p1"), _chunk("p2"), _chunk("p3")],
           "reporte": [_chunk("r1"), _chunk("r2"), _chunk("r3")]}
PUNTAJES = {"r1": 0.9, "r2": 0.8, "r3": 0.7, "p1": 0.5, "p2": 0.4, "p3": 0.3}
CUOTAS = {"políticas": 2, "reporte": 1}


def test_sin_cuotas_una_fuente_copa_los_tres_lugares():
    rr = RerankerFijo(PUNTAJES)
    todos = [h for c in FUENTES.values() for h in c]
    assert [h.chunk.id for h in rr.rerank("q", todos, 3)] == ["r1", "r2", "r3"]      # el problema


def test_cuota_reserva_lugar_a_cada_fuente():
    rr = RerankerFijo(PUNTAJES)
    r = select_with_quotas("q", FUENTES, rr, threshold=0.35, quotas=CUOTAS, n=3)
    assert [h.chunk.id for h in r] == ["r1", "p1", "p2"]                             # 1 reporte + 2 políticas
    assert rr.llamadas == 1                                                          # UNA sola llamada al reranker


def test_la_cuota_respeta_el_umbral():
    r = select_with_quotas("q", FUENTES, RerankerFijo(PUNTAJES), threshold=0.45, quotas=CUOTAS, n=3)
    assert [h.chunk.id for h in r] == ["r1", "p1"]                                   # p2 (0.4) no llega al umbral
    assert select_with_quotas("q", FUENTES, RerankerFijo(PUNTAJES), threshold=0.95, quotas=CUOTAS) == []


def test_la_cuota_nunca_pasa_de_n_ni_de_la_cuota():
    r = select_with_quotas("q", FUENTES, RerankerFijo(PUNTAJES), 0.0, {"políticas": 5, "reporte": 5}, n=3)
    assert len(r) == 3
    assert select_with_quotas("q", {"a": []}, RerankerFijo({}), 0.0, {"a": 1}) == []


def _recuperador():
    chunks = load_corpus(POLICIES_DIR)
    ret = TfidfRetriever(chunks)
    return (lambda q: ret.search(q, 20)), LexicalReranker()


def test_calibrar_umbral_encuentra_el_hueco():
    retrieve, rr = _recuperador()
    umbral, info = calibrate_threshold(retrieve, rr, [c["descripcion"] for c in CASOS],
                                       ["xyzzy qwerty plugh", "Receta de paella valenciana para ocho personas"])
    assert info["hay_hueco"] and info["max_irrelevantes"] < umbral <= info["min_relevantes"]


def test_hit_at_n_con_reranking_acierta_los_6_casos():
    retrieve, rr = _recuperador()
    sin, con = hit_at_n(retrieve, rr, CASOS)
    assert con == len(CASOS) and con >= sin


def test_ranking_config_deriva_del_proyecto_si_queda_el_valor_de_ejemplo(monkeypatch):
    from rag.retrieval import ranking_config
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "mi-proyecto")
    monkeypatch.setenv("RANKING_CONFIG", "projects/tu-proyecto/locations/global/rankingConfigs/default_ranking_config")
    assert ranking_config() == "projects/mi-proyecto/locations/global/rankingConfigs/default_ranking_config"
    monkeypatch.delenv("RANKING_CONFIG")
    assert ranking_config() == "projects/mi-proyecto/locations/global/rankingConfigs/default_ranking_config"
    monkeypatch.setenv("RANKING_CONFIG", "projects/otro/locations/global/rankingConfigs/mio")
    assert ranking_config() == "projects/otro/locations/global/rankingConfigs/mio"      # un valor real se respeta


def test_ranking_config_falla_con_claridad_sin_proyecto(monkeypatch):
    import pytest
    from rag.retrieval import ranking_config
    monkeypatch.delenv("RANKING_CONFIG", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "tu-proyecto")
    with pytest.raises(RuntimeError, match="GOOGLE_CLOUD_PROJECT"):
        ranking_config()
