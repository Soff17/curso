"""Gate de CI/CD: evalúa Faithfulness del agente RAG y bloquea el despliegue si no alcanza el umbral.

Uso:  python -m agentops.eval_gate --threshold 0.85 [--agent offline|cloud]
Código de salida: 0 = autorizado, 1 = bloqueado.
"""
import argparse
import json
import sys

from rag.auditor import buscar_politicas

from shared.config import DATA_DIR

from .metrics import answer_relevance, context_recall, faithfulness


def offline_agent(descripcion: str) -> dict:
    """Agente de referencia determinista: responde SOLO con texto de los fragmentos recuperados."""
    ev = buscar_politicas(descripcion)
    cites = ev["citations"]
    if not cites:
        return {"answer": "ESCALAR: sin evidencia suficiente.", "contexts": [], "ids": []}
    top = cites[0]
    body = top["text"].split("\n", 1)[1]
    return {"answer": f"Según {top['citation']}: {body}",
            "contexts": [c["text"] for c in cites], "ids": [c["chunk_id"] for c in cites]}


def run_eval(agent_fn=offline_agent) -> dict:
    casos = json.loads((DATA_DIR / "casos_gasto.json").read_text(encoding="utf-8"))
    rows = []
    for c in casos:
        out = agent_fn(c["descripcion"])
        retrieved_articles = [i.split("#")[1] for i in out["ids"]]  # "1.3" (sin sufijo de sub-chunk)
        rows.append({
            "id": c["id"],
            "faithfulness": faithfulness(out["answer"], out["contexts"]),
            "answer_relevance": answer_relevance(c["descripcion"], out["answer"]),
            "context_recall": context_recall(retrieved_articles, c["articulos_esperados"]),
        })
    n = len(rows)
    agg = {k: round(sum(r[k] for r in rows) / n, 4) for k in ("faithfulness", "answer_relevance", "context_recall")}
    return {"casos": rows, "promedio": agg}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--threshold", type=float, default=0.85)
    ap.add_argument("--report", default="eval_report.json")
    args = ap.parse_args(argv)
    rep = run_eval()
    ok = rep["promedio"]["faithfulness"] >= args.threshold
    rep["umbral_faithfulness"], rep["autorizado"] = args.threshold, ok
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(json.dumps(rep["promedio"], ensure_ascii=False), "->", "AUTORIZADO" if ok else "BLOQUEADO")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
