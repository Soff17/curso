"""Configuración común. Lee variables de entorno (.env opcional)."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:  # python-dotenv opcional
    pass

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
POLICIES_DIR = DATA_DIR / "politicas"
DB_PATH = DATA_DIR / "finanzas.db"

MODE = os.getenv("AGENTS_MODE", "offline")  # offline | cloud
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-005")

RETRIEVE_K = 20   # candidatos de la búsqueda vectorial (Módulo 2)
RERANK_N = 3      # fragmentos finales tras reranking
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.05"))


def is_cloud() -> bool:
    return MODE == "cloud"
