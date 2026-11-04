# Módulo 2 · SESIÓN PRÁCTICA (tutoría) — Guía del instructor

**Formato:** 5 células de 6 personas trabajando en `notebooks/practica_alumnos.ipynb`; tú proyectas `notebooks/practica_instructor.ipynb` (resuelto). Mientras trabajan, haces **code review** por célula.
La explicación de los conceptos tendrá su propia guía: **`SESION_TEORICA.md`** (pendiente). Los comandos paso a paso para los alumnos están en **`COMANDOS.md`**.

**Contenido de esta guía:** Antes de la clase · El lab (qué se entrega) · Línea de tiempo y reparto · Guion por parte (0 a 10) · Cierre · Code review · Contingencias · Problemas fuera del notebook · Nota de instructor: conexión con el Módulo 1 y el capstone · Lo no probado.

> ⏱️ **Ojo con el tiempo:** el notebook suma **unos 195 minutos** (200 con la limpieza), más de las 2 h de una tutoría. Léelo junto con la sección *Línea de tiempo y reparto*: ahí están las dos formas de repartirlo y qué recortar.

---
## Antes de la clase (día anterior)
- [ ] `. .\env.ps1` y `python -m pytest modulo2_rag_reranking -q` → **44 passed** (corren **siempre sin servicios**, aunque tu `.env` diga `cloud`). *(Verificado: 44 passed.)*
- [ ] Ejecuta `notebooks/practica_instructor.ipynb` completo (Run All): debe terminar con **🎉** en las celdas 7.4 y 9.4 y con la limpieza enviada. Usa **servicios reales** (Gemini, embeddings, Ranking API, RAG Engine con el analizador de LLM) y cuesta **centavos** (estimación): hazla **una sola vez**, no en bucle.
- [ ] Los dos notebooks tienen **la misma estructura**: `practica_alumnos.ipynb` es el del instructor con **5 ejercicios añadidos (🧪)** y salidas vacías. Ya no hay script que los genere: **si cambias uno, aplica el mismo cambio al otro**.
- [ ] **Las 4 APIs habilitadas** en el proyecto del curso (las habilitas tú, no los alumnos): Vertex AI, **Discovery Engine** (Ranking API), **Vector Search** y **Cloud Resource Manager**. Comando en `COMANDOS.md`, paso 3. Si falta una, el error aparece **a mitad del notebook** (Parte 2) y a veces engaña (ver *Contingencias*).
- [ ] **RAG Engine en modo sin servidores** (celda 2.1 del notebook: debe decir `modo SIN SERVIDORES ✅`). Es un ajuste **del proyecto**, no de cada alumno. Si no lo está, cambiarlo (celda 2.3 con `CAMBIAR_A_SERVERLESS = True`) afecta a **todos**: hazlo tú, una vez, antes de la clase, y comprueba antes que no haya corpus de otros modos que quieras conservar (celda 2.2).
- [ ] **Sin corpus de pruebas anteriores:** la celda 2.2 debe decir `0 corpus existentes` (o solo los que conozcas). Los de ensayos previos siguen guardando datos.
- [ ] **Región `us-central1`** en el `.env` de todos (`GOOGLE_CLOUD_LOCATION`): el modo sin servidores solo existe ahí, y en otra región los embeddings y Gemini pueden dar 404.
- [ ] **Permisos:** los alumnos crean **buckets y corpus** en el proyecto. ⚠️ Las pruebas se hicieron con una cuenta **Propietaria**; los **roles mínimos no se han verificado**. Pruébalo con una cuenta de alumno **antes** de la clase.
- [ ] **Prueba de concurrencia:** ⚠️ la documentación dice que las operaciones sobre corpus **no admiten concurrencia**, y **no se ha probado con 30 personas a la vez** en un mismo proyecto. Haz un ensayo con 3 a 5 alumnos creando corpus al mismo tiempo (Partes 2 y 3). Si falla, ver *Contingencias*.
- [ ] Credenciales de **todos** probadas (`gcloud auth application-default login`), y en su `.env`: `GOOGLE_CLOUD_PROJECT=<ID>`, `MODEL_NAME=gemini-2.5-flash`, `EMBEDDING_MODEL=text-embedding-005`. `RANKING_CONFIG` **no hace falta tocarlo**: el código lo calcula.
- [ ] Presupuesto: **alerta de presupuesto** en Facturación antes de la clase (el consumo por alumno es bajo, pero son 30 y cada uno crea 5 corpus).
- [ ] Alumnos con el entorno instalado y la Parte 0 ejecutada (`COMANDOS.md`, pasos 1 a 6).
- [ ] Si harás la demo del proyecto (`src`) al final: `python modulo2_rag_reranking/preparar_corpus.py --dry-run` debe mostrar el plan (🟢, no cuesta).

## El lab: qué se entrega
**Objetivo (cronograma):** un **Módulo de RAG para un Agente Auditor de Políticas Financieras** que **busca en normativas internas**, aplica **reranking** para seleccionar **únicamente los 3 fragmentos más relevantes** y **justifica la aprobación o el rechazo de un gasto**.

**Requisitos:**
1. Leer documentos **no estructurados** (PDFs, uno **escaneado**) y saber **por qué** un analizador de LLM y no el de por defecto.
2. **Cortar** el texto con criterio y elegir una forma de chunking **con datos** (no a ojo).
3. Indexar en **Vector Search** (RAG Engine, modo sin servidores).
4. **Dos etapas:** recuperar K = 20 y reordenar con la Ranking API para quedarse con N = 3.
5. **Umbral** calibrado: si nada es relevante, el agente **escala**; no inventa.
6. Un **agente auditor** con salida estructurada (`AuditDecision`: decisión, justificación y fuentes citadas) que **solo decide con lo que devuelve la herramienta**.
7. Comparar con documentos **estructurados** (markdown por artículo).

**Criterios de aceptación:**
- Los 6 casos de `data/casos_gasto.json` coinciden con lo esperado y **ninguna cita es inventada**.
- Una consulta **fuera del corpus** (el yate) devuelve **ESCALAR** sin citas.
- El agente no decide sin pasar por la herramienta.
- Sus recursos de nube **están borrados** al terminar (Parte 10).

**Entrega:** notebook ejecutado (con los 🎉 de 7.4 y, si hicieron la 9, de 9.4) + repositorio de la célula + demo de 5 min.
**Extensión (opcional):** la **Parte 9** (combinar con el reporte 10-Q) y una prueba con **un quinto documento** de su propia empresa.

> **Qué NO es parte del entregable:** buscar en el reporte trimestral. El entregable dice «normativas internas»; el 10-Q entra en el notebook por el tema de *chunking de reportes* y se combina en la Parte 9 como **extensión**.

## Línea de tiempo y reparto
| Hora | Parte | Tema | Min |
|---|---|---|---|
| 0:00–0:10 | 0 | Preparación | 10 |
| 0:10–0:15 | 1 | Los documentos | 5 |
| 0:15–0:40 | 2 | Leer los PDFs (analizador por defecto contra LLM) | 25 |
| 0:40–1:15 | 3 | Cortar el texto: tres formas de chunking | 35 |
| 1:15–1:25 | 4 | Indexar: embeddings y Vector Search | 10 |
| 1:25–1:50 | 5 | Recuperar en dos etapas (K = 20 → N = 3) | 25 |
| 1:50–2:00 | 6 | Umbral de relevancia | 10 |
| 2:00–2:30 | 7 | **El auditor** (el entregable) | 30 |
| 2:30–2:50 | 8 | Lo mismo con documentos estructurados | 20 |
| 2:50–3:15 | 9 | Combinado con el reporte 10-Q *(extensión)* | 25 |
| 3:15–3:20 | 10 | Limpieza (**obligatoria**) | 5 |

Son **3 h 20 min sin pausas**. Dos formas de repartirlo:

**Opción A — un solo bloque** (recomendada): todo seguido, con **una pausa de 10 min después de la Parte 3**. Si vas justa, **la Parte 9 es lo primero que se recorta** (queda como tarea o demo tuya) y terminas a las 2:55.

**Opción B — dos sesiones de 2 h** (el modelo semanal del cronograma): ⚠️ **hay un problema real.** El estado del notebook vive en la memoria del kernel (`c_A`, `c_B`, `c_C`, `UMBRAL`, las funciones…). Al cerrarlo entre sesiones **se pierde**, mientras que los **corpus siguen en la nube** (y siguen guardando datos). Si partes en dos:
- Sesión 1: Partes 0 a 3 (75 min) más tu teoría.
- **No ejecutes la limpieza** al final de la sesión 1; los corpus se quedan.
- Sesión 2: vuelve a ejecutar las Partes 0 a 3 (los corpus se **reutilizan por nombre**, pero las importaciones se repiten y cuestan unos minutos) y sigue con la 4. ⚠️ **No está probado** reanudar así.
Por eso la Opción A es más segura.

**Qué recortar, en este orden** (de lo que menos daña al entregable): Parte 9 → multimodal (celda de la Parte 4) → Parte 8 (la dejas como demo tuya) → ejercicios 🧪 → Parte 5.3.
**Qué protege el entregable:** Partes 2, 3, 6, 7 y 10.

---
## Preparación de la sala y reglas de juego

**Antes de empezar (5 min antes de que lleguen):**
- Proyecta `practica_instructor.ipynb` **ya ejecutado hasta la Parte 0** (para ir al ritmo del grupo, no por delante).
- Ten una terminal en la raíz del proyecto y la consola de Google Cloud en otra pestaña (RAG Engine → *Corpus*, para enseñar que existen y que se borran).
- Define cómo sabrás quién está atascado: **semáforo** (vaso/papel verde = voy bien, rojo = necesito ayuda) o reacción en el chat.

**Reglas que dices al inicio (2 min):**
> "Esto es una **práctica guiada**, no una clase: aquí se equivocan, y los errores son parte del aprendizaje. Trabajan **en parejas dentro de la célula**: una persona escribe, la otra lee y cuestiona; **rotan en cada parte**. Ejecutan las celdas **en orden**, con Shift+Enter, y **sin repetirlas**: varias crean recursos en la nube y cuestan. Donde vean `🧪`, es un ejercicio: ejecuten primero con el valor que trae, y luego lo cambian. Al final de cada parte hay un **checkpoint**: no avancen hasta verlo. Si se atoran más de **3 minutos**, pongan el semáforo en rojo y voy.
> **Dos reglas de seguridad:** **no ejecuten la celda 2.3** (cambia la configuración de todo el proyecto) y **al final ejecutan la Parte 10**, que borra lo que crearon. Todo lo que crean lleva su usuario en el nombre."

**Mapa de tiempos y checkpoints**
| Hora | Parte | Checkpoint (lo que todos deben tener) |
|---|---|---|
| 0:00 | 0 Preparación | Ven `✅ text-embedding-005 → dimensión 768` |
| 0:10 | 1 Documentos | Ven los 7 archivos, dos «escaneados» |
| 0:15 | 2 Leer PDFs | El escaneado da **0 fragmentos** con el analizador por defecto y ✅ con el de LLM |
| 0:40 | 3 Cortar | La tabla de las tres formas y la elegida (C) |
| 1:15 | 4 Indexar | Entienden que el almacén ya es persistente |
| 1:25 | 5 Dos etapas | El caso de la cena cambia con reranking; ven el **84 % menos de contexto** |
| 1:50 | 6 Umbral | Un hueco entre lo relevante y lo irrelevante; el yate queda sin fragmentos |
| 2:00 | 7 Auditor | 7 ✅ y el 🎉 |
| 2:30 | 8 Estructurado | Las dos columnas de decisiones coinciden |
| 2:50 | 9 Combinado | MIXTA cita una política y el reporte *(extensión)* |
| 3:15 | 10 Limpieza | La celda 2.2 dice `0 corpus existentes` |

**Rotación del code review (10 min por célula; mientras el resto espera una importación o trabaja):**
| Slot | Célula | Mientras ellos están en… |
|---|---|---|
| 0:45–0:55 | 1 | Parte 3 (importaciones B y C) |
| 0:55–1:05 | 2 | Parte 3 |
| 1:05–1:15 | 3 | Parte 3–4 |
| 1:25–1:35 | 4 | Parte 5 |
| 1:35–1:45 | 5 | Parte 5–6 |

---
## Apertura (2 min)

**🎤 Dices:**
> "Al final de hoy tienen que poder demostrar **tres cosas**: que un agente **solo decide con lo que le devuelve una búsqueda** y **dice «no sé»** cuando no hay base, que esa búsqueda funciona sobre **documentos reales** —PDFs, hasta uno escaneado—, y que **cada decisión de diseño** —cómo leer, cómo cortar, cuántos fragmentos, qué umbral— se **mide**, no se adivina. El notebook los lleva paso a paso; yo les voy a decir qué tienen que **ver** en cada paso. Si lo que ven no coincide con lo que digo, **esa es la pista**: me llaman."

**🛠 Haces:** abre el notebook y muestra la tabla de partes. Enseña la consola de RAG Engine **vacía** («así empezamos; así vamos a terminar»).

---
## Parte 0 · Preparación (10 min)

**🎤 Dices (primera celda):**
> "La Parte 0 no tiene nada de agentes. La primera celda **encuentra la raíz del proyecto**, carga el `.env` y **fija que este módulo usa los servicios reales** (`AGENTS_MODE=cloud`) **antes** de importar la configuración. Luego comprueba que estén instalados los paquetes del módulo; si falta alguno, **se detiene y les dice el comando exacto**."

**🎤 Dices (segunda y tercera celda):**
> "La segunda verifica que haya **proyecto y credenciales** (no llama a nada) y **calcula la configuración del reranker** a partir del proyecto. La tercera es la primera que **sí llama a un servicio**: manda dos textos de prueba al modelo de embeddings para confirmar que responde y que devuelve **un vector por texto**. Fíjense en la dimensión: **768 números por texto**. De ahí en adelante, «texto» significa «vector de 768 números»."

**👀 Deben ver:**
```
RAIZ: C:\...\GeminiAgentsBI
Proyecto: <tu-id> | Región Gemini: us-central1
Ranking config: projects/<tu-id>/locations/global/rankingConfigs/default_ranking_config
✅ text-embedding-005 → dimensión 768
Embeddings: text-embedding-005 | Modelo de texto: gemini-2.5-flash | K = 20 | N = 3
```

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `RuntimeError: Faltan paquetes ... pip install ...` | Falta una librería del módulo | Ejecutar **ese** comando en una terminal con el `.venv` activo y **reiniciar el kernel** |
| `ModuleNotFoundError` en cualquier celda | El notebook usa otro Python (kernel equivocado) | *Seleccionar kernel* → el `.venv` del proyecto |
| `StopIteration` al buscar RAIZ | Abrieron el notebook fuera del proyecto | Abrir la carpeta `GeminiAgentsBI` completa |
| `RuntimeError: Falta GOOGLE_CLOUD_PROJECT` | `.env` sin proyecto o con `tu-proyecto` | Poner el **ID** del proyecto (no el nombre) y reiniciar el kernel |
| `RuntimeError: No hay credenciales` | No hicieron el login | `gcloud auth application-default login` |
| `404 NOT_FOUND ... Publisher model` o `Location ... is not found` | `GOOGLE_CLOUD_LOCATION` distinto de `us-central1` en el `.env` | Dejarlo en `us-central1` y reiniciar el kernel |
| `403 ... has not been used in project` | API sin habilitar o cuota en otro proyecto | Que el instructor habilite la API; `gcloud auth application-default set-quota-project <ID>` |
| `❌ text-embedding-005 → ...` en las dos opciones | Vertex AI sin habilitar o permisos | Revisar el proyecto y la región |

**✅ Checkpoint:** todos ven el `✅ text-embedding-005 → dimensión 768`. **No sigas hasta que todas las células lo tengan.**

---
## Parte 1 · Los documentos (5 min)

**🎤 Dices:**
> "Un documento **estructurado** trae marcas que un programa puede seguir: en nuestras políticas en markdown, cada artículo empieza con `## Artículo 1.3`. Basta cortar ahí. Un **PDF** no trae esas marcas de forma utilizable, y un **escaneo** ni siquiera tiene texto: es una **imagen de texto**. Antes de buscar nada hay que **leerlo**. Todo lo que van a ver hoy es consecuencia de esto."

**🛠 Haces:** ejecuta la celda. Señala las dos filas que dicen «escaneado (solo imagen)»: `AUD-2026.pdf` y `10q_norte_3t26_escaneado.pdf`.

**👀 Deben ver:**
```
politicas_pdf  AUD-2026.pdf                     97,500 bytes   escaneado (solo imagen)
politicas_pdf  POL-COB-2026.pdf                  2,151 bytes   con texto
politicas_pdf  POL-CON-2026.pdf                  2,262 bytes   con texto
politicas_pdf  POL-PRE-2026.pdf                  2,297 bytes   con texto
politicas_pdf  POL-VIA-2026.pdf                  2,497 bytes   con texto
reportes       10q_norte_3t26.pdf                4,070 bytes   con texto
reportes       10q_norte_3t26_escaneado.pdf    165,154 bytes   escaneado (solo imagen)
```
(Fíjate: los escaneados pesan **decenas de veces más** y no tienen texto: es una foto.)

**❓ Pregunta de discusión (1 min):** "Si un escaneo no tiene texto, ¿cómo lo lee un programa?" → *Con un modelo que **lee imágenes**, o con OCR. Es lo que veremos en la Parte 2.*

**✅ Checkpoint:** ven los 7 archivos.

---
## Parte 2 · Leer los PDFs: analizador por defecto contra analizador de LLM (25 min)

**🎤 Dices (antes de ejecutar):**
> "Usamos **RAG Engine** en su modo **sin servidores**: nosotros subimos archivos a un bucket de Cloud Storage y él los lee, los corta, calcula los embeddings y los guarda en **Vector Search**. Hoy no administramos servidores. Primero comparamos **dos formas de leer un PDF**, con el mismo reporte importado a **dos corpus**: el analizador **por defecto**, que es gratis, y el **analizador de LLM**, que usa Gemini y se paga por página."

**🛠 Haces:** ejecuta 2.1 a 2.5 (preparación). Pasa rápido por 2.1 (el modo del proyecto), 2.2 (cuántos corpus hay) y 2.3 (**no se cambia nada**: di en voz alta que esa celda es solo del instructor). Detente en 2.4 y 2.6.

**🎤 Dices (celda 2.1):**
> "Esta celda pregunta al proyecto **en qué modo está RAG Engine** y debe decir **sin servidores**. Ese modo es **del proyecto, no suyo**: cambiarlo afecta a todos, por eso la celda 2.3 **no se toca**."

**🎤 Dices (celda 2.4):**
> "Se crea **un bucket con su usuario en el nombre** y se suben los PDFs en dos carpetas. Así los recursos de cada uno **no chocan** con los de sus compañeros."

**🎤 Dices (celda 2.6):**
> "Aquí se crean los dos corpus y se importa **el mismo reporte** con cada analizador. Las operaciones sobre corpus **no admiten concurrencia**, por eso van **una tras otra**. Tarda **unos 20 segundos por importación**. Dos detalles de cómo se crea el corpus: **se indica el backend de forma explícita** y la ruta que se importa es **la carpeta con barra final**. Los dos nos costaron un rato en las pruebas, y los dejamos escritos en el código."

**👀 Deben ver (2.6 y 2.7):**
```
Creado: pdf_defecto_<usuario>
Creado: pdf_llm_<usuario>
✅ importación terminada con el analizador por defecto (21 s)
✅ importación terminada con el analizador de LLM (23 s)

=== analizador por defecto: 1 fragmentos recuperados
  10q_norte_3t26.pdf              1 fragmentos | ✅ utilidad neta (4,015)  ✅ consultoría (2,880)
  10q_norte_3t26_escaneado.pdf    0 fragmentos | ❌ utilidad neta (4,015)  ❌ consultoría (2,880)

=== analizador de LLM: 4 fragmentos recuperados
  10q_norte_3t26.pdf              3 fragmentos | ✅ utilidad neta (4,015)  ✅ consultoría (2,880)
  10q_norte_3t26_escaneado.pdf    1 fragmentos | ✅ utilidad neta (4,015)  ✅ consultoría (2,880)
```
(Los tiempos y el número de fragmentos pueden variar un poco; **lo que no debe variar** es el ❌❌ del escaneado con el analizador por defecto y los ✅ con el de LLM.)

**🔬 Lo que se obtuvo al ejecutarlo — úsalo como demo:**
| | Analizador por defecto | Analizador de LLM |
|---|---|---|
| PDF **con texto** | ✅ lee las cifras | ✅ lee las cifras |
| PDF **escaneado** | ❌ **0 fragmentos, sin error** | ✅ lee la imagen y recupera las cifras |
| Tabla escaneada | no se lee | **HTML** (`<table>`) |
| Texto extra | — | **Añade comentarios propios** («Context: …», en inglés) |

**🎤 Dices (la lección, celda 2.8):**
> "Miren dos cosas. **Una:** el analizador por defecto importó el escaneado **y dijo ✅**, pero **no guardó nada**. Nadie avisa. Es una **pérdida silenciosa**: si no lo miden, creen que ese documento está en su buscador y **no está**. **Dos:** el analizador de LLM leyó hasta una foto, pero lo que devuelve es **texto que escribió un modelo**: la tabla en HTML y comentarios que no están en el documento. Sirve para buscar mejor, pero **hay que verificar las cifras contra el original**: abran el PDF y comparen 4,015 con la tabla de la pantalla."

**❓ Preguntas de discusión (2 min) y respuestas:**
1. "¿Qué analizador usarías para un PDF con texto simple?" → *El de por defecto: gratis y suficiente.*
2. "¿Y para un escaneo o una tabla compleja?" → *El de LLM, y se paga por página; la documentación pone como ejemplo 1,000 PDFs de 50 páginas ≈ US$3.75.*
3. "¿Cómo te enterarías de que un documento no se indexó?" → *Contando fragmentos por archivo, como hace la celda 2.7.*
4. "¿Qué otra opción existe?" → *El **Layout Parser de Document AI**, especializado en estructura; necesita crear un procesador aparte y **no lo ejecutamos**.*

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `RuntimeError: El proyecto no está en modo sin servidores` (celda 2.4) | El modo es del proyecto | **No sigas**: avisa al instructor |
| `Vector Search API has not been used in project ...` | API sin habilitar | El instructor habilita `vectorsearch.googleapis.com` (`COMANDOS.md`, paso 3); espera unos minutos |
| `ValueError: Bucket ... does not belong to project ...` | **Casi siempre es Cloud Resource Manager** deshabilitada: el SDK oculta el error real | El instructor habilita `cloudresourcemanager.googleapis.com` |
| `... does not exist or is empty` | La ruta no es la carpeta con barra final, o el bucket no tiene archivos | Volver a ejecutar 2.4 y comprobar la lista de archivos |
| `No available indexing project found` | Corpus creado sin indicar el backend (ya lo evita el código) | Si aparece igual, avisa al instructor |
| Una operación de corpus falla porque hay otra en curso | Concurrencia: otro compañero (o tú) tiene una operación activa | Esperar un minuto y repetir **solo esa celda** |
| `ExperimentalWarning: The Vertex SDK GenAI rag module is experimental` | El módulo es experimental | Esperado; no es un error |

**✅ Checkpoint:** ven el ❌❌ del escaneado con el analizador por defecto y los ✅✅ con el de LLM.

---
## Parte 3 · Cortar el texto: tres formas de chunking (35 min)

**🎤 Dices (antes de ejecutar):**
> "Ya sabemos **leer**. Ahora hay que **cortar** el texto en fragmentos, y es la decisión que más pesa en la calidad de un RAG. Comparamos **tres formas**. **A:** subimos los PDFs tal cual y el **servicio** los corta. **B:** tomamos el texto que ya extrajo el analizador y lo cortamos **nosotros por significado**: donde baja la similitud entre una oración y la siguiente. **C:** lo cortamos **nosotros por estructura**: un trozo por artículo. Los de B y C los **subimos como archivos**, uno por trozo, para que el servicio respete nuestros cortes: cada archivo es más corto que su tamaño de corte, así que queda entero. En un proyecto real eso se llama **etapa de preparación de documentos**."

**🛠 Haces:** ejecuta 3.1 y 3.2, y luego **detente** en 3.3.

**👀 Deben ver (3.2):**
```
Forma A: 5 fragmentos · anotaciones «Context»: 0
  AUD-2026       | artículos: 5.1, 5.2, 5.3              |   389 car.
  POL-COB-2026   | artículos: 4.1, 4.2, 4.3, 4.4         |   603 car.
  POL-CON-2026   | artículos: 2.1, 2.2, 2.3, 2.4         |   767 car.
  POL-PRE-2026   | artículos: 3.1, 3.2, 3.3, 3.4         |   810 car.
  POL-VIA-2026   | artículos: 1.1, 1.2, 1.3, 1.4, 1.5    |  1085 car.
```

**🎤 Dices (3.2):**
> "Cinco documentos, **cinco fragmentos**: cada política salió **entera** en un solo trozo. El servicio no partió nada. Y fíjense en la cuarta columna: cada fragmento trae **cuatro o cinco artículos juntos**. Si el agente cita este fragmento, ¿qué artículo está citando? **Todos**. Se acaba de perder la precisión de la cita. Ese es el costo de dejar que el servicio corte."
> *«Anotaciones Context: 0»: con el prompt propio que usamos para leer las políticas, el analizador **ya no añade** esos comentarios en inglés. El prompt controla el formato.*

**👀 Deben ver (3.3: los mismos artículos cortados de tres formas):**
```
=== A · RAG Engine (lo que dejó el servicio): 1 trozos
=== C · por estructura (en cada «Artículo»): 6 trozos     (el encabezado + un trozo por artículo 1.1 a 1.5)
=== B · semántico (donde baja la similitud): 3 trozos
```
Lo que se obtuvo con **B** en la corrida de ensayo: `[1.1, 1.2, 1.3]` · `[1.4]` · `[1.5]`. ⚠️ **Este corte no es fijo**: en la corrida de un alumno B dejó `[1.1, 1.2, 1.3, 1.4]` · `[1.5]` (el 1.4 junto a la regla). El analizador de LLM no devuelve el texto idéntico cada vez (la política de consultoría salió con 767 y 765 caracteres en dos corridas) y el corte semántico depende de ese texto. Mira qué salió en tu proyector y **di lo que realmente se ve**.

**🎤 Dices (3.3):**
> "Esto es **la misma política** cortada de tres formas. **C** acierta siempre, pero **solo si el texto conserva los encabezados**: en un PDF mal leído no hay dónde cortar. **B** no necesita marcas, corta donde cambia el tema… pero es una **heurística**. Miren **dónde cortó**. **En nuestra corrida de ensayo** dejó el Art. 1.3 con el 1.1 y el 1.2, y **separó el 1.4 en su propio trozo**. El 1.3 es la **regla** (los viajes sin autorización se rechazan) y el 1.4 es la **excepción** (salvo emergencia). Si el agente recibe solo el trozo de la regla, **no ve la excepción**. Ese es el peor error de un corte semántico."
> *Si en tu corrida B dejó el 1.3 y el 1.4 juntos:* "Aquí tuvo suerte y los dejó juntos. Pero **no es una garantía**: es una heurística. Cambien el percentil en el ejercicio 3 y vean si sigue acertando."

**🔬 Una observación de una corrida previa (úsala si preguntan por el tamaño):** al pedir cortes de **128 tokens** en lugar de 512 con el analizador de LLM, los fragmentos **no cambiaron**: cada política siguió entera. **No sabemos por qué**: puede que ese analizador decida sus propios cortes. Por eso en este notebook **no jugamos con el tamaño**, sino con **quién corta**.

**👀 Deben ver (3.4 y 3.5):**
```
B: 14 archivos · C: 20 archivos
✅ B: importado en 12 s
✅ C: importado en 12 s

forma                                fragmentos  arts/fragmento  Hit@3 sin  Hit@3 con
A · RAG Engine (cortes del servicio)          5             4.0        6/6        6/6
B · semántico, nuestro                       14             1.5        6/6        6/6
C · por estructura, nuestro                  20             1.1        6/6        6/6

→ Seguimos con la forma C · por estructura, nuestro
```

**🎤 Dices (3.5, la lección):**
> "Las tres sacan **6 de 6**. Si midiéramos solo el Hit@3, diríamos que da igual. Pero fíjense en la columna de **artículos por fragmento**: 4.0, 1.5 y 1.1. **Lo que las distingue es la precisión de la cita**, y el Hit@3 no lo ve. Por eso el notebook **desempata** por esa columna y elige la **C**. Lección: **una métrica puede empatar y aun así haber una diferencia que importa**; hay que mirar más de una."

**❓ Preguntas de discusión (3 min) y respuestas:**
1. "¿Por qué las tres empatan en Hit@3?" → *Es un corpus de 20 artículos; el acierto es fácil. Con cientos de documentos, probablemente no empatarían.*
2. "¿Cuándo usarías cada forma?" → *C si el texto conserva la estructura; B si no hay marcas (un PDF sin encabezados, un correo, una transcripción); A cuando lo genérico basta.*
3. "¿Se pueden combinar?" → *Sí, y es lo habitual: primero por estructura y solo las secciones muy largas por significado.*
4. "¿Por qué subir los trozos como archivos?" → *Porque RAG Engine solo corta por tamaño: si cada archivo es más corto que el corte, queda entero y se respeta nuestro criterio.*

**🧪 Ejercicio 3 (alumnos, 5 min):** cambian `PERCENTIL` de 25 a **10** y a **50** y miran cuántos trozos salen y si el Art. 1.3 queda separado del 1.4. *(Resultado de otros percentiles: ⚠️ no se probó; lo esperable es que con un percentil más bajo haya menos cortes y con uno más alto, más. Pídeles que lo observen y lo cuenten.)* **Para pensar** (después de la tabla 3.5): por qué el Hit@3 no refleja la cita menos precisa de A, y qué otra medida usarían.

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `NameError: c_A` / `FRAG_A` | No ejecutaron 3.1 o 3.2 | Ejecutarlas **en orden** |
| `RuntimeError: La Ranking API falló ...` (3.5) | Discovery Engine sin habilitar, permisos o `RANKING_CONFIG` | El mensaje lo dice; el instructor habilita la API |
| Las importaciones de B y C tardan mucho | Otros compañeros operando a la vez (concurrencia) | Esperar; repetir solo esa celda si falla |
| Cuentan **más o menos de 14/20 archivos** | El texto extraído por el analizador cambió | Normal: el analizador es un modelo y no es determinista |
| 3.3 imprime otros trozos para B (por ejemplo, el 1.4 junto al 1.3) | El corte semántico depende del texto que extrajo el analizador, y ese texto cambia de una corrida a otra | Normal; lo que importa es **si separó la regla de su excepción**. Si no la separó, úsalo como lección: un corte semántico puede acertar por suerte (ejercicio 3) |

**✅ Checkpoint:** ven la tabla de tres formas y que el notebook eligió la **C**.

---
## Parte 4 · Indexar: embeddings y Vector Search (10 min)

**🎤 Dices:**
> "Aquí **no hay nada que ejecutar para indexar**: ya pasó. Al importar, RAG Engine **calculó los embeddings** de cada fragmento (768 números por texto) y los **guardó en Vector Search**, creando una colección por corpus en nuestro proyecto. Lo importante: **el almacén es persistente**. Si cierro el notebook, los vectores siguen ahí. Un índice en memoria, como el que haremos en la Parte 8, se pierde al cerrar. Eso es lo que pide el cronograma: *embeddings y almacenamiento en Vector Search*."

**🎤 Dices (celda multimodal, opcional):**
> "Los embeddings no son solo de texto. `gemini-embedding-2` pone **texto e imágenes en el mismo espacio**. Dibujamos en memoria un gráfico de barras y lo comparamos con dos frases: la imagen se parece **más** a «gráfico de barras con ingresos trimestrales» que a «receta de paella». **Cuándo sirve:** buscar un gráfico con una pregunta en texto. **Ojo:** para **tablas** en documentos, suele ser mejor un **analizador** que embeber la imagen."

**👀 Deben ver (💸 3 llamadas pequeñas):**
```
✅ gemini-embedding-2 respondió: imagen y texto en el mismo espacio (3072 dim.)
  similitud imagen ↔ «gráfico de barras con ingresos trimestrales»: 0.401
  similitud imagen ↔ «receta de paella valenciana»: 0.219
```
(La imagen **debe** parecerse más al texto del gráfico que a la paella; los números exactos pueden variar.)

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `404 NOT_FOUND ... gemini-embedding-2` | Ese modelo solo está en `global`, `us` y `eu`, **no** en `us-central1`. El notebook ya usa un cliente `global` para esta celda | Si aun así falla, la celda **avisa y no rompe nada**: sigue |
| La celda dice `⚠️ No pude usar gemini-embedding-2` | El modelo no está disponible en el proyecto | Se puede **saltar**; el resto no depende de ella |

**✅ Checkpoint:** entienden que el almacén es persistente (y, si la hicieron, ven la similitud imagen ↔ gráfico mayor que la de la paella).

---
## Parte 5 · Recuperar en dos etapas: K = 20 → N = 3 (25 min)

**🎤 Dices (antes de ejecutar):**
> "La búsqueda tiene **dos etapas**. **Etapa 1:** la búsqueda vectorial trae los **20 fragmentos más cercanos**; es **rápida pero basta**, compara vectores. **Etapa 2:** la **Ranking API** —un modelo que **lee la pregunta y cada fragmento juntos**— los reordena y nos quedamos con **3**. Más lenta, pero más precisa. K = 20 y N = 3 vienen del cronograma. Medimos con los **6 casos** de gasto: un caso **acierta** si alguno de los artículos esperados aparece en los 3 fragmentos."

**👀 Deben ver (5.1):**
```
Forma elegida: C · por estructura, nuestro

caso  esperado  solo etapa 1                   con reranking
G1    1.2,1.5   ['1.2', '1.3', '1.5'] ✅        ['1.2', '1.3', '1.5'] ✅
G2    1.3       ['1.1', '1.2', '1.3'] ✅        ['1.2', '1.3', '1.5'] ✅
...
Hit@3  sin reranking: 6/6   con reranking: 6/6
(6, 6)
```
(El `(6, 6)` suelto al final es el valor que devuelve la función: **no es un error**. ⚠️ Es un detalle cosmético sin arreglar.)

**🎤 Dices (5.1, honestidad):**
> "Seis de seis **sin** reranking y seis de seis **con** reranking. ¿Entonces el reranking no sirve? **Con este corpus, no se nota.** Son solo 20 artículos y K es 20: la etapa 1 ya devuelve **todo el corpus**. No hay nada que mejorar. Esa es una **limitación de nuestro ejemplo**, no del método. El reranking brilla cuando hay cientos de documentos. Para ver el efecto, miren este caso."

**👀 Deben ver (5.2, la cena sin factura):**
```
Solo etapa 1:                                    Con reranking:
  POL-VIA-2026, Art. 1.5 (Comprobación)            0.456  POL-VIA-2026, Art. 1.5 (Comprobación)
  AUD-2026, Art. 5.3 (Conflicto de interés)        0.218  AUD-2026, Art. 5.3 (Conflicto de interés)
  AUD-2026, Art. 5.1 (Evidencia)                   0.147  POL-COB-2026, Art. 4.2 (Provisión)
→ el reranking CAMBIÓ el top-3
```

**🎤 Dices (5.2):** "El tercer lugar **cambió**: la etapa 1 puso la nota de auditoría de *evidencia*, y el reranker prefirió la política de *provisión*. Además, ahora hay un **puntaje**: 0.456 contra 0.147. **Ese puntaje es lo que vamos a usar para el umbral en la Parte 6.**"

**👀 Deben ver (5.3 y 5.4):**
```
K =  3 → Hit@3 con reranking: 6/6
K =  5 → Hit@3 con reranking: 6/6
K = 10 → Hit@3 con reranking: 6/6
K = 20 → Hit@3 con reranking: 6/6
(el corpus elegido tiene 20 fragmentos en total)

Con los 20 candidatos:  3,515 caracteres · 1,052 tokens (exacto)
Con los 3 del reranking:    642 caracteres ·   173 tokens (exacto)
→ el modelo recibe 84 % menos contexto
```

**🎤 Dices (5.4):**
> "El cronograma dice que el reranking sirve para **optimizar la ventana de contexto**. Aquí está **medido**: al modelo le llegan **173 tokens en lugar de 1,052**, un **84 % menos**. Menos tokens es **menos costo** y **menos ruido** para el modelo. Y esto con un corpus pequeño; con fragmentos más largos, la diferencia crece."

**❓ Preguntas de discusión (4 min) y respuestas:**
1. "¿Cómo se eligen K y N en un proyecto real?" → ***K:*** *lo bastante grande para que el fragmento correcto esté entre los candidatos; se mide el recall@K con un conjunto de preguntas conocidas y se elige el menor K donde deja de mejorar.* ***N:*** *cuántos fragmentos necesita el modelo para responder (1 a 3 para un dato; 5 a 10 si cruza fuentes); se prueba con las mismas preguntas.*
2. "¿Por qué todos los K dan 6/6?" → *Mismo motivo: el corpus es tan chico que la respuesta está siempre entre los primeros.*
3. "¿Qué cambia si el corpus tuviera 500 documentos?" → *K = 3 empezaría a perder aciertos, y el reranking sí aportaría.*

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `RuntimeError: La Ranking API falló ...` | Discovery Engine sin habilitar, permisos o `RANKING_CONFIG` | El instructor habilita `discoveryengine.googleapis.com` |
| `InvalidArgument: 400 RankRequest.records() is empty` | El reranker recibió **0 candidatos**: la búsqueda anterior no devolvió nada (corpus aún sin indexar, o no se reconoció el texto) | Esperar un minuto y repetir la celda anterior |
| Los puntajes difieren de los de la guía | El reranker es un modelo | Normal; lo que importa es el **orden** |

**✅ Checkpoint:** ven el caso de la cena cambiar con reranking y el **84 %** menos de contexto.

---
## Parte 6 · Umbral de relevancia: poder decir «no sé» (10 min)

**🎤 Dices (antes de ejecutar):**
> "El reranking **siempre devuelve tres fragmentos**, aunque la pregunta no tenga **nada que ver** con el corpus. Un auditor que contesta con lo que sea es **peligroso**. La solución es un **umbral**: si ni el mejor fragmento lo supera, **no se aprueba ni se rechaza: se escala**. ¿Cómo se elige? Se miden los mejores puntajes de preguntas **cubiertas** por el corpus y de preguntas que **no tienen nada que ver**. Si hay un hueco entre los dos grupos, cualquier valor dentro lo separa."

**👀 Deben ver (6.1):**
```
  consultas CUBIERTAS:        (mínimo 0.202: «Contrato de consultoría por USD 80,000...»)
    0.354 ... 0.479 ... 0.739 ... 0.479 ... 0.202 ... 0.744
  consultas FUERA del corpus:
    0.032  Compra de un yate para la dirección
    0.014  Receta de paella valenciana para ocho personas
    0.023  xyzzy qwerty plugh

máximo de las irrelevantes = 0.032   mínimo de las relevantes = 0.202
→ hay un hueco: cualquier umbral dentro de ese rango separa los dos grupos

UMBRAL elegido: 0.12
«Compra de un yate para la dirección» → 0 fragmentos tras el umbral → ESCALAR
```

**🎤 Dices:**
> "Lo irrelevante **nunca pasa de 0.032**; lo relevante **nunca baja de 0.202**. Hay un hueco enorme, y el notebook toma el **punto medio**, 0.12. El yate **se queda sin fragmentos**, y eso significa ESCALAR. **Dos advertencias.** **Una:** este umbral **solo vale para este corpus y este reranker**. Cambien cualquiera de los dos y hay que **calibrarlo de nuevo**. En la Parte 8 verán que el mismo método da **0.14**, porque los puntajes cambian. **Dos:** con un hueco así de limpio es fácil; con documentos reales los grupos suelen **solaparse**, y ahí hay que decidir **qué error cuesta más**: escalar de más, o contestar sin base."

**🧪 Ejercicio 6 (alumnos, 5 min):** eligen **su** umbral (uno dentro del hueco, uno muy bajo y uno muy alto) y miran cuántos fragmentos pasan para las consultas **fuera del corpus** (deben quedar en cero) y para las **cubiertas** (deben conservar al menos uno). *(Lo esperable: un umbral demasiado bajo deja pasar el yate; uno demasiado alto deja sin evidencia casos legítimos. ⚠️ No se probó con valores distintos; que lo observen.)* **Al terminar, deben dejar un valor razonable**, porque lo usan las partes siguientes.

**❓ Preguntas de discusión (2 min) y respuestas:**
1. "¿Qué pasa con un umbral demasiado bajo?" → *El agente decide con evidencia irrelevante: contesta cosas que no sabe.*
2. "¿Y con uno demasiado alto?" → *Escala casos que sí podía resolver: el auditor se vuelve inútil.*
3. "¿Cuándo hay que recalibrar?" → *Cada vez que cambia el corpus, el reranker o los documentos.*

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `UMBRAL` queda muy bajo o muy alto tras el ejercicio | Dejaron el valor del experimento | Volver a ejecutar 6.1 para recuperar el calculado |
| Dice `NO hay hueco limpio ... uso el mínimo de las relevantes` | Los grupos se solapan con sus documentos | Es una **buena señal para discutir**: revisar los casos antes de aceptar el valor |

**✅ Checkpoint:** ven el hueco, un umbral razonable y el yate sin fragmentos.

---
## Parte 7 · El auditor sobre documentos no estructurados (30 min)

**🎤 Dices (antes de ejecutar):**
> "Juntamos todo. Una **herramienta** hace el RAG de dos etapas con el umbral y devuelve **citas**. Un **agente** decide con **solo** lo que la herramienta le devuelve y responde con una **salida estructurada**: decisión, justificación y fuentes citadas. La **lista vacía** significa «no apruebes ni rechaces: escala». Y para no repetir código después, la herramienta y el agente se **fabrican** con funciones que reciben **una sola cosa que cambia: de dónde salen los candidatos**."

**🛠 Haces:** ejecuta 7.1 y explica las tres funciones (`evidencia`, `herramienta_de`, `auditor_con`). Insiste en que **la instrucción dice «si la lista de citas está vacía… responde ESCALAR»**.

**👀 Deben ver (7.1):**
```
3 citas
  0.527  POL-VIA-2026, Art. 1.3 (Autorización previa)
  0.214  POL-VIA-2026, Art. 1.4 (Excepciones por emergencia)
  0.207  POL-VIA-2026, Art. 1.2 (Límites diarios)
```

**🎤 Dices (7.1):**
> "Esto es **lo que ve el agente**: tres citas con su puntaje, ya filtradas por el umbral. Fíjense en el **0.527** del Art. 1.3: la regla de autorización previa, justo lo que busca un viaje sin autorización. **El agente no ve los documentos**; ve **esto**."

**👀 Deben ver (7.2, los eventos):**
```
👤 Viaje internacional de 4 días, USD 2,400 total, sin autorización previa del Director
   🔧 [auditor_politicas_pdf] llama buscar_politicas({'consulta': '...'})
   📥 [auditor_politicas_pdf] resultado de buscar_politicas: {'query': ..., 'citations': …
🤖 [auditor_politicas_pdf] {
  "decision": "RECHAZADO",
  "justificacion": "El viaje excede los USD 1.500 y no cuenta con la autorización previa por escrito del Director de División...",
  "articulos_citados": ["POL-VIA-2026, Art. 1.3 (Autorización previa)", ...]
}
```
(Un aviso `there are non-text parts in the response: ['function_call']` es **normal**.) La redacción cambia; **la decisión y el Art. 1.3 no**.

**🎤 Dices (7.2):**
> "Tres símbolos: **🔧** el agente decidió llamar a la herramienta, **📥** lo que ella devolvió, **🤖** la decisión. Pregúntense: **¿de dónde sale 'Art. 1.3'?** De la **herramienta**, no del modelo. Y fíjense que **la consulta que el agente mandó a la herramienta no es la que escribí yo**: el modelo la **reformuló**. Eso es normal, pero tiene una consecuencia: **si reformula mal, la búsqueda trae otra cosa**."

**👀 Deben ver (7.3 y 7.4):**
```
caso   esperado   obtenido   citas inválidas
G1     APROBADO   APROBADO   ninguna
G2     RECHAZADO  RECHAZADO  ninguna
G3     APROBADO   APROBADO   ninguna
G4     RECHAZADO  RECHAZADO  ninguna
G5     RECHAZADO  RECHAZADO  ninguna
G6     APROBADO   APROBADO   ninguna
FUERA  ESCALAR    ESCALAR    ninguna

✅ Etapa 1 devuelve candidatos (hasta K = 20)
✅ Etapa 2 devuelve como máximo N = 3
✅ El umbral deja vacía una consulta fuera del corpus
✅ Las 7 respuestas del agente son AuditDecision válidas
✅ Los 6 casos coinciden con lo esperado
✅ FUERA: ESCALAR sin citas
✅ Ninguna cita del agente es inventada
 🎉 El auditor funciona sobre documentos no estructurados
```

**🎤 Dices (la lección escondida):**
> "Si con Gemini algún caso falla aunque la respuesta parezca razonable, **no concluyan que algo está roto**: la tabla muestra la **justificación** del agente; léanla primero. Acaban de descubrir **por qué evaluar agentes es difícil**: el modelo no es determinista. En la semana cinco veremos cómo medirlo sin depender del texto exacto."

**🧪 Ejercicio 7 (alumnos, 5 min):** en la celda 7.1 ponen `QUITAR_REGLA_ESCALAR = True` (la instrucción deja de decir «si no hay citas, escala»), ejecutan 7.1 de nuevo, y vuelven a ejecutar **7.3**. La pregunta: **¿qué responde ahora el agente con el yate**, cuando la herramienta le devuelve una lista **vacía** pero la instrucción ya no le dice qué hacer? **¿Por qué hacen falta las dos cosas: el umbral y la instrucción?** Al terminar vuelven a ponerlo en `False`. *(Resultado: ⚠️ no se probó. Depende del modelo; pídeles que lo observen y lo discutan. Es un buen momento para repetir: **el umbral decide qué ve el agente; la instrucción decide qué hace con lo que no ve**.)*

**❓ Preguntas de discusión (3 min) y respuestas:**
1. "¿Qué evento demuestra que el agente no inventó el artículo?" → *El 📥: la cita viene de la herramienta.*
2. "¿Dónde viven los 'Art. 1.3': en el prompt o en el almacén?" → *En el almacén; el modelo no los memoriza.*
3. "Si el agente reformula la consulta y busca algo distinto, ¿quién lo detecta?" → *Nadie, salvo que miremos el 📥 y las citas. Por eso se revisa el rastro de eventos.*

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `NameError: auditor_con` / `recuperar_pol` | No ejecutaron 7.1 o la Parte 3 | Ejecutar en orden |
| `ValidationError ... must be a valid Python identifier` | El `name` del agente tiene espacios o caracteres raros | Solo letras, números y `_` |
| `PermissionDenied` / 403 / 429 | Credenciales o cuota | Esperar un minuto si es 429; revisar `gcloud auth application-default login` |
| `⚠️ no es AuditDecision` en la tabla | El modelo no devolvió el formato esperado | Repetir esa celda; si persiste, mostrar la respuesta cruda |
| Un caso no coincide | **No determinismo** o el reformulado de la consulta | Leer la **justificación** que muestra la tabla antes de concluir que algo falló |
| El agente responde **sin 🔧** | Instrucción débil (o `QUITAR_REGLA_ESCALAR = True`) | Dejarla en `False` y volver a ejecutar 7.1 |

**✅ Checkpoint:** cada célula muestra **🎉 El auditor funciona sobre documentos no estructurados** (captura para la entrega).

---
## Parte 8 · Lo mismo con documentos estructurados (20 min)

**🎤 Dices:**
> "Ahora el **mismo auditor** con las políticas en **markdown**, cortadas **por artículo**: un fragmento es **un** artículo. Los vectores viven **en memoria**, pero el reranker, el umbral y el agente son **los mismos**. Solo cambia una función: la que da los candidatos. La pregunta de esta parte es: **¿qué compra la estructura?**"

**👀 Deben ver (8.1 a 8.3):**
```
20 chunks (uno por artículo) · matriz en memoria: (20, 768)
...
Hit@3  sin reranking: 6/6   con reranking: 6/6

máximo de las irrelevantes = 0.039   mínimo de las relevantes = 0.250
UMBRAL_E = 0.14

caso   esperado   obtenido   PDF
G1     APROBADO   APROBADO   APROBADO
...(las 7 filas coinciden en las dos columnas)
```

**🎤 Dices (8.2):**
> "Miren los números: con los PDFs, lo irrelevante llegaba a **0.032** y lo relevante bajaba a **0.202**. Con el markdown, **0.039** y **0.250**. **Mismo reranker, misma pregunta, otros puntajes**, porque el texto es distinto. **Por eso el umbral se calcula otra vez**: 0.12 allí, 0.14 aquí. Un umbral copiado de otro corpus es un error silencioso."

**🎤 Dices (8.3, la lección):**
> "Las **decisiones son idénticas**. Entonces ¿qué compra la estructura? Tres cosas: las **citas son exactas** («Art. 1.3», no «Arts. 1.1 y 1.2 y 1.3…»), el reranking tiene **artículos sueltos entre los que elegir**, y **no hay cortes que separen una regla de su excepción**. A cambio, hace falta que el documento **tenga** esa estructura, o alguien que la reconstruya. Con PDFs no estructurados, **leer y cortar bien es el trabajo**; con documentos estructurados, **ese trabajo ya está hecho**."

**❓ Pregunta de discusión (2 min):** "Si todo da igual, ¿para qué leer PDFs?" → *Porque en la vida real, los documentos **no** llegan estructurados. La estructura es un lujo que alguien tuvo que fabricar.*

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `NameError: recuperar_est` / `auditor_con` | No ejecutaron 7.1 o 8.1 | Ejecutar en orden |
| Las dos columnas no coinciden en algún caso | No determinismo | Leer la justificación que imprime la tabla; no es un error |

**✅ Checkpoint:** las dos columnas de decisiones coinciden y ven los dos umbrales distintos.

---
## Parte 9 · Combinado: políticas por artículo + reporte 10-Q (25 min) — *extensión*

> Esta parte **no es el entregable** (el entregable busca en normativas). **Recórtala sin culpa** si vas justa. Si la haces, el mensaje central es **qué pasa al mezclar fuentes**.

**🎤 Dices (antes de ejecutar):**
> "En una empresa real los documentos no llegan todos iguales: las **políticas** son un reglamento limpio y el **reporte trimestral** llega como PDF. Cada uno se trata a su manera y el auditor busca en **los dos a la vez**. Una pregunta que **necesita las dos**: la cifra de consultoría sale del reporte (+60 %, sin aprobación del Comité) y la regla sale de las políticas. **Un riesgo al mezclar:** si el reranker ordena todo junto, los fragmentos **largos** de una fuente pueden quedarse con **los 3 lugares**, y la otra fuente **nunca llega al agente**. En una corrida previa pasó justo eso: la pregunta mixta recibió **solo el reporte** y no vio la política."

**👀 Deben ver (9.2):**
```
SIN cuotas (todo junto):                                     CON cuotas (2 políticas + 1 reporte):
  0.726  10-Q ... (PDF escaneado), fragmento 2                 0.726  10-Q ... (PDF escaneado), fragmento 2
  0.484  10-Q ... (PDF), fragmento 1                           0.451  POL-CON-2026, Art. 2.3 (Exceso presupuestal)
  0.451  POL-CON-2026, Art. 2.3 (Exceso presupuestal)          0.322  POL-CON-2026, Art. 2.1 (Principio general)
```

**🎤 Dices (9.2):**
> *(En la corrida de ensayo.)* "Sin cuotas, **dos de los tres lugares fueron del reporte**. Con cuotas —**dos para las políticas, uno para el reporte**— el agente recibe **las dos fuentes**. Cuesta **lo mismo**: sigue siendo **una sola llamada al reranker**; la cuota se aplica **después** de ordenar. **Una salvedad honesta:** el Art. 2.1 que entró, «Principio general», es **más débil** (0.322) que el fragmento del reporte que quedó fuera (0.484). La cuota **garantiza presencia**, pero a veces mete un fragmento menos relevante. El **umbral** es la protección: si no llega, no entra."
> ⚠️ **Esto no es fijo.** En la corrida de un alumno el 10-Q se partió distinto (3 fragmentos en vez de 4) y, **con y sin cuotas, el resultado fue el mismo** (dos políticas y un fragmento del reporte): las cuotas no cambiaron nada. Si te pasa, dilo así: "las cuotas **garantizan** presencia, pero solo se nota cuando una fuente se llevaría todos los lugares; hoy no pasó". Y usa el ejercicio 9 con `{"políticas": 3, "reporte": 0}` para ver su efecto.

**👀 Deben ver (9.3 y 9.4):**
```
🤖 MIXTA: { "decision": "RECHAZADO", "justificacion": "... Según la política POL-CON-2026, Art. 2.3 ... requiere la aprobación del Comité Financiero ...",
            "articulos_citados": ["POL-CON-2026, Art. 2.3 ...", "POL-CON-2026, Art. 2.1 ...", "10-Q 3T 2026 (PDF escaneado), fragmento 2 ..."] }

caso   esperado   obtenido   PDF        MD
...(los 6 casos coinciden)
MIXTA  RECHAZADO  RECHAZADO  —          —
FUERA  ESCALAR    ESCALAR    ESCALAR    ESCALAR

✅ Las 8 respuestas son AuditDecision válidas
✅ MIXTA: RECHAZADO citando una política y el reporte
✅ FUERA: ESCALAR sin citas
✅ Ninguna cita inventada
✅ Los 6 casos coinciden con lo esperado (¿el reporte los alteró?)
```
(⚠️ **La decisión de MIXTA no es fija:** en la corrida de ensayo dio `RECHAZADO`; en la de un alumno dio `ESCALAR` (el modelo razonó que no podía saber si el aumento estaba presupuestado), y la comprobación 9.4 mostró ❌ en esa línea. Es una respuesta defendible, no un fallo: la lección es que la decisión depende de **qué fragmentos recibió**.) (La justificación de MIXTA dice que el reporte «no detalla específicamente la partida de consultoría»: el único fragmento del reporte que pasó la cuota no traía la nota con ese detalle. **Es un compromiso real**: más cuota para el reporte da más contexto y más ruido.)

**🧪 Ejercicio 9 (alumnos):** cambian `CUOTAS` en 9.2 a `{"políticas": 3, "reporte": 0}` y a `{"políticas": 1, "reporte": 2}` (la suma debe seguir siendo N = 3), ejecutan **9.2 y 9.3**, y observan **cuándo deja de citar la política** y **cuándo deja de ver el reporte**. Después: ¿en qué casos preferirían un **enrutador** (que decida a qué fuente preguntar) a las cuotas? *(⚠️ no se probó con otras cuotas.)*

**🎤 Dices (la lección de la última comprobación):**
> "Fíjense en la última línea. El 10-Q habla de la **división Norte** y de **consultoría**, igual que los casos G3 y G4. Al **añadir un documento sobre el mismo tema**, el agente recibe **evidencia nueva** y **sus respuestas pueden cambiar**. En esta corrida **no cambiaron**, pero **podrían**. Cada vez que amplíen un corpus, **vuelvan a correr sus casos**."

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `NameError: c_llm` | No ejecutaron la Parte 2 | Ejecutarla; esa celda crea el corpus del reporte |
| MIXTA cita **solo el reporte** | Cuotas mal puestas, o la consulta reformulada pierde las palabras de la política | Revisar `CUOTAS` y mirar el rastro de la herramienta |
| ❌ en «los 6 casos coinciden» | El reporte alteró algún caso | **No es un bug**: leer la justificación; es la lección de la parte |
| ❌ en «MIXTA: RECHAZADO citando una política y el reporte» (la decisión salió `ESCALAR`) | La evidencia que recibió el agente cambió (el analizador parte el 10-Q distinto en cada corrida) y Gemini no es determinista | **No es un bug**: leer la justificación y las citas. Si cita una política y el reporte y explica por qué no puede decidir, es un resultado razonable |

**✅ Checkpoint (si la hicieron):** MIXTA cita una política **y** el reporte (la decisión puede ser `RECHAZADO` o `ESCALAR`).

---
## Parte 10 · 🧹 Limpieza (5 min) — **obligatoria**

**🎤 Dices:**
> "Esta es la **única parte que no es opcional**. Cada uno de ustedes creó **cinco corpus y un bucket** en el proyecto. Mientras existan, **siguen guardando datos y siguen costando**. Ejecuten la celda de limpieza; después **vuelvan a la celda 2.2** y compruebo yo que dice `0 corpus existentes`."

**🛠 Haces:** ejecuta la limpieza en el proyector; luego la celda 2.2; abre la consola de RAG Engine y enséñala **vacía** otra vez.

**👀 Deben ver:** una respuesta de borrado por corpus (cinco: `pdf_defecto`, `pdf_llm`, `pol_A`, `pol_B`, `pol_C`) y `limpieza enviada: vuelve a ejecutar la celda 2.2...`. Después, en 2.2: `0 corpus existentes en us-central1`.

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `NameError: CORPUS_CREADOS` / `gcs` | Reiniciaron el kernel antes de limpiar | Borrar desde la terminal: `python modulo2_rag_reranking/preparar_corpus.py --limpiar` **solo sirve para los corpus de ese script**; para los del notebook, desde la consola de RAG Engine |
| Un borrado falla por otra operación en curso | Concurrencia | Esperar un minuto y repetir la celda |
| 2.2 todavía lista corpus | El borrado es asíncrono | Esperar un minuto y repetir 2.2 |

**✅ Checkpoint final:** la celda 2.2 dice **`0 corpus existentes`** (captura para la entrega).

---
## Cierre (5 min)

**🎤 Dices:**
> "Hoy construyeron lo esencial de un **RAG financiero**: **leyeron documentos reales** —hasta un escaneo—, **eligieron cómo cortarlos con datos**, los indexaron en **Vector Search**, recuperaron en **dos etapas** con un **reranker**, calibraron un **umbral** para poder decir «no sé», y un **agente** que **decide con lo que encuentra y cita sus fuentes**. Esto es el **Agente Auditor** del cronograma. En las próximas semanas le vamos a poner **bases de datos** y **modelos**, y en el capstone lo van a **conectar** con lo que hicieron en el Módulo 1.
> **Para entregar:** el notebook ejecutado (con el 🎉 de la 7.4 visible), la captura de **`0 corpus existentes`**, y el repositorio de la célula. La demo de 5 minutos: muéstrenme **el auditor respondiendo el caso del yate y un caso con citas**, y expliquen **una decisión de diseño** que tomaron: cómo leyeron, cómo cortaron o cómo eligieron el umbral.
> **Para la próxima semana:** lean el Módulo 3 —el mismo RAG, pero sobre el catálogo de datos antes de generar SQL— y tráiganme una pregunta: **¿qué tablas de su empresa responderían lo que el auditor no puede contestar?** Por ejemplo, ¿cuánto se gastó realmente en consultoría?"

---
## Code review: qué preguntar (10 min por célula)

**Estructura (10 min):** 2 min ven su pantalla · 5 min preguntas · 3 min devolución con **una cosa buena y una mejora**.

**Preguntas que hacer** (obliga a explicar, no solo a mostrar):
1. "¿Qué analizador usaste para el escaneo y **cómo sabes** que no se perdió?" *(debe poder enseñar el conteo de fragmentos)*
2. "¿Por qué elegiste esa forma de chunking? Enséñame **la columna** que lo decidió."
3. "Léeme una cita de tu agente. ¿Es **exacta**? ¿Qué pasaría con una cita de la forma A?"
4. "¿**Cómo calculaste el umbral**? ¿Valdría para otro corpus?"
5. "Haz una pregunta **fuera del corpus**. ¿Qué ve el agente? ¿Qué responde?"
6. "Quita una frase de la instrucción. ¿Qué crees que cambia?"
7. "¿Qué pasa si añades un documento sobre el mismo tema?" *(solo si hicieron la Parte 9)*
8. "¿Borraste tus recursos? Muéstrame la celda 2.2." y "¿Tu `.env` está en Git?" *(debe ser **no**)*

**Checklist rápido (para tus notas):**
- [ ] Saben qué analizador usar y por qué (y qué es la pérdida silenciosa)
- [ ] Eligieron el chunking **con una medida**, no a ojo
- [ ] Saben que K = 20 y N = 3 vienen del cronograma, y cómo se elegirían en un proyecto real
- [ ] El umbral **se calcula**, no se copia
- [ ] Las citas son **exactas** y vienen de la herramienta
- [ ] La consulta fuera del corpus **escala**
- [ ] Sin secretos en el repo
- [ ] **Recursos borrados** (Parte 10)
- [ ] Un test o un caso nuevo (pídelo como mejora)

---
## Si algo sale mal (contingencias)
| Situación | Plan |
|---|---|
| Gemini o la Ranking API dan error 429 | Esperar 1 minuto y reintentar la celda; si persiste, tú ejecutas en el proyector y las células siguen el flujo |
| Una **API sin habilitar** a mitad de la Parte 2 | El mensaje dice cuál. La habilitas tú (`COMANDOS.md`, paso 3) y esperas unos minutos; mientras, sigue en el proyector |
| Más de la mitad no pasó la Parte 0 a los 15 min | Parar y resolver el origen común (kernel equivocado, `.env` sin proyecto, región distinta de `us-central1`, falta de `gcloud auth application-default login`); trabajar en parejas con **una** máquina que funcione |
| **Fallan las operaciones de corpus** al hacerlas todos a la vez (concurrencia) | Escalonar: que una mitad de las células haga la Parte 2 y la otra mitad empiece 3 minutos después; o que **tú** crees los corpus en el proyector y ellos solo los consulten ⚠️ *(no probado; implicaría cambiar las Partes 2 y 3)* |
| Vas 10 min atrasada a la mitad | Recorta en este orden: **Parte 9**, multimodal (Parte 4), **Parte 8** como demo tuya, ejercicios 🧪. **Protege** 2, 3, 6, 7 y **10** |
| Alguien terminó antes | Que haga la Parte 9 o el reto: añadir **un quinto documento** de su empresa y volver a correr sus casos |
| Alguien cerró el kernel y perdió el estado | Volver a ejecutar las Partes 0 a 3 (los corpus **se reutilizan por nombre**; las importaciones se repiten y tardan unos minutos) |
| Te preguntan algo que no sabes | "Buena pregunta; no voy a inventarlo. Lo verifico y respondo por el chat." |

---
## Problemas fuera del notebook (el proyecto `src`)
Si al final haces la demo del proyecto: `adk web --port 8501 modulo2_rag_reranking/src` y eliges **`auditor_rag_app`**. Todos los comandos y qué esperar están en **`COMANDOS.md`, paso 8**.
| Síntoma | Causa | Solución |
|---|---|---|
| `adk web` no lista el agente | Carpeta equivocada | Pasa la carpeta que **contiene** los paquetes: `modulo2_rag_reranking/src` |
| Aparecen `auditor_rag_app` **y `rag`** | `rag` es la librería, no un agente | Elige `auditor_rag_app` |
| `Errno 13` al abrir `adk web` | Windows reserva el puerto 8000 | `--port 8501` |
| `No module named 'shared'` o `'rag'` | Falta `. .\env.ps1` en esa terminal | Ejecutarlo antes |
| `cannot import name 'storage' from 'google.cloud'` | La terminal usa el Python del sistema, no el `.venv` | `.\.venv\Scripts\Activate.ps1` (debe verse `(.venv)`) |
| El agente busca en el reporte sin que lo quieras | El `.env` tiene `RAG_CORPUS_REPORTES` | Quitarlo o comentarlo y **reiniciar** `adk web` |
| La pregunta del reporte da ESCALAR | Sin el reporte no hay base para decidir | Es lo **correcto** |
| Cambié el `.env` y no pasa nada | `adk web` lee el `.env` al arrancar | Reinicia `adk web` |
| Avisos `EXPERIMENTAL` / `deprecated` | ADK 2.x | Esperados; no son errores |

---
## Nota de instructor: cómo se conectará con el Módulo 1 (capstone)
**Este módulo deja al auditor local y sin A2A, a propósito:** el cronograma pide A2A en el Módulo 1 y en el capstone, no aquí. La **conexión la hacen los alumnos como práctica del capstone** (semana 6), con lo que aprendieron en el Módulo 1. Qué tienes que tener listo para esa sesión:
- **El auditor ya es conectable:** es un agente de ADK con `root_agent`, con salida estructurada `AuditDecision` (el **contrato**) y una `description` que un supervisor puede leer para decidir a quién delegar. Exponerlo por A2A es, en principio, una línea (`to_a2a(root_agent, port=8003)`) ⚠️ **no se ha probado con este auditor**; el patrón sale del Módulo 1.
- **Acuerdo de puertos** para que las células no choquen: 8001 presupuestos, 8002 tesorería, **8003 auditor**, 8004 SQL, 8005 ML y BI.
- **Pasos para los alumnos:** (1) exponer el auditor por A2A; (2) registrarlo como agente remoto en el supervisor; (3) probar con una pregunta que necesite presupuesto **y** política (por ejemplo, el exceso de consultoría de Norte).
- **Trampas del Módulo 1 que volverán:** el puerto 8000 reservado en Windows, la **respuesta duplicada en `adk web`** con agentes remotos (el bloque THOUGHT), y que **un agente solo puede tener un padre**.
- Un **repaso breve de A2A** al inicio del capstone: habrán pasado cinco semanas.
- **Tu solución de referencia:** la carpeta `capstone/` ya existe, pero **conecta los agentes en el mismo proceso** (`AgentTool`), no por A2A; habrá que adaptarla antes de usarla para revisar.

## Lo que no está probado
- **Notebook de alumnos:** se ejecutó **una vez**, de la Parte 0 a la 9 (21 de octubre), sin errores y con los valores que traen los ejercicios. **No se ejecutó la Parte 10** en esa corrida. Los resultados de los ejercicios 3, 6, 7 y 9 **con otros valores** no se probaron.
- **Reproducibilidad entre corridas:** en esa corrida el 10-Q quedó en 3 fragmentos (la del instructor, en 4), el corte semántico (B) dejó el Art. 1.3 junto al 1.4, la pregunta mixta dio `ESCALAR` (con ❌ en la comprobación 9.4) y las cuotas no cambiaron el reparto. Las conclusiones principales se mantuvieron; los detalles no.
- **Corrida completa del notebook del instructor con servicios reales:** se ejecutó completa, con los 🎉 de 7.4 y 9.4 y la limpieza enviada. **Una corrida no demuestra estabilidad**: Gemini, el analizador y el reranker no son deterministas. Los números exactos (puntajes, número de archivos de B, tiempos) pueden variar.
- **30 alumnos a la vez en un mismo proyecto:** las operaciones sobre corpus no admiten concurrencia (según la documentación) y no se probó con ese volumen. Tampoco el **costo total** de 30 corridas.
- **Permisos mínimos** de un alumno para crear buckets y corpus: las pruebas fueron con una cuenta Propietaria.
- **Opción B (dos sesiones)**: reanudar tras cerrar el kernel no se ha probado.
- **El tamaño de corte con el analizador de LLM:** en una corrida previa no cambió los fragmentos; **no sabemos si ese analizador ignora el tamaño**. No se investigó más.
- **`preparar_corpus.py` con `--con-reportes`** (la extensión) no se ejecutó. Sí se verificó el flujo por defecto (solo políticas).
- **Hit@3 con este corpus:** da 6/6 casi siempre; es poco informativo. Una evaluación seria (Faithfulness, Context Recall) es del Módulo 5.
- **Modelos y versiones:** el analizador de LLM usa `gemini-2.5-flash`, que **se retira el 31 de marzo de 2027** según la documentación; los Gemini 3.x solo se sirven desde `global`, `us` y `eu`, no desde `us-central1`. ADK: se probó con la 2.12.0.
- **El `(6, 6)` suelto** de la celda 5.1 es cosmético y sigue sin arreglarse.
- **Windows** pidiendo permiso de firewall: no aplica a este módulo (no levanta servidores), pero sí si haces la demo de `adk web`.
- Despliegue a Agent Engine.
