"""Guardrails de ejecución SQL. Defensa en profundidad: esto NO sustituye a un usuario de BD de solo lectura.

Analiza la consulta con `sqlglot` en el dialecto de la base (sqlite, tsql o bigquery) en vez de
buscar palabras con expresiones regulares: así ve las tablas de verdad (comas, JOIN, subconsultas,
nombres con comillas o con proyecto.dataset) y pone el límite de filas con la sintaxis correcta
(`LIMIT` en SQLite/BigQuery, `TOP` en T-SQL).
"""
import re

import sqlglot
from sqlglot import exp
from sqlglot.errors import SqlglotError

MAX_ROWS = 1000
DIALECTS = {"sqlite", "tsql", "bigquery"}

# Funciones que leen fuera de la base o ejecutan cosas del servidor.
FORBIDDEN_FUNCS = re.compile(
    r"^(xp_\w+|sp_\w+|fn_\w+|openrowset|opendatasource|openquery|external_query|load_file|readfile)$", re.I)


# Funciones de tabla de BigQuery ML que se permiten (leen un modelo o una tabla, no escriben nada).
# El modelo o la tabla que reciben cuentan como tablas y pasan por la misma lista de permitidas.
ML_TABLE_FUNCS = tuple(getattr(exp, n) for n in ("MLForecast", "AIForecast", "Predict") if hasattr(exp, n))


class UnsafeSQL(ValueError):
    pass


def validate_sql(sql: str, allowed_tables: set[str], max_rows: int = MAX_ROWS,
                 dialect: str = "sqlite", allowed_schemas: set[str] | None = None) -> str:
    """Devuelve el SQL saneado (con límite de filas) o lanza UnsafeSQL.

    Args:
        sql: la consulta propuesta por el modelo.
        allowed_tables: tablas que puede leer (las que devuelve el catálogo).
        max_rows: tope de filas; se aplica como LIMIT o como TOP según el dialecto.
        dialect: "sqlite", "tsql" o "bigquery".
        allowed_schemas: si se da, una tabla con prefijo (dataset o esquema) solo se acepta
            cuando ese prefijo está aquí. Una tabla sin prefijo siempre se acepta si está permitida.
    """
    if dialect not in DIALECTS:
        raise ValueError(f"Dialecto no soportado: {dialect}")
    s = sql.strip().rstrip(";").strip()
    if re.search(r"--|/\*", s):
        raise UnsafeSQL("Comentarios no permitidos")
    try:
        statements = [t for t in sqlglot.parse(s, read=dialect) if t is not None]
    except SqlglotError as e:
        raise UnsafeSQL(f"SQL no válido para {dialect}: {str(e)[:120]}") from e
    if len(statements) != 1:
        raise UnsafeSQL("Solo se permite una sentencia")
    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Union)):
        raise UnsafeSQL("Solo SELECT")
    if tree.find(exp.Into):
        raise UnsafeSQL("SELECT ... INTO no permitido")

    for f in tree.find_all(exp.Anonymous):
        if FORBIDDEN_FUNCS.match(str(f.name)):
            raise UnsafeSQL(f"Función no permitida: {f.name}")

    ctes = {c.alias_or_name.lower() for c in tree.find_all(exp.CTE)}
    allowed = {t.lower() for t in allowed_tables}
    schemas = {x.lower() for x in allowed_schemas} if allowed_schemas is not None else None
    unknown = set()
    for t in tree.find_all(exp.Table):
        if isinstance(t.this, ML_TABLE_FUNCS) and dialect == "bigquery":
            continue                                          # ML.FORECAST(MODEL m, ...): m se revisa aparte
        if not isinstance(t.this, exp.Identifier):
            raise UnsafeSQL("Origen de datos no permitido (función de tabla)")
        name, prefix = t.name.lower(), t.db.lower()
        if not prefix and name in ctes:
            continue
        if name not in allowed or (prefix and schemas is not None and prefix not in schemas):
            unknown.add(f"{prefix}.{name}" if prefix else name)
    if unknown:
        raise UnsafeSQL(f"Tablas no permitidas: {sorted(unknown)}")

    limit = tree.args.get("limit")
    n = limit.args.get("expression") if limit is not None else None
    if not (isinstance(n, exp.Literal) and n.is_int and int(n.this) <= max_rows):
        tree = tree.limit(max_rows)
    return tree.sql(dialect=dialect)
