"""RAG Engine en modo SIN SERVIDORES (= Vector Search administrado): lo que el notebook del Módulo 2 hace
con servicios reales, empaquetado para reutilizarlo.

Verificado en el notebook (2026-10-19/20): modo sin servidores, creación de corpus por REST con el backend
explícito, importación de PDFs con el analizador de LLM, recuperación y borrado.

Lecciones que costaron tiempo (están aquí para que no se repitan):
- El corpus se crea por REST INDICANDO el backend `rag_managed_vertex_vector_search`. Con `create_corpus` del SDK
  (sin backend explícito) el proyecto devolvió «No available indexing project found».
- Importar desde un bucket exige habilitar las APIs Vector Search, Discovery Engine y **Cloud Resource Manager**:
  el SDK comprueba el dueño del bucket con esta última y, si está deshabilitada, oculta el error real.
- La ruta de importación es la CARPETA con barra final (`gs://bucket/carpeta/`); con el comodín `carpeta/*`
  el servicio respondió «does not exist or is empty».
- Las operaciones sobre corpus no admiten concurrencia: una tras otra.
- Con PDFs escaneados, el analizador por defecto importa SIN ERROR y SIN guardar nada (pérdida silenciosa).

Los imports de Google son perezosos: este módulo se puede importar sin credenciales (p. ej. en las pruebas).
"""
import json
import time

PARSER_MODEL = "gemini-2.5-flash"      # los 2.5 se retiran el 2027-03-31; los 3.x solo se sirven desde global/us/eu
DEFAULT_PARSER_PROMPT = ("Transcribe el documento fielmente, en español. Conserva los encabezados («Artículo», «Nota», "
                         "«Item») con su numeración y las tablas. No añadas comentarios, resúmenes ni explicaciones.")


class RagEngineProject:
    """Un proyecto + una región de RAG Engine (el modo sin servidores solo existe en us-central1)."""

    def __init__(self, project: str, location: str = "us-central1"):
        self.project, self.location = project, location
        self._cred = None
        self._sdk_client = None

    # ------------------------------------------------------------------ REST (v1beta1)
    def rest(self, method: str, path: str, **kw) -> dict:
        import google.auth
        import google.auth.transport.requests
        import httpx
        if self._cred is None:
            self._cred, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        self._cred.refresh(google.auth.transport.requests.Request())
        url = f"https://{self.location}-aiplatform.googleapis.com/v1beta1/{path}"
        cab = {"Authorization": f"Bearer {self._cred.token}", "Content-Type": "application/json",
               "x-goog-user-project": self.project}
        r = httpx.request(method, url, headers=cab, timeout=120, **kw)
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} → HTTP {r.status_code}: {r.text[:400]}")
        return r.json() if r.text else {}

    def _esperar(self, op: dict, intentos: int = 24, pausa: float = 5.0) -> dict:
        for _ in range(intentos):
            op = self.rest("GET", op["name"])
            if op.get("done"):
                break
            time.sleep(pausa)
        if "error" in op or not op.get("done"):
            raise RuntimeError("La operación no terminó bien: " + json.dumps(op, ensure_ascii=False)[:600])
        return op

    # ------------------------------------------------------------------ modo del proyecto
    @property
    def _ruta_config(self) -> str:
        return f"projects/{self.project}/locations/{self.location}/ragEngineConfig"

    def config(self) -> dict:
        return self.rest("GET", self._ruta_config)

    def is_serverless(self) -> bool:
        """True si el proyecto está en modo sin servidores. La forma exacta de la respuesta no está documentada;
        se busca la palabra «serverless» en el JSON (así se comportó en el notebook)."""
        return "serverless" in json.dumps(self.config()).lower()

    def switch_to_serverless(self) -> dict:
        """⚠️ Cambia el modo de TODO el proyecto en esta región. No mueve ni borra datos del otro modo."""
        return self.rest("PATCH", self._ruta_config, json={"ragManagedDbConfig": {"serverless": {}}})

    # ------------------------------------------------------------------ corpus
    def list_corpora(self) -> list[dict]:
        return self.rest("GET", f"projects/{self.project}/locations/{self.location}/ragCorpora").get("ragCorpora", [])

    def create_corpus(self, display_name: str) -> str:
        """Crea el corpus con el backend EXPLÍCITO (Vector Search administrado) y devuelve su nombre de recurso.
        Si ya existe uno con ese nombre, lo reutiliza (así no se acumulan corpus al repetir una celda)."""
        for c in self.list_corpora():
            if c.get("displayName") == display_name:
                return c["name"]
        op = self.rest("POST", f"projects/{self.project}/locations/{self.location}/ragCorpora",
                       json={"display_name": display_name,
                             "vector_db_config": {"rag_managed_vertex_vector_search": {}}})
        return self._esperar(op)["response"]["name"]

    def delete_corpus(self, name: str) -> dict:
        return self.rest("DELETE", name, params={"force": "true"})

    # ------------------------------------------------------------------ importación (SDK agentplatform, experimental)
    def _sdk(self):
        if self._sdk_client is None:
            import agentplatform
            self._sdk_client = agentplatform.Client(project=self.project, location=self.location)
        return self._sdk_client

    def import_folder(self, corpus: str, folder_uri: str, chunk_size: int = 512, overlap: int = 100,
                      llm_parser: bool = False, parser_prompt: str | None = None) -> None:
        """Importa una carpeta de Cloud Storage. `llm_parser=True` lee los PDFs con Gemini (necesario para
        escaneos y tablas; se paga por página). La carpeta siempre con barra final."""
        from agentplatform import types as ap
        from google.genai import types as genai_types
        cfg = dict(
            gcs_source=genai_types.GcsSource(uris=[folder_uri.rstrip("/") + "/"]),
            rag_file_transformation_config=ap.RagFileTransformationConfig(
                rag_file_chunking_config=ap.RagFileChunkingConfig(chunk_size=chunk_size, chunk_overlap=overlap)),
            max_embedding_requests_per_min=1000)
        if llm_parser:
            kw = dict(model_name=f"projects/{self.project}/locations/{self.location}/publishers/google/models/{PARSER_MODEL}",
                      max_parsing_requests_per_min=30)
            if parser_prompt:
                kw["custom_parsing_prompt"] = parser_prompt
            cfg["rag_file_parsing_config"] = ap.RagFileParsingConfig(llm_parser=ap.RagFileParsingConfigLlmParser(**kw))
        self._sdk().rag.import_files(name=corpus, import_config=ap.ImportRagFilesConfig(**cfg))

    def retrieve(self, corpus: str, query: str, k: int = 20, attempts: int = 4) -> list:
        """Etapa 1: los k fragmentos más cercanos. Reintenta si el corpus aún no tiene nada indexado."""
        from agentplatform import types as ap
        from google.genai import types as genai_types
        for _ in range(attempts):
            resp = self._sdk().rag.retrieve_contexts(
                vertex_rag_store=genai_types.VertexRagStore(
                    rag_resources=[genai_types.VertexRagStoreRagResource(rag_corpus=corpus)]),
                query=ap.RagQuery(text=query, rag_retrieval_config=genai_types.RagRetrievalConfig(top_k=k)))
            ctx = getattr(getattr(resp, "contexts", None), "contexts", None) or []
            if ctx:
                return ctx
            time.sleep(10)
        return []

    # ------------------------------------------------------------------ Cloud Storage (mismas credenciales)
    def upload(self, bucket: str, prefix: str, files: dict[str, bytes | str]) -> None:
        """Sube {nombre_de_archivo: contenido} a gs://bucket/prefix/. Crea el bucket si no existe."""
        from google.cloud import storage
        gcs = storage.Client(project=self.project)
        b = gcs.bucket(bucket)
        if not b.exists():
            b = gcs.create_bucket(bucket, location=self.location)
        for nombre, contenido in files.items():
            blob = b.blob(f"{prefix}/{nombre}")
            if isinstance(contenido, str):
                blob.upload_from_string(contenido, content_type="text/markdown")
            else:
                blob.upload_from_string(contenido)

    def delete_bucket(self, bucket: str) -> None:
        from google.cloud import storage
        b = storage.Client(project=self.project).bucket(bucket)
        if b.exists():
            b.delete(force=True)
