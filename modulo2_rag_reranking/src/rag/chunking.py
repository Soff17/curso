"""Chunking financiero.

Dos familias de documentos:

1. ESTRUCTURADOS (markdown con «## Artículo n.m – Título»): `semantic_chunks` / `load_corpus` cortan por artículo,
   así un chunk es un artículo y la cita es exacta («Art. 1.3»).
2. NO ESTRUCTURADOS (texto que sale de un PDF leído por un analizador): `ChunkDoc`, `to_chunk_doc`,
   `split_by_structure` y `split_semantic` reconstruyen documento, artículos y cita DENTRO del texto.
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

ART_RE = re.compile(r"^##\s+((?:Art[íi]culo|Nota)\s+(\d+\.\d+))\s*[–-]\s*(.+)$", re.M)


@dataclass(frozen=True)
class Chunk:
    id: str            # p.ej. POL-VIA-2026#1.3
    doc: str           # nombre del documento
    article: str       # "1.3"
    title: str         # título del artículo
    text: str          # texto del artículo (con encabezado, mejora el embedding)
    source: str        # ruta del archivo

    @property
    def citation(self) -> str:
        return f"{self.doc}, Art. {self.article} ({self.title})"


def _doc_code(text: str, fallback: str) -> str:
    m = re.search(r"\(([^)]*\d{4})\)", text.splitlines()[0])
    if m:
        return m.group(1).split()[-1] if " " in m.group(1) else m.group(1)
    return fallback


def semantic_chunks(path: Path, max_chars: int = 900) -> list[Chunk]:
    """Chunking POR ESTRUCTURA de un .md: un chunk por artículo (los muy largos se parten por oraciones)."""
    raw = path.read_text(encoding="utf-8")
    doc = _doc_code(raw, path.stem)
    matches = list(ART_RE.finditer(raw))
    chunks: list[Chunk] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        body = raw[m.end():end].strip()
        header = f"{doc} – {m.group(1)} – {m.group(3)}"
        # Si un artículo excede max_chars se divide por oraciones (nunca a mitad de frase).
        parts, cur = [], ""
        for sent in re.split(r"(?<=[.;])\s+", body):
            if len(cur) + len(sent) > max_chars and cur:
                parts.append(cur.strip())
                cur = ""
            cur += sent + " "
        parts.append(cur.strip())
        for j, part in enumerate(p for p in parts if p):
            cid = f"{doc}#{m.group(2)}" + (f".{j}" if len(parts) > 1 else "")
            chunks.append(Chunk(cid, doc, m.group(2), m.group(3).strip(), f"{header}\n{part}", str(path)))
    return chunks


def load_corpus(folder: Path) -> list[Chunk]:
    out: list[Chunk] = []
    for p in sorted(folder.glob("*.md")):
        out.extend(semantic_chunks(p))
    return out


# ======================================================================================================
# Documentos NO estructurados: el texto sale de un PDF (analizador por defecto o de LLM) y no trae ids.
# ======================================================================================================
@dataclass(frozen=True)
class ChunkDoc(Chunk):
    """Fragmento de un documento no estructurado. `articulos` son los números de artículo o nota que
    aparecen DENTRO del texto (puede haber varios, o ninguno, p. ej. en un reporte 10-Q)."""
    articulos: tuple = ()

    @property
    def citation(self) -> str:
        if self.articulos:
            etiqueta = "Art." if len(self.articulos) == 1 else "Arts."
            return f"{self.doc}, {etiqueta} {' y '.join(self.articulos)} ({self.title or 'sin título'})"
        return f"{self.doc}, fragmento {self.article} ({self.title or 'sin sección'})"


ARTICLE_REF_RE = re.compile(r"(?:Art[íi]culo|Nota)\s+(\d+\.\d+)")
ARTICLE_TITLE_RE = re.compile(r"(?:Art[íi]culo|Nota)\s+(\d+\.\d+)\s*[-–]\s*([^\n*<|]+)")
ITEM_RE = re.compile(r"Item\s+(1A|1|2)\s*[-–]\s*([^\n<*(]+)")
_STRUCTURE_SPLIT_RE = re.compile(r"\n(?=\W*(?:Art[íi]culo|Nota)\s+\d+\.\d+)")


def doc_from_source(source: str) -> str:
    """Nombre del documento a partir de la ruta del archivo.
    `gs://b/pdf_politicas/POL-VIA-2026.pdf` y `.../POL-VIA-2026__1.3.md` → `POL-VIA-2026`."""
    nombre = source.split("/")[-1].rsplit(".", 1)[0].split("__")[0]
    if nombre.startswith("10q"):
        return "10-Q 3T 2026 (PDF escaneado)" if "escaneado" in nombre else "10-Q 3T 2026 (PDF)"
    return nombre


def to_chunk_doc(text: str, source: str, index: int = 0) -> ChunkDoc:
    """Convierte un fragmento de texto (p. ej. de RAG Engine) en un `ChunkDoc` con documento, artículos y cita."""
    doc = doc_from_source(source)
    arts = tuple(dict.fromkeys(ARTICLE_REF_RE.findall(text)))
    titulos: dict[str, str] = {}
    for n, t in ARTICLE_TITLE_RE.findall(text):
        titulos.setdefault(n, t.strip())
    if arts:
        titulo, cid, art = titulos.get(arts[0], ""), f"{doc}#{arts[0]}", arts[0]
    else:
        m = ITEM_RE.search(text)
        titulo = f"Item {m.group(1)} – {m.group(2).strip()}" if m else ""
        cid, art = f"{doc}#frag{index}", str(index + 1)
    return ChunkDoc(id=cid, doc=doc, article=art, title=titulo, text=text, source=source, articulos=arts)


def chunk_articles(chunk: Chunk) -> set[str]:
    """Artículos que contiene un chunk. Un fragmento sin artículos (p. ej. del 10-Q) no aporta ninguno."""
    return set(chunk.articulos) if hasattr(chunk, "articulos") else {chunk.article}


def split_by_structure(text: str) -> list[str]:
    """Corta el texto extraído en cada «Artículo n.m» / «Nota n.m». La primera pieza (título) suele no tener artículo."""
    return [p for p in _STRUCTURE_SPLIT_RE.split(text) if p.strip()]


def structure_pieces(doc: str, text: str) -> dict[str, str]:
    """Forma C: {«DOC__n.m»: texto} con un trozo por artículo (se descarta el encabezado sin artículo)."""
    piezas: dict[str, str] = {}
    for p in split_by_structure(text):
        m = ARTICLE_REF_RE.search(p)
        if m:
            piezas[f"{doc}__{m.group(1)}"] = f"{doc}\n{p.strip()}"
    return piezas


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", text) if s.strip()]


def split_semantic(text: str, embed: Callable[[list[str]], np.ndarray], percentile: int = 25) -> list[str]:
    """Forma B: corta donde baja la similitud entre una oración y la siguiente (por debajo del `percentile`).
    `embed` recibe una lista de textos y devuelve una matriz normalizada (n, d). Es una HEURÍSTICA: puede
    cortar de más o de menos, y a veces separa una regla de su excepción."""
    ors = sentences(text)
    if len(ors) < 3:
        return [text]
    v = embed(ors)
    sims = (v[:-1] * v[1:]).sum(axis=1)
    umbral = float(np.percentile(sims, percentile))
    grupos, actual = [], [ors[0]]
    for i, s in enumerate(sims):
        if s <= umbral:
            grupos.append(" ".join(actual))
            actual = []
        actual.append(ors[i + 1])
    grupos.append(" ".join(actual))
    return grupos


def semantic_pieces(doc: str, text: str, embed: Callable[[list[str]], np.ndarray],
                    percentile: int = 25) -> dict[str, str]:
    """Forma B: {«DOC__sN»: texto} con los trozos semánticos de un documento."""
    return {f"{doc}__s{i}": t for i, t in enumerate(split_semantic(text, embed, percentile))}
