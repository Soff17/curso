"""Agente SQL + RAG híbrido: esquema por rerank -> SQL -> ejecución con guardrails -> contraste con informe."""
from shared.config import MODEL_NAME

from .catalog import buscar_esquema
from .connectors import get_connector
from .guardrails import UnsafeSQL, validate_sql


def ejecutar_sql(sql: str) -> dict:
    """Ejecuta una consulta SELECT de solo lectura (máx. 1000 filas) en el dialecto de la base.

    Args:
        sql: sentencia SELECT usando únicamente tablas devueltas por buscar_esquema.
    """
    con = get_connector()
    try:
        safe = validate_sql(sql, con.tables(), dialect=con.dialect, allowed_schemas=con.schemas)
        rows = con.run(safe)
        return {"status": "ok", "sql": safe, "rows": rows, "n": len(rows)}
    except UnsafeSQL as e:
        return {"status": "bloqueado", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def contrastar_con_informe(valor_sql: float, valor_informe: float, tolerancia_pct: float = 1.0) -> dict:
    """Compara una cifra obtenida por SQL contra la citada en el informe/RAG.

    Returns: coincide (bool), diferencia absoluta y %.
    """
    diff = valor_sql - valor_informe
    pct = abs(diff) / abs(valor_informe) * 100 if valor_informe else float("inf")
    return {"coincide": pct <= tolerancia_pct, "diferencia": round(diff, 2), "diferencia_pct": round(pct, 2)}


def contrastar_cifras(cifras_sql: dict[str, float], cifras_informe: dict[str, float],
                      tolerancia_pct: float = 1.0, escala_informe: float = 1.0) -> dict:
    """Compara, cifra por cifra, lo que devolvió el SQL con lo que dice el informe. La regla es fija: el modelo no calcula.

    Usa el MISMO nombre en las dos listas para la misma magnitud (por ejemplo «Marketing presupuesto»).
    Las dos cifras deben medir lo mismo y estar en la misma unidad: si el informe viene en miles de USD y
    el SQL en USD, pasa escala_informe=1000.

    Args:
        cifras_sql: nombre de la cifra -> valor que devolvió ejecutar_sql.
        cifras_informe: nombre de la cifra -> valor que dice el informe (leído de las citas de buscar_informe).
        tolerancia_pct: diferencia relativa aceptada para decir que coinciden (1 % por defecto).
        escala_informe: factor que multiplica las cifras del informe para ponerlas en la unidad del SQL.

    Returns:
        dict con 'filas' (cifra, sql, informe, diferencia, diferencia_pct, estado: coincide | difiere |
        sin_contraparte) y los conteos 'coinciden', 'difieren' y 'sin_contraparte'.
    """
    filas = []
    for nombre in sorted(set(cifras_sql) | set(cifras_informe)):
        a, b = cifras_sql.get(nombre), cifras_informe.get(nombre)
        if a is None or b is None:
            filas.append({"cifra": nombre, "sql": a, "informe": b, "estado": "sin_contraparte"})
            continue
        b = b * escala_informe
        pct = abs(a - b) / abs(b) * 100 if b else float("inf")
        filas.append({"cifra": nombre, "sql": a, "informe": b, "diferencia": round(a - b, 2),
                      "diferencia_pct": round(pct, 2), "estado": "coincide" if pct <= tolerancia_pct else "difiere"})
    cuenta = lambda e: sum(1 for f in filas if f["estado"] == e)   # noqa: E731
    return {"filas": filas, "coinciden": cuenta("coincide"), "difieren": cuenta("difiere"),
            "sin_contraparte": cuenta("sin_contraparte")}


INSTRUCTION = (
    "Eres un analista financiero que combina datos (SQL), el informe de presupuesto (texto) y las políticas "
    "internas. Dialecto SQL: {dialecto}. Flujo para cada pregunta: 1) buscar_esquema(pregunta) y escribe UN SELECT "
    "usando solo las tablas que devuelve; 2) ejecutar_sql; si devuelve 'bloqueado', corrige el SQL y nunca intentes "
    "eludir el guardrail; 3) buscar_informe para encontrar las cifras equivalentes en el informe y lee los valores "
    "SOLO del texto de las citas (fíjate en la unidad: USD o miles de USD); 4) contrastar_cifras con el mismo nombre "
    "para cada magnitud; 5) buscar_politicas para la norma que aplica. Responde con tres partes: lo que dicen los "
    "datos (con la consulta ejecutada), lo que dice el informe (con su cita) y lo que dice la política (con su cita). "
    "Si alguna cifra difiere o no tiene contraparte, dilo; si una herramienta no devuelve citas, no inventes la cifra: "
    "di que no la encontraste. Nunca calcules diferencias tú: usa contrastar_cifras. "
    "Los valores de texto (división, categoría, trimestre) deben ser EXACTOS como los muestra el catálogo, sin acentos "
    "añadidos: «Consultoria», no «Consultoría». Si ejecutar_sql devuelve 0 filas, revisa esos valores y reintenta UNA vez; "
    "si sigue vacío, di que la base no devolvió datos y NO completes la parte de los datos con cifras del informe ni "
    "calcules nada a partir de ellas. "
    "Para contrastar con el informe, filtra el SQL con el mismo alcance que el informe declara (su división y su periodo); "
    "si la pregunta no los dice, usa los del informe y avísalo. "
    "Compara siempre la misma magnitud: si el informe da dos cifras para lo mismo (por ejemplo una original y otra "
    "modificada después), compara con la VIGENTE, la que aparece en su tabla de presupuesto aprobado, y menciona el cambio "
    "en vez de usar la otra para que coincidan. "
    "Nunca afirmes que algo no está en el informe, en la base o en las políticas sin haber llamado antes a la herramienta "
    "correspondiente. "
    "Solo respondes preguntas sobre las finanzas de la empresa con estas herramientas. Si la pregunta es de otro tema "
    "(recetas, deportes, cultura general...), responde que está fuera de tu alcance y no uses conocimiento externo.")


def build_sql_agent():
    from google.adk.agents import Agent   # verificado: google-adk 2.11.0
    from .informe import buscar_informe
    from .politicas import buscar_politicas
    return Agent(
        name="agente_sql",
        model=MODEL_NAME,
        description="Responde preguntas cuantitativas con SQL, las contrasta con el informe y con la normativa.",
        instruction=INSTRUCTION.format(dialecto=get_connector().dialect),
        tools=[buscar_esquema, ejecutar_sql, buscar_informe, contrastar_cifras, buscar_politicas],
    )
