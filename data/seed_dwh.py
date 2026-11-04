"""Almacén de datos sintético del Módulo 3: 19 tablas además de las 3 originales (22 en total).

Existe para que elegir la tabla correcta sea un problema real: hay tablas parecidas (presupuesto frente a
presupuesto_historico, cuentas_por_cobrar frente a pagos_clientes, gastos frente a gastos_marketing_campanas)
y tablas que no tienen nada que ver con la pregunta (inventario de tiendas, tipo de cambio).

Se llama desde `seed_data.build()` al final, con su propio generador aleatorio: los datos de las tablas
originales no cambian.
"""
import csv
import random
import sqlite3
from pathlib import Path

DIVISIONES = ["Norte", "Sur", "Centro", "Occidente"]
TRIMESTRES = ["2026-Q1", "2026-Q2", "2026-Q3"]
CATEGORIAS = ["Viaticos", "Consultoria", "Tecnologia", "Marketing", "Servicios"]

# (tabla, descripción de negocio, [(columna, tipo, descripción)])
TABLAS = [
    ("presupuesto", "Presupuesto asignado y ejecutado de 2026 por division, trimestre y categoria de gasto. "
     "Sirve para saber si una division excedio su presupuesto en el año en curso.", None),
    ("gastos", "Cada gasto individual de 2026 con fecha, proveedor y monto. Sirve para ver el detalle "
     "de en que se gasto, no el total presupuestado.", None),
    ("cuentas_por_cobrar", "Saldos pendientes de cobro a clientes al cierre del trimestre, con dias de atraso. "
     "Sirve para cartera vencida y clientes en mora.", None),
    ("presupuesto_historico", "Presupuesto y ejecucion ANUAL de años cerrados (2024 y 2025) por division y categoria. "
     "No incluye 2026: para el año en curso usar presupuesto.", [
        ("division", "TEXT", "Division de negocio: Norte, Sur, Centro, Occidente"),
        ("anio", "INTEGER", "Año fiscal cerrado: 2024 o 2025"),
        ("categoria", "TEXT", "Categoria de gasto. Valores exactos, sin acentos: Viaticos, Consultoria, Tecnologia, Marketing, Servicios"),
        ("presupuestado", "REAL", "Presupuesto anual asignado"),
        ("ejecutado", "REAL", "Gasto anual realmente ejecutado")]),
    ("viaticos_detalle", "Detalle de cada viaje de la categoria Viaticos: destino, dias y si tuvo autorizacion previa "
     "del Director de Division. Sirve para auditar viajes sin autorizacion.", [
        ("gasto_id", "INTEGER", "Identificador del gasto en la tabla gastos"),
        ("empleado_id", "INTEGER", "Empleado que viajo"),
        ("destino", "TEXT", "Ciudad o pais de destino"),
        ("dias", "INTEGER", "Dias de duracion del viaje"),
        ("autorizacion_previa", "TEXT", "si o no: el viaje tuvo autorizacion previa por escrito"),
        ("autorizado_por", "TEXT", "Quien autorizo; vacio si no hubo autorizacion")]),
    ("contratos_consultoria", "Contratos de consultoria externa con su monto, estado y si el Comite Financiero los aprobo. "
     "Sirve para revisar excesos y fraccionamiento de contratos.", [
        ("contrato_id", "INTEGER", "Identificador del contrato"),
        ("division", "TEXT", "Division que contrato"),
        ("proveedor", "TEXT", "Firma consultora"),
        ("monto", "REAL", "Valor total del contrato en USD"),
        ("fecha_inicio", "TEXT", "Inicio del contrato AAAA-MM-DD"),
        ("estado", "TEXT", "vigente, terminado o cancelado"),
        ("aprobado_por_comite", "TEXT", "si, no o no_aplica (los de bajo monto no lo requieren)")]),
    ("proveedores", "Catalogo de proveedores con su categoria, pais y calificacion de desempeño.", [
        ("proveedor", "TEXT", "Nombre del proveedor, igual que en gastos"),
        ("categoria", "TEXT", "Categoria principal del proveedor"),
        ("pais", "TEXT", "Pais de domicilio"),
        ("calificacion", "INTEGER", "Evaluacion de desempeño de 1 (mala) a 5 (excelente)")]),
    ("empleados", "Plantilla de empleados con su division, cargo y nivel jerarquico.", [
        ("empleado_id", "INTEGER", "Identificador del empleado"),
        ("division", "TEXT", "Division donde trabaja"),
        ("cargo", "TEXT", "Puesto"),
        ("nivel", "INTEGER", "Nivel jerarquico: 1 director, 5 operativo")]),
    ("centros_costo", "Centros de costo de cada division con su responsable.", [
        ("centro_id", "INTEGER", "Identificador del centro de costo"),
        ("division", "TEXT", "Division a la que pertenece"),
        ("nombre", "TEXT", "Nombre del centro de costo"),
        ("responsable", "TEXT", "Persona responsable del presupuesto del centro")]),
    ("aprobaciones", "Registro de aprobaciones de excesos presupuestales, viajes y contratos: quien aprobo, cuando "
     "y con que resultado.", [
        ("aprobacion_id", "INTEGER", "Identificador de la aprobacion"),
        ("tipo", "TEXT", "exceso_presupuestal, viaje o contrato"),
        ("referencia", "TEXT", "Division o identificador del elemento aprobado"),
        ("aprobador", "TEXT", "Director de Division o Comite Financiero"),
        ("fecha", "TEXT", "Fecha AAAA-MM-DD"),
        ("resultado", "TEXT", "aprobado o rechazado")]),
    ("ingresos_ventas", "Ingresos por ventas y margen bruto por division y trimestre de 2026.", [
        ("division", "TEXT", "Division de negocio: Norte, Sur, Centro, Occidente"),
        ("trimestre", "TEXT", "Trimestre fiscal AAAA-Qn, por ejemplo 2026-Q3"),
        ("ingresos", "REAL", "Ingresos del trimestre en USD"),
        ("margen_bruto_pct", "REAL", "Margen bruto como porcentaje de los ingresos")]),
    ("pagos_clientes", "Pagos efectivamente recibidos de clientes, con fecha y metodo. Es lo cobrado, no lo pendiente: "
     "para saldos pendientes usar cuentas_por_cobrar.", [
        ("cliente", "TEXT", "Cliente que pago"),
        ("fecha_pago", "TEXT", "Fecha del pago AAAA-MM-DD"),
        ("monto", "REAL", "Monto cobrado en USD"),
        ("metodo", "TEXT", "transferencia, cheque o tarjeta")]),
    ("inventario_tiendas", "Existencias de productos por tienda y SKU (operacion de retail). No contiene gastos ni presupuesto.", [
        ("tienda", "TEXT", "Nombre de la tienda"),
        ("sku", "TEXT", "Codigo del producto"),
        ("existencias", "INTEGER", "Unidades en inventario"),
        ("costo_unitario", "REAL", "Costo por unidad en USD")]),
    ("nomina_resumen", "Total de nomina y numero de empleados por division y trimestre.", [
        ("division", "TEXT", "Division de negocio: Norte, Sur, Centro, Occidente"),
        ("trimestre", "TEXT", "Trimestre fiscal AAAA-Qn, por ejemplo 2026-Q3"),
        ("total_nomina", "REAL", "Costo total de nomina en USD"),
        ("headcount", "INTEGER", "Numero de empleados al cierre")]),
    ("tipo_cambio", "Tipo de cambio diario de monedas extranjeras a USD.", [
        ("fecha", "TEXT", "Fecha AAAA-MM-DD"),
        ("moneda", "TEXT", "Codigo de moneda: MXN, EUR, COP"),
        ("tasa", "REAL", "Unidades de moneda por 1 USD")]),
    ("hallazgos_auditoria", "Hallazgos de auditoria interna por division con su severidad y estado de atencion.", [
        ("hallazgo_id", "INTEGER", "Identificador del hallazgo"),
        ("division", "TEXT", "Division auditada"),
        ("area", "TEXT", "Area revisada: viaticos, consultoria, cobranza, tecnologia"),
        ("severidad", "TEXT", "alta, media o baja"),
        ("estado", "TEXT", "abierto o cerrado"),
        ("fecha", "TEXT", "Fecha del hallazgo AAAA-MM-DD")]),
    ("provisiones_cobranza", "Provision por cuentas incobrables por division, trimestre y rango de dias de mora.", [
        ("division", "TEXT", "Division de negocio: Norte, Sur, Centro, Occidente"),
        ("trimestre", "TEXT", "Trimestre fiscal AAAA-Qn, por ejemplo 2026-Q3"),
        ("rango_mora", "TEXT", "31-90 dias o mas de 90 dias"),
        ("monto_provisionado", "REAL", "Monto provisionado en USD")]),
    ("divisiones", "Catalogo de divisiones con su region y su director.", [
        ("division", "TEXT", "Nombre de la division"),
        ("region", "TEXT", "Region geografica"),
        ("director", "TEXT", "Director de Division")]),
    ("calendario_fiscal", "Calendario fiscal: fechas de inicio y fin de cada trimestre y si ya esta cerrado.", [
        ("trimestre", "TEXT", "Trimestre fiscal AAAA-Qn, por ejemplo 2026-Q3"),
        ("fecha_inicio", "TEXT", "Primer dia del trimestre"),
        ("fecha_fin", "TEXT", "Ultimo dia del trimestre"),
        ("estado_cierre", "TEXT", "abierto o cerrado")]),
    ("categorias_gasto", "Catalogo de categorias de gasto y si exigen aprobacion previa.", [
        ("categoria", "TEXT", "Nombre de la categoria"),
        ("tipo", "TEXT", "operacional o inversion"),
        ("requiere_aprobacion", "TEXT", "si o no")]),
    ("metas_kpi", "Metas de indicadores clave (KPI) contra el resultado real, por division y trimestre.", [
        ("division", "TEXT", "Division de negocio: Norte, Sur, Centro, Occidente"),
        ("trimestre", "TEXT", "Trimestre fiscal AAAA-Qn, por ejemplo 2026-Q3"),
        ("kpi", "TEXT", "Nombre del indicador: margen_operativo, dso, rotacion"),
        ("meta", "REAL", "Valor objetivo"),
        ("real", "REAL", "Valor alcanzado")]),
    ("gastos_marketing_campanas", "Inversion de marketing por campaña y canal. Es un detalle de la categoria Marketing; "
     "para el total gastado por categoria usar presupuesto o gastos.", [
        ("campana", "TEXT", "Nombre de la campaña"),
        ("division", "TEXT", "Division que la pago"),
        ("trimestre", "TEXT", "Trimestre fiscal AAAA-Qn, por ejemplo 2026-Q3"),
        ("canal", "TEXT", "digital, tienda o radio"),
        ("monto", "REAL", "Inversion en USD")]),
]


def _rows(rng: random.Random, con: sqlite3.Connection) -> dict[str, list[tuple]]:
    r = {}
    r["presupuesto_historico"] = [
        (d, a, c, float(b := rng.randint(150, 320) * 1000), round(b * rng.uniform(0.88, 1.03), 2))
        for d in DIVISIONES for a in (2024, 2025) for c in CATEGORIAS]
    viajes = con.execute("SELECT id, division, trimestre FROM gastos WHERE categoria='Viaticos' ORDER BY id").fetchall()
    destinos = ["Ciudad de Mexico", "Bogota", "Madrid", "Houston", "Lima", "Monterrey"]
    jefes = {"Norte": "Director Norte", "Sur": "Director Sur", "Centro": "Director Centro", "Occidente": "Director Occidente"}
    r["viaticos_detalle"] = []
    for gid, d, q in viajes:
        sin = rng.random() < (0.45 if (d == "Norte" and q == "2026-Q3") else 0.08)
        r["viaticos_detalle"].append((gid, rng.randint(1, 40), rng.choice(destinos), rng.randint(2, 9),
                                      "no" if sin else "si", "" if sin else jefes[d]))
    firmas = ["Consultora Alfa", "Consultora Beta", "Asesores Delta", "Grupo Sigma"]
    r["contratos_consultoria"] = []
    for i in range(1, 21):
        d = DIVISIONES[(i - 1) % 4]
        monto = rng.randint(20, 160) * 1000
        r["contratos_consultoria"].append((i, d, rng.choice(firmas), float(monto), f"2026-{rng.randint(1, 9):02d}-{rng.randint(1, 28):02d}",
                                           rng.choice(["vigente", "vigente", "terminado"]),
                                           "si" if monto > 100000 else ("no_aplica" if monto < 50000 else rng.choice(["si", "no"]))))
    paises = ["Mexico", "Colombia", "España", "Estados Unidos", "Peru"]
    r["proveedores"] = [(f"Proveedor-{i}", rng.choice(CATEGORIAS), rng.choice(paises), rng.randint(1, 5)) for i in range(1, 21)]
    cargos = ["Analista", "Gerente", "Coordinador", "Director", "Auxiliar"]
    r["empleados"] = [(i, DIVISIONES[i % 4], rng.choice(cargos), rng.randint(1, 5)) for i in range(1, 41)]
    r["centros_costo"] = [(i * 10 + j, d, f"CC {d} {n}", f"Responsable {d[0]}{n}")
                          for i, d in enumerate(DIVISIONES, 1) for j, n in enumerate(["Operacion", "Comercial", "Soporte"], 1)]
    r["aprobaciones"] = [(i, rng.choice(["exceso_presupuestal", "viaje", "contrato"]), rng.choice(DIVISIONES + ["C-" + str(i)]),
                          rng.choice(["Director de Division", "Comite Financiero"]),
                          f"2026-{rng.randint(1, 9):02d}-{rng.randint(1, 28):02d}", rng.choice(["aprobado", "aprobado", "rechazado"]))
                         for i in range(1, 31)]
    r["ingresos_ventas"] = [(d, q, float(rng.randint(9, 16) * 1_000_000), round(rng.uniform(34, 41), 1))
                            for d in DIVISIONES for q in TRIMESTRES]
    clientes = [f"Cliente-{d[0]}{i}" for d in DIVISIONES for i in range(1, 13)]
    r["pagos_clientes"] = [(rng.choice(clientes), f"2026-{rng.randint(1, 9):02d}-{rng.randint(1, 28):02d}",
                            rng.randint(10, 120) * 1000.0, rng.choice(["transferencia", "cheque", "tarjeta"])) for _ in range(60)]
    r["inventario_tiendas"] = [(f"Tienda {t}", f"SKU-{s:04d}", rng.randint(0, 400), round(rng.uniform(2, 90), 2))
                               for t in "ABCDE" for s in range(1, 9)]
    r["nomina_resumen"] = [(d, q, float(rng.randint(20, 45) * 100_000), rng.randint(80, 220)) for d in DIVISIONES for q in TRIMESTRES]
    r["tipo_cambio"] = [(f"2026-{m:02d}-15", mon, round(base * rng.uniform(0.97, 1.03), 4))
                        for m in range(1, 10) for mon, base in (("MXN", 18.5), ("EUR", 0.92), ("COP", 4100.0))]
    r["hallazgos_auditoria"] = [(i, rng.choice(DIVISIONES), rng.choice(["viaticos", "consultoria", "cobranza", "tecnologia"]),
                                 rng.choice(["alta", "media", "media", "baja"]), rng.choice(["abierto", "cerrado"]),
                                 f"2026-{rng.randint(1, 9):02d}-{rng.randint(1, 28):02d}") for i in range(1, 25)]
    r["provisiones_cobranza"] = [(d, "2026-Q3", rg, float(rng.randint(5, 60) * 1000))
                                 for d in DIVISIONES for rg in ("31-90 dias", "mas de 90 dias")]
    r["divisiones"] = list(zip(DIVISIONES, ["Norte", "Sur", "Centro", "Occidente"], [jefes[d] for d in DIVISIONES]))
    r["calendario_fiscal"] = [("2026-Q1", "2026-01-01", "2026-03-31", "cerrado"), ("2026-Q2", "2026-04-01", "2026-06-30", "cerrado"),
                              ("2026-Q3", "2026-07-01", "2026-09-30", "cerrado"), ("2026-Q4", "2026-10-01", "2026-12-31", "abierto")]
    r["categorias_gasto"] = [(c, "operacional", "si" if c in ("Consultoria", "Viaticos") else "no") for c in CATEGORIAS]
    r["metas_kpi"] = [(d, q, k, m, round(m * rng.uniform(0.85, 1.1), 2)) for d in DIVISIONES for q in TRIMESTRES
                      for k, m in (("margen_operativo", 12.0), ("dso", 45.0), ("rotacion", 6.0))]
    r["gastos_marketing_campanas"] = [(f"Campaña {n}", d, q, rng.choice(["digital", "tienda", "radio"]), float(rng.randint(3, 25) * 1000))
                                      for d in DIVISIONES for q in TRIMESTRES for n in ("Verano", "Regreso a clases")]
    return r


def build_dwh(con: sqlite3.Connection, csv_dir: Path) -> int:
    """Crea las tablas nuevas y llena `catalogo_tablas` y `catalogo_datos`. Devuelve el número de tablas del catálogo."""
    rng = random.Random(2026)
    con.executescript("DROP TABLE IF EXISTS catalogo_tablas;")
    con.execute("CREATE TABLE catalogo_tablas (tabla TEXT, descripcion TEXT)")
    nuevas = [t for t in TABLAS if t[2] is not None]
    for nombre, _, cols in nuevas:
        con.execute(f"DROP TABLE IF EXISTS {nombre}")
        con.execute(f"CREATE TABLE {nombre} ({', '.join(f'{c} {t}' for c, t, _ in cols)})")
    datos = _rows(rng, con)
    csv_dir.mkdir(exist_ok=True)
    for nombre, _, cols in nuevas:
        filas = datos[nombre]
        con.executemany(f"INSERT INTO {nombre} VALUES ({','.join('?' * len(cols))})", filas)
        con.executemany("INSERT INTO catalogo_datos VALUES (?,?,?,?)", [(nombre, c, t, d) for c, t, d in cols])
        with open(csv_dir / f"{nombre}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([c for c, _, _ in cols])
            w.writerows(filas)
    con.executemany("INSERT INTO catalogo_tablas VALUES (?,?)", [(n, d) for n, d, _ in TABLAS])
    con.commit()
    return len(TABLAS)
