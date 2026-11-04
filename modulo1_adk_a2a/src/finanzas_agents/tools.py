"""Herramientas del Especialista en Presupuestos (lectura de SQLite en modo offline)."""
import sqlite3

from shared.config import DB_PATH

from .contracts import BudgetLine, BudgetRequest, BudgetResponse


def get_budget(req: BudgetRequest) -> BudgetResponse:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        sql = ("SELECT categoria, presupuestado, ejecutado FROM presupuesto "
               "WHERE division=? AND trimestre=?")
        params: list = [req.division, req.trimestre]
        if req.categoria:
            sql += " AND categoria=?"
            params.append(req.categoria)
        rows = con.execute(sql, params).fetchall()
    finally:
        con.close()
    if not rows:
        raise ValueError(f"Sin datos para {req.division} {req.trimestre}")
    lines = [BudgetLine(categoria=c, presupuestado=p, ejecutado=e) for c, p, e in rows]
    tp = sum(l.presupuestado for l in lines)
    te = sum(l.ejecutado for l in lines)
    return BudgetResponse(division=req.division, trimestre=req.trimestre, lineas=lines,
                          total_presupuestado=round(tp, 2), total_ejecutado=round(te, 2),
                          desviacion_pct=round((te - tp) / tp * 100, 2))


def consultar_presupuesto(division: str, trimestre: str, categoria: str = "") -> dict:
    """Consulta presupuesto vs ejecutado de una división y trimestre.

    Args:
        division: Norte, Sur, Centro u Occidente.
        trimestre: formato AAAA-Qn, por ejemplo 2026-Q3.
        categoria: opcional (Viaticos, Consultoria, Tecnologia, Marketing, Servicios).

    Returns:
        dict con líneas por categoría, totales y desviación porcentual.
    """
    try:
        req = BudgetRequest(division=division, trimestre=trimestre, categoria=categoria or None)
        return {"status": "ok", **get_budget(req).model_dump()}
    except Exception as exc:  # el LLM recibe el error de forma estructurada
        return {"status": "error", "message": str(exc)}
