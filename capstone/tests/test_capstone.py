import re

from capstone_agent.report import build_report


def test_informe_norte_q3():
    r = build_report("Norte", "2026-Q3")
    md, d = r["markdown"], r["datos"]
    assert d["desviacion_pct"] > 15
    assert "Consultoria" in d["categorias_excedidas"]
    assert "Art. 2.3" in md and "Art. 3.2" in md
    assert d["mora"]["riesgo"] in {"MEDIO", "ALTO"}


def test_toda_afirmacion_tiene_referencia():
    r = build_report("Norte", "2026-Q3")
    ids = {x["id"] for x in r["refs"]}
    body = r["markdown"].split("## Referencias")[0]
    cited = set(re.findall(r"\[(R\d+)\]", body))
    assert cited and cited <= ids
    for line in body.splitlines():
        if re.search(r"USD [\d,]+", line):
            assert re.search(r"\[R\d+\]", line), line


def test_pregunta_sorpresa_otra_division():
    r = build_report("Sur", "2026-Q2")
    assert r["datos"]["desviacion_pct"] < 15 and not r["datos"]["categorias_excedidas"]
