import pytest
from finanzas_agents.tools import consultar_presupuesto


@pytest.mark.parametrize("cat", ["Tecnología", "tecnologia", "TECNOLOGÍA", " Tecnologia "])
def test_categoria_con_tildes_y_mayusculas(cat):
    r = consultar_presupuesto("Sur", "2026-Q1", cat)
    assert r["status"] == "ok" and r["lineas"][0]["categoria"] == "Tecnologia"


def test_categoria_invalida_da_mensaje_claro():
    r = consultar_presupuesto("Sur", "2026-Q1", "Comida")
    assert r["status"] == "error" and "Categoría inválida" in r["message"] and "Viaticos" in r["message"]


def test_viaticos_con_tilde():
    assert consultar_presupuesto("Norte", "2026-Q3", "Viáticos")["lineas"][0]["categoria"] == "Viaticos"
