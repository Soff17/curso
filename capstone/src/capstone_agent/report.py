"""Consolidación determinista (referencia offline) del informe ejecutivo del Capstone.

Cada cifra del informe sale de una herramienta y lleva una referencia [R#]. En cloud, el
Supervisor (LLM) redacta el texto, pero DEBE usar estas mismas herramientas y referencias.
"""
from bi_agents.agent import diagnosticar_division
from bi_agents.ml_tools import estimar_probabilidad_mora
from rag.auditor import buscar_politicas
from sqlagent.agent import ejecutar_sql


def _usd(x: float) -> str:
    return f"USD {x:,.0f}"


def build_report(division: str = "Norte", trimestre: str = "2026-Q3") -> dict:
    refs: list[dict] = []

    def ref(kind: str, detail: str) -> str:
        refs.append({"id": f"R{len(refs) + 1}", "tipo": kind, "detalle": detail})
        return f"[R{len(refs)}]"

    # 1) Agente SQL
    sql = (f"SELECT categoria, presupuestado, ejecutado FROM presupuesto "
           f"WHERE division='{division}' AND trimestre='{trimestre}' ORDER BY (ejecutado-presupuestado) DESC")
    q = ejecutar_sql(sql)
    if q["status"] != "ok":
        raise RuntimeError(q)
    rows = q["rows"]
    r_sql = ref("SQL", q["sql"])
    tp = sum(r["presupuestado"] for r in rows)
    te = sum(r["ejecutado"] for r in rows)
    dev = (te - tp) / tp * 100
    excess = [r for r in rows if r["ejecutado"] > r["presupuestado"] * 1.10]

    # 2) Agente RAG + Rerank
    ev = buscar_politicas(f"exceso presupuestal consultoría viáticos división {division} aprobación desviación trimestral")
    cites = ev["citations"]
    r_pol = [ref("POLITICA", c["citation"]) for c in cites]
    by_art = {c["chunk_id"]: r for c, r in zip(cites, r_pol)}  # "POL-CON-2026#2.3" -> "[R2]"
    # Segunda consulta RAG (+rerank) para la normativa de cobranza/riesgo.
    for c in buscar_politicas("cartera en mora porcentaje alerta riesgo de impago comité de riesgos")["citations"]:
        if c["chunk_id"] not in by_art:
            by_art[c["chunk_id"]] = ref("POLITICA", c["citation"])

    # 3) Agente ML & BI
    mora = estimar_probabilidad_mora(division)  # la cartera solo tiene corte 2026-Q3 (último disponible)
    diag = diagnosticar_division(division)
    if mora["status"] != "ok" or diag["status"] != "ok":
        raise RuntimeError(f"Fuente ML/BI no disponible: {mora} {diag.get('forecast')}")
    r_ml = ref("ML", f"{mora['modelo']} -> probabilidad_mora (cartera corte 2026-Q3)")
    r_bi = ref("BI", f"Tableau/{diag['fuente_grafica']} vista GastoMensual: {diag['lectura_visual']}")

    # 4) Supervisor: consolida
    lines = [f"# Informe ejecutivo – División {division}, {trimestre}", "",
             "## Hallazgos",
             f"- Presupuestado {_usd(tp)} vs ejecutado {_usd(te)}: desviación **{dev:+.1f}%** {r_sql}."]
    for r in excess:
        p = (r["ejecutado"] - r["presupuestado"]) / r["presupuestado"] * 100
        lines.append(f"- {r['categoria']}: {_usd(r['ejecutado'])} vs {_usd(r['presupuestado'])} ({p:+.1f}%) {r_sql}.")
    lines += ["", "## ¿Estaba permitido el exceso?"]
    if cites:
        lines.append("Artículos relevantes tras reranking (top-3): " + ", ".join(r_pol) + ".")
    # Solo se afirma una norma si fue recuperada por el RAG (con su referencia exacta).
    if dev > 15 and "POL-PRE-2026#3.2" in by_art:
        lines.append(f"- La desviación total supera 15 % → requiere plan de remediación (POL-PRE-2026, Art. 3.2) {by_art['POL-PRE-2026#3.2']}.")
    if any(r["categoria"] == "Consultoria" for r in excess) and "POL-CON-2026#2.3" in by_art:
        lines.append(f"- El exceso en Consultoría supera 10 % → exigía aprobación previa del Comité Financiero (POL-CON-2026, Art. 2.3) {by_art['POL-CON-2026#2.3']}.")
    lines += ["", "## Riesgo de impago proyectado",
              f"- Modelo {mora['modelo']}: probabilidad de mora **{mora['probabilidad_mora']:.1%}** "
              f"(riesgo {mora['riesgo']}); {mora['pct_cartera_mora']:.0%} de la cartera está en mora {r_ml}.",
              *(["- Más de 20 % de la cartera en mora → alerta al Comité de Riesgos (POL-COB-2026, Art. 4.3) "
                 + by_art["POL-COB-2026#4.3"] + "."] if mora["pct_cartera_mora"] > 0.20 and "POL-COB-2026#4.3" in by_art else []),
              f"- Validación visual: {diag['lectura_visual']} {r_bi}", "",
              "## Referencias"] + [f"- {r['id']} ({r['tipo']}): {r['detalle']}" for r in refs]
    return {"markdown": "\n".join(lines), "refs": refs,
            "datos": {"desviacion_pct": round(dev, 2), "total_presupuestado": tp, "total_ejecutado": te,
                      "mora": mora, "categorias_excedidas": [r["categoria"] for r in excess]}}


if __name__ == "__main__":
    print(build_report()["markdown"])
