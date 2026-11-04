"""Conectores: SQLite (sin servicios), SQL Server (SQLAlchemy + pyodbc) y BigQuery. Todos solo lectura.

Cada conector dice su `dialect` (para el prompt y los guardrails) y sus `schemas` (los prefijos que
puede llevar una tabla: el dataset en BigQuery, `dbo` en SQL Server). La barrera principal es el
permiso de la base (un login `db_datareader`, un rol `bigquery.dataViewer`); los guardrails son la segunda.
"""
import os
import sqlite3
from functools import lru_cache
from typing import Protocol

from shared.config import DB_PATH

MAX_ROWS = 1000


class Connector(Protocol):
    dialect: str
    schemas: set[str]
    def tables(self) -> set[str]: ...
    def run(self, sql: str) -> list[dict]: ...


class SqliteConnector:
    dialect = "sqlite"
    schemas: set[str] = set()                      # en SQLite no se aceptan prefijos

    def _con(self):
        return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=5)

    def tables(self) -> set[str]:
        with self._con() as c:
            return {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}

    def run(self, sql: str) -> list[dict]:
        con = self._con()
        con.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in con.execute(sql).fetchall()]
        finally:
            con.close()


class SqlServerConnector:
    """SQL Server con SQLAlchemy + pyodbc. Usa un login con el rol `db_datareader` únicamente.

    Tiempos: `login_timeout_s` limita el intento de conexión; `query_timeout_s` (atributo `timeout` de
    la conexión de pyodbc) limita cada consulta; `SET LOCK_TIMEOUT` limita la espera de bloqueos.
    Filas: el guardrail pone `TOP n` y aquí además se leen como máximo `max_rows`.
    """
    dialect = "tsql"

    def __init__(self, url: str | None = None, login_timeout_s: int = 15, query_timeout_s: int = 30,
                 max_rows: int = MAX_ROWS, schema: str = "dbo"):
        from sqlalchemy import create_engine, event   # pip install sqlalchemy pyodbc (y ODBC Driver 18)
        self.max_rows, self.schema, self.schemas = max_rows, schema, {schema}
        self.engine = create_engine(url or os.environ["MSSQL_URL"],
                                    connect_args={"timeout": login_timeout_s})

        @event.listens_for(self.engine, "connect")
        def _query_timeout(dbapi_con, _record):
            dbapi_con.timeout = query_timeout_s

    def tables(self) -> set[str]:
        from sqlalchemy import inspect
        return set(inspect(self.engine).get_table_names(schema=self.schema))

    def run(self, sql: str) -> list[dict]:
        # exec_driver_sql: el SQL llega tal cual (con text() un ":x" se leería como parámetro).
        with self.engine.connect() as c:
            c.exec_driver_sql("SET LOCK_TIMEOUT 5000")
            res = c.exec_driver_sql(sql)
            return [dict(r._mapping) for r in res.fetchmany(self.max_rows)]
        # al salir sin confirmar, SQLAlchemy deshace la transacción: nunca se hace commit


class BigQueryConnector:
    """BigQuery con tope de bytes: primero una prueba (dry run) y, si cabe, la consulta con
    `maximum_bytes_billed` (si la estimación lo supera, BigQuery falla sin cobrar)."""
    dialect = "bigquery"

    def __init__(self, dataset: str | None = None, max_bytes: int = 1_000_000_000,
                 max_rows: int = MAX_ROWS, client=None, location: str | None = None):
        from google.cloud import bigquery
        self.bq, self.max_bytes, self.max_rows = bigquery, max_bytes, max_rows
        self.client = client or bigquery.Client(location=location or os.environ.get("BQ_LOCATION"))
        self.dataset = dataset or os.environ["BQ_DATASET"]
        self.schemas = {self.dataset}

    def tables(self) -> set[str]:
        """Tablas y modelos del dataset (los modelos de BigQuery ML también se pueden consultar)."""
        names = {t.table_id for t in self.client.list_tables(self.dataset)}
        return names | {m.model_id for m in self.client.list_models(self.dataset)}

    def _config(self, **kw):
        # default_dataset: el SQL puede decir `FROM gastos`, sin proyecto ni dataset
        return self.bq.QueryJobConfig(default_dataset=f"{self.client.project}.{self.dataset}",
                                      use_legacy_sql=False, **kw)

    def dry_run_bytes(self, sql: str) -> int:
        job = self.client.query(sql, job_config=self._config(dry_run=True, use_query_cache=False))
        return job.total_bytes_processed

    def run(self, sql: str) -> list[dict]:
        n = self.dry_run_bytes(sql)
        if n > self.max_bytes:
            raise ValueError(f"La consulta procesaría {n:,} bytes y el tope es {self.max_bytes:,}")
        job = self.client.query(sql, job_config=self._config(maximum_bytes_billed=self.max_bytes))
        return [dict(r) for r in job.result(timeout=30, max_results=self.max_rows)]


# Ejemplo BigQuery ML para la sesión: pronóstico del gasto MENSUAL por división (ene-sep 2026 -> oct-dic).
# - La columna de tiempo debe ser DATE, DATETIME o TIMESTAMP (en el CSV `fecha` es texto: DATE(fecha) la convierte).
# - La frecuencia de los datos de entrada define qué es un «periodo» del pronóstico. Con los gastos sueltos por
#   día (irregulares) BigQuery infería ~3 días y «3 periodos» eran 9 días; sumando por mes y fijando
#   data_frequency='MONTHLY', horizon 3 son octubre, noviembre y diciembre.
BQML_EXAMPLE = """
CREATE OR REPLACE MODEL `finanzas.forecast_gasto`
OPTIONS(model_type='ARIMA_PLUS', time_series_timestamp_col='mes',
        time_series_data_col='monto', time_series_id_col='division',
        data_frequency='MONTHLY', horizon=6) AS
SELECT DATE_TRUNC(DATE(fecha), MONTH) AS mes, division, SUM(monto) AS monto
FROM `finanzas.gastos` GROUP BY 1, 2;
-- SELECT * FROM ML.FORECAST(MODEL `finanzas.forecast_gasto`, STRUCT(3 AS horizon));
"""


@lru_cache(maxsize=4)
def _build(kind: str) -> Connector:
    return {"sqlite": SqliteConnector, "sqlserver": SqlServerConnector, "bigquery": BigQueryConnector}[kind]()


def get_connector() -> Connector:
    """Elige por `SQL_BACKEND` (sqlite | sqlserver | bigquery). Sin esa variable: BigQuery en `cloud`
    y SQLite en `offline`, como antes."""
    from shared.config import is_cloud
    kind = os.environ.get("SQL_BACKEND") or ("bigquery" if is_cloud() else "sqlite")
    if kind not in ("sqlite", "sqlserver", "bigquery"):
        raise ValueError(f"SQL_BACKEND no válido: {kind}")
    return _build(kind)
