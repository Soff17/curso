# Módulo 3 · SESIÓN PRÁCTICA (tutoría) — Guía del instructor

**Formato:** 5 células de 6 personas trabajando en `notebooks/practica_alumnos.ipynb`; tú proyectas `notebooks/practica_instructor.ipynb` (resuelto). Mientras trabajan, haces **code review** por célula.
La explicación de los conceptos está en **`SESION_TEORICA.md`**. Los comandos paso a paso para los alumnos irán en **`COMANDOS.md`** (pendiente).

**Contenido de esta guía:** Antes de la clase · El lab (qué se entrega) · Línea de tiempo y reparto · Guion por parte (0 a 9) · Cierre · Code review · Contingencias · Problemas fuera del notebook · Nota de instructor: conexión con el capstone · Lo no probado.

> ⏱️ **Los tiempos son estimaciones, no se cronometraron.** El notebook suma **unos 165 minutos** (170 con la limpieza). Lee *Línea de tiempo y reparto*: ahí está qué recortar.
> ⚠️ **El notebook completo todavía no se ha ejecutado de arriba abajo.** Las celdas que no usan servicios (🟢) sí se ejecutaron sin errores en las dos versiones; las que usan servicios (💸) se escribieron con lo que ya verificamos por separado (scripts y `adk web`). **Antes de la clase, ejecútalo tú una vez completo** y guárdalo con salidas.

---
## Antes de la clase (día anterior)
- [ ] `pip install sqlglot` en el entorno de **todos** (los guardrails lo necesitan) y `. .\env.ps1`. Luego `python -m pytest modulo3_sql_bigquery -q` → **79 passed, 1 xfailed** (el *xfailed* es esperado: el buscador léxico no encuentra «pagaron»). Corren **siempre sin servicios**, aunque tu `.env` diga `cloud`. *(Verificado el 3 de noviembre de 2026; el repositorio completo: 165 passed, 1 xfailed.)*
- [ ] **Ejecuta `notebooks/practica_instructor.ipynb` completo** y guárdalo con salidas. Usa **servicios reales** (BigQuery, BigQuery ML, embeddings, Ranking API, Gemini y, si usas RAG Engine, el analizador de LLM) y cuesta **centavos** (estimación): una sola vez.
- [ ] Los dos notebooks tienen **la misma estructura**: `practica_alumnos.ipynb` es el del instructor con **7 ejercicios `TODO`** y sin salidas. **Si cambias uno, aplica el mismo cambio al otro.**
- [ ] **API de BigQuery habilitada** en el proyecto del curso. Para los corpus de RAG Engine, las **4 APIs del Módulo 2** (Vertex AI, Discovery Engine, Vector Search y Cloud Resource Manager) y RAG Engine en **modo sin servidores**: lo mismo que en el Módulo 2.
- [ ] **Cada alumno corre antes de la clase** `python modulo3_sql_bigquery/preparar_bigquery.py` (crea **su** dataset `finanzas_<usuario>` y carga las 22 tablas) y, si van a usar RAG Engine, `python modulo3_sql_bigquery/preparar_rag.py`. Los dos imprimen las líneas del `.env` que deben copiar. Con `--dry-run` muestran el plan sin llamar a nada (🟢).
- [ ] **El corpus de políticas del Módulo 2** se **borró en su limpieza**: `preparar_rag.py` lo recrea con los mismos PDFs (unos minutos y centavos). Cuéntalo, para que no se asusten cuando tarde.
- [ ] Variables del `.env` de cada alumno: `AGENTS_MODE=cloud`, `SQL_BACKEND=bigquery`, `BQ_DATASET=<el que imprimió el script>`, `BQ_LOCATION=US`, y para RAG Engine: `AUDITOR_FUENTE=rag_engine`, `INFORME_FUENTE=rag_engine`, `RAG_CORPUS_POLITICAS`, `RAG_CORPUS_INFORMES`. Sin las de RAG Engine, el notebook usa markdown (respaldo).
- [ ] **Permisos:** cada alumno crea **datasets, tablas y modelos** en BigQuery y, con RAG Engine, buckets y corpus. ⚠️ Las pruebas se hicieron con tu cuenta; **los roles mínimos no se han verificado**. Pruébalo con una cuenta de alumno **antes**.
- [ ] **Prueba de concurrencia:** ⚠️ **no se ha probado con 30 personas** a la vez. Haz un ensayo con 3 a 5 alumnos creando datasets, y recuerda que en RAG Engine las operaciones sobre corpus no admiten concurrencia (ver Módulo 2).
- [ ] **Presupuesto:** alerta en Facturación antes de la clase. Según la documentación, cada consulta de BigQuery factura **como mínimo 10 MiB**; con estos datos el costo es de centavos, pero son 30 personas.
- [ ] Alumnos con el entorno instalado y la Parte 0 ejecutada.
- [ ] Lleva la consola de Google Cloud abierta (BigQuery → tu dataset) para enseñar que existe y que se borra.

## El lab: qué se entrega
**Objetivo (cronograma):** un **agente que realiza reranking sobre el catálogo de datos, genera y ejecuta la consulta en SQL Server/BigQuery y contrasta los resultados cuantitativos contra el presupuesto del informe RAG.**

**Requisitos:**
1. **Elegir las tablas** con RAG y reranking sobre el catálogo (22 tablas), con un umbral calibrado.
2. **Ejecutar el SQL con guardrails** (un solo SELECT, tablas permitidas, tope de filas) y con **tope de bytes** en BigQuery.
3. **Contrastar** las cifras del SQL con las del informe con una **regla fija** (`contrastar_cifras`): misma magnitud, misma unidad.
4. **Citar la política** que aplica (la del Módulo 2).
5. Cubrir **BigQuery ML**: entrenar un pronóstico y consultarlo con `ML.FORECAST`.
6. Entender el **conector de SQL Server** (en código) y por qué el permiso de la base importa más que la expresión regular.

**Criterios de aceptación:**
- Los 5 casos de la Parte 8 pasan, y **ninguna cifra es inventada**: si el informe no la tiene, el agente lo dice.
- «Borra los gastos de Norte» **no borra nada**.
- Lo que no es de finanzas **no se contesta**.
- Sus recursos de nube **están borrados** al terminar (Parte 9).

**Entrega:** notebook ejecutado (con la Parte 8 completa) + repositorio de la célula + demo de 5 min.

> **Sobre SQL Server:** el cronograma dice «SQL Server/BigQuery». **El entregable corre en BigQuery**; el conector de SQL Server se **enseña en código** (Parte 4) y está probado solo con un servidor simulado. Dilo con claridad: no hay un SQL Server para la clase.

## Línea de tiempo y reparto
| Hora | Parte | Tema | Min |
|---|---|---|---|
| 0:00–0:10 | 0 | Preparación | 10 |
| 0:10–0:15 | 1 | El problema: Text-to-SQL con muchas tablas | 5 |
| 0:15–0:30 | 2 | El catálogo son documentos (descripciones) | 15 |
| 0:30–0:55 | 3 | RAG y reranking del catálogo (K = 8 → N = 3) | 25 |
| 0:55–1:15 | 4 | SQL seguro: guardrails, dialectos y el conector de SQL Server | 20 |
| 1:15–1:30 | 5 | BigQuery: dry run y topes de bytes | 15 |
| 1:30–1:55 | 6 | BigQuery ML: un pronóstico con SQL | 25 |
| 1:55–2:30 | 7 | **El agente híbrido** (el entregable) | 35 |
| 2:30–2:40 | 8 | ¿Lo logramos? Verificación | 10 |
| 2:40–2:45 | 9 | Limpieza (**obligatoria**) | 5 |

Son **2 h 45 min sin pausas**. **Opción A — un solo bloque** (recomendada): con **una pausa de 10 min después de la Parte 3**. **Opción B — dos sesiones de 2 h:** ⚠️ el estado del notebook vive en la memoria del kernel (`catalogo`, `retriever`, `UMBRAL`, `agente`…); al cerrarlo **se pierde**, mientras que el dataset, el modelo y los corpus **siguen en la nube cobrando**. Si partes en dos: sesión 1 = Partes 0 a 4 (70 min) más tu teoría; **no ejecutes la limpieza** al final; en la sesión 2 vuelve a ejecutar la Parte 0 y las celdas que definen variables. ⚠️ **No está probado** reanudar así.

**Qué recortar, en este orden:** la lección de la frecuencia (celda 6.3, que entrena un segundo modelo) → 6.4 → la celda 5.2 → los ejercicios `TODO` → la Parte 8 como demo tuya.
**Qué protege el entregable:** Partes 3, 4, 7, 8 y 9.

---
## Preparación de la sala y reglas de juego
**Antes de que lleguen (5 min):** proyecta `practica_instructor.ipynb` **ya ejecutado hasta la Parte 0**. Ten una terminal en la raíz del proyecto y la consola de BigQuery en otra pestaña. Define el **semáforo** (verde = voy bien, rojo = necesito ayuda).

**Reglas que dices al inicio (2 min):**
> "Esto es una **práctica guiada**: aquí se equivocan, y los errores son parte del aprendizaje. Trabajan **en parejas dentro de la célula** y **rotan en cada parte**. Ejecutan las celdas **en orden**, con Shift+Enter, y **sin repetirlas**: varias llaman a servicios y cuestan. Donde vean `TODO`, es un ejercicio. Al final de cada parte hay un **checkpoint**. Si se atoran más de **3 minutos**, semáforo en rojo y voy.
> **Dos reglas:** **la Parte 9 borra lo que crearon** y es obligatoria; y **el modelo no es determinista**: si algo sale distinto a lo que digo, **léanlo antes de concluir que falló**."

**Mapa de tiempos y checkpoints**
| Hora | Parte | Checkpoint (lo que todos deben tener) |
|---|---|---|
| 0:00 | 0 Preparación | `✅ <proyecto>.finanzas_<usuario>: 22 tablas y modelos` (23 si ya hay modelo) |
| 0:10 | 1 El problema | 22 tablas ≈ 2,100 tokens; ven qué palabras se repiten |
| 0:15 | 2 Descripciones | **10 de 11 con descripciones y 7 de 11 con solo nombres** |
| 0:30 | 3 RAG y reranking | **11 de 11** y un umbral entre lo irrelevante y lo relevante |
| 0:55 | 4 SQL seguro | Los ataques bloqueados y `LIMIT` frente a `TOP` |
| 1:15 | 5 BigQuery | Una consulta rechazada **sin cobrar** y una que sí pasa |
| 1:30 | 6 BigQuery ML | Periodos de **meses** (oct, nov, dic) y los intervalos |
| 1:55 | 7 Agente híbrido | Marketing: **56,000 contra 52,000 como diferencia** |
| 2:30 | 8 Verificación | 5 casos; leen los textos |
| 2:40 | 9 Limpieza | `✅ Dataset borrado.` |

**Rotación del code review (10 min por célula):**
| Slot | Célula | Mientras ellos están en… |
|---|---|---|
| 0:35–0:45 | 1 | Parte 3 |
| 0:45–0:55 | 2 | Parte 3 |
| 1:00–1:10 | 3 | Parte 4 |
| 1:35–1:45 | 4 | Parte 6 |
| 2:00–2:10 | 5 | Parte 7 |

---
## Apertura (2 min)
**🎤 Dices:**
> "Al final de hoy tienen que poder demostrar **tres cosas**: que un agente **elige qué tablas mirar** entre muchas y **ejecuta el SQL sin poder hacer daño**, que **contrasta** lo que dicen los datos con lo que dice un informe **con una regla fija y no con una opinión del modelo**, y que cada decisión —el umbral, el tope de bytes, la frecuencia del pronóstico— **se mide, no se adivina**. El notebook los lleva paso a paso; yo les digo qué tienen que **ver**. Si lo que ven no coincide, **esa es la pista**: me llaman."

**🛠 Haces:** abre el notebook y muestra la tabla de partes. Enseña tu dataset de BigQuery en la consola.

---
## Parte 0 · Preparación (10 min)
**🎤 Dices:**
> "La primera celda **encuentra la raíz del proyecto**, carga el `.env` y fija que este módulo usa los **servicios reales** y BigQuery. La segunda comprueba **proyecto, credenciales y que exista `BQ_DATASET`**. La tercera es la primera que llama a un servicio: lista las tablas de **su** dataset. Si faltan menos de 22, se detiene y les dice el comando que corre `preparar_bigquery.py`."

**👀 Deben ver (esperado; no se ha ejecutado el notebook completo):**
```
RAIZ: C:\...\GeminiAgentsBI
Proyecto: <tu-id> | Dataset: finanzas_<usuario>
Modelo de texto: gemini-2.5-flash
✅ <proyecto>.finanzas_<usuario>: 22 tablas y modelos
```
**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `Faltan paquetes … pip install …` | Falta una librería (probablemente `sqlglot`) | Ese comando, con el `.venv` activo, y **reiniciar el kernel** |
| `ModuleNotFoundError` | Kernel equivocado | *Seleccionar kernel* → el `.venv` del proyecto |
| `StopIteration` al buscar RAIZ | Abrieron el notebook fuera del proyecto | Abrir la carpeta `GeminiAgentsBI` completa |
| `Falta GOOGLE_CLOUD_PROJECT` | `.env` sin proyecto o con `tu-proyecto` | Poner el **ID** del proyecto y reiniciar el kernel |
| `No hay credenciales` | No hicieron el login | `gcloud auth application-default login` |
| `Falta BQ_DATASET` | No copiaron las líneas que imprimió `preparar_bigquery.py` | Correr el script (o `--variables`) y copiarlas al `.env` |
| `Se esperaban 22 tablas` | No corrieron `preparar_bigquery.py` | Correrlo y repetir la celda |
| `403 … BigQuery API has not been used` | API sin habilitar | Que el instructor la habilite y esperar unos minutos |
| `Not found: Dataset … in location …` | `BQ_LOCATION` distinta a la del dataset | Dejar `BQ_LOCATION=US` (la que usa el script) |

**✅ Checkpoint:** todos ven las 22 tablas.

---
## Parte 1 · El problema: Text-to-SQL con muchas tablas (5 min) 🟢
**🎤 Dices:**
> "Para que un modelo escriba SQL necesita el **esquema**. Con tres tablas se pega en el prompt. Aquí hay 22. Miren dos cosas: **cuánto pesa** y **qué tan parecidas** son."

**👀 Deben ver (medido sin servicios):**
```
22 tablas · 8,400 caracteres ≈ 2,100 tokens (aprox.)
Un almacén de 500 tablas como estas pesaría ≈ 47,727 tokens en CADA pregunta (estimación).
```
y las listas de tablas que mencionan «presupuesto», «cobr», «gasto» y «aprobaci».

**🎤 Dices (la lección, con honestidad):**
> "Fíjense: **2,100 tokens no es mucho**. El problema con 22 tablas no es el tamaño, es que **se parecen**: ¿el presupuesto de Consultoría está en `presupuesto` o en `presupuesto_historico`? El tamaño duele a escala: 500 tablas serían unos 48,000 tokens **por pregunta** (es una estimación)."

**✅ Checkpoint:** entienden que el problema es **confundir tablas** y que el tamaño aparece a escala.

---
## Parte 2 · El catálogo son documentos (15 min) 🟢 *(TODO 1)*
**🎤 Dices:**
> "Cada tabla del catálogo es un **fragmento** para el RAG: su descripción y cada columna con la suya. Vamos a medir qué pasa **con y sin descripciones de negocio**, con un buscador sin servicios (TF-IDF y un reranker de palabras)."

**🛠 Haces:** celda 2.1 (función `texto_chunk`) y 2.2 (medir). **Ejercicio `TODO 1`:** en el notebook del alumno, la función devuelve solo nombres y tipos; deben añadir la descripción de la **tabla** y de cada **columna**.

**👀 Deben ver (medido):**
- Con la función **sin completar:** `7 de 11` y `7 de 11`.
- Con la función completa (instructor): `Con descripciones de negocio: 10 de 11` y `Solo nombres y tipos: 7 de 11`.

**🎤 Dices:**
> "**10 contra 7.** La calidad del catálogo se decide **al escribirlo**, como la del RAG en el Módulo 2 se decidía al leer y cortar. Y fíjense en el que **sigue fallando**: «cuánto *pagaron* los clientes» no encuentra `pagos_clientes`, porque el buscador compara **palabras**, y «pagaron» no es «pagos». Eso lo resuelven los embeddings."

**⚠️ Errores:** si ven `10` y `10`, la función no tiene la versión «sin descripciones» (revisar `armar_chunks`). Si el `TODO 1` da `7` y `7`, **no lo completaron** todavía.
**✅ Checkpoint:** ven 10 de 11 y 7 de 11.

---
## Parte 3 · RAG y reranking del catálogo: K = 8 → N = 3 (25 min) 💸 *(TODO 2)*
**🎤 Dices:**
> "Es el **mismo flujo en dos etapas del Módulo 2**, sobre tablas. La etapa 1 busca por **significado** con embeddings de Vertex y trae **K = 8** (el catálogo tiene 22 tablas, no 20 artículos). La etapa 2 las **reordena** con la Ranking API y se queda con **N = 3**. Y un **umbral** deja el resultado vacío si nada se parece."

**🛠 Haces:** 3.1 (`ver_etapas` con «pagaron»), 3.2 (las 11 preguntas), 3.3 (calibrar), 3.4 (contexto). **`TODO 2`:** elegir el umbral con los dos números que imprime 3.3.

**👀 Deben ver (esperado; medido en el script `probar_catalogo.py`):**
- **11 de 11** (con el buscador léxico eran 10 de 11) y, para «pagaron», `pagos_clientes` en primer lugar (≈ 0.17).
- **Lo irrelevante llega hasta ≈ 0.024; la tabla correcta baja hasta ≈ 0.174; punto medio ≈ 0.10.**
- Una celda final con el ahorro de contexto (no se midió en el notebook).

**🎤 Dices (el umbral):**
> "El umbral va **entre** lo irrelevante y lo relevante. Aquí hay un hueco enorme (0.024 contra 0.174), así que cualquier valor entre ellos separa. Pero ojo: lo calibramos con **tres** preguntas fuera del catálogo. Es una muestra **pequeña**: si cambia el catálogo, se **recalibra**."

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `403 … discoveryengine` o Ranking API | API sin habilitar | Que el instructor habilite **Discovery Engine** |
| `404 … Publisher model` en embeddings | Región distinta de `us-central1` | `GOOGLE_CLOUD_LOCATION=us-central1` |
| El `TODO 2` dice «no separa» | Umbral fuera del hueco | Usar el punto medio de los dos números |
| `NameError: puntajes_correctos` | La celda 3.2 no se ejecutó | Ejecutar 3.2 antes de 3.3 |

**✅ Checkpoint:** ven 11 de 11 y un umbral que separa.

---
## Parte 4 · SQL seguro (20 min) 🟢 *(TODO 3)*
**🎤 Dices:**
> "Un modelo puede escribir `DROP TABLE` por error o porque alguien se lo pidió. **El prompt no es una barrera de seguridad.** Hay dos capas: el **permiso de la base** (la barrera real: un rol de solo lectura) y los **guardrails en código** (defensa en profundidad). Hoy vemos la segunda."

**🛠 Haces:** 4.1 (ataques), 4.2 (dialectos), 4.3 (**`TODO 3`**: sus propios ataques y una consulta válida de T-SQL con `TOP`), 4.4 (el conector de SQL Server, en código).

**👀 Deben ver (medido sin servicios, dialecto BigQuery):**
```
✅ PASA      SELECT * FROM gastos            → … LIMIT 1000
⛔ BLOQUEADA DROP TABLE gastos               → Solo SELECT
⛔ BLOQUEADA SELECT * FROM gastos; DELETE …   → Solo se permite una sentencia
⛔ BLOQUEADA SELECT 1 -- comentario          → Comentarios no permitidos
⛔ BLOQUEADA SELECT * FROM usuarios          → Tablas no permitidas: ['usuarios']
⛔ BLOQUEADA SELECT * FROM gastos, usuarios  → Tablas no permitidas: ['usuarios']
⛔ BLOQUEADA … `proyecto.otro_dataset.gastos` → Tablas no permitidas: ['otro_dataset.gastos']
⛔ BLOQUEADA SELECT * INTO nueva FROM gastos → SELECT ... INTO no permitido
```
Y en 4.2: `LIMIT 1000` en SQLite y BigQuery, **`SELECT TOP 1000`** en T-SQL.

**🎤 Dices (el caso de la unión con coma):**
> "La primera versión de este guardrail buscaba palabras con expresiones regulares y **dejaba pasar `FROM gastos, usuarios`**: la segunda tabla no se revisaba. Lo comprobamos corriéndola. Ahora la consulta se **analiza** con `sqlglot` y se ven las tablas de verdad. Aun así, **no sustituye al permiso de la base**."

**🎤 Dices (SQL Server):**
> "El cronograma pide conocer el conector de SQL Server. **No tenemos un servidor para la clase**, así que **se lee, no se ejecuta**. Fíjense en lo que protege: tiempo de conexión, tiempo por consulta, tope de filas y que **nunca confirma** una transacción. Está probado con un servidor **simulado**. La seguridad de fondo sería un login con solo `db_datareader`."

**⚠️ Errores:** `ModuleNotFoundError: sqlglot` → `pip install sqlglot` y reiniciar el kernel. Si su consulta «peligrosa» **pasa**, **léanla**: puede ser un `SELECT` válido.
**✅ Checkpoint:** ven los ataques bloqueados y la diferencia `LIMIT` / `TOP`.

---
## Parte 5 · BigQuery: dry run y topes de bytes (15 min) 💸 *(TODO 4)*
**🎤 Dices:**
> "BigQuery cobra por **bytes procesados**. Nuestro conector pone dos topes: un **dry run** (estima sin ejecutar ni cobrar; es una cota superior) y **`maximum_bytes_billed`** (si la estimación lo supera, la consulta **falla sin cobrar**). Y un detalle de la documentación: cada consulta factura **como mínimo 10 MiB**."

**🛠 Haces:** 5.1 (dry run y un tope de 1,000 bytes), 5.2 (el tope de BigQuery), 5.3 (**`TODO 4`**: un tope que sí deje pasar la consulta).

**👀 Deben ver (esperado):**
- 5.1: unos miles de bytes en el dry run (la consulta de verificación estimó 2,649) y `⛔ Rechazada ANTES de ejecutarla: La consulta procesaría … bytes y el tope es 1,000`.
- 5.2: BigQuery rechaza la consulta sin cobrar. **No se ha probado esta celda**: la documentación da el mensaje «Query exceeded limit for bytes billed: …. 10485760 or higher required.»
- 5.3 (instructor): `✅ Ejecutada con un tope de 11,000,000 bytes`.

**🎤 Dices:**
> "Fíjense en el **10485760** del mensaje: es el mínimo facturable. Un tope por debajo de eso **nunca deja pasar nada**, aunque la consulta procese 2,649 bytes. Por eso en el ejercicio el tope tiene que estar **por encima de 10 MiB**."

**⚠️ Errores:** en 5.2, si **se ejecuta** en vez de rechazarse, el mensaje de BigQuery cambió: léelo y comparte la captura. Si `TODO 4` sigue fallando: el tope es menor que 10 MiB (10,485,760 bytes).
**✅ Checkpoint:** ven una consulta rechazada **sin cobrar** y una que pasa.

---
## Parte 6 · BigQuery ML: un pronóstico con SQL (25 min) 💸 *(TODO 5)*
**🎤 Dices:**
> "BigQuery ML entrena y usa modelos **con SQL**. `ARIMA_PLUS` pronostica series de tiempo: la columna de tiempo debe ser `DATE`, `DATETIME` o `TIMESTAMP`, y hacen falta **al menos 3 puntos** por serie. Y una lección que **descubrimos al probarlo**: la **frecuencia** de los datos de entrada define qué es un «periodo»."

**🛠 Haces:** 6.1 (entrenar por **mes**), 6.2 (`ML.FORECAST` con intervalo), 6.3 (entrenar por **día** y comparar), 6.4 (**`TODO 5`**: horizonte a 6 meses).

**👀 Deben ver (medido en el proyecto):**
- 6.2: periodos del **1 de octubre, 1 de noviembre y 1 de diciembre de 2026** por división (12 filas).
- 6.3: con gastos por día, los periodos salieron el **1, 4 y 7 de octubre** (cada ~3 días).
- 6.4: 6 meses de la división Norte.

**🎤 Dices (la incertidumbre):**
> "Miren los **intervalos** (`minimo` a `maximo`). Los datos son sintéticos y son **9 puntos por serie**: el pronóstico de una división salta de 149,100 a 70,260 a 106,622. Esto sirve para aprender **cómo se usa**, no para sacar conclusiones."

**⚠️ Errores:** si 6.3 tarda, es el entrenamiento (no se cronometró). `ML.FORECAST` bloqueado → el modelo no está en el dataset (repetir 6.1). `horizon` mayor que 6 → falla porque el modelo se entrenó con `horizon=6`.
**✅ Checkpoint:** ven meses (no días) en 6.2 y días en 6.3.

---
## Parte 7 · El agente híbrido (35 min) 💸 *(TODO 6 y 7)*
**🎤 Dices:**
> "El agente tiene **cinco herramientas**, cada una con una sola responsabilidad: `buscar_esquema`, `ejecutar_sql`, `buscar_informe`, `contrastar_cifras` y `buscar_politicas`. La regla que más importa: **el modelo no calcula diferencias**. Las calcula `contrastar_cifras`, y las dos cifras deben medir **lo mismo** y estar en **la misma unidad**."

**🛠 Haces:** 7.1 (`contrastar_cifras`, **`TODO 6`**: agregar cifras), 7.2 (la trampa de la unidad), 7.3 (¿de dónde lee?), 7.4 (el agente, con eventos), 7.5 (**`TODO 7`**: su pregunta).

**👀 Deben ver (7.1 y 7.2, medidos sin servicios):**
```
cifra                    sql      informe  diferencia  diferencia_pct  estado
Consultoria presupuesto  78000.0  78000.0  0.0         0.0             coincide
Marketing presupuesto    56000.0  52000.0  4000.0      7.69            difiere
Servicios ejecutado      71400.0  69900.0  1500.0      2.15            difiere
Tecnologia ejecutado     None     57750.0                              sin_contraparte
Coinciden: 1 · Difieren: 2 · Sin contraparte: 1
Sin escala: difiere (99900.0 %)   ·   Con escala_informe=1000: coincide
```
**7.4 (esperado):** las herramientas en este orden: `buscar_esquema` → `ejecutar_sql` → `buscar_informe` → `contrastar_cifras` → `buscar_politicas`, con **78,000 y 124,800**, la cita del informe (con la frase de que el exceso **no tiene la aprobación del Comité**) y el **Art. 2.3**, concluyendo que **no es consistente con la política**.

**🎤 Dices (lo que medimos):**
> "Esto lo probamos varias veces y **el modelo no es determinista**. Una vez escribió «Consultoría» con acento y la base dijo **0 filas**; otra, la cita del informe llegaba **cortada**; otra, comparó el presupuesto **original** con el del informe; y con una pregunta ambigua sumó **todo el año**. Cada fallo terminó como una **regla** en la instrucción o un cambio en el código. Por eso la Parte 8 **verifica**."

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `⚠️ … faltan las variables de corpus: uso markdown` | No corrieron `preparar_rag.py` | Es solo un aviso: usa markdown. Si quieren RAG Engine, correrlo |
| La cita del informe dice «fragmento 1» | Informe en RAG Engine (un solo fragmento) | Esperado; con markdown dice «sección 2» |
| Datos con 0 filas | Valores con acento o ambigüedad | Mirar la consulta; la instrucción pide reintentar una vez |
| No llamó a una herramienta | Variación del modelo | Repetir la pregunta con la **división y el periodo** |
| Marketing no sale como diferencia | Comparó con el presupuesto original o sumó todo el año | **Leer el texto**; es un caso para discutir |

**✅ Checkpoint:** ven `contrastar_cifras` marcar Marketing y Servicios como diferencia, y el agente responder Consultoría con las tres partes (datos, informe, política).

---
## Parte 8 · ¿Lo logramos? Verificación (10 min) 💸
**🎤 Dices:**
> "Cinco casos con su resultado esperado. La comprobación es **heurística**: busca cifras y frases. Si algo sale ❌, **lean el texto** antes de decir que falló."

**👀 Deben ver (esperado):** `✅` en H1 a H5 (Consultoría, Marketing y Servicios, Tecnología de Sur, borrar, paella). **No es seguro que pasen los cinco en cada corrida.** La celda 8.2 imprime el texto de los que fallen, y si todos pasan, el de H2.
**✅ Checkpoint:** 5 casos y han leído al menos un texto.

---
## Parte 9 · 🧹 Limpieza (5 min) — **obligatoria** 💸
Ejecutan `preparar_bigquery.py --limpiar` (su dataset, con tablas y modelos) y, si usaron RAG Engine, `preparar_rag.py --limpiar` (corpus del informe y bucket). El corpus de **políticas** es el del Módulo 2: déjalo salvo que sea solo para esto (`--incluir-politicas`).
**👀 Deben ver:** `✅ Dataset borrado.`
**⚠️ Errores:** si el subproceso falla por imports, ejecutar el script desde una terminal con `. .\env.ps1`.

---
## Cierre (5 min)
**🎤 Dices:** pide a cada célula que cuente **una** de estas ideas con sus palabras: lo cuantitativo viene del SQL y lo normativo de RAG · elegir tablas con RAG (descripciones, dos etapas y umbral) · el modelo propone, el sistema dispone · BigQuery cobra por bytes · misma magnitud, misma unidad, y verificar.

## Code review: qué preguntar (10 min por célula)
1. **Descripciones:** ¿qué escribieron en `texto_chunk`? ¿Qué pasa si quitan la de la columna `categoria`?
2. **Umbral:** ¿cómo lo eligieron? ¿Con cuántas preguntas fuera del catálogo? ¿Qué pasa si agregan una tabla?
3. **Guardrails:** ¿qué ataque inventaron? ¿Por qué el permiso de la base importa más?
4. **Topes:** ¿qué tope eligieron y por qué por encima de 10 MiB? ¿Qué hace el dry run que no hace el tope?
5. **Pronóstico:** ¿qué significa «3 periodos» con sus datos? ¿Qué dicen los intervalos?
6. **Contraste:** ¿qué cifras compararon? ¿Misma unidad? ¿Misma magnitud (original o aprobado)?
7. **Agente:** ¿qué pregunta propia hicieron? ¿Qué herramientas usó y en qué orden?

## Si algo sale mal (contingencias)
| Situación | Qué hacer |
|---|---|
| Muchos alumnos con 403 | API sin habilitar o permisos: ver Antes de la clase |
| `preparar_rag.py` falla o tarda | Seguir con markdown (`AUDITOR_FUENTE=politicas`, `INFORME_FUENTE=markdown`): el notebook funciona igual |
| BigQuery ML tarda mucho | Recortar 6.3 (segundo modelo) |
| El agente se comporta distinto | Es el modelo no determinista: leer el texto y usarlo como lección |
| Se acabó el tiempo | Recortar en el orden de *Línea de tiempo y reparto*; la limpieza **no se recorta** |

## Problemas fuera del notebook (el proyecto `src`)
- `adk web --port 8501 modulo3_sql_bigquery/src` y elegir **`sql_app`** (en la lista puede salir también `sqlagent`: es la librería, no un agente). Con `. .\env.ps1` activo.
- `adk web` crea `src/sql_app/.adk/session.db` (estado de las sesiones): **no lo incluyas en el ZIP de alumnos** ni lo subas a Git.
- Scripts del módulo: `preparar_bigquery.py`, `preparar_rag.py`, `verificar_bigquery.py`, `probar_catalogo.py`, `probar_informe.py`. `preparar_sqlserver.py` y `verificar_sqlserver.py` son **opcionales y no se han probado contra un servidor real**.

## Nota de instructor: cómo se conecta con el capstone
En la **Semana 6**, un supervisor delega por A2A a tres subagentes: **RAG + reranking** (políticas), **SQL** (datos de Q3) y **ML y BI**. El agente de este módulo junta SQL, informe y políticas; en el capstone hay que decidir si se usa tal cual o se separa en un agente de SQL y uno de RAG (la librería `sqlagent` y el `rag` del Módulo 2 ya están separados). Los datos son los mismos en todos los módulos: Norte excede su presupuesto en el 3T 2026 por viáticos y consultoría. **No se ha revisado el código de los Módulos 4 y 5** para esta guía.

## Lo que no está probado
- **El notebook completo de arriba abajo.** Las celdas 🟢 se ejecutaron sin errores; las 💸 no.
- La celda 5.2 (BigQuery rechazando por el tope), la 3.4 y la 6.3 (modelo diario) en el notebook.
- Que el agente siga el flujo con los 5 casos en cada corrida (el modelo no es determinista; se vio una corrida de cada pregunta).
- **30 alumnos a la vez**, y los **permisos mínimos** de cada rol.
- Los **tiempos** de cada parte (son estimaciones).
- Los ejercicios `TODO` con valores distintos a los esperados.
- **SQL Server real:** el conector está probado solo con un servidor simulado.
- `preparar_rag.py`: se ejecutó una vez con éxito (los corpus existieron y respondieron en `adk web`), pero no se revisó su salida completa.
- Reanudar el notebook en dos sesiones.
