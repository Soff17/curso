"""Prepara el corpus de RAG Engine con las POLÍTICAS (en PDF) para el auditor: lo que hace el notebook del Módulo 2,
como script reutilizable.

    python modulo2_rag_reranking/preparar_corpus.py --dry-run   # muestra el plan; no llama a ningún servicio
    python modulo2_rag_reranking/preparar_corpus.py             # sube los PDFs de políticas, crea el corpus e importa
    python modulo2_rag_reranking/preparar_corpus.py --variables # vuelve a imprimir las variables de corpus ya creados
    python modulo2_rag_reranking/preparar_corpus.py --limpiar   # borra los corpus y el bucket

El entregable del módulo es un auditor que busca en las NORMATIVAS INTERNAS (las políticas). Por eso, por defecto,
solo se crea el corpus de políticas. Extensión opcional: `--con-reportes` añade el reporte 10-Q (PDF) como segunda
fuente (el notebook lo usa en la parte «combinado»); con ella, el auditor busca en las dos con cuota por fuente.

Al terminar imprime las variables de entorno que necesita `adk web` (AUDITOR_FUENTE=rag_engine).
Requisitos (una vez por proyecto): APIs Vertex AI, Discovery Engine, Vector Search y Cloud Resource Manager;
RAG Engine en modo sin servidores; credenciales de aplicación (`gcloud auth application-default login`).
💸 El analizador de LLM llama a Gemini por cada página. Verificado el 2026-10-20: crea el corpus, importa y el
auditor responde en `adk web`.
"""
import argparse
import getpass
import os
import re
import sys

from rag.ragengine import DEFAULT_PARSER_PROMPT, RagEngineProject
from shared.config import DATA_DIR

PDF_POLITICAS = DATA_DIR / "politicas_pdf"
PDF_REPORTES = DATA_DIR / "reportes"


def nombres(proyecto: str) -> dict:
    usuario = re.sub(r"[^a-z0-9]", "", getpass.getuser().lower())[:12] or "alumno"
    return {"usuario": usuario, "bucket": f"{proyecto}-rag-m2-{usuario}",
            "politicas": f"auditor_politicas_{usuario}", "reportes": f"auditor_reportes_{usuario}"}


def imprimir_variables(corpus_pol: str, corpus_rep: str | None = None) -> None:
    print("AGENTS_MODE=cloud\nAUDITOR_FUENTE=rag_engine")
    print(f"RAG_CORPUS_POLITICAS={corpus_pol}")
    if corpus_rep:
        print(f"RAG_CORPUS_REPORTES={corpus_rep}      # extensión opcional: busca también en el reporte 10-Q")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="muestra el plan sin llamar a ningún servicio")
    ap.add_argument("--limpiar", action="store_true", help="borra los corpus y el bucket de este usuario")
    ap.add_argument("--variables", action="store_true", help="imprime las variables de los corpus que ya existen")
    ap.add_argument("--con-reportes", action="store_true", help="extensión: añade el reporte 10-Q (PDF) como segunda fuente")
    args = ap.parse_args(argv)

    proyecto = os.getenv("GOOGLE_CLOUD_PROJECT", "tu-proyecto")
    n = nombres(proyecto)
    pdfs_pol, pdfs_rep = sorted(PDF_POLITICAS.glob("*.pdf")), sorted(PDF_REPORTES.glob("*.pdf"))

    if args.dry_run:
        print(f"Proyecto: {proyecto} · bucket: {n['bucket']}")
        print(f"1. Subir {len(pdfs_pol)} PDFs de políticas -> gs://{n['bucket']}/pdf_politicas/")
        print(f"2. Crear el corpus «{n['politicas']}» (backend explícito: Vector Search administrado)")
        print("3. Importar la carpeta con el analizador de LLM (gemini-2.5-flash)")
        if args.con_reportes:
            print(f"   + extensión: subir {len(pdfs_rep)} PDFs de reportes -> gs://{n['bucket']}/pdf_reportes/ "
                  f"y crear el corpus «{n['reportes']}»")
        print("4. Imprimir las variables de entorno para `adk web`")
        return 0

    if proyecto == "tu-proyecto":
        print("Falta GOOGLE_CLOUD_PROJECT en tu .env.", file=sys.stderr)
        return 2
    rag = RagEngineProject(proyecto)

    if args.variables:
        existentes = {c.get("displayName"): c["name"] for c in rag.list_corpora()}
        if n["politicas"] not in existentes:
            print("No existe todavía el corpus de políticas - ejecuta el script sin opciones para crearlo.", file=sys.stderr)
            return 1
        print("Define en tu .env:")
        imprimir_variables(existentes[n["politicas"]], existentes.get(n["reportes"]))
        return 0

    if args.limpiar:
        for c in rag.list_corpora():
            if c.get("displayName") in (n["politicas"], n["reportes"]):
                rag.delete_corpus(c["name"])
                print("borrado:", c["displayName"])
        rag.delete_bucket(n["bucket"])
        print("bucket borrado:", n["bucket"])
        return 0

    if not rag.is_serverless():
        print("El proyecto NO está en modo sin servidores: no sigas sin hablar con quien administra el proyecto.", file=sys.stderr)
        return 2
    rag.upload(n["bucket"], "pdf_politicas", {p.name: p.read_bytes() for p in pdfs_pol})
    corpus_pol = rag.create_corpus(n["politicas"])           # las operaciones sobre corpus no admiten concurrencia
    rag.import_folder(corpus_pol, f"gs://{n['bucket']}/pdf_politicas", llm_parser=True, parser_prompt=DEFAULT_PARSER_PROMPT)
    corpus_rep = None
    if args.con_reportes:
        rag.upload(n["bucket"], "pdf_reportes", {p.name: p.read_bytes() for p in pdfs_rep})
        corpus_rep = rag.create_corpus(n["reportes"])
        rag.import_folder(corpus_rep, f"gs://{n['bucket']}/pdf_reportes", llm_parser=True, parser_prompt=DEFAULT_PARSER_PROMPT)
    print("\nListo. Para usar estos corpus en `adk web`, define en tu .env:")
    imprimir_variables(corpus_pol, corpus_rep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
