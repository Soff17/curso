import os
import sys
from pathlib import Path

# Las pruebas NUNCA llaman a servicios de Google, aunque tu .env diga AGENTS_MODE=cloud o apunte a un corpus.
# `shared.config` carga el .env sin pisar lo que ya esté definido, así que se fija aquí, antes de importarlo.
os.environ["AGENTS_MODE"] = "offline"
os.environ["AUDITOR_FUENTE"] = "politicas"
os.environ["INFORME_FUENTE"] = "markdown"           # Módulo 3: el informe en RAG Engine también necesita la nube
os.environ["SQL_BACKEND"] = "sqlite"                # y la base real (BigQuery) tampoco se toca desde las pruebas
for _v in ("RAG_CORPUS_POLITICAS", "RAG_CORPUS_REPORTES", "RAG_CORPUS_INFORMES", "UMBRAL_AUDITOR", "UMBRAL_INFORME",
           "UMBRAL_CATALOGO"):
    os.environ[_v] = ""

ROOT = Path(__file__).parent
for p in [ROOT, *ROOT.glob("modulo*/src"), ROOT / "capstone" / "src"]:
    sys.path.insert(0, str(p))
sys.path.insert(0, str(ROOT / "modulo4_ml_multimodal_bi"))
