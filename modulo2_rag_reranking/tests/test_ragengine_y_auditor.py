"""RAG Engine (con piezas simuladas), la fábrica del auditor y la app de ADK. Nada llama a un servicio."""
import importlib
import inspect
import json
from types import SimpleNamespace as NS

import pytest

from rag.auditor import AuditDecision, INSTRUCTION, build_auditor, evidence, make_tool
from rag.chunking import ChunkDoc
from rag.ragengine import DEFAULT_PARSER_PROMPT, RagEngineProject
from rag.retrieval import RagEngineRetriever, Scored
from shared.config import DATA_DIR

CASOS = json.loads((DATA_DIR / "casos_gasto.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ RagEngineRetriever
class ProyectoFalso:
    def __init__(self, contextos):
        self.contextos, self.pedidos = contextos, []

    def retrieve(self, corpus, query, k):
        self.pedidos.append((corpus, query, k))
        return self.contextos


def test_retriever_de_rag_engine_arma_chunkdoc_y_quita_duplicados():
    ctx = [NS(text="Artículo 1.3 - Autorización previa\nTodo viaje...", source_uri="gs://b/pdf/POL-VIA-2026.pdf"),
           NS(text="Artículo 1.3 - Autorización previa\n  Todo   viaje...", source_uri="gs://b/pdf/POL-VIA-2026.pdf"),  # mismo texto
           NS(text="Item 2 - Discusión\nLos ingresos crecieron", source_uri="gs://b/pdf/10q_norte_3t26.pdf")]
    proyecto = ProyectoFalso(ctx)
    hits = RagEngineRetriever(proyecto, "corpus/1").search("viaje", k=7)
    assert len(hits) == 2 and all(isinstance(h.chunk, ChunkDoc) for h in hits)
    assert hits[0].chunk.citation == "POL-VIA-2026, Art. 1.3 (Autorización previa)"
    assert proyecto.pedidos == [("corpus/1", "viaje", 7)]


# ------------------------------------------------------------------ RagEngineProject (REST simulado)
class ProyectoRestFalso(RagEngineProject):
    def __init__(self, respuestas):
        super().__init__("mi-proyecto")
        self.respuestas, self.llamadas = respuestas, []

    def rest(self, method, path, **kw):
        self.llamadas.append((method, path, kw))
        return self.respuestas[(method, path.split("?")[0])] if (method, path) in self.respuestas else self.respuestas[method]


RUTA_CORPORA = "projects/mi-proyecto/locations/us-central1/ragCorpora"


def test_is_serverless_lee_la_configuracion():
    sin = ProyectoRestFalso({"GET": {"ragManagedDbConfig": {"serverless": {}}}})
    spanner = ProyectoRestFalso({"GET": {"ragManagedDbConfig": {"basic": {}, "spanner": {"basic": {}}}}})
    assert sin.is_serverless() is True and spanner.is_serverless() is False


def test_create_corpus_reutiliza_si_ya_existe():
    p = ProyectoRestFalso({("GET", RUTA_CORPORA): {"ragCorpora": [{"displayName": "pol_C", "name": "corpora/7"}]}})
    assert p.create_corpus("pol_C") == "corpora/7"
    assert [m for m, _, _ in p.llamadas] == ["GET"]                      # no creó otro


def test_create_corpus_indica_el_backend_explicito():
    p = ProyectoRestFalso({("GET", RUTA_CORPORA): {"ragCorpora": []},
                           ("POST", RUTA_CORPORA): {"name": "op/1"},
                           ("GET", "op/1"): {"done": True, "response": {"name": "corpora/9"}}})
    assert p.create_corpus("nuevo") == "corpora/9"
    post = next(kw for m, _, kw in p.llamadas if m == "POST")
    assert post["json"]["vector_db_config"] == {"rag_managed_vertex_vector_search": {}}      # sin esto el servicio falló


def test_create_corpus_falla_con_claridad_si_la_operacion_da_error():
    p = ProyectoRestFalso({("GET", RUTA_CORPORA): {"ragCorpora": []},
                           ("POST", RUTA_CORPORA): {"name": "op/2"},
                           ("GET", "op/2"): {"done": True, "error": {"code": 13, "message": "No available indexing project"}}})
    with pytest.raises(RuntimeError, match="No available indexing project"):
        p.create_corpus("nuevo")


def test_import_folder_usa_carpeta_con_barra_final_y_el_analizador_de_llm():
    pytest.importorskip("agentplatform")
    capturado = {}
    p = RagEngineProject("mi-proyecto")
    p._sdk_client = NS(rag=NS(import_files=lambda name, import_config: capturado.update(name=name, cfg=import_config)))
    p.import_folder("corpora/1", "gs://bucket/pdf_politicas", chunk_size=256, overlap=20,
                    llm_parser=True, parser_prompt=DEFAULT_PARSER_PROMPT)
    cfg = capturado["cfg"]
    assert capturado["name"] == "corpora/1"
    assert cfg.gcs_source.uris == ["gs://bucket/pdf_politicas/"]                 # carpeta con barra, no «carpeta/*»
    assert cfg.rag_file_transformation_config.rag_file_chunking_config.chunk_size == 256
    llm = cfg.rag_file_parsing_config.llm_parser
    assert "publishers/google/models/gemini-2.5-flash" in llm.model_name and llm.custom_parsing_prompt == DEFAULT_PARSER_PROMPT


def test_import_folder_sin_analizador_de_llm_no_configura_parsing():
    pytest.importorskip("agentplatform")
    capturado = {}
    p = RagEngineProject("mi-proyecto")
    p._sdk_client = NS(rag=NS(import_files=lambda name, import_config: capturado.update(cfg=import_config)))
    p.import_folder("corpora/1", "gs://bucket/pol_C/")
    assert capturado["cfg"].rag_file_parsing_config is None


# ------------------------------------------------------------------ fábrica del auditor
class RerankerSimple:
    def rerank(self, query, candidates, n):
        return sorted(candidates, key=lambda s: -s.score)[:n]


def _candidatos():
    return [Scored(ChunkDoc("a#1", "A", "1", "t", "x" * 2000, "s", ("1.3",)), 0.9),
            Scored(ChunkDoc("b#1", "B", "2", "t", "y", "s"), 0.05)]


def test_evidence_aplica_umbral_y_recorta_el_texto():
    ev = evidence("q", _candidatos(), RerankerSimple(), threshold=0.1)
    assert [c["chunk_id"] for c in ev["citations"]] == ["a#1"]
    assert len(ev["citations"][0]["text"]) == 1200
    assert evidence("q", _candidatos(), RerankerSimple(), threshold=0.99)["citations"] == []        # → ESCALAR


def test_make_tool_tiene_nombre_firma_y_docstring_para_el_modelo():
    t = make_tool("buscar_x", lambda q: {"query": q, "citations": []}, "en las políticas")
    assert t.__name__ == "buscar_x" and "Args:" in t.__doc__ and "Returns:" in t.__doc__
    assert str(inspect.signature(t)) == "(consulta: str) -> dict"
    assert t("hola") == {"query": "hola", "citations": []}


def test_build_auditor_usa_la_herramienta_y_la_salida_estructurada():
    pytest.importorskip("google.adk")
    t = make_tool("buscar_politicas_y_reporte", lambda q: {}, "en dos fuentes")
    a = build_auditor(t, "auditor_demo", extra=" EXTRA.")
    assert a.name == "auditor_demo" and a.output_schema is AuditDecision and len(a.tools) == 1
    assert "buscar_politicas_y_reporte" in a.instruction and a.instruction.endswith(" EXTRA.")
    assert "ESCALAR" in INSTRUCTION


# ------------------------------------------------------------------ app de ADK (adk web)
def test_la_app_expone_root_agent_con_politicas_por_defecto(monkeypatch):
    pytest.importorskip("google.adk")
    monkeypatch.delenv("AUDITOR_FUENTE", raising=False)
    import auditor_rag_app.agent as app
    app = importlib.reload(app)
    assert app.root_agent.name == "auditor_politicas" and app.root_agent.tools[0].__name__ == "buscar_politicas"
    r = app.root_agent.tools[0]("viaje internacional sin autorización previa")
    assert 0 < len(r["citations"]) <= 3
    # El umbral offline se calibra solo: con el 0.05 por defecto del reranker léxico el yate dejaba pasar una cita.
    assert app.root_agent.tools[0]("Compra de un yate para la dirección")["citations"] == []
    for caso in CASOS:
        assert app.root_agent.tools[0](caso["descripcion"])["citations"], caso["id"]       # y los 6 casos conservan evidencia


def test_la_app_rechaza_rag_engine_sin_modo_cloud_y_fuentes_desconocidas(monkeypatch):
    pytest.importorskip("google.adk")
    import auditor_rag_app.agent as app
    monkeypatch.setenv("AUDITOR_FUENTE", "rag_engine")
    with pytest.raises(RuntimeError, match="AGENTS_MODE=cloud"):
        importlib.reload(app)
    monkeypatch.setenv("AUDITOR_FUENTE", "otra")
    with pytest.raises(RuntimeError, match="desconocida"):
        importlib.reload(app)
    monkeypatch.delenv("AUDITOR_FUENTE")
    importlib.reload(app)                                        # deja el módulo en su estado normal
