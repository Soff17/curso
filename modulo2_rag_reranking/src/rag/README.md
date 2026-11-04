# `rag` + `auditor_rag_app` · Proyecto base del Módulo 2

Es el **proyecto real** al que llegas con el notebook: el **Agente Auditor de Políticas Financieras** (el entregable del módulo: busca en las normativas internas, aplica reranking para quedarse con los 3 fragmentos más relevantes y justifica la aprobación o el rechazo de un gasto), ya organizado como lo mantendrías en tu repositorio. **Cópialo y amplíalo**: en el Módulo 3 se reutiliza para buscar en el catálogo de datos, y en el capstone será el «Agente RAG + Reranking» del orquestador.

## Qué contiene
```
auditor_rag_app/agent.py   root_agent para `adk web`: el auditor, con la fuente de documentos que elijas
rag/
 ├── chunking.py      cortar: por artículo (.md), y para PDFs: ChunkDoc, corte por estructura y semántico
 ├── retrieval.py     etapa 1 (TF-IDF / Vertex / RAG Engine), etapa 2 (reranker), umbral, cuota por fuente, Hit@3
 ├── ragengine.py     RAG Engine en modo sin servidores: corpus, importar PDFs con analizador de LLM, recuperar
 └── auditor.py       Citation, AuditDecision, fábrica de herramienta y agente, buscar_politicas (el de siempre)
preparar_corpus.py    (en modulo2_rag_reranking/) sube los PDFs, crea los corpus e importa: lo que hace el notebook
```
El flujo es siempre el mismo y **solo cambia de dónde salen los candidatos**:
```
consulta → etapa 1: K = 20 candidatos → etapa 2: reranking → N = 3 → umbral → citas → agente → AuditDecision
```

## Mapa de archivos
| Archivo | Para qué sirve | ¿Obligatorio en un proyecto tuyo? |
|---|---|---|
| `auditor_rag_app/agent.py` | Define el agente. ADK busca **`root_agent`** | **Sí** |
| `rag/chunking.py` | `semantic_chunks`/`load_corpus` (un chunk por artículo, citas exactas) y, para texto de PDF, `to_chunk_doc`, `split_by_structure`, `split_semantic` | Sí |
| `rag/retrieval.py` | `TfidfRetriever` (offline), `VertexEmbeddingRetriever`, `RagEngineRetriever`, `LexicalReranker` (offline), `VertexRanker` (Ranking API), `two_stage_retrieve`, `select_with_quotas`, `calibrate_threshold`, `hit_at_n` | Sí |
| `rag/auditor.py` | `evidence`, `make_tool`, `build_auditor` (el auditor con cualquier fuente), `buscar_politicas` y `build_auditor_agent` (los usan el Módulo 3 y el capstone) | Sí |
| `rag/ragengine.py` | `RagEngineProject`: modo del proyecto, corpus, importación, recuperación, Cloud Storage | Solo si usas RAG Engine |
| `preparar_corpus.py` | Prepara los corpus de punta a punta. `--dry-run` muestra el plan; `--limpiar` borra | Solo si usas RAG Engine |
| `compare_rerank.py` | Compara Hit@3 sin y con reranking (offline) | No (demo) |

Fuera de esta carpeta: `shared/config.py` (rutas, `MODEL_NAME`, K, N), `data/politicas/` (markdown), `data/politicas_pdf/` y `data/reportes/` (PDFs sintéticos, uno de ellos escaneado) y `.env`.

## Cómo ejecutarlo
Desde la raíz del proyecto, en PowerShell y con el entorno activado:
```powershell
. .\env.ps1                                              # deja listo el PYTHONPATH
python modulo2_rag_reranking/compare_rerank.py           # offline: Hit@3 sin y con reranking
adk web --port 8501 modulo2_rag_reranking/src            # elige auditor_rag_app
```
**Fuente de los documentos** (variable `AUDITOR_FUENTE` en el `.env`):

| Valor | Documentos | Requiere |
|---|---|---|
| `politicas` (por defecto) | Las políticas en markdown, un chunk por artículo | Nada más (offline usa TF-IDF; con `AGENTS_MODE=cloud`, Vertex y la Ranking API) |
| `rag_engine` | Las políticas en PDF, ya importadas en RAG Engine (Vector Search administrado) | `AGENTS_MODE=cloud` y `RAG_CORPUS_POLITICAS` |

Para obtener el corpus: `python modulo2_rag_reranking/preparar_corpus.py` (💸 llama al analizador de LLM; imprime las variables que debes copiar al `.env`; `--variables` las vuelve a imprimir). Con `--limpiar` se borra todo.
**Extensión opcional (no es parte del entregable):** `preparar_corpus.py --con-reportes` añade el reporte trimestral 10-Q (PDF) como segunda fuente y la variable `RAG_CORPUS_REPORTES`; con ella, el auditor busca en las dos con **cuota por fuente** (2 políticas + 1 reporte). Sirve para preguntas que cruzan una cifra del reporte con una regla de las políticas; sin el reporte, el auditor **escala** esas preguntas, que es lo correcto.
**Umbral:** `UMBRAL_AUDITOR` si lo defines. Si no: 0.14 en cloud (calibrado con la Ranking API) y, en offline, **se calibra solo al arrancar** con los 6 casos y tres consultas fuera del corpus (el 0.05 por defecto del reranker léxico dejaba pasar el caso del yate). **Se recalibra** cuando cambia el corpus o el reranker: los puntajes de cada fuente no son comparables.
- En la lista de `adk web` aparecen `auditor_rag_app` **y `rag`**: `rag` es la librería, no un agente; elige `auditor_rag_app`.
- Usa `--port 8501`: en Windows el puerto 8000 puede estar reservado.
- Preguntas para probar: `Viaje internacional de 4 días, USD 2,400 total, sin autorización previa del Director` (debe rechazar citando el Art. 1.3) y `Compra de un yate para la dirección` (debe responder ESCALAR).

## Cómo ampliarlo
1. **Otra fuente de documentos:** escribe una clase con `search(consulta, k) -> list[Scored]` (o una función que devuelva candidatos), y pásala a `evidence(...)` o a `select_with_quotas(...)`. Es lo único que cambia.
2. **Más de una fuente:** `select_with_quotas` reordena todo con **una sola llamada** al reranker y reserva lugar a cada fuente, para que una no copie los N lugares. Las cuotas son una decisión de diseño; otra opción es un **enrutador** que decida a qué fuente preguntar.
3. **Otra forma de cortar:** `split_by_structure` si el texto conserva los encabezados; `split_semantic` si no (necesita una función que dé embeddings). En la práctica se combinan.
4. **Otro reranker** (Cohere, BGE…): basta un objeto con `rerank(consulta, candidatos, n)`. Recalibra el umbral: la escala del puntaje cambia.
5. **Reglas que ya nos mordieron:**
   - **Un fragmento sin artículos** (p. ej. del 10-Q) no puede acertar un Hit@3 por artículo ni citarse como «Art. n»: su cita es `fragmento n (sección)`.
   - **El texto de un analizador de LLM no es el original:** puede añadir anotaciones («Context: …») y equivocarse en un escaneo. Verifica las cifras contra el documento.
   - **Al añadir un documento sobre el mismo tema**, el agente recibe evidencia nueva y sus respuestas pueden cambiar. Vuelve a correr los 6 casos.
   - La respuesta del modelo **no es determinista**: valida decisiones y citas, no redacción.

## Lecciones de RAG Engine (están también en `rag/ragengine.py`)
- El corpus se crea por REST **indicando el backend** `rag_managed_vertex_vector_search`; con `create_corpus` del SDK, sin backend explícito, el proyecto devolvió «No available indexing project found».
- Hay que habilitar las APIs **Vector Search, Discovery Engine y Cloud Resource Manager**. El SDK comprueba el dueño del bucket con la última y, si está deshabilitada, oculta el error real («Bucket … does not belong to project»).
- La ruta de importación es la **carpeta con barra final** (`gs://bucket/carpeta/`), no `carpeta/*`.
- Las operaciones sobre corpus **no admiten concurrencia**: una tras otra.
- Con un **PDF escaneado**, el analizador por defecto importa **sin error y sin guardar nada**. El de LLM sí lo lee.
- El modo del proyecto (Spanner o sin servidores) es **del proyecto**: cambiarlo afecta a todos. En modo Spanner se cobra una instancia mientras exista; el único modo de detener ese cobro (Unprovisioned) borra los datos.

## Pruebas (no llaman a ningún servicio)
```powershell
python -m pytest modulo2_rag_reranking -q
```
Cubren el chunking (estructurado y de PDF), el corte semántico, la cuota por fuente, la calibración del umbral, el Hit@3, `RagEngineRetriever` y `RagEngineProject` con piezas simuladas, la fábrica del auditor, la app de ADK y el plan de `preparar_corpus.py`. **No prueban el comportamiento del modelo ni de los servicios reales**: para eso, ejecuta el notebook.

## Qué NO es todavía
- Es una base para aprender y ampliar, **no** un proyecto listo para producción: credenciales de usuario (en producción, cuentas de servicio con permisos mínimos), datos sintéticos y pequeños (el corpus tiene 20 artículos, así que K = 20 devuelve casi todo) y sin evaluación sistemática (eso es el Módulo 5: *Faithfulness*, *Context Recall*).
- **No está conectado al supervisor del Módulo 1.** El auditor es local y no usa A2A; exponerlo por A2A (por ejemplo, en el puerto 8003) es parte del capstone, con `AuditDecision` como contrato.
- **Sin verificar con servicios reales desde este proyecto:** `preparar_corpus.py` tal cual, la app con `AUDITOR_FUENTE=rag_engine` y el arranque de `adk web` con `auditor_rag_app`. La **misma secuencia de llamadas** sí se ejecutó en el notebook.
