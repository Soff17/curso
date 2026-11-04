"""Chunking de documentos NO estructurados (texto que sale de un PDF): documento, artículos y cita se reconstruyen
DENTRO del texto. Todo offline."""
import numpy as np

from rag.chunking import (ChunkDoc, Chunk, chunk_articles, doc_from_source, sentences, split_by_structure,
                          split_semantic, structure_pieces, semantic_pieces, to_chunk_doc)

TEXTO_PDF = (
    "Política de Viáticos y Gastos de Viaje (Documento POL-VIA-2026)\n"
    "EJEMPLO SINTÉTICO PARA EL CURSO.\n"
    "## Artículo 1.1 - Alcance\nAplica a todo empleado.\n"
    "## Artículo 1.2 - Límites diarios\nEl límite es de USD 150 por día. Incluye hospedaje.\n"
    "**Artículo 1.3 - Autorización previa**\nTodo viaje que exceda USD 1,500 requiere autorización previa.")


def test_doc_from_source_varios_formatos():
    assert doc_from_source("gs://b/pdf_politicas/POL-VIA-2026.pdf") == "POL-VIA-2026"
    assert doc_from_source("gs://b/pol_C/POL-VIA-2026__1.3.md") == "POL-VIA-2026"       # trozo subido como archivo
    assert doc_from_source("gs://b/pol_B/AUD-2026__s2.md") == "AUD-2026"
    assert doc_from_source("gs://b/x/10q_norte_3t26.pdf") == "10-Q 3T 2026 (PDF)"
    assert doc_from_source("gs://b/x/10q_norte_3t26_escaneado.pdf") == "10-Q 3T 2026 (PDF escaneado)"


def test_to_chunk_doc_un_articulo_cita_exacta():
    c = to_chunk_doc("**Artículo 1.3 - Autorización previa**\nTodo viaje que exceda USD 1,500.",
                     "gs://b/pol_C/POL-VIA-2026__1.3.md")
    assert isinstance(c, ChunkDoc)
    assert c.id == "POL-VIA-2026#1.3" and c.articulos == ("1.3",)
    assert c.citation == "POL-VIA-2026, Art. 1.3 (Autorización previa)"


def test_to_chunk_doc_varios_articulos_en_un_fragmento():
    c = to_chunk_doc(TEXTO_PDF, "gs://b/pdf_politicas/POL-VIA-2026.pdf")
    assert c.articulos == ("1.1", "1.2", "1.3")
    assert c.citation.startswith("POL-VIA-2026, Arts. 1.1 y 1.2 y 1.3")


def test_to_chunk_doc_reporte_sin_articulos_usa_el_item():
    c = to_chunk_doc("Norte Retail – Item 1 - Estados financieros\n<table>...</table>",
                     "gs://b/x/10q_norte_3t26_escaneado.pdf", index=1)
    assert c.articulos == () and c.id == "10-Q 3T 2026 (PDF escaneado)#frag1"
    assert c.citation == "10-Q 3T 2026 (PDF escaneado), fragmento 2 (Item 1 – Estados financieros)"


def test_chunk_articles_distingue_chunk_y_chunkdoc():
    assert chunk_articles(Chunk("x#1.3", "D", "1.3", "T", "t", "s")) == {"1.3"}
    assert chunk_articles(ChunkDoc("x", "D", "1", "", "t", "s", ("1.1", "1.2"))) == {"1.1", "1.2"}
    assert chunk_articles(ChunkDoc("x", "D", "3", "", "t", "s")) == set()       # un fragmento sin artículos no aporta ninguno


def test_corte_por_estructura_un_trozo_por_articulo():
    piezas = split_by_structure(TEXTO_PDF)
    assert len(piezas) == 4                                    # el encabezado + 3 artículos
    solo_articulos = structure_pieces("POL-VIA-2026", TEXTO_PDF)
    assert list(solo_articulos) == ["POL-VIA-2026__1.1", "POL-VIA-2026__1.2", "POL-VIA-2026__1.3"]
    assert all(t.startswith("POL-VIA-2026\n") for t in solo_articulos.values())


def _embed_dos_temas(textos: list[str]) -> np.ndarray:
    """Embedding simulado: oraciones de «viaje» y de «consultoría» forman dos grupos bien separados."""
    v = []
    for i, t in enumerate(textos):
        base = np.array([1.0, 0.05 * i]) if "viaje" in t else np.array([0.05 * i, 1.0])
        v.append(base / np.linalg.norm(base))
    return np.array(v)


def test_corte_semantico_nunca_mezcla_dos_temas():
    texto = ("El viaje nacional tiene un límite diario. El viaje internacional tiene otro límite. "
             "Todo viaje requiere autorización. Un viaje de emergencia permite excepciones. "
             "La consultoría externa debe estar en el presupuesto. Los contratos de consultoría piden tres cotizaciones. "
             "Un exceso de consultoría requiere aprobación. La consultoría no se puede fraccionar.")
    grupos = split_semantic(texto, _embed_dos_temas, percentile=25)
    assert len(grupos) >= 2
    for g in grupos:                                           # cada trozo habla de UN solo tema
        assert ("viaje" in g) != ("consultoría" in g)
    piezas = semantic_pieces("POL-X", texto, _embed_dos_temas)
    assert list(piezas)[0] == "POL-X__s0" and len(piezas) == len(grupos)


def test_corte_semantico_con_muy_pocas_oraciones_no_corta():
    assert split_semantic("Una sola oración. Y otra.", _embed_dos_temas) == ["Una sola oración. Y otra."]
    assert len(sentences("Uno. Dos; tres. Cuatro")) == 4
