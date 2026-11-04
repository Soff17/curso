# Módulo 2 · Comandos de la práctica, paso a paso

Un recorrido **en orden**: desde que preparas tu equipo hasta que corres el proyecto (`src`) y compruebas que **todo lo que hiciste en el notebook también existe ahí**.

- Todos los comandos son para **PowerShell** (Windows 11). En macOS o Linux los equivalentes **no se han probado**.
- Se ejecutan **desde la raíz del proyecto** (la carpeta `GeminiAgentsBI`), salvo que se diga otra cosa.
- **Leyenda:** 🟢 no usa servicios de Google (no cuesta) · 💸 usa servicios (Gemini, embeddings, reranking o RAG Engine: pocos centavos) · ⚠️ no verificado en este proyecto
- Los pasos **1 a 6** se hacen **antes de la sesión**. El **7** es durante la práctica. El **8** es para **después del notebook**. El **9** es **obligatorio al terminar**: borra lo que creaste en tu proyecto.
- Si algo falla, ve al **paso 10**.
- Si ya hiciste el Módulo 1, **tu entorno de Python y tu inicio de sesión de Google Cloud ya sirven**: salta a lo que cambia (pasos 2, 3 y 4).

---
## 1. Descargar y abrir la carpeta
| Comando | Qué hace | |
|---|---|---|
| `Expand-Archive "$HOME\Downloads\GeminiAgentsBI_Modulo2_Alumnos.zip" -DestinationPath "$HOME\Documents" -Force` | Descomprime el ZIP en `Documentos`. Si ya tienes la carpeta del Módulo 1, **se une a ella** (`-Force` solo reemplaza archivos del curso; **tu `.env` y tu `.venv` no se tocan**) | 🟢 |
| `cd "$HOME\Documents\GeminiAgentsBI"` | Entra a la carpeta del proyecto | 🟢 |
| `dir` | Debes ver `data`, `modulo2_rag_reranking`, `shared`, `env.ps1`, `.env.example` | 🟢 |
| `code .` | Abre **la carpeta completa** en VS Code ⚠️ (si no funciona: VS Code → *Archivo → Abrir carpeta…*) | 🟢 |

⚠️ Abre **`GeminiAgentsBI`**, la carpeta que contiene `modulo2_rag_reranking`, **no la de arriba**. VS Code solo encuentra el `.venv` que está dentro de la carpeta que abriste; si abres otra, el entorno no aparecerá en la lista de kernels.

Abre la **carpeta completa**, no solo el notebook. Las siguientes terminales conviene abrirlas **dentro de VS Code** (*Terminal → Nueva terminal*).

## 2. Entorno de Python
| Comando | Qué hace | |
|---|---|---|
| `python --version` | Debe decir `Python 3.11.x` (o 3.10 o superior) | 🟢 |
| `python -m venv .venv` | Crea un entorno virtual (solo la primera vez; si ya lo hiciste en el Módulo 1, sáltalo) | 🟢 |
| `.\.venv\Scripts\Activate.ps1` | Lo activa. El inicio de la línea debe mostrar `(.venv)` | 🟢 |
| `pip install "google-adk[a2a]>=2.11.0" google-cloud-aiplatform google-cloud-discoveryengine numpy scikit-learn python-dotenv httpx pydantic ipykernel` | Instala lo que necesita este módulo (si ya hiciste el Módulo 1, solo se añade lo nuevo) | 🟢 |

- ⏱️ **La instalación tarda varios minutos** (en las pruebas, unos 4). No cierres la terminal. Al terminar, comprueba con `pip list`: debe mostrar `google-adk`, `google-cloud-aiplatform`, `numpy`, `scikit-learn` e `ipykernel`. Si la lista casi está vacía, no se instaló: repite el `pip install`.
- `google-cloud-aiplatform` ya trae `google-genai`, Cloud Storage y Cloud Resource Manager; **no hace falta instalarlos aparte**. Es también la que aporta el módulo `agentplatform` que usa RAG Engine.
- Si PowerShell dice que la ejecución de scripts está deshabilitada: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (vale solo para esa terminal) y repite la activación.
- **No uses `pip install -r requirements.txt`** salvo que el instructor lo pida: es de todo el programa e incluye `pyodbc`, que a veces falla en Windows.
- ⚠️ **Cada terminal nueva necesita volver a activar el entorno** (`.\.venv\Scripts\Activate.ps1`). Si no, el script usa el Python del sistema y falla con `cannot import name 'storage' from 'google.cloud'`.

## 3. Google Cloud: sesión y APIs
**Tu sesión** (una sola vez por equipo; igual que en el Módulo 1):
```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project <ID_DEL_PROYECTO>
gcloud auth application-default set-quota-project <ID_DEL_PROYECTO>
```
Sustituye `<ID_DEL_PROYECTO>` por el **ID** (no el nombre) que te dio el instructor. El **segundo** comando es el que usa el código. 🟢

**Las APIs del módulo** (una sola vez **por proyecto**; **lo hace el instructor**, no cada alumno):
```powershell
gcloud services enable aiplatform.googleapis.com discoveryengine.googleapis.com vectorsearch.googleapis.com cloudresourcemanager.googleapis.com --project=<ID_DEL_PROYECTO>
```
🟢 Para qué sirve cada una: **Vertex AI** (embeddings y Gemini), **Discovery Engine** (la Ranking API del reranking), **Vector Search** (donde RAG Engine guarda los vectores) y **Cloud Resource Manager** (el SDK la usa al importar archivos desde un bucket; si falta, el error que muestra engaña).
Comprobar cuáles están activas ⚠️: `gcloud services list --enabled | Select-String "aiplatform|discoveryengine|vectorsearch|cloudresourcemanager"`.

**Dos cosas que también hace el instructor, una vez por proyecto:**
- Que **RAG Engine esté en modo sin servidores** (celda 2.3 del notebook; el modo es **del proyecto** y afecta a todos). Alumnos: **no la ejecuten**.
- Dar a cada alumno **permisos** para crear buckets y corpus. ⚠️ En las pruebas se usó una cuenta **Propietaria**; los roles mínimos **no se han verificado**.

## 4. El archivo `.env`
| Comando | Qué hace | |
|---|---|---|
| `Copy-Item .env.example .env` | Crea tu `.env` a partir del ejemplo (si ya lo tienes del Módulo 1, edítalo) | 🟢 |
| `notepad .env` | Ábrelo y deja tu ID de proyecto en `GOOGLE_CLOUD_PROJECT` | 🟢 |

Debe quedar así para el notebook (el resto no se usa en el Módulo 2):
```
GOOGLE_CLOUD_PROJECT=<ID_DEL_PROYECTO>
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_ENTERPRISE=TRUE
MODEL_NAME=gemini-2.5-flash
EMBEDDING_MODEL=text-embedding-005
```
- **`GOOGLE_CLOUD_LOCATION` debe ser `us-central1`**: el modo sin servidores de RAG Engine solo existe ahí, y en otra región los embeddings y Gemini pueden dar 404.
- `MODEL_NAME` debe ser **`gemini-2.5-flash`**; **no** `gemini-flash-latest`.
- `RANKING_CONFIG` **no hace falta tocarlo**: si conserva el valor de ejemplo (`tu-proyecto`), el código lo calcula a partir de tu proyecto.
- `AGENTS_MODE` **no importa para el notebook** (él mismo se pone en `cloud`). Importa para el proyecto (paso 8): para el camino principal, con RAG Engine, pon **`AGENTS_MODE=cloud`** y **`AUDITOR_FUENTE=rag_engine`** (se explica en 8.2). `offline` usa una búsqueda local de ejemplo, sin servicios.
- **El `.env` es privado: no lo compartas ni lo subas a Git.**

## 5. Dejar la terminal lista (en cada terminal nueva)
| Comando | Qué hace | |
|---|---|---|
| `. .\env.ps1` | Deja el `PYTHONPATH` listo para `adk web` y los scripts. **Lleva punto y espacio al inicio.** Imprime `PYTHONPATH listo para ...` | 🟢 |

Sin este paso aparece `No module named 'shared'` o `'rag'`. **El notebook no lo necesita**; lo necesitan las terminales del paso 8.

## 6. Verificar que todo está bien (antes de la sesión)
| Comando | Debes ver | |
|---|---|---|
| `pip show google-adk` | `Version: 2.11.x` o superior | 🟢 |
| `pip show google-cloud-aiplatform` | una versión (en las pruebas, `2.5.0`) | 🟢 |
| `gcloud config get-value project` | tu ID de proyecto | 🟢 |
| `gcloud auth list` | tu cuenta marcada como activa | 🟢 |

**Prueba de embeddings** (un solo vector; cambia el ID) ⚠️ *(el mismo servicio se usa en la Parte 0 del notebook, que sí se verificó)*:
```powershell
$env:GOOGLE_GENAI_USE_ENTERPRISE="TRUE"; $env:GOOGLE_CLOUD_PROJECT="<ID_DEL_PROYECTO>"; $env:GOOGLE_CLOUD_LOCATION="us-central1"
python -c "from google import genai; c=genai.Client(); print(len(c.models.embed_content(model='text-embedding-005', contents=['hola']).embeddings[0].values))"
```
💸 Debe imprimir `768`.

**Prueba del proyecto (sin servicios):**
```powershell
. .\env.ps1
python -c "from rag.chunking import load_corpus; from shared.config import POLICIES_DIR; c=load_corpus(POLICIES_DIR); print(len(c), c[0].id)"
```
🟢 Debe imprimir `20 AUD-2026#5.1` (20 chunks, uno por artículo).

## 7. Durante la práctica: el notebook
1. Abre `modulo2_rag_reranking/notebooks/practica_alumnos.ipynb` (el instructor proyecta `practica_instructor.ipynb`, con las respuestas).
2. Arriba a la derecha: **Seleccionar kernel** → el Python de `.venv` **de esta carpeta** (`GeminiAgentsBI\.venv`).
   - **Comprueba que es el correcto** ejecutando en una celda `import sys; print(sys.executable)`: debe terminar en `GeminiAgentsBI\.venv\Scripts\python.exe`. Si apunta a otra carpeta, la Parte 0 dirá «Faltan paquetes».
   - **Si el `.venv` no aparece en la lista** (con el entorno activado, en la terminal): `python -m ipykernel install --user --name modulo2alumnos --display-name "Modulo 2 alumnos (.venv)"`, reinicia VS Code y elige ese kernel.
3. Ejecuta **de arriba hacia abajo** con **Shift+Enter**. Para empezar de cero: **Reiniciar** el kernel y volver a la Parte 0.
4. Las celdas de la Parte 0 deben mostrar:
```
RAIZ: C:\...\GeminiAgentsBI
Proyecto: <ID_DEL_PROYECTO> | Región Gemini: us-central1
Ranking config: projects/<ID_DEL_PROYECTO>/locations/global/rankingConfigs/default_ranking_config
✅ text-embedding-005 → dimensión 768
Embeddings: text-embedding-005 | Modelo de texto: gemini-2.5-flash | K = 20 | N = 3
```

**Qué hace el notebook por ti, y qué no:**
- Desde la **Parte 2** crea un **bucket** y varios **corpus** de RAG Engine con **tu usuario en el nombre** (así no chocan con los de tus compañeros). **No los crees además a mano.**
- Las operaciones sobre corpus **no admiten concurrencia**: si una celda falla porque hay otra operación en curso, espera un minuto y repite **solo esa celda**.
- **No repitas celdas que importan o crean** sin necesidad: cada importación llama al analizador de LLM y cuesta.
- **No ejecutes la celda 2.3** (cambiar el modo del proyecto): es del instructor.
- **Al terminar, ejecuta la Parte 10** (limpieza). Después vuelve a ejecutar la celda 2.2 y comprueba que dice `0 corpus existentes`.
- Casi todas las partes usan servicios (💸, centavos). Las Partes 1 y 1b no.
- Este módulo **no levanta servidores ni usa puertos** (no hay A2A).

## 8. Después del notebook: correr el proyecto (`src`) y comprobar que es lo mismo
Lo que construiste celda por celda ya existe como proyecto en `modulo2_rag_reranking/src/`. Esta sección lo demuestra **pieza por pieza** y luego **todo junto**. Antes, en la terminal: `. .\env.ps1` (paso 5).

### 8.1 Pieza por pieza (🟢, sin servicios)
| Lo que hiciste en el notebook | Dónde está en `src` | Comando que lo comprueba |
|---|---|---|
| **Parte 1:** chunking por artículo | `rag/chunking.py` | `python -c "from rag.chunking import load_corpus; from shared.config import POLICIES_DIR; c=load_corpus(POLICIES_DIR); print(len(c), c[0].id)"` → `20 AUD-2026#5.1` |
| **Parte 3:** cortar el texto de un PDF por estructura | `rag/chunking.py` (`split_by_structure`) | `python -c "from rag.chunking import split_by_structure, structure_pieces; t='Politica (POL-VIA-2026)\n## Articulo 1.1 - Alcance\nAplica a todos.\n## Articulo 1.2 - Limites\nUSD 150 por dia.'; print(len(split_by_structure(t)), list(structure_pieces('POL-VIA-2026', t)))"` → `3 ['POL-VIA-2026__1.1', 'POL-VIA-2026__1.2']` (el encabezado y 2 artículos) |
| **Partes 3 y 5:** dos etapas (K = 20 → N = 3) y Hit@3 | `rag/retrieval.py`, `compare_rerank.py` | `python modulo2_rag_reranking/compare_rerank.py` → `Hit@3 sin rerank: 5/6   con rerank: 6/6` (con el reranker léxico de ejemplo) |
| **Parte 6:** calibrar el umbral | `rag/retrieval.py` (`calibrate_threshold`) | Se comprueba en las pruebas (8.4). Con el reranker léxico de ejemplo sale ≈ 0.21 (con las tres consultas fuera del corpus que usa la app); con la Ranking API se usó 0.14 |
| **Parte 7:** herramienta de búsqueda del auditor | `rag/auditor.py` (`buscar_politicas`) | `python -c "from rag.auditor import buscar_politicas as b; print([c['citation'] for c in b('viaje internacional sin autorización previa')['citations']])"` → `POL-VIA-2026, Art. 1.3 (Autorización previa)` primero |
| **Parte 7:** el agente auditor | `auditor_rag_app/agent.py` | `python -c "import auditor_rag_app.agent as a; print(a.root_agent.name, a.root_agent.tools[0].__name__)"` → `auditor_politicas buscar_politicas` |
| **Parte 9:** cuota por fuente | `rag/retrieval.py` (`select_with_quotas`) | Se comprueba en las pruebas (8.4) |
| **Partes 2 a 4:** RAG Engine y Vector Search | `rag/ragengine.py`, `preparar_corpus.py` | Ver 8.3 |

(Los avisos `[EXPERIMENTAL]` o de Pydantic al importar son normales.)

### 8.2 Todo junto en `adk web`
En una terminal (con `. .\env.ps1`): `adk web --port 8501 modulo2_rag_reranking/src` → abre **http://127.0.0.1:8501** y elige **`auditor_rag_app`** arriba a la izquierda. (En la lista aparece también `rag`: es la librería, no un agente.) Usa **`--port 8501`**: en Windows el 8000 puede estar reservado (`Errno 13`).

**El camino principal es RAG Engine:** el agente busca en tus políticas en PDF, dentro de un corpus de RAG Engine. **Antes de abrir `adk web`, crea tu corpus con el paso 8.3** (cada célula crea el suyo) y copia al `.env` las variables que imprime.

**De dónde busca el agente** (variables en tu `.env`; **reinicia `adk web` cada vez que las cambies**):
| Quiero | En el `.env` | Necesita |
|---|---|---|
| **Las políticas en PDF dentro de RAG Engine (principal)** | `AGENTS_MODE=cloud`, `AUDITOR_FUENTE=rag_engine`, `RAG_CORPUS_POLITICAS=<…>` | El corpus creado en 8.3 💸 |
| Los mismos documentos, sin RAG Engine | `AGENTS_MODE=cloud` | Embeddings y Ranking API reales, en memoria 💸 |
| Probar rápido, sin crear nada | `AGENTS_MODE=offline` | Nada más: búsqueda local de ejemplo; el modelo sí es Gemini real 💸 |

**Preguntas de prueba (💸), en una sesión nueva** *(verificadas el 2026-10-20 con `cloud` y `rag_engine`)*:
| Pregunta | Debe responder |
|---|---|
| `Viaje internacional de 4 días, USD 2,400 total, sin autorización previa del Director` | **RECHAZADO**, citando el Art. 1.3 |
| `Exceso de 8% en Consultoría de Norte aprobado por el Director de División` | **APROBADO**, citando el Art. 2.3 |
| `Compra de un yate para la dirección` | **ESCALAR**, con `articulos_citados: []` |
| `El reporte trimestral 10-Q del 3T 2026 muestra servicios de consultoría de 2,880 frente a 1,800 del año anterior. ¿Cumple ese gasto con la política?` | **ESCALAR**: sin el reporte no hay base para decidir |

- **Qué mirar** en *Events*: la llamada a `buscar_politicas`, su respuesta (las citas con su puntaje) y la decisión final. **El yate es la prueba clave:** sin citas, el agente debe **escalar**, no inventar.
- El modelo **no es determinista**: valida la **decisión** y las **citas**, no la redacción. Con la fuente `rag_engine`, la cita puede salir gruesa («Arts. 1.1 y 1.2 y 1.3…»), porque el servicio deja cada política como un solo fragmento.

### 8.3 Crear y borrar el corpus de RAG Engine (💸)
**Es el flujo normal del proyecto: hazlo antes de abrir `adk web` (8.2).** **Cada célula crea su propio corpus** (lo hace una persona por célula): así cada célula puede rehacerlo o borrarlo sin afectar a las demás. Con el entorno activado y `. .\env.ps1`:
| Comando | Qué hace | |
|---|---|---|
| `python modulo2_rag_reranking/preparar_corpus.py --dry-run` | Muestra el plan; **no llama a ningún servicio** | 🟢 |
| `python modulo2_rag_reranking/preparar_corpus.py` | Sube los PDFs de políticas, crea el corpus e importa con el analizador de LLM. Tarda un par de minutos. **Imprime las variables que debes copiar al `.env`** | 💸 |
| `python modulo2_rag_reranking/preparar_corpus.py --variables` | Vuelve a imprimir esas variables si ya no las ves | 💸 |
| `python modulo2_rag_reranking/preparar_corpus.py --limpiar` | **Borra** el corpus y el bucket | 💸 |

La opción `--con-reportes` añade el reporte 10-Q como segunda fuente (**extensión opcional, no es parte del entregable**).

### 8.4 Pruebas automáticas (solo en el proyecto completo del instructor)
| Comando | Esperado | |
|---|---|---|
| `python -m pytest modulo2_rag_reranking -q` | **44 passed** (verificado) | 🟢 |

El ZIP de alumnos **no incluye las pruebas**. Corren **siempre sin servicios**, aunque tu `.env` diga `cloud`. Cubren el chunking, el corte semántico, la cuota por fuente, el umbral, el Hit@3, RAG Engine con piezas simuladas, la fábrica del auditor, la app de ADK y el plan de `preparar_corpus.py`. **No prueban el comportamiento del modelo ni de los servicios reales.**

## 9. Cerrar todo (no te lo saltes)
1. **Borra lo que creaste:** `python modulo2_rag_reranking/preparar_corpus.py --limpiar` (el corpus del paso 8.3; solo lo borra quien lo creó), y la **Parte 10** del notebook si lo ejecutaste. Mientras existan, el corpus y el bucket siguen guardando datos en el proyecto.
2. En cada terminal con `adk web`: **`Ctrl + C`**.
3. Para salir del entorno virtual: `deactivate`.
4. Comprueba que no quedó nada vivo: `netstat -ano | findstr 8501`. Si algo sigue ahí: `taskkill /PID <pid> /F`.

## 10. Si algo falla
| Síntoma | Qué hacer |
|---|---|
| `No module named 'shared'` o `'rag'` | Falta `. .\env.ps1` en esa terminal |
| La Parte 0 dice «Faltan paquetes» | El kernel no es el `.venv` de tu carpeta, o el `pip install` no terminó. En una celda: `import sys; print(sys.executable)`. Si no termina en `GeminiAgentsBI\.venv\Scripts\python.exe`: elige el kernel correcto (paso 7), o regístralo con `python -m ipykernel install --user --name modulo2alumnos`. Si sí es el correcto: `pip list` y repite el `pip install` del paso 2 |
| `cannot import name 'storage' from 'google.cloud'` | La terminal no usa el entorno del proyecto: `.\.venv\Scripts\Activate.ps1` (debe verse `(.venv)`) |
| `Errno 13 ... 8000` | Usa `--port 8501` |
| `404 NOT_FOUND ... Publisher model` | `MODEL_NAME=gemini-2.5-flash` en `.env` y `GOOGLE_CLOUD_LOCATION=us-central1` |
| `403 ... has not been used in project` o `SERVICE_DISABLED` | Falta habilitar una API (paso 3). El mensaje dice cuál: pídele al instructor que la habilite y espera unos minutos |
| `Bucket ... does not belong to project` | Casi siempre es **Cloud Resource Manager** deshabilitada: el SDK oculta el error real |
| `Vector Search API has not been used in project` | Habilitar `vectorsearch.googleapis.com` (paso 3) |
| `No available indexing project found` | El corpus se debe crear por REST **indicando el backend** (el notebook y `preparar_corpus.py` ya lo hacen). Si te sale igual, avisa al instructor |
| `... does not exist or is empty` al importar | La ruta debe ser la **carpeta con barra final** (`gs://bucket/carpeta/`), no `carpeta/*`; y el bucket debe tener archivos |
| `RankRequest.records() is empty` | El reranker recibió 0 candidatos: la etapa anterior no devolvió nada (corpus aún sin indexar, o los textos no se reconocieron). Espera un minuto y repite la celda anterior |
| Un PDF escaneado «se importó» pero no aparece en las búsquedas | Es lo esperado con el analizador **por defecto**: importa sin error y sin guardar nada. Se necesita el **analizador de LLM** |
| `404 ... gemini-embedding-2` | Ese modelo (multimodal) solo está en `global`, `us` y `eu`, no en `us-central1`; el notebook ya usa un cliente `global` |
| `El proyecto no está en modo sin servidores` | El modo lo cambia el **instructor**; no sigas |
| Una operación de corpus falla por otra en curso | Espera un minuto y repite **solo esa celda** |
| `UnicodeEncodeError` al imprimir | `. .\env.ps1` ya fija `PYTHONIOENCODING=utf-8`; vuelve a ejecutarlo en esa terminal |
| Cambié el `.env` y no pasa nada | Reinicia el kernel o `adk web`: leen el `.env` al arrancar |
| `RuntimeError: Falta GOOGLE_CLOUD_PROJECT` | El `.env` no tiene el ID real (o dice `tu-proyecto`); corrígelo y reinicia |

Más detalle: `src/rag/README.md` (mapa del proyecto, cómo ampliarlo y las lecciones de RAG Engine).
