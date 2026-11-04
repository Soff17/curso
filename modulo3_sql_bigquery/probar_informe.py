"""Mide los puntajes de la búsqueda en el informe de presupuesto, para calibrar su umbral (UMBRAL_INFORME).

    . .\\env.ps1
    python modulo3_sql_bigquery/probar_informe.py             # con tu .env en cloud: 💸 embeddings + Ranking API (centavos)
    $env:AGENTS_MODE="offline"; python modulo3_sql_bigquery/probar_informe.py     # sin servicios

Imprime, sin aplicar el umbral, el puntaje de las tres secciones mejor puntuadas para cada pregunta. Las preguntas
«relevantes» deberían encontrar su sección; las «fuera del informe» no deberían pasar el umbral.
Ojo: el informe solo cubre la división Norte; una pregunta por otra división parece relevante para el buscador
(habla de presupuesto y categorías) y la tiene que detectar el agente al leer el texto, no el umbral.
"""
import os
import unicodedata

from shared.config import RETRIEVE_K, is_cloud
from sqlagent.informe import UMBRAL_INFORME, _markdown, _rag_engine

# (pregunta, sección esperada en el markdown, texto que debe contener el fragmento si el informe viene de RAG Engine,
#  donde los fragmentos los corta el servicio y ya no coinciden con las secciones)
RELEVANTES = [
    ("presupuesto aprobado y ejecucion por categoria de la division Norte", "2", "78,000"),
    ("presupuesto aprobado de Consultoria de la division Norte en el 3T 2026", "2", "78,000"),
    ("el exceso de consultoria tiene aprobacion del Comite Financiero", "3", "Comité Financiero"),
    ("por que se redujo el presupuesto de Marketing", "2", "reasignación"),
    ("que espera la administracion del gasto de consultoria en el cuarto trimestre", "4", "4T 2026"),
    ("para que sirve este informe y que fecha de corte tiene", "1", "cierre contable"),
]
RAG_ENGINE = os.getenv("INFORME_FUENTE", "markdown").lower() == "rag_engine"
FUERA_DEL_INFORME = ["Receta de paella valenciana para ocho personas", "xyzzy qwerty plugh",
                     "Quien gano el mundial de futbol de 1998", "existencias de productos en las tiendas"]


def _norm(texto: str) -> str:
    """Minúsculas, sin acentos y con los espacios y saltos de línea reducidos a uno solo."""
    sin_acentos = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    return " ".join(sin_acentos.lower().split())


def _top3(pregunta: str) -> list[tuple[str, float, str]]:
    retriever, reranker = _rag_engine() if RAG_ENGINE else _markdown()
    hits = reranker.rerank(pregunta, retriever.search(pregunta, RETRIEVE_K), 3)
    return [(h.chunk.id.split("#")[-1] if RAG_ENGINE is False else h.chunk.id[-12:], h.score, h.chunk.text) for h in hits]


def _fmt(top: list[tuple[str, float, str]]) -> str:
    etiqueta = "fragmento" if RAG_ENGINE else "sección"
    return "  ".join(f"{etiqueta} {a}={s:.3f}{'' if s >= UMBRAL_INFORME else '*'}" for a, s, _ in top) or "(sin candidatos)"


def main() -> None:
    fuente = "RAG Engine (PDF)" if RAG_ENGINE else "markdown"
    print(f"Modo: {'cloud (embeddings + Ranking API)' if is_cloud() else 'offline (TF-IDF + reranker léxico)'} · informe: {fuente} "
          f"| umbral = {UMBRAL_INFORME}  (* = por debajo del umbral)\n")
    aciertos, relevantes = 0, []
    for pregunta, esperada, clave in RELEVANTES:
        top = _top3(pregunta)
        # markdown: la sección esperada; RAG Engine: los fragmentos los corta el servicio, se busca el texto esperado
        # el texto que devuelve el analizador puede traer saltos de línea o letras sin acento: se normaliza antes de buscar
        correcto = (lambda a, t: _norm(clave) in _norm(t)) if RAG_ENGINE else (lambda a, t: a == esperada)
        ok = bool(top) and correcto(top[0][0], top[0][2])
        aciertos += ok
        relevantes += [s for a, s, t in top if correcto(a, t)]
        print(("OK  " if ok else "MAL ") + pregunta + f"  (esperada: {'texto «' + clave + '»' if RAG_ENGINE else 'sección ' + esperada})\n      " + _fmt(top))
        if RAG_ENGINE and not ok and top:
            print("      texto del fragmento (primeros 400 caracteres):", " ".join(top[0][2].split())[:400])
    print(f"\nAciertos: {aciertos} de {len(RELEVANTES)}\n\nFuera del informe (ninguna debería pasar el umbral):")
    irrelevantes = []
    for pregunta in FUERA_DEL_INFORME:
        top = _top3(pregunta)
        irrelevantes += [s for _, s, _ in top]
        print(f"  {pregunta}\n      {_fmt(top)}")
    if relevantes and irrelevantes:
        print(f"\nPara calibrar: lo irrelevante llega a {max(irrelevantes):.3f} y la sección correcta baja hasta "
              f"{min(relevantes):.3f}. El umbral va entre los dos (punto medio {(max(irrelevantes) + min(relevantes)) / 2:.3f}).")


if __name__ == "__main__":
    main()
