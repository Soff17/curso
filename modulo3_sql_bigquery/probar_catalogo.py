"""Prueba la búsqueda del catálogo (¿qué tablas elige el RAG de metadata?) y muestra los puntajes.

    . .\\env.ps1
    python modulo3_sql_bigquery/probar_catalogo.py            # offline: sin servicios, no cuesta
    $env:AGENTS_MODE="cloud"; python modulo3_sql_bigquery/probar_catalogo.py    # 💸 embeddings + Ranking API (centavos)

Para cada pregunta imprime las tres tablas mejor puntuadas con su puntaje, SIN aplicar el umbral (las que
quedarían fuera llevan un asterisco). Las preguntas «fuera del catálogo» no deberían devolver tablas: su
puntaje más alto y el más bajo de las preguntas relevantes sirven para calibrar el umbral
(variable UMBRAL_CATALOGO), igual que en el Módulo 2: el umbral va entre los dos.
"""
from shared.config import is_cloud
from sqlagent.catalog import K_CATALOGO, UMBRAL, _pipeline

CASOS = [
    ("exceso de presupuesto ejecutado por division", "presupuesto"),
    ("presupuesto ejecutado en 2025 por categoria", "presupuesto_historico"),
    ("clientes en mora dias vencido", "cuentas_por_cobrar"),
    ("cuanto pagaron los clientes en septiembre", "pagos_clientes"),
    ("viajes sin autorizacion previa del director", "viaticos_detalle"),
    ("contratos de consultoria aprobados por el comite financiero", "contratos_consultoria"),
    ("inversion en campañas de marketing por canal", "gastos_marketing_campanas"),
    ("hallazgos de auditoria abiertos de severidad alta", "hallazgos_auditoria"),
    ("provision por cuentas incobrables de mas de 90 dias", "provisiones_cobranza"),
    ("existencias de productos en tiendas", "inventario_tiendas"),
    ("Norte excedio el presupuesto de Consultoria en Q3", "presupuesto"),
]
FUERA_DEL_CATALOGO = ["Receta de paella valenciana para ocho personas", "xyzzy qwerty plugh",
                      "Quien gano el mundial de futbol de 1998"]


def _top3(pregunta: str) -> list[tuple[str, float]]:
    retriever, reranker = _pipeline()
    hits = reranker.rerank(pregunta, retriever.search(pregunta, K_CATALOGO), 3)
    return [(h.chunk.title, h.score) for h in hits]


def _fmt(top: list[tuple[str, float]]) -> str:
    return "  ".join(f"{t}={s:.3f}{'' if s >= UMBRAL else '*'}" for t, s in top) or "(sin candidatos)"


def main() -> None:
    print(f"Modo: {'cloud (embeddings + Ranking API)' if is_cloud() else 'offline (TF-IDF + reranker léxico)'} "
          f"| umbral = {UMBRAL}  (* = por debajo del umbral)\n")
    aciertos, relevantes = 0, []
    for pregunta, esperada in CASOS:
        top = _top3(pregunta)
        ok = bool(top) and top[0][0] == esperada
        aciertos += ok
        relevantes += [s for t, s in top if t == esperada]
        print(("OK  " if ok else "MAL ") + pregunta + f"  (esperada: {esperada})\n      " + _fmt(top))
    print(f"\nAciertos: {aciertos} de {len(CASOS)}")
    print("\nFuera del catálogo (ninguna debería pasar el umbral):")
    irrelevantes = []
    for pregunta in FUERA_DEL_CATALOGO:
        top = _top3(pregunta)
        irrelevantes += [s for _, s in top]
        print(f"  {pregunta}\n      {_fmt(top)}")
    if relevantes and irrelevantes:
        print(f"\nPara calibrar: lo irrelevante llega a {max(irrelevantes):.3f} y la tabla correcta baja hasta "
              f"{min(relevantes):.3f}. El umbral va entre los dos (el punto medio es {(max(irrelevantes) + min(relevantes)) / 2:.3f}).")


if __name__ == "__main__":
    main()
