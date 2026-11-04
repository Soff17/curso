"""Prepara RAG Engine para el agente híbrido del Módulo 3: el corpus de POLÍTICAS (PDF) y el del INFORME de presupuesto (PDF).

    python modulo3_sql_bigquery/preparar_rag.py --dry-run     # muestra el plan; no llama a ningún servicio
    python modulo3_sql_bigquery/preparar_rag.py               # 💸 sube los PDFs, crea los corpus e importa (analizador de LLM)
    python modulo3_sql_bigquery/preparar_rag.py --variables   # vuelve a imprimir las variables del .env
    python modulo3_sql_bigquery/preparar_rag.py --limpiar     # borra el corpus del informe y el bucket de este módulo
    python modulo3_sql_bigquery/preparar_rag.py --limpiar --incluir-politicas    # además, el corpus de políticas

El corpus de políticas es el MISMO del Módulo 2 si todavía existe (se llama `auditor_politicas_<usuario>`): se reutiliza y no se
vuelve a importar. Si ya lo borraste (el cierre del Módulo 2 lo borra), se crea de nuevo con los mismos PDFs. El corpus del informe
es nuevo: es otro documento y va en un corpus aparte para que las fuentes no se tapen entre sí.
Requisitos: los del Módulo 2 (APIs de Vertex AI, Discovery Engine, Vector Search y Cloud Resource Manager; RAG Engine en modo sin
servidores; `gcloud auth application-default login`). Sin verificar contra el servicio real: lo corre quien lo prueba.
"""
import argparse
import getpass
import os
import re
import sys

from rag.ragengine import DEFAULT_PARSER_PROMPT, RagEngineProject
from shared.config import DATA_DIR

PDF_POLITICAS = DATA_DIR / "politicas_pdf"
PDF_INFORMES = DATA_DIR / "informes"


def nombres(proyecto: str) -> dict:
    usuario = re.sub(r"[^a-z0-9]", "", getpass.getuser().lower())[:12] or "alumno"
    return {"usuario": usuario, "bucket": f"{proyecto}-rag-m3-{usuario}",
            "politicas": f"auditor_politicas_{usuario}",             # el mismo nombre que usa preparar_corpus.py (Módulo 2)
            "informe": f"informe_presupuesto_{usuario}"}


def imprimir_variables(corpus_pol: str, corpus_inf: str) -> None:
    print("AGENTS_MODE=cloud\nAUDITOR_FUENTE=rag_engine\nINFORME_FUENTE=rag_engine")
    print(f"RAG_CORPUS_POLITICAS={corpus_pol}\nRAG_CORPUS_INFORMES={corpus_inf}")


def main(argv: list[str] | None = None, rag_factory=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="muestra el plan sin llamar a ningún servicio")
    ap.add_argument("--variables", action="store_true", help="imprime las variables de los corpus que ya existen")
    ap.add_argument("--limpiar", action="store_true", help="borra el corpus del informe y el bucket de este módulo")
    ap.add_argument("--incluir-politicas", action="store_true", help="con --limpiar: borra también el corpus de políticas")
    args = ap.parse_args(argv)

    proyecto = os.getenv("GOOGLE_CLOUD_PROJECT", "tu-proyecto")
    n = nombres(proyecto)
    pdfs_pol, pdfs_inf = sorted(PDF_POLITICAS.glob("*.pdf")), sorted(PDF_INFORMES.glob("*.pdf"))
    if not pdfs_pol or not pdfs_inf:
        print("Faltan PDFs en data/politicas_pdf o data/informes.", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Proyecto: {proyecto} · bucket: {n['bucket']}")
        print(f"1. Corpus de políticas «{n['politicas']}»: si existe (Módulo 2), se reutiliza; si no, subir {len(pdfs_pol)} PDFs "
              f"-> gs://{n['bucket']}/pdf_politicas/ , crearlo e importar")
        print(f"2. Corpus del informe «{n['informe']}»: subir {len(pdfs_inf)} PDF -> gs://{n['bucket']}/pdf_informes/ , crearlo e importar")
        print("   (importar con el analizador de LLM, gemini-2.5-flash; backend explícito: Vector Search administrado)")
        print("3. Imprimir las variables de entorno para `adk web`\n\nNo se llamó a ningún servicio.")
        return 0

    if proyecto == "tu-proyecto":
        print("Falta GOOGLE_CLOUD_PROJECT en tu .env.", file=sys.stderr)
        return 2
    rag = (rag_factory or RagEngineProject)(proyecto)
    existentes = {c.get("displayName"): c["name"] for c in rag.list_corpora()}

    if args.variables:
        if n["politicas"] not in existentes or n["informe"] not in existentes:
            print("Falta algún corpus: ejecuta el script sin opciones para crearlo.", file=sys.stderr)
            return 1
        print("Define en tu .env:")
        imprimir_variables(existentes[n["politicas"]], existentes[n["informe"]])
        return 0

    if args.limpiar:
        borrar = [n["informe"]] + ([n["politicas"]] if args.incluir_politicas else [])
        for nombre in borrar:
            if nombre in existentes:
                rag.delete_corpus(existentes[nombre])
                print("borrado:", nombre)
        rag.delete_bucket(n["bucket"])
        print("bucket borrado:", n["bucket"])
        if not args.incluir_politicas:
            print(f"El corpus de políticas «{n['politicas']}» NO se tocó (es el del Módulo 2): bórralo con "
                  "`--limpiar --incluir-politicas` o con el script del Módulo 2.")
        return 0

    if not rag.is_serverless():
        print("El proyecto NO está en modo sin servidores: no sigas sin hablar con quien administra el proyecto.", file=sys.stderr)
        return 2
    if n["politicas"] in existentes:
        print(f"Corpus de políticas «{n['politicas']}»: ya existe, se reutiliza.")
        corpus_pol = existentes[n["politicas"]]
    else:
        rag.upload(n["bucket"], "pdf_politicas", {p.name: p.read_bytes() for p in pdfs_pol})
        corpus_pol = rag.create_corpus(n["politicas"])           # las operaciones sobre corpus no admiten concurrencia
        rag.import_folder(corpus_pol, f"gs://{n['bucket']}/pdf_politicas", llm_parser=True, parser_prompt=DEFAULT_PARSER_PROMPT)
        print(f"Corpus de políticas «{n['politicas']}»: creado e importado.")
    rag.upload(n["bucket"], "pdf_informes", {p.name: p.read_bytes() for p in pdfs_inf})
    corpus_inf = rag.create_corpus(n["informe"])
    rag.import_folder(corpus_inf, f"gs://{n['bucket']}/pdf_informes", llm_parser=True, parser_prompt=DEFAULT_PARSER_PROMPT)
    print(f"Corpus del informe «{n['informe']}»: creado e importado.")
    print("\nListo. Para usarlos en `adk web`, define en tu .env:")
    imprimir_variables(corpus_pol, corpus_inf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
