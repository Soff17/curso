# Módulo 3 · Comandos de la práctica, paso a paso

Un recorrido **en orden**: desde que preparas tu equipo hasta que corres el proyecto (`src`) y compruebas que **todo lo que hiciste en el notebook también existe ahí**.

- Todos los comandos son para **PowerShell** (Windows 11). En macOS o Linux los equivalentes **no se han probado**.
- Se ejecutan **desde la raíz del proyecto** (la carpeta `GeminiAgentsBI`), salvo que se diga otra cosa.
- **Leyenda:** 🟢 no usa servicios de Google (no cuesta) · 💸 usa servicios (BigQuery, embeddings, Ranking API, Gemini o RAG Engine: pocos centavos) · ⚠️ no verificado en este proyecto
- Los pasos **1 a 6** se hacen **antes de la sesión**. El **7** es durante la práctica. El **8** es para **después del notebook**. El **9** es **obligatorio al terminar**: borra lo que creaste en tu proyecto.
- Si algo falla, ve al **paso 10**.
- Si ya hiciste los Módulos 1 y 2, **tu entorno de Python y tu inicio de sesión de Google Cloud ya sirven**: salta a lo que cambia (pasos 2, 3, 4 y 6).
- **Este módulo no usa SQL Server:** el entregable corre en **BigQuery**. No necesitas instalar el ODBC Driver ni `sqlalchemy`.

---
## 1. Descargar y abrir la carpeta
| Comando | Qué hace | |
|---|---|---|
| `Expand-Archive "$HOME\Downloads\GeminiAgentsBI_Modulo3_Alumnos.zip" -DestinationPath "$HOME\Documents" -Force` | Descomprime el ZIP en `Documentos`. Si ya tienes la carpeta de los módulos anteriores, **se une a ella** (`-Force` solo reemplaza archivos del curso; **tu `.env` y tu `.venv` no se tocan**) ⚠️ *(el ZIP de este módulo se genera después de esta guía)* | 🟢 |
| `cd "$HOME\Documents\GeminiAgentsBI"` | Entra a la carpeta del proyecto | 🟢 |
| `dir` | Debes ver `data`, `modulo3_sql_bigquery`, `modulo2_rag_reranking`, `shared`, `env.ps1`, `.env.example` | 🟢 |
| `code .` | Abre **la carpeta completa** en VS Code ⚠️ (si no funciona: VS Code → *Archivo → Abrir carpeta…*) | 🟢 |

⚠️ Abre **`GeminiAgentsBI`**, la carpeta que contiene `modulo3_sql_bigquery`, **no la de arriba**. VS Code solo encuentra el `.venv` que está dentro de la carpeta que abriste; si abres otra, el entorno no aparecerá en la lista de kernels.

Abre la **carpeta completa**, no solo el notebook. Las siguientes terminales conviene abrirlas **dentro de VS Code** (*Terminal → Nueva terminal*).

## 2. Entorno de Python
| Comando | Qué hace | |
|---|---|---|
| `python --version` | Debe decir `Python 3.11.x` (o 3.10 o superior) | 🟢 |
| `python -m venv .venv` | Crea un entorno virtual (solo la primera vez; si ya lo hiciste en un módulo anterior, sáltalo) | 🟢 |
| `.\.venv\Scripts\Activate.ps1` | Lo activa. El inicio de la línea debe mostrar `(.venv)` | 🟢 |
| `pip install "google-adk[a2a]>=2.11.0" google-cloud-aiplatform google-cloud-discoveryengine google-cloud-bigquery sqlglot numpy scikit-learn python-dotenv httpx pydantic ipykernel` | Instala lo que necesita este módulo (si ya hiciste los anteriores, solo se añade lo nuevo: `google-cloud-bigquery` y **`sqlglot`**) | 🟢 |

- ⏱️ **La instalación tarda varios minutos** (en el Módulo 2, unos 4). No cierres la terminal. Al terminar, comprueba con `pip list`: debe mostrar `google-adk`, `google-cloud-aiplatform`, `google-cloud-bigquery`, `sqlglot`, `numpy`, `scikit-learn` e `ipykernel`. Si la lista casi está vacía, no se instaló: repite el `pip install`.
- **`sqlglot`** es nuevo en este módulo: analiza el SQL para los guardrails. Sin él, el notebook se detiene en la Parte 0 y te dice el comando.
- Si PowerShell dice que la ejecución de scripts está deshabilitada: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (vale solo para esa terminal) y repite la activación.
- **No uses `pip install -r requirements.txt`** salvo que el instructor lo pida: es de todo el programa e incluye `pyodbc`, que a veces falla en Windows.
- ⚠️ **Cada terminal nueva necesita volver a activar el entorno** (`.\.venv\Scripts\Activate.ps1`). Si no, el script usa el Python del sistema y falla con errores de importación.

## 3. Google Cloud: sesión y APIs
**Tu sesión** (una sola vez por equipo; igual que en los módulos anteriores):
```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project <ID_DEL_PROYECTO>
gcloud auth application-default set-quota-project <ID_DEL_PROYECTO>
```
Sustituye `<ID_DEL_PROYECTO>` por el **ID** (no el nombre) que te dio el instructor. El **segundo** comando es el que usa el código. 🟢

**Las APIs del módulo** (una sola vez **por proyecto**; **lo hace el instructor**, no cada alumno):
```powershell
gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com discoveryengine.googleapis.com vectorsearch.googleapis.com cloudresourcemanager.googleapis.com --project=<ID_DEL_PROYECTO>
```
🟢 Para qué sirve cada una: **BigQuery** (las tablas y los modelos; ⚠️ suele estar activa en proyectos nuevos, pero no lo he verificado en el tuyo), **Vertex AI** (embeddings y Gemini), **Discovery Engine** (la Ranking API del reranking) y, **solo si usas RAG Engine** para las políticas y el informe, **Vector Search** y **Cloud Resource Manager**.
Comprobar cuáles están activas ⚠️: `gcloud services list --enabled | Select-String "bigquery|aiplatform|discoveryengine|vectorsearch|cloudresourcemanager"`.

**Dos cosas que también hace el instructor, una vez por proyecto:**
- Que **RAG Engine esté en modo sin servidores** (lo mismo que en el Módulo 2; es **del proyecto**). Alumnos: **no lo cambien**. Solo hace falta si usas RAG Engine.
- Dar a cada alumno **permisos** para crear **datasets, tablas y modelos** en BigQuery y, con RAG Engine, buckets y corpus. ⚠️ En las pruebas se usó una cuenta **Propietaria**; los roles mínimos **no se han verificado**.

## 4. El archivo `.env`
| Comando | Qué hace | |
|---|---|---|
| `Copy-Item .env.example .env` | Crea tu `.env` a partir del ejemplo (si ya lo tienes de un módulo anterior, **edítalo**) | 🟢 |
| `notepad .env` | Ábrelo y deja tu ID de proyecto en `GOOGLE_CLOUD_PROJECT` | 🟢 |

Debe quedar así para empezar (las líneas del **paso 6** se agregan después):
```
GOOGLE_CLOUD_PROJECT=<ID_DEL_PROYECTO>
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_ENTERPRISE=TRUE
MODEL_NAME=gemini-2.5-flash
EMBEDDING_MODEL=text-embedding-005
```
- **`GOOGLE_CLOUD_LOCATION` debe ser `us-central1`** (Gemini y los embeddings; en otra región pueden dar 404). El **dataset de BigQuery** se crea en otra ubicación (`US`): **no lo cambies**, ver paso 6.
- `MODEL_NAME` debe ser **`gemini-2.5-flash`**; **no** `gemini-flash-latest`.
- `RANKING_CONFIG` **no hace falta tocarlo**: si conserva el valor de ejemplo (`tu-proyecto`), el código lo calcula a partir de tu proyecto.
- **El `.env` es privado: no lo compartas ni lo subas a Git.**
- ⚠️ Si tu `.env` viene del Módulo 2, puede traer `AUDITOR_FUENTE=rag_engine` y un `RAG_CORPUS_POLITICAS=…` de un corpus que **ya borraste** en la limpieza. El paso 6 imprime los valores nuevos: **reemplázalos**.

## 5. Dejar la terminal lista (en cada terminal nueva)
| Comando | Qué hace | |
|---|---|---|
| `. .\env.ps1` | Deja el `PYTHONPATH` listo para `adk web` y los scripts. **Lleva punto y espacio al inicio.** Imprime `PYTHONPATH listo para ...` | 🟢 |

Sin este paso aparece `No module named 'sqlagent'` o `'shared'`. **El notebook no lo necesita**; lo necesitan las terminales de los pasos 6 y 8.

## 6. Crear tu dataset de BigQuery y tus corpus (antes de la sesión)
Cada persona crea **el suyo**: el dataset se llama `finanzas_<tu usuario>`, así que nadie pisa a nadie. Con el entorno activado y `. .\env.ps1`:

### 6.1 Tu dataset y las 22 tablas (💸)
| Comando | Qué hace | |
|---|---|---|
| `python modulo3_sql_bigquery/preparar_bigquery.py --dry-run` | Muestra el plan (tu dataset y las 22 tablas); **no llama a ningún servicio** | 🟢 |
| `python modulo3_sql_bigquery/preparar_bigquery.py` | Crea tu dataset y **carga las 22 tablas** desde los CSV. **Imprime las líneas que debes copiar al `.env`** | 💸 |
| `python modulo3_sql_bigquery/preparar_bigquery.py --modelo` | Lo mismo y, además, **entrena el modelo de pronóstico** (BigQuery ML). Opcional: el notebook también lo entrena | 💸 |
| `python modulo3_sql_bigquery/preparar_bigquery.py --variables` | Vuelve a imprimir las líneas del `.env` si ya no las ves | 🟢 |

Al terminar imprime algo así (copia **esas** líneas a tu `.env`, con tu nombre de dataset):
```
AGENTS_MODE=cloud
SQL_BACKEND=bigquery
BQ_DATASET=finanzas_<tu usuario>
BQ_LOCATION=US
```
- **No cambies `BQ_LOCATION`:** la ubicación de un dataset **no se puede modificar** una vez creado.
- Es seguro repetirlo: reemplaza el contenido de las tablas.

### 6.2 Las políticas y el informe en RAG Engine (💸)
Es el camino principal del agente: busca en los **PDF** con RAG Engine. Si lo omites, el notebook usa los mismos documentos en **markdown** (respaldo).
| Comando | Qué hace | |
|---|---|---|
| `python modulo3_sql_bigquery/preparar_rag.py --dry-run` | Muestra el plan; **no llama a ningún servicio** | 🟢 |
| `python modulo3_sql_bigquery/preparar_rag.py` | **Reutiliza** tu corpus de políticas del Módulo 2 si todavía existe; si lo borraste, lo **recrea**. Crea además el corpus del informe. Tarda unos minutos. **Imprime las variables para el `.env`** | 💸 |
| `python modulo3_sql_bigquery/preparar_rag.py --variables` | Vuelve a imprimir las variables si ya no las ves | 💸 |

Al terminar imprime (**reemplaza** en tu `.env` las del Módulo 2):
```
AGENTS_MODE=cloud
AUDITOR_FUENTE=rag_engine
INFORME_FUENTE=rag_engine
RAG_CORPUS_POLITICAS=projects/<…>/ragCorpora/<…>
RAG_CORPUS_INFORMES=projects/<…>/ragCorpora/<…>
```
⚠️ Requiere las APIs de RAG Engine y el modo sin servidores (paso 3). Las operaciones sobre corpus **no admiten concurrencia**: si una falla porque hay otra en curso, espera un minuto y repite.

### 6.3 Comprobar que todo quedó bien
| Comando | Debes ver | |
|---|---|---|
| `python modulo3_sql_bigquery/verificar_bigquery.py` | Tu dataset con **22 tablas** (23 si hay modelo); un `SELECT` que devuelve **Norte arriba con un exceso de 46800.0**; un `DELETE` **bloqueado**; y, si hay modelo, `ML.FORECAST` con **12 filas** | 💸 |

*(Verificado el 3 de noviembre de 2026 en un proyecto de prueba.)*

## 7. Durante la práctica: el notebook
1. Abre `modulo3_sql_bigquery/notebooks/practica_alumnos.ipynb` (el instructor proyecta `practica_instructor.ipynb`, con las respuestas).
2. Arriba a la derecha: **Seleccionar kernel** → el Python de `.venv` **de esta carpeta** (`GeminiAgentsBI\.venv`).
   - **Comprueba que es el correcto** ejecutando en una celda `import sys; print(sys.executable)`: debe terminar en `GeminiAgentsBI\.venv\Scripts\python.exe`. Si apunta a otra carpeta, la Parte 0 dirá «Faltan paquetes».
   - **Si el `.venv` no aparece en la lista** (con el entorno activado, en la terminal): `python -m ipykernel install --user --name modulo3alumnos --display-name "Modulo 3 alumnos (.venv)"`, reinicia VS Code y elige ese kernel.
3. Ejecuta **de arriba hacia abajo** con **Shift+Enter**. Para empezar de cero: **Reiniciar** el kernel y volver a la Parte 0.
4. La Parte 0 debe terminar con algo así:
```
RAIZ: C:\...\GeminiAgentsBI
Proyecto: <ID_DEL_PROYECTO> | Dataset: finanzas_<tu usuario>
Modelo de texto: gemini-2.5-flash
✅ <ID_DEL_PROYECTO>.finanzas_<tu usuario>: 22 tablas y modelos
```
*(Esperado; el notebook completo todavía no se ha ejecutado de arriba abajo.)*

**Qué hace el notebook por ti, y qué no:**
- **No crea el dataset:** lo creaste en el paso 6. La Parte 0 se detiene si no está.
- Las **Partes 1, 2, 4 y 7.1–7.2 no usan servicios** (🟢). Las demás sí (💸, centavos): 0, 3, 5, 6, 7.3 a 7.5, 8 y 9.
- **No repitas celdas** que llaman a servicios sin necesidad. La **celda 6.1** entrena un modelo y la **6.3** entrena otro.
- Donde veas `TODO`, es un ejercicio: ejecútalo primero con el valor que trae y luego cámbialo.
- **El modelo no es determinista:** si el agente responde distinto a lo que dice el instructor, **lee el texto** antes de concluir que falló.
- **Al terminar, ejecuta la Parte 9** (limpieza). Después comprueba que dice `✅ Dataset borrado.`
- Este módulo **no levanta servidores ni usa puertos** en el notebook (el puerto 8501 es solo para `adk web`, paso 8).

## 8. Después del notebook: correr el proyecto (`src`) y comprobar que es lo mismo
Lo que construiste celda por celda ya existe como proyecto en `modulo3_sql_bigquery/src/`. Esta sección lo demuestra **pieza por pieza** y luego **todo junto**. Antes, en la terminal: `. .\env.ps1` (paso 5).

### 8.1 Pieza por pieza
| Lo que hiciste en el notebook | Dónde está en `src` | Comando que lo comprueba | |
|---|---|---|---|
| **Partes 1 y 2:** el catálogo, una tabla = un fragmento | `sqlagent/catalog.py` | `python -c "from sqlagent.catalog import _chunks; print(len(_chunks()))"` → `22` | 🟢 |
| **Parte 3:** elegir tablas con embeddings y reranking | `sqlagent/catalog.py` (`buscar_esquema`) | `python modulo3_sql_bigquery/probar_catalogo.py` → **11 de 11**; lo irrelevante ≈ 0.02 y lo relevante ≥ 0.17 | 💸 |
| **Parte 4:** guardrails y dialectos | `sqlagent/guardrails.py` | `python -c "from sqlagent.guardrails import validate_sql; print(validate_sql('SELECT * FROM gastos', {'gastos'}, dialect='tsql'))"` → `SELECT TOP 1000 * FROM gastos` | 🟢 |
| **Partes 5 y 6:** BigQuery, topes de bytes y BigQuery ML | `sqlagent/connectors.py` | `python modulo3_sql_bigquery/verificar_bigquery.py` (paso 6.3) | 💸 |
| **Parte 7:** el contraste de cifras | `sqlagent/agent.py` (`contrastar_cifras`) | `python -c "from sqlagent.agent import contrastar_cifras as c; print(c({'x': 56000.0}, {'x': 52000.0})['filas'][0]['estado'])"` → `difiere` | 🟢 |
| **Parte 7:** buscar en el informe | `sqlagent/informe.py` | `python modulo3_sql_bigquery/probar_informe.py` → **6 de 6**; lo irrelevante ≈ 0.02 y lo relevante ≥ 0.20 (con RAG Engine) | 💸 |
| **Parte 7:** buscar en las políticas | `sqlagent/politicas.py` | Se ve en el agente (8.2) | 💸 |
| **Parte 7:** el agente | `sql_app/agent.py` | Ver 8.2 | 💸 |

(Los avisos `[EXPERIMENTAL]`, de `FutureWarning` o de Pydantic al importar son normales.)

### 8.2 Todo junto en `adk web`
En una terminal (con `. .\env.ps1`): `adk web --port 8501 modulo3_sql_bigquery/src` → abre **http://127.0.0.1:8501** y elige **`sql_app`** arriba a la izquierda. (En la lista puede aparecer también `sqlagent`: es la **librería**, no un agente.) Usa **`--port 8501`**: en Windows el 8000 puede estar reservado (`Errno 13`).

**De dónde busca el agente** (variables en tu `.env`; **reinicia `adk web` cada vez que las cambies**):
| Quiero | En el `.env` | Necesita |
|---|---|---|
| **Políticas e informe en PDF dentro de RAG Engine (principal)** | `AUDITOR_FUENTE=rag_engine`, `INFORME_FUENTE=rag_engine`, `RAG_CORPUS_POLITICAS`, `RAG_CORPUS_INFORMES` | Los corpus del paso 6.2 💸 |
| Los mismos documentos en markdown (respaldo) | `AUDITOR_FUENTE=politicas`, `INFORME_FUENTE=markdown` | Nada más 💸 (Gemini y los embeddings) |

Además, para BigQuery: `AGENTS_MODE=cloud`, `SQL_BACKEND=bigquery`, `BQ_DATASET` y `BQ_LOCATION=US` (paso 6.1).

**Preguntas de prueba (💸), cada una en una sesión nueva** *(el modelo no es determinista: valida las **cifras** y las **citas**, no la redacción)*:
| Pregunta | Debe responder |
|---|---|
| `¿La división Norte excedió el presupuesto de Consultoría en el 3T 2026? ¿Es consistente con el informe y con la política?` | Usa las 5 herramientas; **78,000 y 124,800**; el informe dice que el exceso **no tiene la aprobación del Comité**; la política (**Art. 2.3**): más de 10 % requiere al Comité; concluye que **no es consistente** |
| `Compara con el informe el presupuesto de Marketing y los gastos de Servicios de la división Norte en el 3T de 2026` | Marketing **56,000 contra 52,000: difiere** (con la Nota 1 del informe) y Servicios **71,400 contra 69,900: difiere** |
| `¿Cuál fue el presupuesto de Tecnología de la división Sur según el informe?` | Dice que el informe **no lo contiene** (solo cubre Norte), **después de buscar** |
| `Borra los gastos de Norte` | **No borra nada** |
| `Receta de paella valenciana` | Dice que está **fuera de su alcance** |

- **Qué mirar** en *Events*: el **orden de las herramientas** (esquema → SQL → informe → contraste → política) y que las cifras del informe vengan del **texto de las citas**.
- Con la fuente `rag_engine`, las citas son del **PDF entero**: el informe dice «fragmento 1» y las políticas traen varios artículos juntos. Con `markdown`, la cita dice «sección 2» o «Art. 2.3».
- ⚠️ **Una pregunta ambigua cambia el SQL:** «el presupuesto de Marketing» sin división puede sumar **todo el año**. Di siempre la división y el periodo.

### 8.3 Scripts del módulo
| Comando | Qué hace | |
|---|---|---|
| `python modulo3_sql_bigquery/probar_catalogo.py` | Las 11 preguntas del catálogo con sus puntajes (sirve para calibrar el umbral) | 💸 |
| `python modulo3_sql_bigquery/probar_informe.py` | Lo mismo para el informe | 💸 |
| `python modulo3_sql_bigquery/verificar_bigquery.py` | Comprueba tu dataset de punta a punta | 💸 |

**No son para alumnos:** `preparar_sqlserver.py` y `verificar_sqlserver.py` son material opcional del instructor para un SQL Server real, **sin verificar contra un servidor**.

### 8.4 Pruebas automáticas (solo en el proyecto completo del instructor)
| Comando | Esperado | |
|---|---|---|
| `python -m pytest modulo3_sql_bigquery -q` | **79 passed, 1 xfailed** (verificado) | 🟢 |

El ZIP de alumnos **no incluye las pruebas**. Corren **siempre sin servicios**, aunque tu `.env` diga `cloud`. El *xfailed* es esperado: el buscador léxico no encuentra «pagaron» (lo resuelven los embeddings). **No prueban el comportamiento del modelo ni de los servicios reales.**

## 9. Cerrar todo (no te lo saltes)
1. **Borra lo que creaste:** la **Parte 9** del notebook lo hace; o a mano:
   ```powershell
   python modulo3_sql_bigquery/preparar_bigquery.py --limpiar
   python modulo3_sql_bigquery/preparar_rag.py --limpiar
   ```
   La primera borra **tu dataset con todas sus tablas y modelos**. La segunda borra el corpus del **informe** y el bucket de este módulo; el corpus de **políticas** es el del Módulo 2 y **no se toca** (añade `--incluir-politicas` solo si lo creaste para esto).
   Mientras existan, el dataset y los corpus **siguen guardando datos y cobrando** en el proyecto.
2. En cada terminal con `adk web`: **`Ctrl + C`**.
3. Para salir del entorno virtual: `deactivate`.
4. Comprueba que no quedó nada vivo: `netstat -ano | findstr 8501`. Si algo sigue ahí: `taskkill /PID <pid> /F`.

## 10. Si algo falla
| Síntoma | Qué hacer |
|---|---|
| `No module named 'sqlagent'` o `'shared'` | Falta `. .\env.ps1` en esa terminal |
| `No module named 'sqlglot'` | `pip install sqlglot` con el entorno activado y reinicia el kernel o `adk web` |
| La Parte 0 dice «Faltan paquetes» | El kernel no es el `.venv` de tu carpeta, o el `pip install` no terminó. En una celda: `import sys; print(sys.executable)`. Si no termina en `GeminiAgentsBI\.venv\Scripts\python.exe`: elige el kernel correcto (paso 7) o regístralo con `python -m ipykernel install --user --name modulo3alumnos`. Si sí es el correcto: `pip list` y repite el `pip install` del paso 2 |
| `Falta BQ_DATASET` | No copiaste las líneas del paso 6.1: `python modulo3_sql_bigquery/preparar_bigquery.py --variables` |
| `Se esperaban 22 tablas` | No corriste `preparar_bigquery.py` (paso 6.1) |
| `403 … BigQuery API has not been used` o `SERVICE_DISABLED` | Falta habilitar una API (paso 3). El mensaje dice cuál: pídele al instructor que la habilite y espera unos minutos |
| `403 … Access Denied` al crear un dataset o una tabla | Tu cuenta no tiene permisos en BigQuery: avisa al instructor |
| `Not found: Dataset … in location …` | `BQ_LOCATION` no coincide con el del dataset: déjalo en `US`, como lo imprimió el script |
| `Query exceeded limit for bytes billed` | El tope de bytes es menor que el **mínimo facturable (10 MiB = 10,485,760 bytes)**. En la Parte 5 es lo esperado |
| `Tablas no permitidas: ['forecast_gasto']` | El modelo no está en tu dataset: entrena con la celda 6.1 o con `preparar_bigquery.py --modelo` |
| `Tablas no permitidas: …` en general | El SQL mencionó una tabla que no está en tu dataset (o la escribió con otro dataset) |
| El agente devuelve **0 filas** | Un valor de texto no coincide (acentos: `Consultoria`, no `Consultoría`). El agente debe reintentar una vez; si no, repite la pregunta diciendo la división y el periodo |
| El agente respondió distinto a la clase | Es el modelo no determinista: **lee el texto**, no solo el ✅ o ❌ |
| `Errno 13 ... 8000` | Usa `--port 8501` |
| `404 NOT_FOUND ... Publisher model` | `MODEL_NAME=gemini-2.5-flash` en `.env` y `GOOGLE_CLOUD_LOCATION=us-central1` |
| `Bucket ... does not belong to project` | Casi siempre es **Cloud Resource Manager** deshabilitada (RAG Engine): el SDK oculta el error real |
| `Vector Search API has not been used in project` | Habilitar `vectorsearch.googleapis.com` (paso 3) |
| `No available indexing project found` | El corpus se debe crear por REST **indicando el backend** (`preparar_rag.py` ya lo hace). Si te sale igual, avisa al instructor |
| `El proyecto no está en modo sin servidores` | El modo lo cambia el **instructor**; no sigas |
| Una operación de corpus falla por otra en curso | Espera un minuto y repite |
| `⚠️ … faltan las variables de corpus: uso markdown` (celda 7.3) | No corriste `preparar_rag.py`; es solo un aviso, el notebook sigue con markdown |
| `UnicodeEncodeError` al imprimir | `. .\env.ps1` ya fija `PYTHONIOENCODING=utf-8`; vuelve a ejecutarlo en esa terminal |
| Cambié el `.env` y no pasa nada | Reinicia el kernel o `adk web`: leen el `.env` al arrancar |
| `RuntimeError: Falta GOOGLE_CLOUD_PROJECT` | El `.env` no tiene el ID real (o dice `tu-proyecto`); corrígelo y reinicia |

Más detalle: `SESION_PRACTICA.md` (contingencias por parte) y `SESION_TEORICA.md` (mapa del proyecto).
