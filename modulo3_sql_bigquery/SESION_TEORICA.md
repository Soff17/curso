# Módulo 3 · SESIÓN TEÓRICA (2 h) — Guía del instructor

**Tema:** un agente que contesta una pregunta de finanzas **consultando una base de datos (SQL en BigQuery) y leyendo documentos (informe y política)**, y que **compara** lo que dicen ambas fuentes. En términos técnicos: agente híbrido con RAG sobre el catálogo de datos, SQL con guardrails, BigQuery ML y contraste de cifras · **Público:** Equipo de BI (30 personas, 5 células) · **Semana 3**
La práctica con el notebook tiene su propia guía: **`SESION_PRACTICA.md`**. Los comandos para los alumnos están en **`COMANDOS.md`**.
Lo que depende de servicios reales (BigQuery, BigQuery ML, embeddings, Ranking API, Gemini, RAG Engine) pruébalo tú antes de la clase: ver sección 4.

**Presentación que acompaña esta guía:** `Modulo 3 - SQL, BigQuery y RAG Estructurado (v2).pptx` (**40 diapositivas**, con el mismo diseño que las de los Módulos 1 y 2; las notas del orador traen los datos clave y de qué página de la documentación salen). Esta guía es tu **guion**: lo que dices, por qué, qué preguntar y qué responder.
**Cómo está armada:** abre con **un caso concreto** (diap. 2) que se retoma en todo el módulo; en cada bloque va **primero lo que dice la documentación** (qué ofrece ADK, cómo se controla el costo en BigQuery, qué dice la documentación de SQL Server y de BigQuery ML) y **después lo que medimos nosotros**. Lo marcado *(docs)* viene de la documentación; lo marcado *(medido)*, de las corridas de este proyecto.

> ⚠️ Las notas del orador de la presentación dicen «Guion completo: SESION_TEORICA.md del Módulo 3 (se escribe después…)». Esta guía ya existe: ese texto de las notas quedó desactualizado.

**Contenido de esta guía:** 1. Antes de la clase · 2. Mensajes clave · 3. Línea de tiempo · 4. Ensayo previo de las demos · 5. Guion por diapositiva (con 5.0: hilo conductor y vocabulario) · 6. Frases de rescate y recortes · 7. Errores comunes y preguntas de repaso · 8. Lo que no está probado · 9. Mapa del proyecto.

---
## 1. Antes de la clase (haz esto el día anterior)
- [ ] `pip install sqlglot`, `. .\env.ps1` y `python -m pytest modulo3_sql_bigquery -q` → **79 passed, 1 xfailed** (todo el repositorio: 165 passed, 1 xfailed; ninguna llama a servicios, aunque tu `.env` diga `cloud`). *(Verificado el 3 de noviembre de 2026.)*
- [ ] Tu dataset de BigQuery creado con `python modulo3_sql_bigquery/preparar_bigquery.py` (y `--modelo` si quieres el modelo de pronóstico ya entrenado). Con `--dry-run` ves el plan sin llamar a nada.
- [ ] Si harás la demo con RAG Engine: `python modulo3_sql_bigquery/preparar_rag.py` y las variables en tu `.env` (ver `SESION_PRACTICA.md`).
- [ ] **API de BigQuery** habilitada; para RAG Engine, las 4 APIs del Módulo 2 y el modo sin servidores.
- [ ] Consola abierta en **BigQuery** (tu dataset) para enseñar que las tablas y el modelo existen y se borran.
- [ ] Tu `.env` con `AGENTS_MODE=cloud` y `SQL_BACKEND=bigquery` si harás la demo en `adk web`.
- [ ] **Alerta de presupuesto** en Facturación.
- [ ] Alumnos con el entorno listo (`COMANDOS.md`).
- [ ] Recuerda **borrar** lo que crees: `python modulo3_sql_bigquery/preparar_bigquery.py --limpiar` y `preparar_rag.py --limpiar`.

## 2. Mensajes clave (las ideas que deben llevarse)
Cada idea, primero en palabras simples y después en términos técnicos.
1. **Las cifras las calcula la base de datos; las reglas salen de los documentos; el modelo no hace cuentas.** *(Técnico: lo cuantitativo viene del SQL, lo normativo de RAG, y la comparación de cifras es código.)*
2. **Con muchas tablas, el problema es que se parecen, no solo que son muchas.** Ayuda **describir cada tabla en lenguaje de negocio** y escribir los **valores exactos** de las columnas de texto. *(Técnico: RAG de metadata; una tabla es un fragmento.)*
3. **El modelo propone y el sistema decide.** La barrera real es el **permiso de solo lectura de la base**; las revisiones en código son la segunda; pedirle al modelo «no borres» no es una barrera. *(Técnico: guardrails.)*
4. **BigQuery cobra por los datos que lee:** se estima antes de ejecutar y se pone un tope. Y en el pronóstico, **la frecuencia de los datos define qué es un «periodo»**. *(Técnico: dry run, `maximum_bytes_billed`, mínimo de 10 MiB; `DATA_FREQUENCY`.)*
5. **Comparar solo cifras de la misma cosa y en la misma unidad, y verificar varias veces:** el modelo puede responder distinto a la misma pregunta; una corrida buena no es una garantía.

## 3. Línea de tiempo
Coincide con los bloques de la presentación (los minutos suman 120). **Es una propuesta sin ensayar:** 40 diapositivas son muchas (cinco son divisores y varias son tablas o código); ver la sección 6 para recortar. **El guion de la sección 5 es más largo de lo que cabe hablado en cada bloque:** es el material completo para que lo adaptes; lo esencial está en 🎤 y lo marcado ⚠️ o *(si preguntan)* puedes dejarlo para las preguntas. Los bloques que más explicación piden son las diap. 2 y 5 a 7 (el caso y el híbrido): si vas justa, recorta después, no ahí.

| Hora | Min | Bloque | Diap. | Qué muestras |
|---|---|---|---|---|
| 0:00–0:05 | 5 | Apertura: el caso y el entregable | 1–3 | La pregunta híbrida: ¿Norte excedió su presupuesto y estaba permitido? |
| 0:05–0:15 | 10 | Datos y documentos | 4–7 | Lo que RAG no puede hacer y lo que el SQL no sabe |
| 0:15–0:39 | 24 | Text-to-SQL: de la pregunta al SELECT | 8–16 | Los 6 pasos; qué contexto necesita el modelo; todo o una parte; cómo escribir un catálogo; lo medido: 7 de 11, 10 de 11, 11 de 11 |
| 0:39–1:03 | 24 | SQL seguro | 17–23 | Ataques bloqueados; `LIMIT` frente a `TOP`; el conector de SQL Server |
| 1:03–1:29 | 26 | BigQuery y BigQuery ML | 24–30 | Dry run y tope; ARIMA_PLUS; meses frente a días |
| 1:29–1:51 | 22 | El agente híbrido | 31–37 | Cinco herramientas; contraste de cifras; qué falló y cómo se previene; cómo armar el tuyo |
| 1:51–2:00 | 9 | Cierre | 38–40 | 5 ideas + abrir el notebook (Parte 0) |

## 4. Ensayo previo de las demos (hazlo tú antes; esto es lo que debes ver)
*Esta sección es para ti, no para el grupo: te dice qué resultado esperar en cada demo.*
Terminal en la raíz del proyecto, con el entorno activado y `. .\env.ps1`. **🟢 no usa servicios · 💸 usa servicios (centavos).** Fuerza `$env:AGENTS_MODE="offline"` en los comandos 🟢 si tu `.env` dice `cloud`.

| Demo | Comando / acción | Debes ver | |
|---|---|---|---|
| Catálogo: tamaño y parecidos | Notebook del instructor, celdas 1.1 y 1.2 | `22 tablas · 8,400 caracteres ≈ 2,100 tokens`; las listas de tablas que mencionan «presupuesto» | 🟢 |
| Descripciones | Notebook, celdas 2.1 y 2.2 | **10 de 11 con descripciones y 7 de 11 con solo nombres** | 🟢 |
| Guardrails | Notebook, celdas 4.1 a 4.3 | `DROP`, `;`, comentario, `usuarios`, **coma**, otro dataset, `INTO` bloqueados | 🟢 |
| Dialectos | Notebook, celda 4.2 | `LIMIT 1000` en SQLite y BigQuery; `SELECT TOP 1000` en T-SQL | 🟢 |
| Contraste de cifras | Notebook, celdas 7.1 y 7.2 | Marketing 56,000 contra 52,000 «difiere»; sin escala 99,900 % | 🟢 |
| Catálogo con servicios | `python modulo3_sql_bigquery/probar_catalogo.py` | **11 de 11**; irrelevante ≤ 0.024, relevante ≥ 0.174 *(medido el 3 de noviembre)* | 💸 |
| Informe con servicios | `python modulo3_sql_bigquery/probar_informe.py` | 6 de 6; irrelevante ≤ 0.019, relevante ≥ 0.201 (informe en RAG Engine) *(medido)* | 💸 |
| BigQuery, guardrails y ML | `python modulo3_sql_bigquery/verificar_bigquery.py` | 22 tablas (23 con el modelo); Norte con exceso de **46,800**; el `DELETE` bloqueado; `ML.FORECAST` con 12 filas | 💸 |
| Dry run en la consola | BigQuery → pega una consulta en el editor | Muestra «esta consulta procesará N bytes» *(docs)* | 🟢 |
| Pronóstico mensual | Notebook, celdas 6.1 y 6.2 | Periodos 1 de oct., 1 de nov. y 1 de dic. de 2026 | 💸 |
| Pronóstico por día | Notebook, celda 6.3 | Periodos cada ~3 días (1, 4 y 7 de octubre) | 💸 |
| Agente en `adk web` | `adk web --port 8501 modulo3_sql_bigquery/src` → `sql_app` → «¿La división Norte excedió el presupuesto de Consultoría en el 3T 2026? ¿Es consistente con el informe y con la política?» | Las 5 herramientas; 78,000 y 124,800; el Art. 2.3; «no es consistente» *(medido; el modelo varía)* | 💸 |
| Discrepancias | La misma app → «Compara con el informe el presupuesto de Marketing y los gastos de Servicios de la división Norte en el 3T de 2026» | Marketing 56,000 contra 52,000 y Servicios 71,400 contra 69,900 *(varió entre corridas)* | 💸 |
| Sin dato | La misma app → «¿Cuál fue el presupuesto de Tecnología de la división Sur según el informe?» | «No encontré información…» (tras llamar a `buscar_informe`) | 💸 |
| Fuera de alcance | La misma app → «Receta de paella valenciana» | Se niega | 💸 |

> **El código de `BigQueryToolset` (diap. 25) no se ejecuta en la clase.** Es el de la documentación, abreviado; no lo probamos.
> **Lo de SQL Server (diap. 21 a 23) no se ejecuta:** el conector está probado solo con un servidor simulado.
> **Los puntajes y hasta el comportamiento del agente varían entre corridas** (los embeddings, la Ranking API y Gemini son modelos). Lo que no debe variar: el `DELETE` queda bloqueado, el informe no inventa una cifra de Sur, y `contrastar_cifras` da siempre el mismo resultado con las mismas entradas.

---
## 5. Guion por diapositiva (40 diapositivas)
**Criterio de la presentación:** igual que en los Módulos 1 y 2, cada bloque explica **el método en general** (sirve para sus propias bases y documentos) y las cifras de nuestro caso van en diapositivas **«Lo medido»** (15, 30 y 36). El caso de Norte aparece en la diap. 2 y como ejemplo.
**Cómo leerlo:** **🛠** = qué haces · **🎤** = qué decir · **💡** = por qué se hace así · **❓** = pregunta para el grupo · **⚠️** = dudas probables y cómo responderlas.
**Tono:** el público es BI, pero **no todos dominan SQL ni qué es un catálogo de datos o un embedding**. Define cada término la primera vez (hay un vocabulario en 5.0) y ancla cada concepto a algo conocido (Excel, tablas dinámicas, permisos de un sistema contable, el «estimado de bytes» del editor de BigQuery).
**Fuentes:** lo marcado *(docs)* viene de la documentación (la página «BigQuery tool for ADK», «Estimate and control costs» de BigQuery, «CREATE MODEL para ARIMA_PLUS», «ML.FORECAST», las palabras clave del ODBC Driver for SQL Server y la wiki de pyodbc): dilo como «según la documentación» y confirma el dato vigente antes de usarlo como cifra. Lo marcado *(medido)* salió de las corridas de este proyecto.

### 5.0 Antes de empezar: el hilo conductor y el vocabulario
**Suposición de esta versión del guion:** parte de la sala **no sabe SQL** ni qué es un catálogo de datos. Por eso el guion **define cada término la primera vez que aparece** y **usa un solo caso de principio a fin**. Si el grupo ya lo domina, salta las partes marcadas *(si preguntan)*.

**El caso, en tres frases (dilo en la diap. 2 y repítelo cada vez que haga falta):**
- **La empresa** es ficticia: *Norte Retail Holdings*. Tiene **divisiones** (Norte, Sur, Centro…): unidades de negocio con su propio presupuesto.
- **El presupuesto** de cada división se reparte por **categoría de gasto** (viáticos, consultoría, tecnología, marketing, servicios) y por **trimestre**. «3T 2026» es julio a septiembre de 2026.
- **La pregunta:** «¿La división Norte gastó en Consultoría más de lo que tenía presupuestado en el 3T 2026? ¿Lo dice igual el informe? ¿La política lo permitía?»

**Las tres fuentes** (pregunta clave de la diap. 2: ¿dónde vive cada respuesta?):

| Fuente | Qué es, en palabras simples | Qué contiene del caso | Quién la «escribe» |
|---|---|---|---|
| **La base de datos** | Tablas, como hojas de Excel muy grandes y ordenadas, con **un registro por fila** (cada gasto, cada presupuesto). Es el sistema donde queda lo que realmente se registró | Consultoría de Norte, 3T: presupuestado **78,000**, ejecutado **124,800** | El sistema contable (aquí, datos sintéticos) |
| **El informe de presupuesto** | Un **documento** (PDF) que la **Administración de la división Norte** redacta cada trimestre para explicar a la dirección de la empresa cuánto tenía aprobado y cuánto gastó, y por qué | «Consultoría ejecutó 124,800 frente a 78,000 aprobados… **no cuenta con la aprobación del Comité Financiero**» | Personas (aquí, un documento ficticio) |
| **La política** | Las **reglas internas** de la empresa: qué se puede hacer y quién debe autorizarlo | **Art. 2.3:** un exceso de hasta 10 % lo aprueba el Director de División; **uno mayor a 10 % requiere al Comité Financiero antes de gastar** | El área de normas (aquí, el PDF del Módulo 2) |

> 🎤 «Cuando digo "la dirección" me refiero a quienes dirigen la división: su **Administración**. El informe es lo que **ellos reportan**; la base de datos es lo que **quedó registrado**. Una de las preguntas del módulo es si los dos cuentan lo mismo.»

**Vocabulario (tenlo a la mano; cada término se explica de nuevo en su diapositiva):**
| Término | Cómo decirlo sin tecnicismos |
|---|---|
| **SQL** | El **idioma para pedirle datos a una base de datos**. Ejemplo: `SELECT ejecutado FROM presupuesto WHERE division = 'Norte'` se lee «dame lo ejecutado de la tabla presupuesto, solo de la división Norte». Quien usa Excel con filtros y sumas ya hace lo mismo con otra herramienta. |
| **Tabla, fila, columna** | Una **tabla** es una hoja (`presupuesto`, `gastos`); una **fila** es un registro; una **columna** es un dato de ese registro (`division`, `ejecutado`). |
| **Esquema** | La **lista de tablas y columnas** que existen y de qué tipo son. Es lo que alguien necesita saber antes de escribir una consulta. |
| **Catálogo de datos** | El **esquema con explicaciones en lenguaje de negocio**: qué significa cada tabla y cada columna («`ejecutado`: monto realmente gastado en el trimestre»). Es el «diccionario» de la base. |
| **Text-to-SQL** | Que el modelo **convierta una pregunta en español en una consulta SQL**. |
| **Modelo / LLM / agente** | El **modelo** (Gemini) redacta texto. El **agente** es el modelo **más herramientas** que puede llamar (buscar, consultar, comparar). |
| **RAG** | «Buscar primero, responder después»: el agente **busca fragmentos de documentos** relevantes y responde **apoyándose en ellos y citándolos**. Es lo del Módulo 2. |
| **Fragmento (chunk)** | Un **trozo de documento** (o, hoy, una descripción de tabla) que se guarda y se busca por separado. |
| **Embeddings** | Convertir un texto en **una lista de números que representa su significado**, de modo que textos con significado parecido queden «cerca». Sirve para buscar **por significado**, no por palabras iguales. |
| **Reranking (reordenar)** | Un **segundo paso de búsqueda, más fino**: un modelo lee la pregunta junto con cada candidato y **los reordena** por relevancia. En el Módulo 2: K = 20 candidatos → N = 3. |
| **Umbral** | Una **nota mínima**: si ningún candidato la alcanza, se responde «no hay nada relevante» en lugar de elegir el «menos malo». |
| **Token** | Una **unidad de texto** que cobra y limita al modelo (aprox. 4 caracteres). Más tokens = más costo y más espacio ocupado. |
| **Guardrail (barandal)** | Una **regla en código que revisa algo antes de ejecutarlo** y lo bloquea si no cumple. |
| **Solo lectura** | Un permiso que deja **consultar pero no cambiar ni borrar** nada. |
| **Dialecto** | SQL no es idéntico en todas partes: SQL Server, BigQuery y SQLite lo escriben **un poco distinto**, como el español de distintos países. |
| **BigQuery** | La **base de datos analítica de Google Cloud**. **Cobra por la cantidad de datos que lee** una consulta. |
| **Prompt / instrucción** | El **texto que se le da al modelo** para decirle qué hacer. La instrucción del agente es su «manual de reglas». |
| **`adk web`** | La **interfaz de chat** de ADK para probar un agente en el navegador. |
| **Dataset** | En BigQuery, la **«carpeta» que agrupa las tablas** de un proyecto. |
| **RAG Engine / corpus** | El **servicio de Google** (el del Módulo 2) que guarda y busca los documentos; un **corpus** es una colección de documentos. |
| **Ranking API** | El **servicio de Google que hace el reordenado** (reranking). |
| **Pronóstico (BigQuery ML)** | Que BigQuery **entrene un modelo de series de tiempo** con tus datos y estime los próximos meses, **con un rango de incertidumbre**. |

---

### Apertura (0:00–0:05)
**Diap. 1 · Portada**
> 🎤 "Hasta ahora el agente sabía hacer dos cosas: en el Módulo 1 **usar herramientas** y en el 2 **buscar en documentos** y citarlos. Hoy le sumamos una tercera: **consultar una base de datos**. Y el reto final es que use las tres a la vez y que sus respuestas **se puedan comprobar**."
> ⚠️ La fecha de la portada viene de la plantilla («Oct, 2026»): corrígela si hace falta.

**Diap. 2 · El caso: ¿Norte excedió su presupuesto y estaba permitido?**
> 🛠 Antes de leer la diapositiva, pon el contexto (30 segundos): "Imaginen una empresa con varias **divisiones** (Norte, Sur, Centro…). Cada trimestre, a cada división se le **aprueba un presupuesto por categoría**: viáticos, consultoría, tecnología… Alguien quiere saber una cosa muy concreta."
> 🎤 "La pregunta es: **«¿La división Norte excedió el presupuesto de Consultoría en el 3T 2026? ¿Es consistente con el informe y con la política?»** Para contestarla, una persona abriría **tres lugares**."
> 🎤 "**Uno: la base de datos**, donde está lo que realmente se registró: cuánto se presupuestó y cuánto se gastó. **Dos: el informe de presupuesto**: un documento que la **Administración de la división Norte** escribe para explicarle a la dirección de la empresa cuánto gastó y por qué. Es **lo que ellos reportan**. **Tres: la política**: las reglas internas que dicen **hasta cuánto exceso se permite y quién lo autoriza**."
> 🎤 "El agente debe hacer lo mismo que esa persona, con una condición: **no inventar ninguna cifra**. Cada número tiene que venir de una fuente que se pueda señalar."
> ❓ ¿Cuántos lugares revisan hoy para contestar algo así? ¿Cuánto tardan?
> 💡 Es el entregable del cronograma: agente que hace reranking sobre el catálogo de datos, ejecuta el SQL y contrasta contra el presupuesto del informe. La historia está embebida en los datos: Norte excede su presupuesto en el 3T 2026 por viáticos y consultoría. **Cifras, empresa y documentos ficticios.**
> ⚠️ *«¿Qué es "la dirección"?»* → "Quienes dirigen la división. El informe es lo que **ellos reportan** de su propio presupuesto; la base es lo que **quedó registrado**. Parte de la pregunta es si coinciden."

**Diap. 3 · Agenda**
> 🎤 "Tenemos 2 horas. Primero entendemos **qué sabe hacer cada fuente** (diap. 4–7). Luego tres bloques técnicos: **cómo el agente elige qué tablas mirar**, **cómo ejecutamos SQL sin riesgo** y **cómo se usa BigQuery**, que cobra por lo que lee y también hace pronósticos. Al final juntamos todo en **un agente**. Después viene la práctica con el notebook."
> 🎤 "El cronograma dice «SQL Server o BigQuery». **Nuestro entregable corre en BigQuery**; SQL Server lo estudiamos **en código**, porque la sesión de hoy no tiene un servidor de SQL Server."
> ⚠️ *«¿Por qué no SQL Server?»* → "No tenemos un servidor para toda la clase; crear uno cobra mientras exista. Explico en la diap. 23 cómo sería y qué cambia: casi nada del patrón."

### Datos y documentos (0:05–0:15)
**Diap. 4 · Divisor.** *(Sin guion; di en una frase: "Vamos a ver qué sabe y qué no sabe hacer cada fuente".)*

**Diap. 5 · Lo que RAG no puede hacer**
> 🎤 "En el Módulo 2 vimos RAG: el agente **busca fragmentos de documentos que se parezcan a la pregunta** y responde con ellos. Es excelente para **textos**: políticas, contratos, informes."
> 🎤 "Pero **no sirve para cuentas**. Si pregunto «¿cuánto gastó Norte en Consultoría en el 3T?», la respuesta no está escrita en ningún párrafo: hay que **sumar muchos registros** (cada pago de consultoría de julio, agosto y septiembre). RAG encuentra texto *parecido*; **no suma, no agrupa y no filtra con exactitud**."
> 🎤 "Eso lo hace una **base de datos**, con un lenguaje llamado **SQL**. SQL es simplemente **el idioma para pedirle datos a una base**: por ejemplo, 'dame la suma de lo gastado, solo de Norte, solo en consultoría, solo en el 3T'. La base **calcula**; no opina. Siempre da el mismo resultado."
> 🎤 "¿Y por qué no dejar que el modelo sume? Porque un modelo de lenguaje **predice texto plausible**. Si le damos 200 filas y le pedimos el total, **puede equivocarse y decirlo con total seguridad**. En finanzas, eso no se acepta."
> 💡 Analogía BI: una tabla dinámica o un `SUMAR.SI` en Excel **no opinan** sobre el total; lo calculan. Un modelo de lenguaje **no es una calculadora**.
> ❓ ¿Alguien ha visto a un chatbot dar un total que no cuadraba?
> ⚠️ *«Pero Gemini sí suma bien muchas veces»* → "Muchas veces no es siempre. En un informe financiero no puedo decir 'casi siempre'. Con SQL el resultado se puede reproducir y auditar."

**Diap. 6 · Lo que el SQL no sabe**
> 🎤 "Ahora al revés. Supongamos que SQL ya nos dijo que Consultoría de Norte gastó **124,800 contra 78,000 presupuestados**: un exceso de **60 %**. ¿Eso estaba permitido? **La base de datos no lo sabe.** Solo guarda números; no conoce las reglas."
> 🎤 "Las reglas están en la **política**: el **Artículo 2.3** dice que un exceso de hasta 10 % lo aprueba el Director de División, y **uno mayor a 10 % requiere la aprobación del Comité Financiero antes de gastar**. Y el **informe** nos dice si esa aprobación existió: «el exceso de Consultoría **no** cuenta con la aprobación del Comité Financiero». Todo eso es **texto**, y es trabajo de **RAG**."
> 🎤 "Un buen analista usa los dos mundos y **contrasta**: lo que dice el informe, ¿coincide con lo que dicen los datos? Y lo que pasó, ¿cumplía la regla?"
> 💡 Los números: base → 124,800 contra 78,000 (+60 %). Política → más de 10 % requiere Comité Financiero. Informe → sin aprobación del Comité. Con estas tres piezas se contesta completo.

**Diap. 7 · El híbrido en una línea** (aquí está el corazón del módulo: tómate tiempo)
> 🎤 "«Híbrido» significa que el agente combina **dos tipos de fuente**: **datos estructurados** (tablas, con SQL) y **documentos** (texto, con RAG). Veamos cómo se contesta nuestra pregunta, paso a paso, y noten que **cada paso es una herramienta distinta** que el agente puede llamar:"
> 🎤 "**1. Catálogo — «¿qué tablas hay que mirar?»** La base tiene 22 tablas. El agente primero busca, en la descripción de las tablas, cuáles sirven para la pregunta. Por ejemplo, la tabla `presupuesto`. *(Es 'RAG', pero sobre tablas en lugar de PDFs.)*"
> 🎤 "**2. SQL — «dame las cifras exactas».** Con esa tabla, el modelo **escribe la consulta** y el sistema la ejecuta, con protecciones. Respuesta: presupuestado 78,000; ejecutado 124,800."
> 🎤 "**3. Informe — «¿qué dice la dirección?»** Busca en el informe y trae la cifra y la **cita**: 78,000 y 124,800, y que el exceso no tiene aprobación del Comité."
> 🎤 "**4. Contraste — «¿coinciden?»** Compara la cifra de la base con la del informe. Aquí hay algo importante: **esta comparación la hace un programa, con una regla fija**, no el modelo. Resultado: «coincide» o «difiere»."
> 🎤 "**5. Política — «¿estaba permitido?»** Trae el Art. 2.3 con su cita. Con eso el agente concluye: excedió 60 %, el informe y la base coinciden, y **la política exigía aprobación del Comité Financiero y no la hubo**."
> 🎤 "**El agente decide cuándo llamar cada herramienta y redacta la respuesta; no hace las cuentas ni inventa números.** Es el mismo patrón del Módulo 2: **la herramienta es la fuente** de lo que se afirma."
> ❓ De los cinco pasos, ¿cuáles creen que **son** el modelo y cuáles **son** código normal? (Solo redactar y decidir son del modelo.)
> ⚠️ *«¿Y si dos fuentes no coinciden?»* → "Justo para eso existe el paso 4: no se esconde; se **reporta** la diferencia. Veremos que en nuestros datos hay dos discrepancias puestas a propósito."
> ⚠️ Las tablas exactas que el agente elige en el paso 1 pueden variar entre corridas; lo que importa es que las cifras coincidan con 78,000 y 124,800.

### Text-to-SQL: de la pregunta al SELECT (0:15–0:39)
**Diap. 8 · Divisor.** *(Sin guion; di: "Primero: ¿cómo sabe el agente **en qué tabla** buscar?".)*

**Diap. 9 · De la pregunta al SELECT: Text-to-SQL**
> 🎤 "**Text-to-SQL** es que el modelo convierta una pregunta en español en una **consulta SQL**. SQL es el idioma para pedirle datos a una base; un `SELECT` es la consulta que **solo lee**: «dame estas columnas de esta tabla, con estos filtros». Por ejemplo, «¿cuánto se presupuestó para Consultoría?» se vuelve `SELECT presupuestado FROM presupuesto WHERE categoria = 'Consultoria'`."
> 🎤 "Este flujo sirve para **cualquier base de datos**. Son seis pasos. **1, la pregunta**, en lenguaje natural. **2, el contexto:** el modelo no conoce su base; hay que contarle qué tablas y columnas existen y qué significan. **3, generar:** el modelo escribe el `SELECT`. **4, validar:** código revisa la consulta antes de ejecutarla. **5, ejecutar:** con un permiso de solo lectura y con topes. **6, responder:** el modelo redacta con las cifras y su fuente."
> 🎤 "Fíjense en algo: **el modelo solo hace dos de los seis pasos** (escribir la consulta y redactar la respuesta). Los otros cuatro son el **sistema**. Hoy vemos el paso 2 en este bloque, los pasos 4 y 5 en «SQL seguro» y «BigQuery», y el 6 en el agente."
> 💡 El riesgo central de todo el flujo: si el modelo escoge **otra tabla que se parece**, la consulta se ejecuta y devuelve un número, **pero de otra cosa**, y no hay ningún error que avise. Por eso el paso 2 importa tanto.
> ❓ ¿En cuál de los seis pasos creen que hay más riesgo de que algo salga mal sin que nadie se dé cuenta?
> ⚠️ *«¿El modelo ejecuta la consulta directamente?»* → "No: la escribe, y el sistema decide si se ejecuta (bloque «SQL seguro»)."

**Diap. 10 · Qué contexto necesita el modelo** *(docs)*
> 🎤 "El paso 2 es contarle al modelo **qué hay en la base**. ¿Qué cuenta ese «contexto»? La guía de Google para agentes de datos de BigQuery lista varios elementos. **Descripciones** de cada tabla y de cada columna, **en lenguaje de negocio**: no «col_7», sino «monto realmente ejecutado en el trimestre». **Sinónimos y etiquetas:** las palabras con que la gente nombra las cosas («gasto», «egreso»). **Relaciones entre tablas:** cómo se unen. **Un glosario** del negocio: qué significa «ejecutado» o «exceso». Y **consultas de ejemplo:** pares de pregunta y SQL que muestran cómo se resuelve algo típico."
> 🎤 "Añadimos uno que **no** aparece como campo en esa guía y que es práctica nuestra: los **valores exactos** de las columnas de texto. Si la columna `categoria` guarda «Consultoria» sin acento, el catálogo lo dice, para que el modelo lo **copie** en el filtro en lugar de adivinar. Si escribe «Consultoría» con acento, para la base es **otro valor**: la consulta no falla, **devuelve 0 filas**, y parece que simplemente no hay datos."
> 🎤 "Una última idea: **el contexto ayuda, pero no sustituye** a la validación ni al permiso de solo lectura. Es lo que sigue en el módulo."
> 💡 La página de Google menciona valores de ejemplo en su introducción, pero no muestra un campo para ellos: dilo así. Y es una guía para **sus** agentes de datos de BigQuery; la usamos como referencia de qué contexto conviene, no la usamos tal cual.
> ⚠️ *«¿Hay que hacer todo esto desde el principio?»* → "No: una forma razonable de empezar son las descripciones de negocio y los valores exactos; lo demás se añade cuando haga falta."

**Diap. 11 · ¿Todo el esquema o solo una parte?**
> 🎤 "Tenemos el contexto. Ahora, **¿cuánto de él le damos al modelo en cada pregunta?** Hay tres caminos. **Uno: todo en el prompt:** se manda el catálogo completo con cada pregunta. Es lo más simple y sirve cuando hay pocas tablas y son claramente distintas; su costo es que se pagan tokens en **cada** pregunta y, si el catálogo crece, el modelo se distrae. **Dos: solo lo relevante,** con RAG de metadata: cada tabla es un fragmento y se buscan las más parecidas a la pregunta. Conviene cuando hay muchas tablas o se parecen; el riesgo es que, si la búsqueda falla, el modelo **no ve** la tabla correcta. **Tres: una herramienta ya hecha,** como `search_catalog` del `BigQueryToolset` de ADK, que busca tablas con lenguaje natural usando Dataplex. **No la probamos.**"
> 🎤 "¿A partir de cuántas tablas conviene la opción dos? **No hay un número mágico.** Se decide **midiendo** dos cosas: cuánto cuesta mandar todo, y qué tan parecidas son las tablas. Eso es lo que hicimos con nuestro catálogo (diap. 15)."
> 💡 Un token es la unidad con la que el modelo cuenta el texto (aprox. 4 caracteres): más tokens, más costo y más espacio ocupado.
> ❓ ¿Qué tendría que pasar en su base para que «mandar todo» deje de funcionar?
> ⚠️ *«¿Entonces con 22 tablas basta mandar todo?»* → "A esa escala el tamaño no duele (medimos unos 2,100 tokens). Lo que nos costó fue que las tablas **se parecen**; lo vemos en la diap. 15."

**Diap. 12 · Cómo escribir un catálogo de datos**
> 🎤 "Un **catálogo de datos** es el diccionario de la base: por tabla, qué contiene; por columna, qué significa. Para usarlo con RAG, aplicamos la idea del Módulo 2: **cada tabla es un fragmento**, con su descripción y cada columna con la suya. Así se puede buscar **por significado**: una pregunta sobre «cuánto gastamos» encuentra la tabla de gastos aunque no tenga esa palabra."
> 🎤 "Cuatro reglas para escribirlo. **Descripciones de negocio,** no solo nombres técnicos: qué es la tabla, para qué se usa y, sobre todo, **en qué se distingue de las que se le parecen**. Un ejemplo real de nuestro catálogo: `presupuesto` dice «sirve para saber si una división excedió su presupuesto **en el año en curso**»; `presupuesto_historico` dice «presupuesto y ejecución **anual de años cerrados**; no incluye 2026: para el año en curso usar `presupuesto`». Dos tablas parecidas, **una frase que las separa**. **Valores exactos** en las columnas de texto. **Las palabras de la gente,** como sinónimos. Y **mantenlo como cualquier dato:** en nuestro ejemplo vive en una tabla propia, `catalogo_datos`."
> 🛠 Muestra el fragmento de `presupuesto` (notebook, celda 1.1). Anuncia el **TODO 1** de la práctica: ellos escribirán cómo se arma el texto de cada fragmento.
> 💡 La calidad de este sistema **se decide al escribir el catálogo**, no al elegir un modelo más grande.

**Diap. 13 · Dos etapas y un umbral**
> 🎤 "Es **el mismo flujo del Módulo 2**, ahora sobre tablas. **Etapa 1:** una búsqueda rápida **por significado** (con *embeddings*: se convierte cada texto en una lista de números que representa su significado, y los significados parecidos quedan cerca) que trae **K** candidatas. **Etapa 2:** el *reranking*, con un servicio de Google llamado Ranking API: un modelo más fino que **lee la pregunta junto con cada candidata y las reordena**; nos quedamos con **N**. Y un **umbral**: una nota mínima. Si ninguna tabla la alcanza, **el agente no recibe tablas** y debe decir que no encontró; no inventa."
> 🎤 "Cómo elegir cada uno, en general. **K:** más que N, pero no todo el catálogo; el reranking solo trabaja sobre esas candidatas. **N:** pocas, para que el modelo no se confunda. **Umbral:** se **calibra** con preguntas **dentro** y **fuera** del catálogo: se pone entre la nota más alta de lo irrelevante y la más baja de lo relevante."
> ⚠️ *«¿Por qué dos etapas y no una?»* → "La primera es rápida pero gruesa; la segunda es precisa pero más lenta. Se usa la rápida para quedarse con unas pocas y la precisa solo sobre esas."
> ⚠️ La muestra de preguntas fuera del catálogo suele ser **pequeña**: se recalibra si cambia el catálogo. Nuestros números están en la diap. 15.

**Diap. 14 · Elegir las tablas en código**
> 🎤 "Así se ve en código; no hace falta leerlo línea por línea. Cuatro pasos: **uno**, cada tabla se convierte en un texto (su descripción y sus columnas). **Dos**, la etapa 1 trae 8 candidatas. **Tres**, la etapa 2 las reordena y deja 3. **Cuatro**, el umbral: solo pasan las que lo superan. Al agente le llegan **solo esas tablas con sus columnas**, no las 22."
> 🎤 "Y si **ninguna** pasa el umbral, el agente no tiene tablas: **no debe inventar el SQL**."
> 💡 Código abreviado de `src/sqlagent/catalog.py`. En offline usa un buscador de palabras (TF-IDF) y un reranker léxico: sin servicios, para ensayar.

**Diap. 15 · Lo medido: nuestro catálogo** *(medido)*
> 🎤 "Ahora sí, **nuestros números**, con nuestro catálogo de 22 tablas. **Tamaño:** unos 8,400 caracteres, **unos 2,100 tokens**: no es mucho. Un almacén de 500 tablas serían unos **48,000 por pregunta** (es una estimación, no una medición)."
> 🎤 "Pero lo que nos costó fue que las tablas **se parecen**: `presupuesto` y `presupuesto_historico`, `cuentas_por_cobrar` y `pagos_clientes`. Medimos con 11 preguntas, cada una con su tabla correcta, con un buscador sencillo sin servicios de Google: con **solo nombres y tipos de columna, 7 de 11** encuentran su tabla; con **descripciones de negocio, 10 de 11**. Con embeddings y la Ranking API, **11 de 11**: la pregunta «cuánto *pagaron*» ya encuentra la tabla de *pagos*, cosa que el buscador sencillo no lograba."
> 🎤 "**¿De dónde sale el 0.10?** Probamos tres preguntas fuera del catálogo: la nota más alta de lo irrelevante fue **0.024**; la más baja de una tabla correcta fue **0.174**. Pusimos el umbral **en medio: 0.10**."
> ⚠️ La muestra de preguntas irrelevantes es pequeña: se recalibra si cambia el catálogo. *(medido el 3 de noviembre de 2026)*
> ⚠️ *«¿Entonces el tamaño no importa?»* → "A esta escala no duele; a la de un almacén real, sí. Hoy duele la confusión."

**Diap. 16 · Lo que ya ofrece ADK para BigQuery** *(docs)*
> 🎤 "Antes de seguir: **no estamos reinventando nada que Google no tenga**. **BigQuery** es la base de datos de Google Cloud que usaremos hoy (la presento mejor en la diap. 25). ADK trae un **`BigQueryToolset`**, un conjunto de herramientas ya hecho para BigQuery: listar tablas, ejecutar SQL, pronosticar, buscar tablas por lenguaje natural (`search_catalog`, con un servicio llamado Dataplex)… Se pueden impedir las escrituras con `write_mode=WriteMode.BLOCKED`."
> 🎤 "Entonces, ¿por qué construimos las piezas a mano? **Para aprender cómo funciona cada una** y para controlar nosotros los guardrails, los topes y las citas. **En un proyecto real conviene evaluar primero lo que ya existe.**"
> ⚠️ La página solo muestra `BLOCKED`; no lista los otros valores ni el predeterminado. **No probamos el toolset.**

### SQL seguro (0:39–1:03)
**Diap. 17 · Divisor.** *(Sin guion; di: "Ahora, ¿cómo evitamos que el modelo haga daño?".)*

**Diap. 18 · El modelo propone, el sistema dispone**
> 🎤 "El modelo escribe el SQL, y lo que escribe **no siempre es lo que queremos**: puede equivocarse, o alguien puede **pedirle** algo dañino, como borrar una tabla o leer datos que no le corresponden. Por eso la regla es: **el modelo propone; el sistema decide si se ejecuta.**"
> 🎤 "¿Cómo se logra? Con la idea de **defensa en profundidad**: no confiar en una sola barrera, sino poner **varias, independientes**, de modo que si una falla, otra detenga el problema. Es como la seguridad de un edificio: no basta la puerta principal; hay credencial, cámaras y llave en cada oficina. Aquí vemos las dos primeras barreras."
> 🎤 "**Primera: el permiso de la base de datos.** Conectamos al agente con una cuenta de **solo lectura**: puede consultar, pero la base **se niega** a borrar o modificar, **sin importar qué SQL escriba el modelo**. Es como darle a un auditor acceso de consulta al sistema contable, no de edición. **Esta es la barrera más fuerte**, porque la hace cumplir la propia base, no nuestro código."
> 🎤 "**Segunda: los guardrails.** Son revisiones **en código** que leen la consulta **antes** de ejecutarla y la rechazan si no cumple las reglas: por ejemplo, que sea un solo `SELECT` y que use solo tablas permitidas. Sirven como respaldo: aunque el permiso estuviera mal configurado, un `DROP` se detendría aquí. **No sustituyen a la primera barrera; la complementan.**"
> 🎤 "Hay **más barreras**, y las vemos en el siguiente bloque: los **topes** de filas, de bytes y de tiempo, que protegen el **costo** y que una consulta no se quede colgada. Y una aclaración importante: **la instrucción que le damos al modelo («no borres nada») no cuenta como barrera.** Ayuda, pero un modelo no es un candado: puede ignorarla o equivocarse."
> 💡 Defensa en profundidad es el **principio**; las barreras son las **capas**. Los roles que se nombran son los habituales (`db_datareader` en SQL Server, `bigquery.dataViewer` en BigQuery): confírmalos en tu entorno.
> ❓ Si solo tuvieran los guardrails y no el permiso de solo lectura, ¿qué pasaría si alguien encuentra una consulta que el guardrail no prevé?
> ⚠️ En `adk web`, ante «Borra los gastos de Norte» el modelo se negó **por su cuenta**, sin llegar a la herramienta. La prueba del guardrail se hizo aparte (`verificar_bigquery.py`): el `DELETE` quedó bloqueado antes de llegar a BigQuery. *(Dilo así, para no sobrevender el guardrail.)*

**Diap. 19 · Guardrails: qué bloquean**
> 🎤 "Aquí vemos la segunda barrera en acción. Cada fila de la tabla es **una consulta que intentamos** y lo que el guardrail hizo con ella."
> 🎤 "**Pasa:** `SELECT * FROM gastos`. Es un solo `SELECT` sobre una tabla permitida; el sistema además le **añade un límite de 1,000 filas**, por si la tabla fuera enorme. **Se bloquea:** `DROP TABLE`, porque solo se permite leer. **Dos sentencias** pegadas con `;`, un truco clásico: se podría colar una segunda orden detrás de la primera. **Comentarios** (`--`), porque sirven para esconder parte de la consulta. Una **tabla que no está en el catálogo** (`usuarios`). **Otro dataset**, que en BigQuery es otra «carpeta» de datos. `INTO`, que crearía una tabla nueva. Y `OPENROWSET`, una función de SQL Server que puede leer archivos o servidores externos."
> 🎤 "La fila que más enseña es la de la **coma**: `FROM gastos, usuarios`. Un buscador de palabras prohibidas **no la ve**, porque no hay ninguna palabra mala: la coma simplemente **une una segunda tabla**. Nuestra primera versión funcionaba así (con expresiones regulares, que son patrones de texto) y **esa consulta se le escapó**: lo comprobamos corriéndola. Ahora el guardrail **analiza la consulta como lo haría el propio SQL**, con una librería llamada `sqlglot`, y sabe **exactamente qué tablas toca**."
> 💡 *(medido, sin servicios, dialecto BigQuery; notebook Parte 4.)* La lección general: **un guardrail debe entender la consulta, no solo buscar palabras.** Y **no sustituye** al permiso de la base. En la práctica, los alumnos escriben **sus propios ataques** (TODO 3).
> ❓ ¿Qué otro truco se les ocurre para colar una consulta peligrosa?

**Diap. 20 · Un límite de filas por dialecto**
> 🎤 "Un **dialecto** es la forma particular en que cada base escribe SQL, como el español de España y el de México: casi igual, pero con diferencias que **sí rompen** la consulta. Un ejemplo: para decir «dame solo las primeras 1,000 filas», SQLite y BigQuery escriben `LIMIT 1000` **al final**; SQL Server escribe `TOP 1000` **al principio**, y si le pones `LIMIT`, **no lo entiende**."
> 🎤 "**¿Por qué nos importa?** Por tres razones. **Primera:** nuestro guardrail **añade** ese límite a cada consulta como protección. Si lo escribiera con la sintaxis de otra base, la consulta **fallaría**, o el límite no se aplicaría. **Segunda:** el modelo tiene que escribir en el dialecto de la base a la que está conectado, y para eso se lo decimos en su instrucción. **Tercera:** para **revisar** una consulta hay que **entenderla**, y las funciones y la sintaxis cambian de un dialecto a otro. Por ejemplo, `ML.FORECAST` solo existe en BigQuery."
> 🎤 "La solución es que el dialecto sea **un parámetro**: el guardrail recibe cuál es y escribe el límite como corresponde. **Así el mismo código sirve para las tres bases**: si mañana cambian de SQL Server a BigQuery, el agente no se reescribe."
> 🎤 "Una distinción útil: el **tope de filas** protege contra consultas que devuelven **demasiado**; el **tope de bytes** de BigQuery (lo vemos enseguida) protege contra las que **cuestan demasiado**. Son dos problemas distintos."
> 💡 Código: `src/sqlagent/guardrails.py` (parámetro `dialect`). En T-SQL, un `UNION` se envuelve en una subconsulta para poder poner `TOP`.
> ❓ Si el modelo escribe `LIMIT 10` y la base es SQL Server, ¿qué pasa? (Error: no existe en ese dialecto.)

**Diap. 21 · SQL Server Connector: lo que dice la documentación** *(docs)*
> 🎤 "Un **conector** es el código que conecta al agente con una base concreta. **¿Por qué hace falta uno propio?** Porque es el **único lugar por donde pasa cada consulta**, así que ahí se aplican los controles: cuánto esperar, qué hacer con las transacciones, cuántas filas leer. Hablamos de SQL Server porque el cronograma dice «SQL Server o BigQuery» y **muchos equipos de BI trabajan con él**: el patrón se traslada a su caso aunque nuestro entregable corra en BigQuery."
> 🎤 "La documentación del controlador (el ODBC Driver 18) y de la librería `pyodbc` nos da **cinco temas que cuidar**, y cada uno responde a un riesgo."
> 🎤 "**Cifrado:** los datos viajan entre el agente y la base. El Driver 18 los **cifra por defecto**; si el servidor tiene un certificado que no es de confianza, se puede aceptar con `TrustServerCertificate=yes`, **solo en pruebas**, porque desactiva una verificación."
> 🎤 "**Tiempo de conexión:** cuánto esperamos a que el servidor responda al conectar (15 segundos por defecto). Sin él, un servidor caído podría **dejar al agente esperando**."
> 🎤 "**Tiempo por consulta:** cuánto dejamos correr una consulta antes de cortarla. Es **otro parámetro**, distinto del anterior. Sin él, una consulta pesada podría **ocupar la base** y bloquear a otros."
> 🎤 "**Transacciones:** una transacción es un grupo de cambios que **solo se guardan si haces `commit`**. Por defecto no se confirma nada, así que **si nunca confirmamos, cualquier cambio se deshace**: es una protección adicional contra escrituras."
> 🎤 "**Solo lectura:** el controlador menciona opciones (`ApplicationIntent` y un modo de acceso), pero **no comprobamos que SQL Server las haga cumplir**. Por eso la barrera es un **login con permiso de solo lectura** (`db_datareader`): lo vimos en la diap. 18."
> 🎤 "El cronograma pide «transacciones de solo lectura, timeouts y límites de filas»; esta tabla muestra **dónde se cubre cada una**."
> ⚠️ **No tenemos un SQL Server para la clase:** el conector está probado solo con un servidor **simulado**.

**Diap. 22 · El conector de SQL Server en código**
> 🎤 "Es la tabla anterior **hecha código**; no hace falta leerlo línea por línea. Tres cosas. **Una:** al crear el motor se fija el **tiempo de conexión**. **Dos:** cada vez que se abre una conexión se fija el **tiempo por consulta**. **Tres:** al final **no hay `commit`**, de modo que cualquier cambio se deshace. Y la lectura se corta en **1,000 filas**."
> 🎤 "¿Qué logra esto junto? Que **aunque el modelo pida algo raro, el conector lo limita**: no espera para siempre, no deja una consulta eterna y no guarda cambios."
> 💡 Un detalle técnico *(si preguntan)*: se usa `exec_driver_sql` para que un texto como `:x` dentro de la consulta no se interprete como parámetro.
> 💡 Código abreviado de `src/sqlagent/connectors.py`; se instala con `pip install sqlalchemy pyodbc` y el ODBC Driver 18. **No se ejecuta en el curso.**

**Diap. 23 · SQL Server en Google Cloud (cómo sería)** *(docs; consola)*
> 🎤 "¿Y si quisiéramos un SQL Server de verdad? Les muestro **cómo sería**, para que sepan el camino. En Google Cloud se llama **Cloud SQL for SQL Server**: un SQL Server **administrado**, es decir, Google se encarga de las copias de seguridad, las actualizaciones y la infraestructura. Para conectarte desde tu computadora se usa el **Cloud SQL Auth Proxy**, un programa que abre un puerto local (`127.0.0.1:1433`) y **crea un túnel seguro** hasta la instancia, sin tener que autorizar direcciones IP."
> 🎤 "**Lo que decidimos fue no crear una.** La consola ofrece un preset de pruebas (SQL Server 2022 Express, 1 vCPU, 3.75 GB y 10 GB), pero **cobra mientras la instancia exista**, y la prueba gratuita de 30 días que muestra la consola es de MySQL y PostgreSQL, **no de SQL Server**. Para una clase de 30 personas, eso es un costo que no justifica lo que aprenderíamos de más."
> 💡 Los scripts `preparar_sqlserver.py` y `verificar_sqlserver.py` existen y **no se han ejecutado contra un servidor real**. No se encontraron cifras de precio en la documentación consultada: usa la calculadora antes de crear una instancia.
> ⚠️ *«¿Y si mi empresa usa SQL Server?»* → "El patrón es el mismo: cambia el conector y el dialecto; la barrera real sigue siendo el login de solo lectura."

### BigQuery y BigQuery ML (1:03–1:29)
**Diap. 24 · Divisor.** *(Sin guion; di: "Ahora la base que sí usaremos: BigQuery".)*

**Diap. 25 · BigQuery en ADK: el código de la documentación** *(docs)*
> 🎤 "**BigQuery** es la **base de datos analítica de Google Cloud**: guarda tablas muy grandes y las consulta con SQL. Lo que la distingue, para nosotros: en el modelo **por demanda** **cobra según la cantidad de datos que lee cada consulta**, no según el tiempo que tarda. En la siguiente diapositiva vemos por qué eso cambia cómo pensamos las consultas."
> 🎤 "Primero, **lo que Google ya ofrece**. ADK trae un conjunto de herramientas para BigQuery, el `BigQueryToolset`. Este es el código de su página oficial, abreviado. Tres cosas: **se bloquean las escrituras** (`WriteMode.BLOCKED`); se usan las **credenciales de tu sesión de Google Cloud** (las que dejó `gcloud auth application-default login`); y se crea el `BigQueryToolset`, que se le entrega al agente como cualquier otra herramienta. Son pocas líneas para tener un agente que consulta BigQuery."
> 🎤 "**Entonces, ¿por qué no lo usamos?** Para aprender qué hace cada pieza y para controlar nosotros los guardrails, los topes y las citas. En la versión instalada (2.12.0), según su código, el toolset también acepta un tope de bytes y un tope de filas (50 por defecto); lo que **no vimos** en su configuración es una lista de tablas permitidas, que es lo que añade nuestro guardrail."
> 💡 La autenticación admite credenciales predeterminadas, cuenta de servicio, token externo o interactiva en `adk web`; `location` debe coincidir con la del dataset.
> ⚠️ **No probamos el toolset:** lo que dije de su configuración sale de leer el código, no de ejecutarlo.

**Diap. 26 · Cuánto procesa una consulta: dry run y tope** *(docs)*
> 🎤 "**¿Por qué nos importa saber cuánto procesa una consulta?** Porque aquí **la escribe un modelo**, sin que una persona la revise antes. Una consulta de apariencia inocente, como `SELECT *` sobre una tabla enorme, puede leer **terabytes** y costar dinero real; y el modelo no se da cuenta. Con nuestros datos de ejemplo no pasa nada, porque son diminutos, pero **en una base real sí importa**, y con 30 alumnos corriendo consultas, más. Por eso queremos **saber el costo antes de ejecutar** y poner un **freno**."
> 🎤 "Cuatro conceptos, todos del modelo por demanda."
> 🎤 "**Dry run** (ejecución de prueba): le pides a BigQuery que **estime cuántos bytes procesaría, sin ejecutarla y sin cobrarte**. Es una **cota superior**: puede decir más de lo que realmente se factura."
> 🎤 "**Tope de bytes** (`maximum_bytes_billed`): si la estimación **supera tu tope**, la consulta **falla sin cobrar**. Es el freno de seguridad que pone el sistema, aunque el modelo escriba una consulta enorme."
> 🎤 "**Mínimo:** BigQuery factura **al menos 10 MiB** por consulta (y por tabla), aunque lea muy poco. Por eso un tope **menor a 10 MiB no deja pasar ninguna consulta**; lo comprobaremos en la práctica."
> 🎤 "**Cuotas:** un límite **diario** por proyecto o por usuario. Es un tope duro y, según la documentación, en el modelo por demanda es la única forma de limitar el gasto acumulado. Nosotros no lo configuramos."
> 🎤 "Lo medido: nuestra consulta de ejemplo estima **2,649 bytes**, muy por debajo de esos 10 MiB: con estos datos pequeños, el costo es casi nulo."
> 💡 Analogía: es el «esta consulta procesará N bytes» que ven en la esquina del editor de BigQuery. El dry run es **ese número, pero desde código**.
> ❓ Si un modelo escribe `SELECT *` sobre una tabla de 5 TB, ¿quién lo detiene? (El tope de bytes.)
> ⚠️ Esto aplica al modelo **por demanda**. Con otros modelos de precio (por capacidad) el cobro es distinto: consulta la documentación vigente.
> ⚠️ La documentación avisa que en tablas con clustering la cota superior puede hacer fallar una consulta que cabía. Con seguridad por filas, el dry run devuelve 0 bytes.

**Diap. 27 · BigQuery en nuestro conector**
> 🎤 "Así se aplica lo anterior en nuestro conector. **Primero el dry run:** pedimos la estimación y, si supera nuestro tope, **ni siquiera enviamos la consulta**. Si pasa, la enviamos con el tope de BigQuery como **segunda barrera**. Dos topes: **uno nuestro y uno de la plataforma**; así, si uno fallara, el otro protege."
> 🎤 "Dos detalles prácticos. **`default_dataset`** le dice a BigQuery en qué «carpeta» de datos buscar, para que el modelo escriba solo `FROM gastos` y no el nombre largo con proyecto y dataset; además evita que el modelo tenga que adivinar nombres. **`max_results`** limita cuántas filas se leen."
> 💡 Es el mismo principio de la diap. 18, la defensa en profundidad, ahora para el **costo**.
> 🛠 En la práctica, la Parte 5 lo demuestra y deja el **TODO 4**.

**Diap. 28 · BigQuery ML: ARIMA_PLUS y ML.FORECAST** *(docs)*
> 🎤 "**¿Qué es BigQuery ML y para qué lo tenemos?** Es una función de BigQuery que permite **entrenar modelos de machine learning escribiendo SQL**, sin sacar los datos de BigQuery. Tres razones por las que nos interesa. **Una:** los datos ya están ahí, así que **no hay que exportarlos** ni montar otra herramienta. **Dos:** se escribe con SQL, que **un equipo de BI ya domina**. **Tres:** el cronograma del módulo lo incluye. Y una aclaración honesta: **para nuestra pregunta principal no hace falta**; es una capacidad más del agente, que nos sirve para ver que **con SQL también se puede pronosticar**."
> 🎤 "El caso de hoy es un **pronóstico de series de tiempo**: «¿cuánto gastará cada división en los próximos meses?». El modelo se llama **ARIMA_PLUS**. Qué necesita: una columna de **tiempo** (una fecha), una columna **numérica** (lo que se pronostica) y **al menos 3 puntos**. Opcionalmente, una columna que distinga **series** (aquí, la división: un pronóstico para cada una). También le indicas la **frecuencia** de los datos: diaria, mensual, etc. (`DATA_FREQUENCY`); si no la dices, la adivina."
> 🎤 "Se hace en **dos pasos**. `CREATE MODEL` **entrena** el modelo (y ya calcula el pronóstico). Luego `ML.FORECAST` **lo consulta**: pides cuántos periodos (`HORIZON`; 3 por defecto) y un nivel de confianza (0.95), y devuelve el valor esperado **con un intervalo**, es decir, un mínimo y un máximo."
> 🎤 "Existe también `AI.FORECAST`, que usa un modelo **ya entrenado por Google** (TimesFM), sin crear el tuyo."
> ⚠️ La documentación no dice que `AI.FORECAST` sustituya a `ML.FORECAST`.

**Diap. 29 · BigQuery ML en código**
> 🎤 "Es el SQL que corren en el notebook. **Arriba, entrenar:** sumamos el gasto **por mes y por división** y le decimos `MONTHLY` y un horizonte máximo de 6 meses (es lo más lejos que podremos pedir con `ML.FORECAST`). **Abajo, pronosticar:** `ML.FORECAST` con 3 periodos y 90 % de confianza; la respuesta trae el pronóstico y el intervalo (`minimo` y `maximo`)."
> 🎤 "Y noten algo clave: **esto pasa por la misma herramienta `ejecutar_sql`**, así que **también tiene guardrails y tope de bytes**. Es decir, aunque sea machine learning, **no abrimos una puerta lateral**. Para eso el guardrail permite `ML.FORECAST` y cuenta el modelo como una tabla permitida: un modelo ajeno se bloquea."
> 💡 Entrenar cuesta centavos con estos datos; consulta los precios de BigQuery ML.

**Diap. 30 · Lo medido: la frecuencia define el periodo**
> 🎤 "Esto nos sorprendió y vale la pena entenderlo. Entrenamos primero con los gastos **por día** (con fechas irregulares) y pedimos **3 periodos**. Esperábamos tres meses. BigQuery respondió: **1, 4 y 7 de octubre**. ¿Por qué? Porque dedujo que la serie avanza cada unos 3 días, y **un «periodo» es un salto de esa frecuencia**."
> 🎤 "Cuando sumamos el gasto **por mes** y le dijimos `MONTHLY`, los 3 periodos fueron **octubre, noviembre y diciembre**. **La frecuencia de los datos de entrada define qué es un «periodo».** Si no se la damos clara, el pronóstico responde **otra pregunta** de la que queríamos."
> 🎤 "Y una advertencia de honestidad: tenemos solo **9 puntos por serie, y sintéticos**. Por eso los tres meses pronosticados para Centro fueron **149,100, 70,260 y 106,622**: saltan demasiado. Siempre hay que mirar el **intervalo**. Hoy es para aprender el uso, **no para sacar conclusiones del negocio**."
> ❓ Si alguien les pide «el pronóstico a 3 periodos», ¿qué le preguntan antes? (¿Periodos de qué: días, meses, trimestres?)
> ⚠️ *«¿Con más datos sería confiable?»* → "Mejoraría, pero no hay garantía: depende de que la serie tenga patrones. El intervalo es la medida honesta de cuánto confiar."

### El agente híbrido (1:29–1:51)
**Diap. 31 · Divisor.** *(Sin guion; di: "Ahora juntamos todas las piezas".)*

**Diap. 32 · Cinco herramientas**
> 🎤 "Recuerden la diap. 7, ahora con nombres reales. Cada herramienta hace **una sola cosa**: `buscar_esquema` (qué tablas mirar), `ejecutar_sql` (consultar la base), `buscar_informe` (leer el informe), `contrastar_cifras` (comparar) y `buscar_politicas` (leer la política)."
> 🎤 "¿Quién hace cada una? **Tres son RAG:** el catálogo, el informe y la política. **`ejecutar_sql` es código con guardrails** que ejecuta la consulta en la base. Y **`contrastar_cifras` es código que compara**: no lo hace el modelo."
> 🎤 "¿Quién dirige el orden? La **instrucción** del agente: un texto que le dice qué hacer y cuándo. Sus reglas más importantes:"
> - Filtrar el SQL con **la misma división y el mismo periodo que el informe**.
> - Usar los **valores exactos** del catálogo.
> - Si salen 0 filas, **reintentar una vez** y **no rellenar** con otra fuente.
> - **Comparar la misma magnitud.**
> - **No decir que algo no existe** sin haber buscado.
> - **Negarse** a temas ajenos a las finanzas.
> ⚠️ **Es una instrucción, no una garantía:** el modelo no es determinista (puede responder distinto a la misma pregunta). Por eso en la diap. 36 mostramos lo que vimos al probarlo.

**Diap. 33 · Antes de comparar: misma magnitud, misma unidad**
> 🎤 "**Contrastar** es poner lado a lado la cifra de la base y la del informe. Y la regla general es esta: **antes de comparar dos cifras, pregunten si miden lo mismo y si están en la misma unidad.**"
> 🎤 "**¿Miden lo mismo?** La misma división, el mismo periodo y la misma versión: presupuesto **original** o **aprobado**. **¿Están en la misma unidad?** Un ejemplo: el 10-Q del Módulo 2, que es **otro documento**, venía en **miles de USD**, y la base está en **USD**. Sin ajustar la escala (`escala_informe=1000`), 2,880 contra 2,880,000 «difiere» en 99,900 %. Una comparación perfecta de dos cosas distintas **sigue siendo un error**."
> 🎤 "Veámoslo con **nuestros datos**, que tienen **dos discrepancias a propósito**. **Marketing:** la base dice 56,000 y el informe 52,000; la Nota 1 del informe explica que el presupuesto se **redujo por una reasignación**. **Servicios:** la base, 71,400; el informe, 69,900. **Consultoría coincide:** 78,000 contra 78,000. Y en **Tecnología** la base no se consultó en este ejemplo, así que **no hay con qué comparar** el 57,750 del informe: el estado es «sin contraparte»."
> ❓ ¿Qué pasa si comparamos el presupuesto **original** con el **aprobado**? (Desaparece una diferencia que importa: justamente la del caso de Marketing.)

**Diap. 34 · Comparar con una regla fija: el código**
> 🎤 "Aquí está la función. No hace falta entender cada línea; la idea: el modelo **lee las cifras** (la del SQL y la del informe) y se las pasa a la función **con el mismo nombre** (por ejemplo, `marketing_presupuesto`). La función calcula la **diferencia porcentual respecto a la cifra del informe** y devuelve «coincide» si está dentro de la tolerancia (**1 % por defecto**) y «difiere» si no. Si una cifra no tiene pareja, dice «sin contraparte»."
> 🎤 "¿Por qué en código? Porque así «coincide» o «difiere» **no depende de que el modelo haga bien una resta**. Con las mismas cifras, **siempre da el mismo resultado**."
> 💡 Código abreviado de `contrastar_cifras` en `src/sqlagent/agent.py`.

**Diap. 35 · Los documentos desde RAG Engine**
> 🎤 "¿De dónde lee el agente los documentos? De **RAG Engine**, el servicio del Módulo 2. Cuatro ideas generales:"
> - **Un corpus por tipo de documento.** Las **políticas** (el mismo corpus del Módulo 2; si lo borraron en la limpieza, `preparar_rag.py` lo recrea) y el **informe** (un corpus aparte) van **separados**, para que las fuentes no se tapen entre sí.
> - **Un documento corto cabe en un solo fragmento:** la cita dice «fragmento 1», no una sección.
> - **Cada corpus tiene su umbral**, calibrado aparte. Para el informe, lo irrelevante llegó hasta **0.019** y lo relevante bajó hasta **0.201**; el umbral es **0.10**, entre los dos.
> - **Citas gruesas:** si el PDF entra entero, la cita es el documento completo y el **modelo decide** qué artículo aplica. Es el problema del Módulo 2. En nuestras políticas pasa así: las citas traen los Arts. 2.1 a 2.4 juntos y el modelo eligió el 2.3 leyendo el texto.
> 🎤 "Si el servicio no está disponible, hay un **respaldo**: los mismos documentos en markdown (`AUDITOR_FUENTE` e `INFORME_FUENTE`)."

**Diap. 36 · Qué falló en nuestras pruebas y cómo se previene** *(medido; pocas corridas por pregunta, repetidas en varias rondas de prueba)*
> 🎤 "`adk web` es la interfaz de chat de ADK. Ahí probamos el agente con **Gemini real**, el catálogo, el informe y las políticas desde RAG Engine. Fueron **pocas corridas**, no una medición estadística. En la tabla, cada fila dice **qué falló, por qué pasa en general y cómo lo previene el sistema**. Lo más importante es la columna del medio: **son fallos que cualquier agente de este tipo puede tener**. Recorramos las seis:"
> - **Un valor con acento.** El modelo escribió «Consultoría» y la base guarda «Consultoria»: 0 filas. Lo previene el catálogo con valores exactos y reintentar **una** vez.
> - **Rellenó con el informe.** Al ver 0 filas, completó los datos con cifras del informe y calculó el 60 % por su cuenta. Regla: **nunca rellenar** con otra fuente.
> - **Cita cortada.** Un tope de 1,200 caracteres, heredado del Módulo 2, le quitó la frase de la aprobación. Subimos el tope.
> - **Pregunta ambigua.** «El presupuesto de Marketing» sin división sumó todo el año (738,000). La instrucción exige el mismo alcance que el informe.
> - **Original contra aprobado.** A veces comparó el presupuesto original con el aprobado. Se pide la misma magnitud: la vigente.
> - **Sin buscar.** Una vez dijo «no se encontró» **sin haber buscado**, y otra respondió una pregunta ajena a las finanzas (una receta de paella). Reglas: buscar antes de afirmar, y de alcance.
> 💡 Moraleja para BI: **una corrida correcta no es una garantía**; hay que verificar varias veces y **leer el texto**, no solo mirar que «suene bien». No se midió la frecuencia de cada fallo. Cada uno terminó como una regla en la instrucción, una prueba automática o un cambio en el código. La evaluación formal (fidelidad, recall de contexto) es del Módulo 5.
> ❓ Si una pregunta ambigua cambia el SQL, ¿cómo evitarían que pase? (Preguntar la división, o fijar el alcance en la instrucción.)

**Diap. 37 · Cómo armar el tuyo**
> 🎤 "Lo que vimos hoy sirve para **sus propias bases y documentos**. El orden que recomendamos: **uno,** escriban un **catálogo** con descripciones de negocio y valores exactos. **Dos,** empiecen con un **conector de solo lectura** y un rol de solo lectura. **Tres,** pongan **guardrails** (un solo `SELECT`, tablas permitidas, tope de filas) y topes de bytes si usan BigQuery. **Cuatro,** calibren el **umbral** con preguntas dentro y fuera del catálogo. **Cinco,** hagan que la **comparación de cifras sea código**, con la misma magnitud y la misma unidad. **Seis,** **verifiquen** con casos y repítanlos: el modelo no es determinista."
> 💡 Cada paso corresponde a un bloque de hoy: catálogo (bloque 2), conector y guardrails (bloque 3), topes de bytes (bloque 4), comparación y verificación (bloque 5). Es la misma lista de la sección 9.3 de esta guía.
> ❓ De esos seis pasos, ¿cuál es el primero que harían con **su** base?

### Cierre (1:51–2:00)
**Diap. 38 · Lo que debe quedarse**
> 🎤 "Cinco ideas. **1:** lo cuantitativo viene del SQL, lo normativo de RAG, y el modelo no calcula. **2:** elegir tablas con RAG: las descripciones de negocio deciden la calidad. **3:** el modelo propone, el sistema dispone: el permiso de la base es la barrera real. **4:** BigQuery cobra por bytes: dry run, tope y el mínimo de 10 MiB; y la frecuencia define el periodo del pronóstico. **5:** misma magnitud, misma unidad, y verificar: el modelo no es determinista."
> 🛠 Pide a cada célula que cuente **una** de las cinco ideas con sus palabras.

**Diap. 39 · Proyecto base y siguiente paso**
> 🎤 "Proyecto base: `src/sqlagent` (la librería con el catálogo, los guardrails, los conectores, el informe y el contraste), `src/sql_app` (el paquete para abrirlo en `adk web`) y los scripts. La práctica es un **notebook guiado** y **al final se borran los recursos** de la nube. **Semana 6:** el agente de datos y el de RAG se conectan al supervisor por A2A."
> 🛠 Deja la Parte 0 del notebook hecha (`preparar_bigquery.py` y `preparar_rag.py`) para no perder los primeros minutos en problemas de entorno.

**Diap. 40 · Preguntas y respuestas** *(frases de rescate: sección 6)*

---
## 6. Frases de rescate y orden de recortes
**Si te quedas en blanco, di esto:**
- "¿Qué pasaría si le preguntamos esto a un modelo **sin** acceso a la base de datos? Respondería algo que suena bien. Por eso las cifras vienen de la base, con SQL."
- "Miren **dos tablas parecidas** de nuestro catálogo: ¿cómo sabría un modelo cuál usar? Por la **descripción de negocio**."
- "El **permiso de la base** es la barrera; el prompt, no."
- "BigQuery cobra por **cuántos datos lee** cada consulta. ¿Cuántos leería esta? Se estima **antes de ejecutarla** con el *dry run*."
- "Si les piden «el pronóstico a 3 periodos», ¿periodos de qué? Depende de **cada cuánto** vienen los datos: días, meses…"
- "Esa cifra del informe, ¿es **la misma magnitud** y **la misma unidad** que la del SQL?"
- "Corrimos esto varias veces y **no siempre dio lo mismo**: por eso verificamos."

**Recortes si vas justa** (de lo que menos daña): 29 (código de BigQuery ML) → 25 (código de ADK) → 22 (código de SQL Server) → 34 (código de `contrastar_cifras`) → 14 (código del catálogo) → 16 → 23.
**Qué protege el mensaje (no las recortes):** 2, 5, 6, 7, 9, 10, 13, 15, 18, 19, 26, 30, 33, 36, 37.

## 7. Errores comunes y preguntas de repaso
**Errores comunes del grupo**
- Creer que **un modelo puede sumar** («lo dijo con seguridad»): la cifra viene del SQL.
- Pensar que **el prompt protege** («le dije que no borre»): el permiso de la base protege.
- Confiar en una **expresión regular** como único guardrail (la unión con coma).
- No ver que **dos cifras no son comparables** (original frente a aprobado; USD frente a miles).
- Esperar que un tope de bytes **menor a 10 MiB** deje pasar algo.
- Tomar el **pronóstico** (con 9 puntos sintéticos) como una conclusión.
- Dar por buena **una** corrida del agente.

**Preguntas de repaso** (con la respuesta corta, para cerrar o para la tutoría)
1. ¿Por qué el SQL y no el modelo calcula el total de Consultoría? → La base suma de forma exacta y repetible; el modelo predice texto y puede equivocarse con seguridad.
2. ¿Qué diferencia hay entre el problema de 3 tablas y el de 22? → Con 3 se pegan en el prompt; con 22 (o cientos) hay que elegir cuáles mostrar, y las parecidas se confunden.
3. ¿Qué cambió entre 7 de 11 y 10 de 11? ¿Qué lección es? → Se agregaron descripciones de negocio al catálogo: la calidad se decide al escribirlo.
4. ¿Cómo se eligió el umbral del catálogo y qué limitación tiene? → En medio de lo irrelevante (hasta 0.024) y lo relevante (desde 0.174); se calibró con solo 3 preguntas fuera del catálogo.
5. ¿Qué barrera es la «real» y cuál la «segunda»? → Real: el permiso de solo lectura de la base. Segunda: los guardrails.
6. ¿Qué hace el dry run y qué hace `maximum_bytes_billed`? ¿Por qué un tope de 5,000 bytes no deja pasar nada? → El dry run estima sin ejecutar ni cobrar; el tope hace fallar sin cobrar lo que lo supere. BigQuery factura mínimo 10 MiB, y 5,000 bytes está por debajo.
7. ¿Por qué los «3 periodos» eran unos 9 días la primera vez? → Los datos eran diarios e irregulares, BigQuery dedujo unos 3 días, y un periodo es un salto de esa frecuencia.
8. ¿Por qué `contrastar_cifras` es código? → Para que «coincide» o «difiere» no dependa de que el modelo reste bien y dé siempre lo mismo con las mismas entradas.
9. Una pregunta dice «el presupuesto de Marketing» sin división: ¿qué puede salir mal? → El modelo puede sumar todo el año o todas las divisiones y comparar contra una cifra de otra cosa.

## 8. Lo que no está probado (sé transparente con el grupo)
- **SQL Server real:** el conector se probó solo con un servidor **simulado**; `preparar_sqlserver.py` y `verificar_sqlserver.py` nunca se ejecutaron contra uno.
- **`BigQueryToolset` de ADK:** su código es el de la documentación; no lo probamos.
- **Que `ApplicationIntent` o el modo de acceso de ODBC hagan cumplir «solo lectura»** en SQL Server.
- **El notebook completo de arriba abajo** (las celdas 🟢 sí; las 💸 no) y la celda 5.2 (el tope de BigQuery rechazando).
- **30 alumnos a la vez**, los **permisos mínimos** y los **tiempos** de cada parte.
- **La frecuencia con la que el agente se equivoca:** se vieron corridas sueltas, no una medición.
- **El umbral del catálogo** se calibró con 3 preguntas irrelevantes; el del informe, con 4.
- **Región:** el dataset está en `US`; no se probó otra.
- **Precios:** no se dan cifras de costo; consulta la documentación vigente.
- **Este guion:** la redacción explicativa de la sección 5 no se ha ensayado en voz alta; los tiempos de cada bloque son estimados.

## 9. Mapa del proyecto
### 9.1 Qué es cada archivo y si lo necesitas
| Archivo | Qué es | ¿Lo necesitan los alumnos? |
|---|---|---|
| `src/sqlagent/catalog.py` | RAG de metadata: elegir tablas (K = 8, N = 3, umbral 0.10) | Sí |
| `src/sqlagent/guardrails.py` | Validación del SQL con `sqlglot`, por dialecto | Sí |
| `src/sqlagent/connectors.py` | SQLite, SQL Server y BigQuery; `BQML_EXAMPLE` | Sí |
| `src/sqlagent/informe.py` | Búsqueda en el informe (markdown o RAG Engine) | Sí |
| `src/sqlagent/politicas.py` | Búsqueda en las políticas (markdown o RAG Engine) | Sí |
| `src/sqlagent/agent.py` | `ejecutar_sql`, `contrastar_cifras` y el agente | Sí |
| `src/sqlagent/dwh.py` | De dónde salen los esquemas y CSV de las 22 tablas (*dwh* = almacén de datos) | Sí (lo usan los scripts) |
| `src/sql_app/` | Paquete para `adk web` | Sí |
| `preparar_bigquery.py` · `verificar_bigquery.py` | Crear el dataset y comprobarlo | Sí |
| `preparar_rag.py` | Corpus de políticas e informe en RAG Engine | Sí (opcional: respaldo en markdown) |
| `probar_catalogo.py` · `probar_informe.py` | Medir puntajes para calibrar umbrales | Opcional |
| `preparar_sqlserver.py` · `verificar_sqlserver.py` | SQL Server real | **No** (sin verificar) |
| `tests/test_modulo3.py` | 79 pruebas, sin servicios | **No** (no van en el ZIP) |
| `data/seed_dwh.py` · `data/dwh/` | Generan y guardan las 19 tablas nuevas | Sí (los CSV) |
| `data/informes/` | El informe de presupuesto (`.md` y `.pdf`) | Sí |

### 9.2 De dónde lee el agente (las decisiones que cambian)
Se controlan con variables del archivo `.env`; `AGENTS_MODE` = `offline` (todo local, sin servicios) o `cloud` (servicios de Google).
- **Base de datos:** `SQL_BACKEND` = `sqlite` (sin servicios), `sqlserver` o `bigquery` (por defecto en `cloud`).
- **Políticas:** `AUDITOR_FUENTE` = `politicas` (markdown) o `rag_engine` (con `RAG_CORPUS_POLITICAS`).
- **Informe:** `INFORME_FUENTE` = `markdown` o `rag_engine` (con `RAG_CORPUS_INFORMES`).
- **Umbrales:** `UMBRAL_CATALOGO`, `UMBRAL_INFORME` y `UMBRAL_AUDITOR`, si quieres sobrescribir los calibrados.

### 9.3 Para armar uno propio: el orden recomendado
1. Escribe un **catálogo** con descripciones de negocio y **valores exactos**.
2. Empieza con **un conector de solo lectura** y un rol de solo lectura.
3. Pon **guardrails** (un solo `SELECT`, tablas permitidas, tope de filas) y **topes de bytes**.
4. Calibra el **umbral** con preguntas dentro y fuera del catálogo.
5. Haz que la **comparación de cifras sea código**.
6. **Verifica** con casos y repítelos: el modelo no es determinista.

### 9.4 Qué sigue
**Semana 6 (capstone):** el agente de datos y el de RAG como subagentes de un supervisor por A2A. **Módulo 4:** modelos de ML internos y Tableau. **Módulo 5:** evaluación formal de RAG (fidelidad y recall de contexto), observabilidad y CI/CD.
