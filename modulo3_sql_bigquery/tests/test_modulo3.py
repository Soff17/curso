import pytest

from sqlagent.agent import contrastar_con_informe, ejecutar_sql
from sqlagent.catalog import buscar_esquema
from sqlagent.guardrails import UnsafeSQL, validate_sql

T = {"presupuesto", "gastos", "cuentas_por_cobrar"}


@pytest.mark.parametrize("bad", [
    "DROP TABLE gastos", "SELECT * FROM gastos; DELETE FROM gastos",
    "UPDATE gastos SET monto=0", "SELECT * FROM usuarios", "SELECT 1 -- x",
    "SELECT * INTO nueva FROM gastos", "PRAGMA table_info(gastos)",
])
def test_bloquea_peligrosos(bad):
    with pytest.raises(UnsafeSQL):
        validate_sql(bad, T)


def test_agrega_y_limita_limit():
    assert validate_sql("SELECT * FROM gastos", T).endswith("LIMIT 1000")
    assert validate_sql("SELECT * FROM gastos LIMIT 99999", T).endswith("LIMIT 1000")
    assert validate_sql("SELECT * FROM gastos LIMIT 5", T).endswith("LIMIT 5")


def test_rag_metadata_elige_tabla_correcta():
    assert buscar_esquema("exceso de presupuesto ejecutado por division")["tablas"][0]["tabla"] == "presupuesto"
    assert buscar_esquema("clientes en mora dias vencido")["tablas"][0]["tabla"] == "cuentas_por_cobrar"


def test_ejecuta_norte_q3():
    r = ejecutar_sql("SELECT SUM(presupuestado) p, SUM(ejecutado) e FROM presupuesto "
                     "WHERE division='Norte' AND trimestre='2026-Q3'")
    assert r["status"] == "ok" and r["rows"][0]["e"] > r["rows"][0]["p"]


def test_ejecutar_bloquea_escritura():
    assert ejecutar_sql("DELETE FROM gastos")["status"] == "bloqueado"


def test_contraste():
    assert contrastar_con_informe(100.0, 100.5)["coincide"] is True
    assert contrastar_con_informe(100.0, 150.0)["coincide"] is False


# --- guardrails por dialecto (sqlglot) -------------------------------------------------------

@pytest.mark.parametrize("bad", [
    "SELECT * FROM gastos, usuarios",                       # unión con coma: la regex anterior la dejaba pasar
    "SELECT * FROM gastos g JOIN usuarios u ON 1=1",
    "SELECT * FROM (SELECT * FROM usuarios) t",
    "WITH x AS (SELECT * FROM usuarios) SELECT * FROM x",
])
@pytest.mark.parametrize("dialect", ["sqlite", "tsql", "bigquery"])
def test_tablas_ocultas_bloqueadas(bad, dialect):
    with pytest.raises(UnsafeSQL):
        validate_sql(bad, T, dialect=dialect)


def test_cte_sobre_tabla_permitida_pasa():
    out = validate_sql("WITH c AS (SELECT * FROM gastos) SELECT * FROM c", T)
    assert "WITH c AS" in out and out.endswith("LIMIT 1000")


def test_tsql_usa_top_y_no_limit():
    assert validate_sql("SELECT * FROM gastos", T, dialect="tsql") == "SELECT TOP 1000 * FROM gastos"
    assert validate_sql("SELECT TOP 5 * FROM gastos", T, dialect="tsql") == "SELECT TOP 5 * FROM gastos"
    assert validate_sql("SELECT TOP 99999 * FROM gastos", T, dialect="tsql") == "SELECT TOP 1000 * FROM gastos"
    assert "LIMIT" not in validate_sql("SELECT * FROM gastos ORDER BY monto DESC", T, dialect="tsql")


def test_tsql_union_se_envuelve():
    out = validate_sql("SELECT division FROM gastos UNION SELECT division FROM presupuesto", T, dialect="tsql")
    assert out.startswith("SELECT TOP 1000 * FROM (") and "UNION" in out


@pytest.mark.parametrize("bad", [
    "EXEC xp_cmdshell 'dir'", "SELECT * FROM OPENROWSET('SQLNCLI','x','select 1')",
    "SELECT * INTO nueva FROM gastos", "SELECT sp_who() FROM gastos",
])
def test_tsql_bloquea_peligrosos(bad):
    with pytest.raises(UnsafeSQL):
        validate_sql(bad, T, dialect="tsql")


def test_bigquery_prefijo_de_dataset():
    ok = validate_sql("SELECT * FROM `proy.finanzas.gastos` LIMIT 5", T, dialect="bigquery",
                      allowed_schemas={"finanzas"})
    assert ok.endswith("LIMIT 5")
    with pytest.raises(UnsafeSQL):                           # misma tabla, otro dataset
        validate_sql("SELECT * FROM `proy.otro.gastos`", T, dialect="bigquery", allowed_schemas={"finanzas"})
    with pytest.raises(UnsafeSQL):
        validate_sql("SELECT * FROM EXTERNAL_QUERY('c', 'select 1')", T, dialect="bigquery")


def test_dialecto_desconocido():
    with pytest.raises(ValueError):
        validate_sql("SELECT 1", T, dialect="oracle")


# --- conectores con servicios simulados (no se llama a ningún servicio) ----------------------

class _FakeJob:
    def __init__(self, nbytes, rows):
        self.total_bytes_processed, self._rows = nbytes, rows

    def result(self, timeout=None, max_results=None):
        return self._rows[:max_results]


class _FakeBQ:
    project = "proy"

    def __init__(self, nbytes=1000, rows=None):
        self.nbytes, self.rows, self.calls = nbytes, rows or [{"n": 1}], []

    def query(self, sql, job_config=None):
        self.calls.append((sql, job_config))
        return _FakeJob(self.nbytes, self.rows)

    def list_tables(self, dataset):
        return [type("T", (), {"table_id": n}) for n in ("gastos", "presupuesto")]

    def list_models(self, dataset):
        return [type("M", (), {"model_id": "forecast_gasto"})]


def _bq(**kw):
    from sqlagent.connectors import BigQueryConnector
    return BigQueryConnector(dataset="finanzas", client=_FakeBQ(**kw.pop("client", {})), **kw)


def test_bigquery_no_cobra_si_supera_el_tope():
    con = _bq(max_bytes=10_000, client={"nbytes": 5_000_000})
    with pytest.raises(ValueError, match="tope"):
        con.run("SELECT * FROM gastos")
    assert len(con.client.calls) == 1 and con.client.calls[0][1].dry_run   # solo la prueba, nunca la consulta real


def test_bigquery_configura_dataset_y_tope():
    con = _bq(max_bytes=10_000)
    assert con.run("SELECT * FROM gastos") == [{"n": 1}]
    prueba, real = con.client.calls[0][1], con.client.calls[1][1]
    assert prueba.dry_run and not real.dry_run
    assert real.maximum_bytes_billed == 10_000
    assert str(real.default_dataset).replace(":", ".") == "proy.finanzas"
    assert con.schemas == {"finanzas"}


def test_bigquery_tables_incluye_modelos():
    assert _bq().tables() == {"gastos", "presupuesto", "forecast_gasto"}


def test_bqml_forecast_solo_con_modelos_conocidos():
    tablas = {"gastos", "forecast_gasto"}
    q = "SELECT * FROM ML.FORECAST(MODEL `finanzas.forecast_gasto`, STRUCT(3 AS horizon))"
    assert "ML.FORECAST" in validate_sql(q, tablas, dialect="bigquery", allowed_schemas={"finanzas"})
    with pytest.raises(UnsafeSQL):                                  # un modelo que no está en el dataset
        validate_sql(q.replace("forecast_gasto", "otro_modelo"), tablas, dialect="bigquery",
                     allowed_schemas={"finanzas"})
    with pytest.raises(UnsafeSQL):                                  # las funciones ML no valen en T-SQL
        validate_sql(q, tablas, dialect="tsql")


def test_ejecutar_sql_usa_el_dialecto_del_conector(monkeypatch):
    import sqlagent.agent as ag
    con = _bq(client={"rows": [{"division": "Norte"}] * 5})
    monkeypatch.setattr(ag, "get_connector", lambda: con)
    r = ag.ejecutar_sql("SELECT division FROM gastos")
    assert r["status"] == "ok" and r["sql"].endswith("LIMIT 1000") and r["n"] == 5
    assert ag.ejecutar_sql("SELECT * FROM `proy.otro.gastos`")["status"] == "bloqueado"
    assert ag.ejecutar_sql("SELECT * FROM gastos, usuarios")["status"] == "bloqueado"


# --- catálogo ampliado (22 tablas) -----------------------------------------------------------

def test_catalogo_tiene_22_tablas_con_descripcion():
    from sqlagent.catalog import _chunks
    ch = _chunks()
    assert len(ch) == 22
    assert all(c.text.startswith(f"Tabla {c.title}: ") for c in ch)       # cada una con su descripción de negocio


@pytest.mark.parametrize("pregunta,esperada", [
    ("exceso de presupuesto ejecutado por division", "presupuesto"),
    ("presupuesto ejecutado en 2025 por categoria", "presupuesto_historico"),       # parecida a la anterior
    ("clientes en mora dias vencido", "cuentas_por_cobrar"),
    ("viajes sin autorizacion previa del director", "viaticos_detalle"),
    ("contratos de consultoria aprobados por el comite financiero", "contratos_consultoria"),
    ("inversion en campañas de marketing por canal", "gastos_marketing_campanas"),
    ("hallazgos de auditoria abiertos de severidad alta", "hallazgos_auditoria"),
    ("provision por cuentas incobrables de mas de 90 dias", "provisiones_cobranza"),
    ("existencias de productos en tiendas", "inventario_tiendas"),
    ("Norte excedio el presupuesto de Consultoria en Q3", "presupuesto"),
])
def test_catalogo_elige_la_tabla_correcta(pregunta, esperada):
    assert buscar_esquema(pregunta)["tablas"][0]["tabla"] == esperada


@pytest.mark.xfail(reason="Limitación del reranker léxico: «pagaron» no coincide con «pagos». "
                          "Con embeddings y la Ranking API se espera que sí (sin verificar).", strict=True)
def test_catalogo_limite_lexico():
    assert buscar_esquema("cuanto pagaron los clientes en septiembre")["tablas"][0]["tabla"] == "pagos_clientes"


def test_catalogo_no_manda_todo_al_prompt():
    assert len(buscar_esquema("presupuesto de consultoria")["tablas"]) <= 3


# --- híbrido: el informe y la comparación de cifras ------------------------------------------

def test_contrastar_cifras_coincide_difiere_y_sin_contraparte():
    from sqlagent.agent import contrastar_cifras
    r = contrastar_cifras(
        {"Consultoria presupuesto": 78000.0, "Marketing presupuesto": 56000.0, "Servicios ejecutado": 71400.0},
        {"Consultoria presupuesto": 78000.0, "Marketing presupuesto": 52000.0, "Servicios ejecutado": 69900.0,
         "Tecnologia ejecutado": 57750.0})
    estados = {f["cifra"]: f["estado"] for f in r["filas"]}
    assert estados == {"Consultoria presupuesto": "coincide", "Marketing presupuesto": "difiere",
                       "Servicios ejecutado": "difiere", "Tecnologia ejecutado": "sin_contraparte"}
    assert (r["coinciden"], r["difieren"], r["sin_contraparte"]) == (1, 2, 1)
    marketing = next(f for f in r["filas"] if f["cifra"] == "Marketing presupuesto")
    assert marketing["diferencia"] == 4000.0 and marketing["diferencia_pct"] == 7.69


def test_contrastar_cifras_respeta_la_unidad():
    from sqlagent.agent import contrastar_cifras
    sin_escala = contrastar_cifras({"gasto": 2_880_000.0}, {"gasto": 2_880.0})
    con_escala = contrastar_cifras({"gasto": 2_880_000.0}, {"gasto": 2_880.0}, escala_informe=1000)
    assert sin_escala["filas"][0]["estado"] == "difiere" and con_escala["filas"][0]["estado"] == "coincide"


def test_informe_se_corta_por_seccion_con_cita():
    from sqlagent.informe import INFORMES_DIR, cargar_secciones
    secciones = cargar_secciones(next(INFORMES_DIR.glob("*.md")))
    assert [s.article for s in secciones] == ["1", "2", "3", "4"]
    tabla = next(s for s in secciones if s.article == "2")
    assert "78,000" in tabla.text and "124,800" in tabla.text            # la tabla queda entera en un fragmento
    assert tabla.citation.endswith("sección 2 (Presupuesto aprobado y ejecución por categoría)")


def test_buscar_informe_encuentra_la_tabla_y_calla_fuera_del_informe():
    from sqlagent.informe import buscar_informe
    citas = buscar_informe("presupuesto aprobado y ejecucion por categoria de la division Norte")["citations"]
    assert citas and "sección 2" in citas[0]["citation"]
    assert buscar_informe("xyzzy qwerty plugh")["citations"] == []


# --- catálogo en modo cloud, con servicios simulados -----------------------------------------

def test_catalogo_en_cloud_usa_embeddings_y_ranking_api(monkeypatch):
    import rag.retrieval as rt
    import sqlagent.catalog as cat
    llamadas = {}

    class FakeRetriever:
        def __init__(self, chunks):
            llamadas["chunks"] = len(chunks)
            self.chunks = chunks

        def search(self, query, k):
            llamadas["k"] = k
            return [rt.Scored(c, 0.5) for c in self.chunks[:k]]

    class FakeRanker:
        def __init__(self, config):
            llamadas["config"] = config

        def rerank(self, query, candidates, n):
            llamadas["n"] = n
            ordenados = sorted(candidates, key=lambda h: h.chunk.title != "presupuesto_historico")
            return [rt.Scored(h.chunk, 0.9) for h in ordenados[:n]]

    monkeypatch.setattr(cat, "is_cloud", lambda: True)
    monkeypatch.setattr(rt, "VertexEmbeddingRetriever", FakeRetriever)
    monkeypatch.setattr(rt, "VertexRanker", FakeRanker)
    monkeypatch.setattr(rt, "ranking_config", lambda: "projects/p/locations/global/rankingConfigs/default_ranking_config")
    cat._pipeline.cache_clear()
    try:
        r = cat.buscar_esquema("presupuesto de 2025")
        assert r["tablas"][0]["tabla"] == "presupuesto_historico"
        assert llamadas["chunks"] == 22 and llamadas["k"] == cat.K_CATALOGO and llamadas["n"] == 3
        assert llamadas["config"].endswith("default_ranking_config")
    finally:
        cat._pipeline.cache_clear()          # que otras pruebas vuelvan al modo sin servicios


# --- preparar_bigquery.py (crea el dataset y carga las tablas), con un cliente simulado -------

def _preparar():
    import importlib.util
    from pathlib import Path
    ruta = Path(__file__).resolve().parents[1] / "preparar_bigquery.py"
    spec = importlib.util.spec_from_file_location("preparar_bigquery", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeLoadJob:
    def result(self):
        return self


class _FakeCliente:
    project = "proy"

    def __init__(self):
        self.creados, self.cargas, self.borrados, self.consultas = [], [], [], []

    def create_dataset(self, ds, exists_ok=False):
        self.creados.append((ds.dataset_id, ds.location, exists_ok))

    def load_table_from_file(self, f, destino, job_config=None):
        self.cargas.append((destino, [c.name + ":" + c.field_type for c in job_config.schema]))
        return _FakeLoadJob()

    def get_table(self, ref):
        return type("T", (), {"num_rows": 1})()

    def delete_dataset(self, ref, delete_contents=False, not_found_ok=False):
        self.borrados.append((ref, delete_contents))

    def query(self, sql, job_config=None):
        self.consultas.append(sql)
        return _FakeLoadJob()


def test_preparar_bigquery_plan_cubre_las_22_tablas_sin_llamar_a_nada(capsys):
    mod = _preparar()
    assert mod.main(["--dry-run"], client_factory=lambda: pytest.fail("no debe crear un cliente")) == 0
    salida = capsys.readouterr().out
    assert "Cargar 22 tablas" in salida and "No se llamó a ningún servicio" in salida
    tablas = {t for t, _, _ in mod.tablas_a_cargar()}
    assert len(tablas) == 22 and {"presupuesto", "viaticos_detalle", "pagos_clientes"} <= tablas
    esquema = dict(next(c for t, _, c in mod.tablas_a_cargar() if t == "presupuesto"))
    assert esquema["presupuestado"] == "FLOAT64" and esquema["division"] == "STRING"
    assert dict(next(c for t, _, c in mod.tablas_a_cargar() if t == "viaticos_detalle"))["dias"] == "INT64"


def test_preparar_bigquery_carga_en_el_dataset_del_usuario_y_solo_borra_el_suyo():
    mod = _preparar()
    cli = _FakeCliente()
    assert mod.main([], client_factory=lambda: cli) == 0
    dataset = mod.nombres()["dataset"]
    assert cli.creados == [(dataset, "US", True)] and len(cli.cargas) == 22
    assert all(d.startswith(f"proy.{dataset}.") for d, _ in cli.cargas)
    assert cli.borrados == []
    cli2 = _FakeCliente()
    assert mod.main(["--limpiar"], client_factory=lambda: cli2) == 0
    assert cli2.borrados == [(f"proy.{dataset}", True)] and cli2.cargas == []


def test_preparar_bigquery_modelo_apunta_al_dataset_del_usuario():
    mod = _preparar()
    cli = _FakeCliente()
    mod.main(["--modelo"], client_factory=lambda: cli)
    dataset = mod.nombres()["dataset"]
    assert len(cli.consultas) == 1 and f"`proy.{dataset}.forecast_gasto`" in cli.consultas[0]
    assert "CREATE OR REPLACE MODEL" in cli.consultas[0] and "`finanzas." not in cli.consultas[0]


def test_app_de_adk_expone_el_agente_hibrido():
    import sql_app
    assert sql_app.agent.root_agent.name == "agente_sql"
    assert [t.__name__ for t in sql_app.agent.root_agent.tools] == [
        "buscar_esquema", "ejecutar_sql", "buscar_informe", "contrastar_cifras", "buscar_politicas"]


# --- preparar_sqlserver.py (base, tablas y logins de solo lectura), con una conexión simulada ---

def _sqlserver():
    import importlib.util
    from pathlib import Path
    ruta = Path(__file__).resolve().parents[1] / "preparar_sqlserver.py"
    spec = importlib.util.spec_from_file_location("preparar_sqlserver", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeConexion:
    def __init__(self, registro, base):
        self.registro, self.base = registro, base

    def execution_options(self, **kw):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def exec_driver_sql(self, sql, params=None):
        self.registro.append((self.base, sql, params))


class _FakeEngine:
    def __init__(self, registro, base):
        self.registro, self.base = registro, base

    def connect(self):
        return _FakeConexion(self.registro, self.base)


def test_sqlserver_ddl_y_conversion_de_tipos():
    m = _sqlserver()
    ddl = m.ddl_tabla("gastos", [("id", "INTEGER"), ("monto", "REAL"), ("proveedor", "TEXT")])
    assert "[id] INT" in ddl and "[monto] FLOAT" in ddl and "[proveedor] NVARCHAR(200)" in ddl
    assert m.convertir("12", "INTEGER") == 12 and m.convertir("1.5", "REAL") == 1.5 and m.convertir("x", "TEXT") == "x"


def test_sqlserver_clave_cumple_la_politica_y_login_solo_lectura():
    m = _sqlserver()
    clave = m.clave_nueva()
    assert len(clave) >= 16 and any(c.isupper() for c in clave) and any(c.islower() for c in clave)
    assert any(c.isdigit() for c in clave) and "!" in clave and clave != m.clave_nueva()
    en_master, en_base = m.sentencias_logins("celda1_ro", clave)
    todo = " ".join(en_master + en_base)
    assert "db_datareader" in todo and "CREATE LOGIN [celda1_ro]" in todo
    assert not any(p in todo for p in ("db_datawriter", "db_owner", "sysadmin", "GRANT"))      # solo lectura


def test_sqlserver_plan_no_se_conecta_ni_imprime_claves(capsys):
    m = _sqlserver()
    assert m.main(["--dry-run"], engine_factory=lambda base: pytest.fail("no debe conectarse")) == 0
    salida = capsys.readouterr().out
    assert "22 tablas" in salida and "No se conectó a nada" in salida and "celda5_ro" in salida
    assert "<clave al azar>" in salida


def test_sqlserver_crea_base_carga_22_tablas_y_logins(monkeypatch, capsys):
    m = _sqlserver()
    registro = []
    assert m.main(["--celdas", "2"], engine_factory=lambda base: _FakeEngine(registro, base)) == 0
    sentencias = [(b, s) for b, s, _ in registro]
    assert sentencias[0][0] == "master" and "CREATE DATABASE [finanzas]" in sentencias[0][1]
    assert sum("CREATE TABLE dbo." in s for _, s in sentencias) == 22
    inserts = [(s, p) for _, s, p in registro if s.startswith("INSERT INTO dbo.[presupuesto]")]
    assert inserts and len(inserts[0][1]) == 60 and isinstance(inserts[0][1][0][3], float)   # 60 filas, presupuestado numérico
    assert sum("CREATE LOGIN" in s for _, s in sentencias) == 2
    assert sum("ADD MEMBER" in s for _, s in sentencias) == 2
    salida = capsys.readouterr().out
    assert salida.count("MSSQL_URL=mssql+pyodbc://celda") == 2 and "TrustServerCertificate=yes" in salida
    assert "sqlserver:" not in salida                                # la cuenta administradora no se imprime


def test_sqlserver_limpiar_borra_la_base_y_los_logins():
    m = _sqlserver()
    registro = []
    assert m.main(["--limpiar", "--celdas", "2"], engine_factory=lambda base: _FakeEngine(registro, base)) == 0
    todo = " ".join(s for _, s, _ in registro)
    assert "DROP DATABASE IF EXISTS [finanzas]" in todo and todo.count("DROP LOGIN") == 2
    assert "CREATE TABLE" not in todo


def test_ml_forecast_con_el_modelo_sin_calificar_pasa_el_guardrail():
    q = ("SELECT division, forecast_timestamp, ROUND(forecast_value, 2) AS pronostico "
         "FROM ML.FORECAST(MODEL forecast_gasto, STRUCT(3 AS horizon)) ORDER BY division, forecast_timestamp")
    out = validate_sql(q, {"gastos", "forecast_gasto"}, dialect="bigquery", allowed_schemas={"finanzas_x"})
    assert "ML.FORECAST(MODEL forecast_gasto" in out and out.endswith("LIMIT 1000")
    with pytest.raises(UnsafeSQL):
        validate_sql(q.replace("forecast_gasto", "otro"), {"gastos", "forecast_gasto"}, dialect="bigquery")


def test_umbral_del_informe_en_offline_es_el_lexico():
    from sqlagent.informe import UMBRAL_INFORME
    assert UMBRAL_INFORME == 0.05                    # las pruebas corren siempre en offline


def test_el_modelo_de_pronostico_se_entrena_con_datos_mensuales():
    from sqlagent.connectors import BQML_EXAMPLE
    entrenamiento = BQML_EXAMPLE.split(";")[0]
    assert "DATE_TRUNC(DATE(fecha), MONTH)" in entrenamiento and "data_frequency='MONTHLY'" in entrenamiento
    assert "time_series_timestamp_col='mes'" in entrenamiento and "time_series_id_col='division'" in entrenamiento


# --- políticas desde RAG Engine y preparar_rag.py (corpus de políticas e informe), con simulados --

def test_politicas_por_defecto_son_las_del_modulo_2():
    from sqlagent.politicas import buscar_politicas
    citas = buscar_politicas("exceso de presupuesto en consultoria aprobacion")["citations"]
    assert citas and any("2.3" in c["citation"] for c in citas)


def test_politicas_desde_rag_engine_usan_el_corpus_y_el_umbral(monkeypatch):
    import rag.retrieval as rt
    import sqlagent.politicas as pol
    visto = {}

    class FakeRetriever:
        def __init__(self, proyecto, corpus):
            visto["corpus"] = corpus

        def search(self, query, k):
            visto["k"] = k
            c1 = pol._politicas_markdown("exceso presupuestal consultoria")["citations"][0]
            chunk = rt.Scored  # noqa: F841  (solo para dejar claro el tipo que devuelve la etapa 1)
            from rag.chunking import load_corpus
            from shared.config import POLICIES_DIR
            ch = {c.id: c for c in load_corpus(POLICIES_DIR)}[c1["chunk_id"]]
            return [rt.Scored(ch, 0.5)]

    class FakeRanker:
        def __init__(self, config):
            pass

        def rerank(self, query, candidates, n):
            return [rt.Scored(candidates[0].chunk, 0.9), rt.Scored(candidates[0].chunk, 0.05)]

    monkeypatch.setenv("AUDITOR_FUENTE", "rag_engine")
    monkeypatch.setenv("RAG_CORPUS_POLITICAS", "projects/p/locations/us-central1/ragCorpora/123")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "p")
    monkeypatch.setattr(pol, "is_cloud", lambda: True)
    monkeypatch.setattr(rt, "RagEngineRetriever", FakeRetriever)
    monkeypatch.setattr(rt, "VertexRanker", FakeRanker)
    monkeypatch.setattr(rt, "ranking_config", lambda: "cfg")
    pol._rag_engine.cache_clear()
    try:
        r = pol.buscar_politicas("exceso presupuestal en consultoria")
        assert visto["corpus"].endswith("/ragCorpora/123") and visto["k"] == 20
        assert len(r["citations"]) == 1 and r["citations"][0]["score"] == 0.9          # el 0.05 queda bajo el umbral 0.14
    finally:
        pol._rag_engine.cache_clear()


def test_politicas_rag_engine_sin_cloud_da_un_error_claro(monkeypatch):
    import sqlagent.politicas as pol
    monkeypatch.setenv("AUDITOR_FUENTE", "rag_engine")
    pol._rag_engine.cache_clear()
    with pytest.raises(RuntimeError, match="AGENTS_MODE=cloud"):
        pol.buscar_politicas("lo que sea")


def _preparar_rag():
    import importlib.util
    from pathlib import Path
    ruta = Path(__file__).resolve().parents[1] / "preparar_rag.py"
    spec = importlib.util.spec_from_file_location("preparar_rag", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeRag:
    def __init__(self, proyecto, existentes=()):
        self.proyecto, self.llamadas = proyecto, []
        self._corpora = [{"displayName": n, "name": f"projects/{proyecto}/ragCorpora/{i}"} for i, n in enumerate(existentes)]

    def list_corpora(self):
        return self._corpora

    def is_serverless(self):
        return True

    def upload(self, bucket, prefijo, archivos):
        self.llamadas.append(("upload", prefijo, sorted(archivos)))

    def create_corpus(self, nombre):
        self.llamadas.append(("create", nombre))
        return f"projects/{self.proyecto}/ragCorpora/nuevo-{nombre}"

    def import_folder(self, corpus, uri, **kw):
        self.llamadas.append(("import", uri, kw.get("llm_parser")))

    def delete_corpus(self, name):
        self.llamadas.append(("delete", name))

    def delete_bucket(self, bucket):
        self.llamadas.append(("bucket", bucket))


def test_preparar_rag_plan_no_llama_a_nada(capsys):
    m = _preparar_rag()
    assert m.main(["--dry-run"], rag_factory=lambda p: pytest.fail("no debe crear el cliente")) == 0
    salida = capsys.readouterr().out
    assert "se reutiliza" in salida and "No se llamó a ningún servicio" in salida


def test_preparar_rag_crea_los_dos_corpus_si_no_existen(monkeypatch, capsys):
    m = _preparar_rag()
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proy")
    rag = _FakeRag("proy")
    assert m.main([], rag_factory=lambda p: rag) == 0
    tipos = [(l[0], l[1] if l[0] != "import" else l[1].rsplit("/", 1)[-1]) for l in rag.llamadas]
    assert [t for t, _ in tipos].count("create") == 2 and [t for t, _ in tipos].count("import") == 2
    assert all(l[2] is True for l in rag.llamadas if l[0] == "import")                  # con el analizador de LLM
    assert any(l[0] == "upload" and l[1] == "pdf_informes" and l[2] == ["informe_presupuesto_norte_3t26.pdf"] for l in rag.llamadas)
    salida = capsys.readouterr().out
    assert "RAG_CORPUS_POLITICAS=" in salida and "RAG_CORPUS_INFORMES=" in salida and "INFORME_FUENTE=rag_engine" in salida


def test_preparar_rag_reutiliza_el_corpus_de_politicas_del_modulo_2(monkeypatch, capsys):
    m = _preparar_rag()
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proy")
    nombre_pol = m.nombres("proy")["politicas"]
    rag = _FakeRag("proy", existentes=[nombre_pol])
    assert m.main([], rag_factory=lambda p: rag) == 0
    assert ("create", nombre_pol) not in rag.llamadas                                   # no se crea otro de políticas
    assert not any(l[0] == "upload" and l[1] == "pdf_politicas" for l in rag.llamadas)  # ni se vuelven a subir los PDFs
    assert [l for l in rag.llamadas if l[0] == "create"] == [("create", m.nombres("proy")["informe"])]
    assert f"RAG_CORPUS_POLITICAS=projects/proy/ragCorpora/0" in capsys.readouterr().out


def test_preparar_rag_limpiar_no_toca_las_politicas_salvo_que_se_pida(monkeypatch):
    m = _preparar_rag()
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proy")
    nom = m.nombres("proy")
    rag = _FakeRag("proy", existentes=[nom["politicas"], nom["informe"]])
    assert m.main(["--limpiar"], rag_factory=lambda p: rag) == 0
    assert [l for l in rag.llamadas if l[0] == "delete"] == [("delete", "projects/proy/ragCorpora/1")]    # solo el del informe
    rag2 = _FakeRag("proy", existentes=[nom["politicas"], nom["informe"]])
    assert m.main(["--limpiar", "--incluir-politicas"], rag_factory=lambda p: rag2) == 0
    assert len([l for l in rag2.llamadas if l[0] == "delete"]) == 2


# --- correcciones tras la prueba en adk web con RAG Engine (2026-11-03) ----------------------

def test_el_informe_llega_completo_al_modelo():
    """Con el tope de 1,200 caracteres del Módulo 2 se perdía la frase de que el exceso no tiene aprobación del Comité."""
    from sqlagent.informe import buscar_informe
    texto = " ".join(c["text"] for c in buscar_informe("presupuesto aprobado y ejecucion por categoria de la division Norte")["citations"])
    assert "no cuenta con la aprobación del Comité Financiero" in texto


def test_el_catalogo_dice_los_valores_exactos_de_las_columnas_de_texto():
    from sqlagent.catalog import _chunks
    por_tabla = {c.title: c.text for c in _chunks()}
    for tabla in ("presupuesto", "gastos", "presupuesto_historico"):
        assert "Valores exactos, sin acentos: Viaticos, Consultoria, Tecnologia" in por_tabla[tabla], tabla
    assert "Norte, Sur, Centro, Occidente" in por_tabla["presupuesto"] and "2026-Q3" in por_tabla["presupuesto"]


def test_la_instruccion_pone_limites():
    from sqlagent.agent import INSTRUCTION
    assert "fuera de tu alcance" in INSTRUCTION                       # temas ajenos (la paella)
    assert "0 filas" in INSTRUCTION and "NO completes" in INSTRUCTION   # datos vacíos: no rellenar con el informe
    assert "«Consultoria», no «Consultoría»" in INSTRUCTION
    assert "Nunca calcules diferencias" in INSTRUCTION


def test_la_instruccion_exige_la_cifra_vigente_y_buscar_antes_de_decir_que_no_hay():
    from sqlagent.agent import INSTRUCTION
    assert "VIGENTE" in INSTRUCTION and "menciona el cambio" in INSTRUCTION           # el caso del presupuesto de Marketing
    assert "sin haber llamado antes a la herramienta" in INSTRUCTION                  # el caso de Sur contestado sin buscar


def test_la_instruccion_pide_el_mismo_alcance_que_el_informe():
    from sqlagent.agent import INSTRUCTION
    assert "mismo alcance que el informe declara" in INSTRUCTION               # el caso del SUM de todo 2026 contra Norte 3T
