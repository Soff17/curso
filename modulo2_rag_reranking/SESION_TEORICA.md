# Módulo 2 · SESIÓN TEÓRICA (2 h) — Guía del instructor

**Tema:** RAG Engine y reranking: la plataforma, su anatomía, y cómo leer, cortar, indexar, recuperar en dos etapas y decir «no sé» · **Público:** Equipo de BI (30 personas, 5 células) · **Semana 2**
La práctica con el notebook tiene su propia guía: **`SESION_PRACTICA.md`**. Los comandos para los alumnos están en **`COMANDOS.md`**.
Lo que depende de servicios reales (Gemini, embeddings, Ranking API, RAG Engine) pruébalo tú antes de la clase: ver sección 4.

**Presentación que acompaña esta guía:** `Modulo 2 - RAG y Reranking.pptx` (**44 diapositivas**, con el mismo diseño que la del Módulo 1; las notas del orador de cada diapositiva traen los datos clave y de qué página de la documentación salen). Esta guía es tu **guion**: lo que dices, por qué, qué preguntar y qué responder.
**Cómo está armada:** igual que la del Módulo 1, primero **lo general de la documentación** (qué es RAG Engine, modos, fuentes, documentos, transformación, guía de inicio) y después **nuestro caso**, con lo que medimos. Lo marcado *(docs)* viene de la documentación; lo marcado *(medido)*, de las corridas de este proyecto.

**Contenido de esta guía:** 1. Antes de la clase · 2. Mensajes clave · 3. Línea de tiempo · 4. Ensayo previo de las demos · 5. Guion por diapositiva · 6. Frases de rescate y recortes · 7. Errores comunes y preguntas de repaso · 8. Lo que no está probado · **9. Mapa del proyecto y cómo armar tu propio RAG**.

---
## 1. Antes de la clase (haz esto el día anterior)
- [ ] `. .\env.ps1` y `python -m pytest modulo2_rag_reranking -q` → **44 passed** (todo el repositorio: 98; ninguna llama a servicios, aunque tu `.env` diga `cloud`). *(Verificado.)*
- [ ] Los comandos «sin servicios» de la sección 4 funcionan (🟢). Los que usan servicios (💸) cuestan centavos: pruébalos **una vez**.
- [ ] Proyecto con las **4 APIs** (Vertex AI, Discovery Engine, Vector Search, Cloud Resource Manager) y **RAG Engine en modo sin servidores**. La región que usamos es **`us-central1`** (ver la nota de la diap. 33 sobre las regiones). Detalle en `SESION_PRACTICA.md` y `COMANDOS.md`, paso 3.
- [ ] **Comprueba el modo del proyecto**: el predeterminado de RAG Engine es **Spanner** *(docs)*, que se cobra. La celda 2.1 del notebook debe decir `modo SIN SERVIDORES ✅`.
- [ ] Consola abierta en **RAG Engine → Corpus** (para enseñar que hay colecciones reales detrás) y, si quieres, en **Vector Search**.
- [ ] Un PDF escaneado a la mano (`data/politicas_pdf/AUD-2026.pdf`) y el mismo texto como PDF con texto (`POL-VIA-2026.pdf`) para la demo de «el escaneo es una foto».
- [ ] Alumnos con el entorno listo (`COMANDOS.md`, pasos 1 a 6).
- [ ] **Si harás la demo de `adk web`** al final: `preparar_corpus.py` ya ejecutado y el `.env` con `AGENTS_MODE=cloud`, `AUDITOR_FUENTE=rag_engine`, `RAG_CORPUS_POLITICAS=...`; o, más simple, sin nada de eso (modo `offline`, con búsqueda local y Gemini real).
- [ ] Recuerda **borrar** lo que crees: `python modulo2_rag_reranking/preparar_corpus.py --limpiar`.

## 2. Mensajes clave (las ideas que deben llevarse)
1. **El modelo no sabe lo de tu empresa, y si no sabe, inventa.** RAG = darle los documentos correctos **en el momento de preguntar**, y obligarlo a citarlos.
2. **Un RAG se rompe antes de la búsqueda:** si el documento no se **leyó** bien o se **cortó** mal, ninguna búsqueda lo rescata. Leer y cortar son decisiones de diseño y **se miden**.
3. **Dos etapas:** buscar **muchos** rápido (K = 20) y **reordenar** pocos con un modelo que lee pregunta y fragmento juntos (N = 3). El reranking limita el contexto: menos costo y menos ruido.
4. **Un buen auditor sabe decir «no sé»:** el **umbral** de relevancia convierte «no hay evidencia» en **ESCALAR**, no en una respuesta inventada.
5. **El modelo propone, el código decide, y la herramienta es la fuente:** las citas vienen de la herramienta, no de la memoria del modelo.

## 3. Línea de tiempo
Coincide con los bloques de la presentación (los minutos suman 120). **Es una propuesta sin ensayar:** 44 diapositivas son muchas (siete son divisores y varias son tablas); ver la sección 6 para recortar.

| Hora | Min | Bloque | Diap. | Qué muestras |
|---|---|---|---|---|
| 0:00–0:05 | 5 | Apertura: el caso y el entregable | 1–3 | El auditor y su pregunta clave: ¿aprobar o rechazar este gasto? |
| 0:05–0:17 | 12 | Por qué RAG y qué es RAG Engine | 4–8 | Lo que el modelo no sabe; el flujo oficial de RAG Engine |
| 0:17–0:43 | 26 | RAG Engine: la plataforma y su anatomía | 9–21 | Modos, fuentes, documentos, analizadores, transformación; el código del quickstart, lo que cambiamos y qué hace RAG Engine frente a nosotros |
| 0:43–1:05 | 22 | Leer y cortar, con nuestro caso | 22–30 | PDF con texto frente a escaneo; tres formas de chunking; el Art. 1.3 y su excepción |
| 1:05–1:15 | 10 | Embeddings y Vector Search | 31–33 | Consola de RAG Engine; vectores de 768 números |
| 1:15–1:31 | 16 | Dos etapas y reranking (K = 20 → N = 3) | 34–37 | Caso de la cena; 84 % menos de contexto |
| 1:31–1:45 | 14 | Umbral, el «no sé» y el auditor en código | 38–40 | El yate: 0.032 contra 0.202; el código del auditor |
| 1:45–1:51 | 6 | Qué sale mal en un RAG | 41 | Pérdida silenciosa, reformulación, citas gruesas |
| 1:51–2:00 | 9 | Cierre | 42–44 | 5 ideas + abrir el notebook (Parte 0) |

## 4. Ensayo previo de las demos (hazlo tú antes; esto es lo que debes ver)
Terminal en la raíz del proyecto, con el entorno activado y `. .\env.ps1`. **🟢 no usa servicios · 💸 usa servicios (centavos).**

| Demo | Comando / acción | Debes ver | |
|---|---|---|---|
| Chunking por artículo | `python -c "from rag.chunking import load_corpus; from shared.config import POLICIES_DIR; c=load_corpus(POLICIES_DIR); print(len(c), c[0].id)"` | `20 AUD-2026#5.1` | 🟢 |
| Corte por estructura | `python -c "from rag.chunking import split_by_structure; t='Politica (POL-VIA-2026)\n## Articulo 1.1 - Alcance\nAplica a todos.\n## Articulo 1.2 - Limites\nUSD 150 por dia.'; print(len(split_by_structure(t)))"` | `3` (el encabezado y 2 artículos) | 🟢 |
| Dos etapas (con reranker léxico de ejemplo) | `python modulo2_rag_reranking/compare_rerank.py` | `Hit@3 sin rerank: 5/6   con rerank: 6/6` | 🟢 |
| Herramienta del auditor (offline) | `python -c "from rag.auditor import buscar_politicas as b; print([c['citation'] for c in b('viaje internacional sin autorización previa')['citations']])"` | `POL-VIA-2026, Art. 1.3 (Autorización previa)` primero | 🟢 |
| Agente | `python -c "import auditor_rag_app.agent as a; print(a.root_agent.name, a.root_agent.tools[0].__name__)"` | `auditor_politicas buscar_politicas` | 🟢 |
| El escaneo es una foto | Abre `data/politicas_pdf/AUD-2026.pdf` e intenta seleccionar texto | No se puede seleccionar nada | 🟢 |
| Modo de RAG Engine del proyecto | Notebook del instructor, celda 2.1 (solo lectura) | `modo SIN SERVIDORES ✅` | 🟢 |
| Lectura por analizador | Notebook del instructor, Parte 2 (celdas 2.6 y 2.7) | Escaneado: **0 fragmentos** con el analizador por defecto y ✅ con el de LLM | 💸 |
| Tres formas de chunking | Notebook, Parte 3 (celdas 3.2, 3.3 y 3.5) | A: 5 fragmentos / 4.0 arts.; B: 14 / 1.5; C: 20 / 1.1; Hit@3 6/6 en las tres | 💸 |
| Reranking que cambia el top-3 | Notebook, celda 5.2 («una cena a un proveedor y no tengo factura») | El tercer lugar cambia (Art. 5.1 de auditoría → Art. 4.2 de provisión) | 💸 |
| Ventana de contexto | Notebook, celda 5.4 | **1,052 → 173 tokens (84 % menos)** | 💸 |
| Umbral | Notebook, celda 6.1 | Irrelevantes ≤ 0.032; relevantes ≥ 0.202; umbral 0.12 | 💸 |
| Auditor en `adk web` | `adk web --port 8501 modulo2_rag_reranking/src` → `auditor_rag_app` → «Compra de un yate para la dirección» | **ESCALAR** con `articulos_citados: []` | 💸 |
| Auditor, caso con citas | La misma app → «Viaje internacional de 4 días, USD 2,400 total, sin autorización previa del Director» | **RECHAZADO**, Art. 1.3 *(verificado el 2026-10-20)* | 💸 |

> **El código del quickstart (diap. 17 y 18) no se ejecuta en la clase.** Es el de la guía de inicio de la documentación, abreviado; en nuestras pruebas, **tal cual no funcionó** (ver diap. 19).

> **Nota:** los puntajes, los conteos de fragmentos y hasta los cortes pueden variar entre corridas (el analizador, el reranker y Gemini son modelos). **Qué cambió en la prueba de un alumno frente a la del instructor:** el 10-Q quedó en 3 fragmentos en vez de 4; el corte semántico (B) dejó el Art. 1.3 junto al 1.4; en la Parte 9 la pregunta mixta dio `ESCALAR` en lugar de `RECHAZADO` y las cuotas no cambiaron el reparto. Lo que no debe variar: el escaneo da 0 con el analizador por defecto, el yate escala, y el Art. 1.3 aparece en el viaje sin autorización.

---
## 5. Guion por diapositiva (44 diapositivas)
**Cómo leerlo:** **🛠** = qué haces · **🎤** = qué decir · **💡** = por qué se hace así · **❓** = pregunta para el grupo · **⚠️** = dudas probables y cómo responderlas.
**Tono:** el público es BI: conocen SQL, modelos de datos y tableros. Ancla cada concepto a algo que ya conocen (índices, vistas, calidad de datos, ETL).
**Fuentes:** lo marcado *(docs)* viene de la documentación de Google Cloud (descripción general, modos de implementación, ingesta de datos, documentos admitidos, transformaciones de fragmentación, Layout Parser, analizador de LLM y la guía de inicio): dilo como «según la documentación» y confirma el dato vigente antes de usarlo como cifra. Lo marcado *(medido)* salió de las corridas de este proyecto.

---
### Apertura (0:00–0:05)

**Diap. 1 · Portada**
> "Bienvenidos al Módulo 2. En el primero construimos agentes que usan **herramientas**. Hoy les damos algo que **ningún modelo trae de fábrica**: los **documentos de su empresa**. Primero veremos **RAG Engine**, la pieza de la plataforma que lo hace posible, y luego construiremos un **auditor de políticas financieras** que justifica cada decisión **citando la norma**."

**Diap. 2 · El caso: ¿se aprueba este gasto?**
> "Un empleado pide un viaje internacional de USD 2,400 sin autorización previa del Director. ¿Se aprueba? Un analista abriría el PDF de la política de viáticos, buscaría el artículo, vería que el 1.3 exige autorización y rechazaría **citando el artículo**. Eso mismo tiene que hacer el agente. Con una condición que va a repetirse hoy: **si no encuentra una norma que aplique, no inventa: escala a una persona**."

💡 El caso hace evidentes los dos requisitos del auditor: **citar** y **no inventar**.
❓ "¿Qué pasa hoy cuando alguien pregunta por una política y nadie recuerda el artículo?" *(Se pierde tiempo, se interpreta mal, o se contesta de memoria. Eso mismo hace un modelo sin documentos.)*

**Diap. 3 · Agenda y entregable**
> "Dos horas y nueve bloques: por qué RAG y qué es RAG Engine; la plataforma y su anatomía; cómo se **leen** y se **cortan** los documentos con nuestro caso; embeddings y Vector Search; la búsqueda en **dos etapas**; el **umbral**; y lo que sale mal. Después una práctica con notebook. El **entregable del módulo** es un **módulo de RAG para un Agente Auditor de Políticas Financieras**: busca en las **normativas internas**, aplica **reranking** para quedarse con los **3 fragmentos más relevantes** y **justifica la aprobación o el rechazo**."

---
### Por qué RAG y qué es RAG Engine (0:05–0:17)

**Diap. 4 · Divisor: Por qué RAG**

**Diap. 5 · Lo que el modelo no sabe**
> "Un modelo de lenguaje aprendió de texto público hasta una fecha. **No conoce** su política de viáticos, ni el reporte de este trimestre, ni sus contratos. Y lo grave: si le preguntan, **no dice «no sé»; produce algo que suena bien**. En el Módulo 1 vimos que un agente sin herramientas inventa; la herramienta fue la solución para **datos**. Para **documentos**, la solución se llama **RAG**."

🛠 *(demo corta, opcional 💸)* Pregunta a Gemini, sin herramientas, «¿cuál es el límite diario de viáticos de mi empresa?». Resultado esperable: responde con algo genérico o inventado. ⚠️ Pruébalo antes y úsalo solo si el resultado es claro.
⚠️ *"¿Y por qué no meter todos los documentos en el prompt?"* → "Cuesta y se degrada: más texto es más tokens y más ruido para el modelo. Lo medimos hoy: con el reranking el modelo recibe **84 % menos** *(medido)*. Y los documentos reales no caben."
⚠️ *"¿Y ajustar (fine-tuning) el modelo con los documentos?"* → "Sirve para el estilo o la tarea, no para **citar** ni para **mantener al día** una política que cambia. Con RAG, para actualizar basta reindexar."

**Diap. 6 · RAG en una línea**
> "**R**etrieval-**A**ugmented **G**eneration: **recuperar** los fragmentos relevantes y **dárselos al modelo junto con la pregunta**. El modelo ya no responde de memoria: **responde con lo que le pasamos**. Es como un examen **a libro abierto**: el modelo es el estudiante y la búsqueda es el libro. Si en el notebook ven que el agente cita «Art. 1.3», ese texto viene de **nuestro almacén**, no del modelo."

💡 Una analogía de examen abierto es suficiente para BI; evita hablar de «espacios vectoriales» todavía.

**Diap. 7 · ¿Qué es RAG Engine?** *(docs: «Descripción general»)*
> "RAG Engine es un componente de **Gemini Enterprise Agent Platform** que facilita RAG; también se describe como un **framework de datos** para desarrollar aplicaciones con modelos adaptados al contexto. El problema es el que acabamos de ver: los modelos **no conocen los datos privados de su organización**. Con RAG Engine se **enriquece el contexto** del modelo con esa información, para que pueda **reducir las alucinaciones** y responder con más precisión. Contexto mejorado más la consulta es igual a una respuesta de mejor calidad."

⚠️ La documentación dice que **puede reducir** las alucinaciones: no promete eliminarlas. Dilo así.
💡 Un ejemplo para BI: es como darle al analista nuevo el manual de políticas **antes** de que conteste.

**Diap. 8 · El flujo de RAG Engine** *(docs: diagrama de la descripción general)*
🛠 Señala los dos carriles del dibujo: **Ingesta de documentos** y **Consulta**.
> "Es el flujo de la documentación. **Ingesta:** una **fuente** (*Source*), se **lee y enriquece** (*Parsing*), se **corta** en fragmentos (*Transformation*), se calculan los **embeddings y se indexa** (*Indexing*) y se guarda en una **base de datos vectorial** (*Vector DB*). **Consulta:** se **procesa la pregunta y se calcula su embedding** (*Preparing*), se **buscan** los fragmentos más cercanos (*Retrieval*), se **reordenan** (*Ranking*) y se **entregan al modelo con el formato adecuado** (*Serving*). La documentación enumera los conceptos en ese orden: ingesta, transformación, embedding, indexación —el **corpus** es el índice, como el de un libro—, recuperación y generación."
> "Hoy los recorremos todos. Y la regla que van a llevarse: **la calidad se decide en los primeros pasos**. Si el documento se leyó mal o se cortó la regla separada de su excepción, la búsqueda más sofisticada no lo arregla."

💡 En BI esto suena a **ETL y calidad de datos**: si la carga es mala, el tablero lo es, por bien diseñado que esté.

---
### RAG Engine: la plataforma y su anatomía (0:17–0:43)

**Diap. 9 · Divisor: RAG Engine, la plataforma**

**Diap. 10 · Modos de implementación** *(docs: «Modos de implementación»)*
> "RAG Engine tiene **dos modos**, y solo uno está activo a la vez. **Sin servidores** es lo **recomendado para empezar** y la forma más económica: usa **Vector Search 2.0 administrado** y la administración de recursos es gratuita; la base vectorial se factura directamente. **Spanner** asigna una infraestructura dedicada, pensada para cargas con **CMEK** o instancias aisladas, con un nivel **Básico** (el predeterminado, de capacidad fija) o **Escalado**; su precio depende del nivel. Un dato práctico que importa: **el modo predeterminado es Spanner**. Si alguien crea un proyecto y no elige, queda en un modo que se **cobra**."
> "El modo es **un ajuste del proyecto**, no de cada usuario. Se cambia con `UpdateRagEngineConfig`, solo si no hay operaciones en curso, y los datos quedan **aislados por modo**: cambiar de modo no mueve ni borra datos. Para detener la facturación de Spanner se pasa el nivel a `Unprovisioned`, y eso **borra la instancia y sus datos**."

⚠️ *"¿En qué regiones está?"* → "La página de modos **no menciona regiones**. Nosotros trabajamos en `us-central1`, y confirmaré las regiones vigentes en la documentación." *(No afirmes «solo us-central1»: no está confirmado.)*
⚠️ *"¿Cuánto cuesta?"* → "La página **no da cifras**: remite a la facturación de RAG Engine. No les doy un número que no puedo sustentar."
⚠️ Las bases vectoriales: sin servidores admite Vector Search 2.0 (predeterminada), Pinecone y Weaviate; Spanner añade `RagManagedDb` (predeterminada) y Vector Search 1.0. **Solo probamos la administrada de sin servidores.**

**Diap. 11 · Fuentes de datos** *(docs: «Ingesta de datos»)*
> "¿De dónde pueden venir los archivos? De **Cloud Storage** —la que usamos—, de un **archivo local** con `upload_file` (hasta **25 MB**, llamada síncrona), de **Google Drive**, y por conectores de **Slack**, **Jira** y **SharePoint**. Slack, Jira y SharePoint piden crear una app, guardar un token en **Secret Manager** y dar permiso a la cuenta de servicio de RAG."
> "Un detalle que enlaza con lo de la pérdida silenciosa: en **Google Drive**, si la carpeta no está compartida con la cuenta de servicio de RAG, **no se importa nada y tampoco hay un error**. Y otro útil: un archivo **sin cambios** y con la misma configuración de corte **se omite** al reimportar (`skipped_rag_files_count`)."

⚠️ **Solo probamos Cloud Storage.** Las otras fuentes salen de la documentación; no las ejecutamos.

**Diap. 12 · Documentos soportados y límites** *(docs: «Documentos admitidos»)*
> "Con el analizador por defecto: **PDF y DOCX hasta 50 MB**; **PPTX, HTML, JSON, JSONL o NDJSON, Markdown y texto hasta 10 MB**; y los documentos, dibujos y presentaciones de Google, 10 MB al exportarlos. Con otros tipos se puede, pero la documentación advierte de **respuestas de menor calidad**. El **Layout Parser** de Document AI tiene sus propios límites: 20 MB y 500 páginas por PDF. Y el **analizador de LLM** admite además imágenes: PNG, JPEG, WEBP, HEIC y HEIF."
> "Fíjense en lo que **no** dice esa página: **no menciona los PDFs escaneados**. Que el analizador por defecto los importe sin guardar nada es un hallazgo **nuestro**, medido. Lo vemos en un momento."

**Diap. 13 · Formas de leer un PDF** *(docs: analizador de LLM y Layout Parser)*
> "RAG Engine ofrece tres. El analizador **por defecto**, gratis, extrae el texto de un PDF que **ya tiene texto**. El analizador de **LLM** usa Gemini para **leer la página como imagen**, así que entiende escaneos y tablas, pero se **paga por página** *(docs: la documentación pone como ejemplo 1,000 PDFs de 50 páginas ≈ US$3.75; es solo un ejemplo educativo, confirma el precio vigente)*. El **Layout Parser de Document AI** reconoce estructura —texto, tablas, listas— y la documentación lo recomienda para documentos con **imágenes o gráficos**; necesita crear un procesador aparte (`LAYOUT_PARSER_PROCESSOR`) y **no lo usamos hoy**."

⚠️ **No probamos el Layout Parser.** Lo sabemos por la documentación.

**Diap. 14 · El prompt del analizador** *(docs: analizador de LLM)*
> "El analizador de LLM acepta un **prompt propio** (`custom_parsing_prompt`); el motor lo **añade** a su instrucción predeterminada. Con el prompt por defecto, la tabla salió en HTML y con comentarios en inglés; con uno propio en español salió en **markdown**, sin comentarios añadidos *(medido)*. **Controlar cómo se lee es parte del diseño**."

⚠️ Dato de vigencia *(docs)*: los modelos compatibles incluyen Gemini 3.x y 2.5; los **`gemini-2.5` se retiran el 31 de marzo de 2027**; los 3.x solo se sirven desde `global`, `us` y `eu`, no desde `us-central1`. Revisa la documentación antes de recomendar un modelo para producción.

**Diap. 15 · Transformación: cómo se corta en RAG Engine** *(docs: «Transformaciones de fragmentación»)*
> "RAG Engine corta con dos parámetros: **`chunk_size`**, el tamaño del fragmento **en tokens**, y **`chunk_overlap`**, cuántos tokens se repiten entre fragmentos consecutivos para mejorar la relevancia. Los valores **por defecto son 1,024 y 256**. Nosotros usamos 512 y 100, como el quickstart. El equilibrio: los fragmentos **pequeños** dan embeddings más precisos; los **grandes**, más generales, que pueden omitir detalles. La documentación **no da cifras para casos concretos**: describe el equilibrio."

⚠️ *"¿Y cuál es mejor?"* → "No hay un valor correcto: depende de sus documentos y de sus preguntas. Se mide. En una corrida previa, con el analizador de LLM, pasar de 512 a 128 **no cambió** los fragmentos de nuestras políticas *(medido)*; no sabemos por qué."

**Diap. 16 · Divisor: Anatomía de RAG Engine** — «Cómo se crea, se importa y se consulta un corpus. El código es el de la guía de inicio de la documentación.»

**Diap. 17 · Anatomía (1/2): crear el corpus e importar** *(docs: guía de inicio)*
🛠 Muestra el código y recórrelo en cuatro pasos. **No se ejecuta.**
> "Este es el código de la guía de inicio, abreviado. Se crea un **cliente** de `agentplatform`; se define el **modelo de embeddings** (`text-embedding-005`); se **crea el corpus** con su configuración de base vectorial; y se **importan archivos** desde Cloud Storage, indicando el corte (512 y 100) y un límite de solicitudes de embeddings por minuto."

💡 Es el mismo flujo del diagrama: *fuente → importar → transformar → indexar*.
⚠️ El ejemplo de la guía usa la ubicación **`us-east4`** y una ruta con comodín (`gs://.../*`).

**Diap. 18 · Anatomía (2/2): recuperar y generar** *(docs: guía de inicio)*
> "Segunda mitad. **Recuperar** contextos directamente, con `top_k` y un **filtro opcional por distancia** (`vector_distance_threshold`). Y **generar**: la guía conecta RAG Engine como **herramienta de Gemini** (`Tool` con `Retrieval`) y llama a `generate_content`. Es la forma más corta de tener RAG."

⚠️ Esa es la **alternativa oficial**. Nosotros no la usamos: construimos nuestra propia herramienta con ADK para controlar el reranking, el umbral y las citas. **No la probamos.**

**Diap. 19 · Lo que cambiamos y por qué**
> "Cada cambio nació de algo que **falló** al probar o de una **necesidad del caso**; no es una crítica a la guía. **Corpus:** `client.rag.create_corpus` sin backend explícito **falló en nuestras pruebas** («No available indexing project found»), también al crearlo desde la consola; lo resolvimos por **REST con el backend explícito**. **Ruta:** con `gs://carpeta/*` la importación dijo «no existe o está vacío»; con la **carpeta y barra final** funcionó. **Lectura:** el analizador por defecto pierde los escaneos en silencio, así que usamos el de **LLM con prompt propio**. **Recuperación:** la guía trae `top_k=3` y filtra por distancia; nosotros traemos **K = 20**, reordenamos hasta **N = 3** y filtramos por **puntaje**. **Generación:** la guía usa la herramienta de Gemini; nosotros, una **herramienta propia de ADK** con citas y `AuditDecision`. **Región:** la guía usa `us-east4`; nosotros, `us-central1`."

💡 Es la mejor ilustración de que **la documentación es el punto de partida, no la última palabra**: hay que probarla en el proyecto propio.
⚠️ *"¿Y si en mi proyecto sí funciona el ejemplo tal cual?"* → "Puede ser: los modos, las regiones y las versiones cambian. Lo nuestro es lo que vimos en **este** proyecto, en estas fechas."

**Diap. 20 · Una forma de agregar un documento a RAG Engine**
> "Esto es lo que hace el notebook, en cuatro pasos: **subir** los PDFs a un bucket, **crear** el corpus, **importar la carpeta** con un analizador, y **recuperar** los K candidatos. Es **una** forma, no la única: ya vimos que hay otras fuentes. Lo que no dice el quickstart y vimos probando: el backend explícito y la carpeta con barra final. Y hacen falta las **4 APIs** y el modo sin servidores; eso lo habilita el instructor."

**Qué usamos de RAG Engine y qué no** *(si preguntan: «¿entonces usamos RAG Engine?» → sí, en parte)*:
- **Sí lo usamos:** la **lectura** de los PDFs (analizador por defecto y de LLM), la **importación y el corte** (forma A, y los trozos de B y C subidos como archivos), la **indexación** en Vector Search administrado, y la **recuperación de la etapa 1** (`retrieve_contexts`, K = 20). Es lo que hacen las Partes 2 a 5 del notebook y `preparar_corpus.py`.
- **No lo usamos:** su **herramienta integrada de generación** (`Tool` con `Retrieval`) ni su filtro por distancia. Construimos una **herramienta propia de ADK**.
- **Va por fuera:** el **reranking** lo hace la **Ranking API** por separado, y el umbral y las citas son nuestros.
- **Sin RAG Engine:** la Parte 8 del notebook y el modo `offline` de `src` guardan los vectores **en memoria**, para ver la diferencia con un almacén persistente.

**Diap. 21 · Qué hace RAG Engine y qué hacemos nosotros**
> "Para que quede claro qué es de la plataforma y qué es nuestro. **Leer los PDFs**, incluso los escaneados: lo hace **RAG Engine**; no construimos ningún OCR. **Subir los archivos:** lo hacemos **nosotros**; creamos el bucket y subimos los PDFs, y RAG Engine importa desde ahí. **Cortar:** la forma A es de RAG Engine; **B y C las cortamos nosotros**, porque el servicio solo corta por tamaño y el módulo pide estrategias de chunking; luego subimos los trozos como archivos y RAG Engine los importa. **Embeddings, almacén y búsqueda de la etapa 1:** los hace **RAG Engine** en las Partes 2 a 7, y solo en la Parte 8 los hacemos nosotros, en memoria, **a propósito**, para contrastar documentos estructurados con no estructurados. **Reordenar, umbral, citas y agente:** son nuestros; el reranking lo hace la **Ranking API**, un servicio aparte."

💡 La regla para recordarlo: **lo que hicimos nosotros, o el servicio no lo hace, o lo hicimos a propósito para contrastar.**
⚠️ *"¿Entonces usamos RAG Engine o no?"* → "Sí, para leer, importar, indexar y buscar los candidatos. Lo que hacemos a mano es el corte de B y C, el reranking, el umbral, las citas y el agente, más la Parte 8 como contraste."
⚠️ El diagrama de la documentación incluye un paso de **Ranking** dentro de RAG Engine. **No lo usamos**: reordenamos con la Ranking API por separado, para controlar el umbral. Los embeddings que calculamos a mano son los de las oraciones para decidir los cortes de B, los de la Parte 8 y la prueba multimodal.

---
### Leer y cortar, con nuestro caso (0:43–1:05)

**Diap. 22 · Divisor: Leer los documentos** — «Ahora lo aplicamos a nuestro caso.»

**Diap. 23 · Estructurado frente a no estructurado**
> "Un documento **estructurado** trae marcas que un programa puede seguir: en nuestras políticas en markdown, cada artículo empieza con `## Artículo 1.3`. Basta cortar ahí. Un **PDF** no trae esas marcas de forma utilizable. Y un **escaneo** ni siquiera tiene texto: es una **foto de texto**. Como una tabla de una base de datos frente a una foto de una hoja de Excel."

🛠 Abre `AUD-2026.pdf` y trata de seleccionar texto. No se puede. «Esto es lo que tiene que *leer* el sistema.»

**Diap. 24 · Lo medido: qué leyó cada analizador (resultado real)**
> "Importamos **el mismo reporte** con los dos analizadores y buscamos las cifras. Con el analizador **por defecto**: el PDF con texto, bien; el **escaneado, cero fragmentos, y sin ningún error**. Con el de **LLM**, las cifras del escaneo aparecen *(medido)*."

| | Analizador por defecto | Analizador de LLM |
|---|---|---|
| PDF **con texto** | ✅ cifras | ✅ cifras |
| PDF **escaneado** | ❌ **0 fragmentos, sin error** | ✅ cifras |
| Tabla escaneada | no se lee | **HTML** |
| Texto extra | — | **«Context: …» en inglés, escrito por el modelo** (con un prompt propio, el formato se controla y desaparece) |

> "Dos lecciones. **Una: la pérdida silenciosa.** El analizador por defecto dijo que importó el escaneo y **no guardó nada**. Nadie avisa. Si no lo miden, creen que ese documento está en su buscador y **no está**. **Dos:** el analizador de LLM lee una foto, pero lo que devuelve es **texto que escribió un modelo**. Hay que **verificar las cifras contra el original**."

💡 Para BI, la analogía es una carga que «terminó sin errores» pero con 0 filas: hay que **contar** lo que entró.
❓ "¿Cómo se darían cuenta de que un documento no se indexó?" *(Contando fragmentos por archivo, como hace la celda 2.7.)*
⚠️ *"¿Qué usaría para un PDF con texto simple?"* → "El de por defecto: gratis y suficiente."
⚠️ *"¿El analizador de LLM no se equivoca con las cifras?"* → "Puede. Por eso se verifica contra el original; **no medimos una tasa de error**, y es una limitación."

**Diap. 25 · Divisor: Cortar el texto**

**Diap. 26 · Por qué se corta**
> "El modelo no puede leer un documento de 200 páginas por pregunta, y la búsqueda funciona mejor con **trozos que traten de una sola cosa**. Cortar es la decisión que más pesa en la calidad de un RAG. **Un trozo demasiado grande** mezcla temas y mete ruido. **Uno demasiado pequeño** pierde el contexto: una regla sin su excepción."
> **Reglas para documentos financieros:** en un **10-K o 10-Q**, la sección va con su tabla, la nota con su cifra y cada estado financiero por separado; en las **políticas**, un artículo por trozo con su encabezado; en las **notas de auditoría**, se conserva la referencia cruzada. Son **recomendaciones**: en el notebook el 10-Q (sintético) solo se **lee** con el analizador y se combina en la Parte 9; el corte propio por artículo se hace solo con las políticas.

⚠️ *Aclaración del 10-K y 10-Q:* el **10-K** es el reporte **anual** que las empresas que cotizan en bolsa en Estados Unidos entregan a la SEC (largo, con estados financieros auditados y notas); el **10-Q** es el **trimestral** (más corto, sin auditoría). Los dos se dividen en secciones llamadas «Item», con tablas y notas. **Nosotros usamos un 10-Q sintético, con cifras ficticias.**

**Diap. 27 · Tres formas de cortar**
| | Quién corta | Cómo | Cuándo |
|---|---|---|---|
| **A · RAG Engine** | El **servicio** | Por tamaño, en tokens | Cuando lo genérico basta |
| **B · Semántica (nuestra)** | **Nosotros** | Donde baja la similitud entre una oración y la siguiente | Texto **sin marcas** (transcripciones, PDFs planos) |
| **C · Por estructura (nuestra)** | **Nosotros** | Un trozo por «Artículo» | Texto que **conserva sus encabezados** |

> "Los de B y C los **subimos como archivos**, uno por trozo: RAG Engine solo corta por tamaño, así que si cada archivo es más corto que el corte, **queda entero** y se respeta nuestro criterio. En un proyecto real eso es la **etapa de preparación de documentos**. Recuerden los valores por defecto de la diapositiva 15: 1,024 y 256; nosotros importamos con 512 y 100."

**Diap. 28 · Lo medido: las tres formas**
🛠 Notebook, celdas 3.2, 3.3 y 3.5.
| Forma | Fragmentos | Artículos por fragmento | Hit@3 con reranking |
|---|---|---|---|
| A · RAG Engine | 5 | 4.0 | 6/6 |
| B · semántica | 14 | 1.5 | 6/6 |
| C · por estructura | 20 | 1.1 | 6/6 |

> "Las tres sacan **6 de 6**. Si midiéramos solo el Hit@3 diríamos que da igual. Pero fíjense en la columna de en medio: en la forma A, **cada fragmento trae cuatro artículos juntos**. Si el agente cita ese fragmento, ¿qué artículo está citando? **Todos**. La cita pierde precisión. **El Hit@3 no ve esa diferencia; hay que mirar más de una métrica.** Por eso se desempata por esa columna y se elige la **C**."

💡 Cuando varias opciones empatan en la métrica principal, **se busca otra que las distinga**. Es una lección que vale para cualquier decisión de diseño, no solo para chunking.

**¿Comparar métodos de corte es buena práctica? Sí, pero no es lo mismo que tener varios en producción.**
- **Comparar se recomienda.** El corte depende de **tus documentos y tus preguntas**: la documentación de transformaciones no da cifras para casos concretos, solo describe el equilibrio entre precisión y generalidad, así que la decisión se toma **probando**. Se prueban los candidatos con **preguntas cuya respuesta conoces** y se elige con una medida, no a ojo. Es práctica común en RAG y es lo que recomendamos; **no está tomada de la documentación de Google**: es criterio general.
- **Varios métodos en producción, normalmente no.** Lo habitual es **elegir uno por tipo de documento** (por estructura para reglamentos con encabezados; por significado o por tamaño para texto sin marcas), o **combinarlos**: primero por estructura y solo las secciones muy largas por significado. Cada método extra es más código que mantener y más cosas que pueden fallar. Aquí, además, B y C requirieron un rodeo: cortar nosotros y subir los trozos como archivos.
- **Nuestra comparación es pequeña:** 20 artículos y 6 casos. Las tres formas empataron en Hit@3 y el desempate lo decidió un criterio **nuestro** (citas más exactas); con más documentos o más casos podría haber decidido el Hit@3. Sirve para **aprender cómo se decide**, no como prueba de que C es la mejor en general: depende de que los documentos conserven sus encabezados. Una evaluación seria, con más casos y métricas como el recall de contexto, es del Módulo 5.
> Cómo plantearlo: "Comparamos tres formas para que vean *cómo se decide*, y elegimos una. En su proyecto probarán con sus documentos y se quedarán con la que funcione mejor."

**Diap. 29 · El Art. 1.3 y su excepción**
🛠 Notebook, celda 3.3: la política de viáticos cortada de tres formas. ⚠️ **Mira antes qué cortó B en tu corrida**: el resultado **no es fijo** (ver el aviso de abajo). Di lo que realmente salga.
> "Miren el corte semántico (B). **En nuestra corrida de ensayo** dejó el Art. 1.3 con el 1.1 y el 1.2, y **separó el 1.4 en su propio trozo**. El 1.3 es la **regla** (el viaje sin autorización se rechaza) y el 1.4 es la **excepción** (salvo emergencia). Si el agente recibe solo el trozo de la regla, **no ve la excepción**. Ese es el **peor error de un corte semántico**: es una heurística y puede separar lo que debía ir junto. La estructura (C), en cambio, **acierta siempre, pero solo si el texto conserva los encabezados**."

⚠️ **El corte de B cambia de una corrida a otra.** El analizador de LLM no devuelve el texto idéntico cada vez (en dos corridas, la política de consultoría salió con 767 y 765 caracteres), y el corte semántico depende de ese texto. En la corrida de un alumno, B dejó el 1.3 **junto** al 1.4 (`[1.1, 1.2, 1.3, 1.4]` y `[1.5]`), y en la de ensayo los separó. **Las dos salidas sirven para enseñar:** si los separó, es el riesgo que se ve; si los dejó juntos, la lección es que **un corte semántico puede acertar por suerte**, y que con otro percentil ya no (ejercicio 3: percentil 10 y 50). Lo que no varía es que C **siempre** deja un artículo por trozo. *(Que el cambio de texto sea la causa del cambio de corte es la explicación más probable; no se comprobó.)*

❓ "¿Qué tipo de documentos de su empresa no tendrían encabezados claros?" *(Correos, actas, transcripciones, PDFs viejos: ahí la semántica ayuda.)*
⚠️ *"¿Se pueden combinar?"* → "Sí, y es lo habitual: primero por estructura, y solo las secciones muy largas por significado."

**Diap. 30 · Cortar en código**
> "Así se ve en código, abreviado. **C** es una **expresión regular** que corta en cada «Artículo» o «Nota»: barata y exacta, pero necesita encabezados. **B** convierte cada oración en un vector, compara cada una con la siguiente y **corta donde la similitud cae por debajo de un percentil** (`PERCENTIL`, por defecto 25). Con un percentil más bajo salen **menos cortes**. El código completo está en `src/rag/chunking.py`."

💡 Esto prepara el ejercicio 3 del notebook (cambiar el percentil a 10 y a 50).

---
### Embeddings y Vector Search (1:05–1:15)

**Diap. 31 · Divisor: Embeddings y Vector Search**

**Diap. 32 · Qué es un embedding**
> "Un **embedding** convierte un texto en una **lista de números** (en nuestro caso **768**) de forma que **textos con significado parecido quedan cerca**. Es como asignar a cada fragmento unas coordenadas en un mapa: «viaje sin autorización» queda cerca de «autorización previa» aunque no compartan palabras. Buscar es poner la pregunta en el mismo mapa y traer **lo más cercano**.
> Dos detalles técnicos por si preguntan: el modelo distingue **para qué** se embebe el texto (`RETRIEVAL_DOCUMENT` para los fragmentos, `RETRIEVAL_QUERY` para la pregunta; así lo hace `retrieval.py`), y «cercano» se mide con **similitud coseno**."

🛠 Notebook, Parte 0: la celda que imprime `✅ text-embedding-005 → dimensión 768`.
💡 Para BI: es una **llave de búsqueda por significado**, que complementa (no reemplaza) el `LIKE` o la búsqueda por palabra clave. Cuando el término exacto importa (un código de política, una cifra), la búsqueda por palabras sigue siendo útil.
**Embeddings multimodales (una celda opcional del notebook):** `gemini-embedding-2` coloca **texto e imágenes en el mismo espacio**: la imagen de un gráfico de barras queda más cerca de «gráfico de barras con ingresos trimestrales» que de «receta de paella» *(medido: 0.401 frente a 0.219)*. Sirve para **buscar un gráfico con una pregunta en texto**. Para **tablas**, normalmente conviene más un **analizador** que embeber la imagen. Este modelo solo está en `global`, `us` y `eu`, no en `us-central1`. Se enseña como **concepto**, no como parte del flujo del auditor: el entregable es texto.

**Diap. 33 · Dónde se guardan: Vector Search**
> "Los vectores se guardan en **Vector Search**. Usamos **RAG Engine en modo sin servidores**: nosotros subimos archivos a Cloud Storage y él los **lee, corta, calcula los embeddings y los guarda** en Vector Search **administrado**, creando una colección por corpus en nuestro proyecto. No administramos servidores. Y **el almacén es persistente**: si cierro el notebook, los vectores siguen ahí. Por eso, **al terminar hay que borrarlos**."

🛠 Consola → RAG Engine → Corpus: enseña los corpus que creó el notebook (o `preparar_corpus.py`).
⚠️ Recuerda lo de la diap. 10 *(docs)*: el modo es **del proyecto**, y el **predeterminado es Spanner**. **Regiones:** la documentación de modos no las menciona y el quickstart usa `us-east4`; nosotros usamos `us-central1`. La afirmación «el modo sin servidores solo existe en `us-central1`» **no está confirmada**: no la hagas.
⚠️ *"¿Es obligatorio usar RAG Engine para usar Vector Search?"* → "No. Vector Search se puede usar directo y construir uno mismo la lectura, el corte y los embeddings; RAG Engine **ahorra** esos pasos. En la Parte 8 del notebook hacemos el almacén **en memoria** para ver la diferencia."
⚠️ *"¿Cuánto cuesta?"* → "No les doy una cifra que no puedo sustentar: depende de lo que se indexe, los tokens y las consultas. Lo que sí sé es lo que **no** cuesta mantener (la administración en sin servidores) y lo que **sí** (el analizador de LLM, por página, y Spanner mientras exista). Se medirá en el Módulo 5."

---
### Dos etapas y reranking (1:15–1:31)

**Diap. 34 · Divisor: Dos etapas y reranking**

**Diap. 35 · Por qué dos etapas**
> "La búsqueda vectorial es **rápida pero basta**: compara vectores calculados **por separado** para la pregunta y para cada fragmento. Un **reranker** es un modelo que **lee la pregunta y el fragmento juntos**: más lento y más preciso. Entonces hacemos las dos: la **etapa 1** trae los **K = 20** más cercanos (barato), y la **etapa 2** los reordena y nos quedamos con **N = 3**. K y N vienen del cronograma. El reranker que usamos es la **Ranking API** (en la nube, con `semantic-ranker-default`).
> Alternativas del mismo tipo que nombra el cronograma: **Cohere Rerank** y **BGE-Reranker** (no se probaron). Los nombres técnicos, si los piden: la etapa 1 es un **bi-encoder** (pregunta y fragmento se convierten en vectores **por separado**, así los del corpus se calculan una sola vez), y la etapa 2 un **cross-encoder** (lee los dos **juntos**, y por eso solo se aplica a los K candidatos)."

💡 Es la misma lógica de un **filtro grueso y un ordenamiento fino**: no se aplica el modelo caro a todo el corpus, solo a los candidatos.

**Diap. 36 · ¿Cambia el reranking el resultado?**
🛠 Notebook, celdas 5.1 y 5.2.
> "Medimos con **6 casos de gasto**: un caso acierta si algún artículo esperado aparece en los 3 fragmentos. Resultado: **6 de 6 sin reranking y 6 de 6 con reranking**. ¿Entonces no sirve? **Con este corpus no se nota.** Son 20 artículos y K es 20: la etapa 1 ya devuelve **todo el corpus**. Es una limitación **de nuestro ejemplo**, no del método. Con cientos de documentos el reranking sí marca diferencia.
> Para ver su efecto, este caso: **«una cena a un proveedor y no tengo factura»**. La etapa 1 pone en tercer lugar la nota de auditoría sobre *evidencia*; el reranker prefiere la política de *provisión*, y además da un **puntaje** (0.456 contra 0.147). Ese puntaje es lo que usaremos para el umbral."

⚠️ Con el reranker **léxico de ejemplo** (offline), el mismo experimento da **5/6 → 6/6** (`compare_rerank.py`): es una demostración sin servicios, con un corpus y un reranker más simples. No lo confundas con la medición en la nube. Su caso estrella es **G5** (contrato de USD 80,000 con una sola cotización): la etapa 1 deja el Art. 2.2 fuera del top-3 (`3.4, 5.2, 2.1`) y el reranking lo sube al primer lugar *(verificado el 2026-10-21)*.
❓ "Si el Hit@3 ya es 6/6 sin reranking, ¿cómo defenderían ante su jefe que se necesita?" *(Con el caso donde cambia el top-3, y con la ventana de contexto, la siguiente diapositiva.)*

**Diap. 37 · K, N y la ventana de contexto**
🛠 Notebook, celdas 5.3 y 5.4.
> "**¿Cómo se eligen K y N en un proyecto real?** **K** se elige lo bastante grande para que el fragmento correcto esté entre los candidatos: se mide el **recall@K** con preguntas cuya respuesta se conoce, y se toma el menor K donde deja de mejorar. **N** es cuántos fragmentos necesita el modelo para responder: 1 a 3 para un dato; 5 a 10 si cruza fuentes; se prueba con las mismas preguntas. En nuestro corpus todos los K dan 6/6 *(medido)*, porque es pequeño.
> **Y por qué importa N:** el cronograma dice que el reranking sirve para **optimizar la ventana de contexto**. Medido: con los 20 candidatos, **1,052 tokens**; con los 3 del reranking, **173**. **84 % menos** *(medido, caso G2)*. Menos tokens es menos costo y menos ruido. Además, con contextos largos los modelos tienden a aprovechar peor lo que queda **en medio** (se le llama *lost in the middle*): otra razón para pasar pocos fragmentos y bien elegidos."

💡 Un RAG no tiene «los parámetros correctos»: tiene los que **mejor funcionan para sus preguntas**. K y N se **calibran**, igual que cualquier umbral en BI.
⚠️ *"¿Hay otros rerankers?"* → "Sí: modelos de código abierto o de terceros (el cronograma menciona alternativas). **No las probamos**; usamos la Ranking API por estar en la misma plataforma."

---
### Umbral, el «no sé» y el auditor en código (1:31–1:45)

**Diap. 38 · El umbral: poder decir «no sé»**
🛠 Notebook, celda 6.1.
> "Aquí viene el problema: el reranking **siempre devuelve tres fragmentos, aunque la pregunta no tenga nada que ver**. Si preguntan por un yate, devuelve los tres artículos «menos malos». Y un modelo que recibe tres fragmentos **los usa**. Un auditor que contesta con lo que sea es **peligroso**. La solución es un **umbral de relevancia**: si ni el mejor fragmento lo supera, **no se aprueba ni se rechaza: se escala**."
> "Se miden los mejores puntajes de preguntas **cubiertas** por el corpus y de preguntas **que no tienen nada que ver**. Lo irrelevante **nunca pasó de 0.032** (el yate 0.032, la paella 0.014, un texto sin sentido 0.023); lo relevante **nunca bajó de 0.202** *(medido)*. Hay un hueco enorme y tomamos el **punto medio**, **0.12**. El yate se queda sin fragmentos y el agente **escala**."
> "Tres advertencias. **Una:** el umbral **solo vale para este corpus y este reranker**; con el markdown, el mismo método dio **0.14**. Cambia el corpus o el reranker, **se recalibra**. **Dos:** aquí el hueco es limpio; con documentos reales los grupos **se solapan**, y hay que decidir **qué error cuesta más**: escalar de más o contestar sin base. **Tres:** el umbral decide **qué ve** el agente; la **instrucción** decide **qué hace** con lo que no ve. Hacen falta **las dos cosas**."

💡 Para BI: un umbral de alerta. Demasiado bajo, ruido; demasiado alto, deja pasar. Se calibra con casos conocidos y se revisa.
❓ "¿Qué cuesta más en un auditor: escalar un caso que sí podía resolver, o contestar uno sin base?" *(Depende del riesgo; en finanzas, normalmente lo segundo. Que lo defiendan.)*

**Diap. 39 · Dos etapas y el umbral en código**
> "Así se ve, abreviado. Se traen los **K** más cercanos (`retriever.search`), se **reordenan** y se queda uno con **N** (`reranker.rerank`), y se **descarta** lo que no llega al umbral (`h.score >= UMBRAL`). El umbral se calcula como el **punto medio** entre el mejor puntaje de las preguntas **fuera** del corpus y el de las **cubiertas**. Si la lista queda vacía, el agente debe responder **ESCALAR**."

⚠️ Ese método del punto medio es **nuestro**, un método práctico; no es una fórmula oficial. Si los grupos se solapan, el código usa el mínimo de las relevantes y avisa.
⚠️ La **alternativa oficial** del quickstart es filtrar por **distancia** (`vector_distance_threshold`) dentro de la propia recuperación; no la probamos.

**Diap. 40 · Anatomía del auditor**
> "Es el mismo patrón del Módulo 1: **description, instruction, tools**. Lo nuevo es el **contrato** `AuditDecision`, con tres decisiones válidas: aprobado, rechazado y **ESCALAR**. La **herramienta** devuelve citas, y su docstring explica que una **lista vacía** significa «no apruebes ni rechaces». Y la **`instruction`** tiene dos reglas: **decidir solo con lo que devuelve la herramienta**, y **escalar si no hay citas**. Son las dos reglas que prueba el ejercicio 7."

💡 Une lo del Módulo 1 con lo de hoy: el modelo **propone**, el código **decide**, y la herramienta es la **fuente**.

---
### Qué sale mal en un RAG (1:45–1:51)

**Diap. 41 · Seis cosas que pasan de verdad**
Todos los ejemplos salen de las pruebas de este proyecto.
> "**Uno:** la **pérdida silenciosa**: un documento que se importó y no está. **Dos:** el **texto lo escribió un modelo**: el analizador de LLM reformula y puede alterar cifras; se verifica contra el original. **Tres:** el agente **reformula la consulta** antes de buscar, y si reformula mal, la búsqueda trae otra cosa; por eso se revisa el rastro de eventos. **Cuatro:** **citas gruesas** («Arts. 1.1 y 1.2 y 1.3…») cuando el fragmento es una política entera. **Cinco:** **al añadir un documento sobre el mismo tema, las respuestas pueden cambiar**: hay que volver a correr los casos. **Seis:** al **mezclar fuentes**, los fragmentos largos de una pueden quedarse con los tres lugares y la otra nunca llega al agente; la solución es una **cuota por fuente** (una sola llamada al reranker; la cuota se aplica después de ordenar), que **garantiza presencia pero a veces mete un fragmento menos relevante**.
> Nada de esto se arregla escribiendo mejor el prompt: se **mide** y se **vigila**. Eso es el Módulo 5."

💡 Cada punto salió en una corrida real, y es la mejor vacuna contra «el RAG ya funciona».
⚠️ *"¿Con qué frecuencia pasa lo del reformulado o lo de las citas gruesas?"* → "No lo sé: lo vimos en corridas sueltas y **no lo medimos**. Son ejemplos de por qué hay que medir, no estadísticas."
⚠️ *"¿Y evaluar un RAG de forma seria?"* → "Hoy usamos Hit@3 y 6 casos: **es poco**. La evaluación formal (qué tan fiel es la respuesta a los fragmentos, cuántos fragmentos relevantes se recuperan) es del Módulo 5."
⚠️ *"¿Por qué a mí me salió distinto?"* → "Porque el documento **no se lee igual dos veces**: el analizador es un modelo, y todo lo que viene después (cortes, puntajes, la decisión del agente) se construye sobre ese texto. Lo que no cambia son las conclusiones: el escaneado se pierde con el analizador por defecto, el yate escala y el reranking reduce el contexto. Por eso en el Módulo 5 se mide con **varios casos**, no con una corrida."

---
### Cierre (1:51–2:00)

**Diap. 42 · Lo que debe quedarse**
> "Si se llevan **cinco ideas**: **uno**, el modelo no sabe lo de su empresa y, si no sabe, inventa; **RAG le da los documentos y exige citar**. **Dos**, **la calidad se decide al leer y al cortar**, y se mide con más de una métrica. **Tres**, **dos etapas**: buscar K = 20, reordenar y quedarse con N = 3; el reranking reduce el contexto. **Cuatro**, **un umbral** para poder decir «no sé», que **se calibra con cada corpus**. **Cinco**, **la herramienta es la fuente**: las citas vienen de la herramienta, no del modelo."

**Diap. 43 · Proyecto base y siguiente paso**
> "Tienen un proyecto base en `src/`: `rag/` con el chunking, la recuperación y el auditor; `auditor_rag_app/` que pueden abrir en `adk web`; y `preparar_corpus.py` que crea el corpus de políticas en RAG Engine. Ahora abran el notebook y ejecuten la **Parte 0**. En la práctica hacemos todo lo de hoy; **al final borren lo que crearon**. El entregable: **un auditor que busca en las normativas internas, aplica reranking y justifica con citas**. **En la semana 6 lo conectarán con el supervisor del Módulo 1**, con lo que aprendieron de A2A. El **Módulo 3** es el mismo RAG con reranking, pero sobre el **catálogo de datos**, antes de generar SQL."

💡 Dejar la Parte 0 hecha evita perder los primeros minutos de la práctica en problemas de entorno.

**Diap. 44 · Preguntas y respuestas**
> "¿Preguntas?" Si te quedas en blanco, usa las frases de rescate de la sección 6.

---
## 6. Frases de rescate y orden de recortes
**Frases de rescate (si te quedas en blanco o se alarga el tiempo)**
- "Eso lo vemos en la semana 5; por ahora quédense con la idea de que *se puede medir*."
- "Buena pregunta: no lo voy a inventar. Lo verifico y lo respondo en el chat."
- "Veámoslo en el notebook, que ahí está la evidencia."
- "Antes de buscar, **cuenten** lo que entró."
- "El umbral decide qué ve el agente; la instrucción decide qué hace con lo que no ve."
- "Eso lo dice la documentación; lo nuestro es lo que vimos probando."

**Si vas corto de tiempo, recorta en este orden** (44 diapositivas son muchas)
1. Las fuentes que no usamos (diap. 11): deja solo «Cloud Storage es la que usamos» y la advertencia de Drive.
2. El prompt del analizador y los datos de vigencia de modelos (diap. 14).
3. Documentos soportados (diap. 12): deja solo «PDF hasta 50 MB» y que los escaneos no se mencionan.
4. El detalle de K y N (diap. 37): deja solo el 84 % de contexto.
5. La demo de «Gemini sin documentos» (diap. 5) y la de `compare_rerank.py`.
6. Una de las dos diapositivas de código del quickstart (diap. 17 o 18): deja la 17.
**Nunca recortes:** los modos y que **Spanner es el predeterminado** (diap. 10), lo que cambiamos y por qué (diap. 19), la pérdida silenciosa del escaneo (diap. 24), el Art. 1.3 y su excepción (diap. 29), el umbral y el yate (diap. 38).

---
## 7. Errores comunes y preguntas de repaso
**Errores que verás en las células:**
- Dar por buena la importación sin **contar los fragmentos** por archivo.
- Elegir el chunking **solo por el Hit@3**, sin mirar la precisión de la cita.
- Copiar el umbral de otro corpus en lugar de **recalibrarlo**.
- Confiar en que el agente «ya sabe decir que no» sin umbral **ni** instrucción.
- No mirar la consulta que el agente mandó a la herramienta (el 📥).
- Dar por buena una cifra que **escribió el analizador** sin cotejarla con el PDF.
- **Reordenar solo los 3 de la etapa 1:** no aporta nada; el valor del reranking está en reordenar los **20** y quedarse con 3.
- Usar el puntaje de un reranker con el umbral de **otro** (hay que recalibrar).
- **Importar con `gs://carpeta/*`** en lugar de la carpeta con barra final.
- **Dar por hecho el modo del proyecto:** el predeterminado es Spanner, que se cobra.
- Dejar corpus y buckets creados al terminar.

**Preguntas de repaso (cierre o evaluación rápida):**
1. ¿Qué dos modos tiene RAG Engine y cuál es el predeterminado? ¿Qué pasa con los datos al cambiar de modo?
2. ¿Qué fuentes de datos admite? ¿Qué pasa en Google Drive si no compartes la carpeta?
3. ¿Qué es la pérdida silenciosa y cómo se detecta?
4. ¿Cuándo usarías cada forma de chunking? ¿Qué métrica distingue las tres cuando el Hit@3 empata?
5. ¿Qué hace cada etapa de la recuperación y por qué no se usa solo el reranker?
6. ¿Cómo se elige K? ¿Y N?
7. ¿Qué pasa con un umbral demasiado bajo? ¿Y con uno demasiado alto? ¿Cuándo se recalibra?
8. ¿Por qué hacen falta **el umbral y la instrucción**?
9. Si añades un documento sobre el mismo tema, ¿qué debes hacer?
10. ¿Qué cambiamos respecto a la guía de inicio, y por qué?

## 8. Lo que no está probado (sé transparente con el grupo)
- **Estabilidad:** el notebook del instructor se ejecutó **completo con servicios reales** y sus comprobaciones dieron ✅, pero **una corrida no garantiza que siempre salga igual**: Gemini, el analizador y el reranker no son deterministas. Los puntajes, los conteos de fragmentos y los tiempos varían.
- **Notebook de alumnos:** se ejecutó una vez, de la Parte 0 a la 9, con los valores por defecto de los ejercicios; con otros valores, no se probaron.
- **30 alumnos a la vez** creando corpus en un mismo proyecto (las operaciones sobre corpus no admiten concurrencia según la documentación) y el **costo total**: no probados. **Permisos mínimos** de un alumno: no verificados (se probó con una cuenta Propietaria).
- **Evaluación formal del RAG** (fidelidad, recall de contexto): no hecha; es del Módulo 5. El Hit@3 con 6 casos y 20 artículos es poco informativo.
- **Reproducibilidad entre corridas:** con el mismo notebook, en otra corrida el 10-Q quedó en 3 fragmentos en lugar de 4, el corte semántico (B) dejó el Art. 1.3 junto al 1.4, la pregunta mixta de la Parte 9 dio `ESCALAR` (la comprobación 9.4 mostró ❌ en esa línea) y las cuotas no cambiaron el reparto. Las conclusiones principales se mantuvieron; los detalles no.
- **Lo que viene de la documentación y no probamos:** el **Layout Parser de Document AI**, las fuentes **Google Drive, Slack, Jira y SharePoint**, la carga de **archivos locales** con `upload_file`, el modo **Spanner**, las bases vectoriales **Pinecone y Weaviate**, la **herramienta de recuperación de Gemini** y el filtro **`vector_distance_threshold`**, y otros rerankers (Cohere, BGE).
- **El código del quickstart** (diap. 17 y 18) **no se ejecutó tal cual**: en nuestras pruebas, la creación del corpus con el SDK sin backend explícito y la importación con `*` fallaron. Lo que usamos es nuestra adaptación.
- **Regiones:** no está confirmado que el modo sin servidores solo exista en `us-central1`. La página de modos no menciona regiones y el quickstart usa `us-east4`. Trabajamos en `us-central1`.
- **Un documento real extenso:** usamos un 10-Q **sintético** con cifras ficticias; **no** hay un 10-K, ni uno real. Tampoco probamos la **búsqueda híbrida** (vectorial más palabras).
- **Tamaño de corte con el analizador de LLM:** no cambió los fragmentos en una corrida previa; no se investigó por qué.
- **Vigencia:** `gemini-2.5-flash` (analizador y agente) se retira el **31 de marzo de 2027** según la documentación; el módulo `agentplatform` del SDK es **experimental** y puede cambiar. Probado con ADK 2.12.0.
- **El reparto de tiempos** de la sección 3 es una propuesta sin ensayar.
- **Despliegue a Agent Runtime.**

---
## 9. Mapa del proyecto y cómo armar tu propio RAG

Esta sección responde: **¿qué hay en `src` y cómo hago yo un RAG propio?** Los comandos de 9.1 se ejecutaron localmente (🟢, sin servicios); la plantilla de 9.3 **no se ejecutó con Gemini**.

### 9.1 Qué es cada archivo y si lo necesitas
**Dentro de `modulo2_rag_reranking/src/`:**
| Archivo | Para qué sirve | ¿Obligatorio en un RAG propio? |
|---|---|---|
| `rag/chunking.py` | Corta por artículo (`load_corpus`, `split_by_structure`), por significado (`split_semantic`) y convierte un fragmento en `ChunkDoc` con **cita** | Algún criterio de corte, **sí** |
| `rag/retrieval.py` | Etapa 1 (`VertexEmbeddingRetriever`), etapa 2 (`VertexRanker`), `select_with_quotas`, `calibrate_threshold`, `hit_at_n`, `ranking_config()` | Las dos etapas y el umbral, **sí** |
| `rag/auditor.py` | `AuditDecision` y `Citation` (el **contrato**), `buscar_politicas` (la herramienta), `build_auditor(...)` (el agente) | El contrato y una herramienta, **sí** |
| `rag/ragengine.py` | `RagEngineProject`: crear corpus, importar con analizador, recuperar, borrar (con las lecciones aprendidas en el docstring) | Solo si usas RAG Engine |
| `auditor_rag_app/agent.py` | Expone el auditor como `root_agent` para `adk web`; la fuente se elige con `AUDITOR_FUENTE` | **Sí** (ADK busca `root_agent`) |
| `preparar_corpus.py` (en la carpeta del módulo) | Sube los PDFs, crea el corpus y lo importa; imprime las variables del `.env` | Solo si usas RAG Engine |
| `rag/README.md` | Mapa del proyecto, cómo ampliarlo y las lecciones | No |

### 9.2 De dónde busca el auditor (la única decisión que cambia)
| Quiero | `.env` |
|---|---|
| Probar sin crear nada | `AGENTS_MODE=offline` (por defecto): búsqueda local de ejemplo; el modelo sí es Gemini real |
| Servicios reales sobre los mismos documentos | `AGENTS_MODE=cloud` |
| Las políticas en PDF dentro de RAG Engine | `AGENTS_MODE=cloud`, `AUDITOR_FUENTE=rag_engine`, `RAG_CORPUS_POLITICAS=<…>` |
Cambia **solo la función que da los candidatos**; el reranker, el umbral y el agente son los mismos. Es la misma idea de las Partes 7 y 8 del notebook.

### 9.3 Para armar uno propio: el orden recomendado
1. **Junta 5 a 10 documentos reales** de tu área y **6 preguntas cuya respuesta conoces** (con el artículo o sección esperada). Sin esto no puedes medir nada.
2. **Léelos** y **cuenta los fragmentos por archivo**: si alguno da 0, lo perdiste.
3. **Elige el corte** con **dos** medidas: si acierta (Hit@3) y qué tan precisa es la cita.
4. **Indexa** y recupera K; añade el **reranking** y mide si cambia el top-3.
5. **Calibra el umbral** con preguntas cubiertas y **fuera del corpus**.
6. **Envuelve** la búsqueda en una herramienta que devuelva **citas** y **puntajes**, y un agente con salida estructurada y una instrucción que diga **qué hacer cuando no hay citas**.
7. **Vuelve a correr tus 6 casos** cada vez que cambies el corpus, el reranker o la instrucción.

Plantilla mínima de la fábrica (la que usa `src`) *(⚠️ no se ejecutó con Gemini)*:
```python
from rag.auditor import build_auditor, buscar_politicas

agente = build_auditor(buscar_politicas)   # tool = una función con tipos y docstring que devuelve citas
```
Para conectar **otra** fuente, escribes **otra función de búsqueda** (con tipos, docstring y citas) y se la das a `build_auditor`.

### 9.4 Qué sigue
- **Módulo 3:** el mismo RAG con reranking, pero sobre el **catálogo de datos** (esquemas y tablas) antes de generar SQL.
- **Capstone (semana 6):** conectar el auditor con el supervisor del Módulo 1 **por A2A**; los alumnos lo hacen como práctica. La nota de instructor está en `SESION_PRACTICA.md`.
