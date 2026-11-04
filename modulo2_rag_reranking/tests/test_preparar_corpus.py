"""El script de preparación: solo el plan (--dry-run) y los nombres. No llama a ningún servicio."""
import importlib.util
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preparar_corpus", RAIZ / "preparar_corpus.py")
preparar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preparar)


def test_dry_run_muestra_el_plan_y_no_toca_la_nube(capsys, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "mi-proyecto")
    assert preparar.main(["--dry-run"]) == 0
    salida = capsys.readouterr().out
    assert "mi-proyecto-rag-m2-" in salida and "Vector Search administrado" in salida
    assert "5 PDFs de políticas" in salida
    assert "reportes" not in salida                      # por defecto SOLO las políticas (lo que pide el entregable)


def test_dry_run_con_reportes_muestra_la_extension(capsys, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "mi-proyecto")
    assert preparar.main(["--dry-run", "--con-reportes"]) == 0
    assert "2 PDFs de reportes" in capsys.readouterr().out


def test_los_nombres_llevan_el_usuario_y_son_validos_para_un_bucket():
    n = preparar.nombres("mi-proyecto")
    assert n["bucket"] == f"mi-proyecto-rag-m2-{n['usuario']}"
    assert n["bucket"] == n["bucket"].lower() and "_" not in n["bucket"]


def test_sin_proyecto_configurado_no_sigue(monkeypatch, capsys):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.setattr(preparar, "RagEngineProject", lambda *_: (_ for _ in ()).throw(AssertionError("no debe llamarse")))
    assert preparar.main([]) == 2


def test_variables_imprime_las_de_los_corpus_que_ya_existen(monkeypatch, capsys):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "mi-proyecto")
    n = preparar.nombres("mi-proyecto")

    class Falso:
        def __init__(self, *_): pass
        def list_corpora(self):
            return [{"displayName": n["politicas"], "name": "projects/1/locations/us-central1/ragCorpora/11"},
                    {"displayName": n["reportes"], "name": "projects/1/locations/us-central1/ragCorpora/22"}]
    monkeypatch.setattr(preparar, "RagEngineProject", Falso)
    assert preparar.main(["--variables"]) == 0
    salida = capsys.readouterr().out
    assert "AUDITOR_FUENTE=rag_engine" in salida
    assert "RAG_CORPUS_POLITICAS=projects/1/locations/us-central1/ragCorpora/11" in salida
    assert "RAG_CORPUS_REPORTES=projects/1/locations/us-central1/ragCorpora/22" in salida     # si existe, se muestra


def test_variables_sin_corpus_de_reportes_imprime_solo_politicas(monkeypatch, capsys):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "mi-proyecto")
    n = preparar.nombres("mi-proyecto")

    class Falso:
        def __init__(self, *_): pass
        def list_corpora(self):
            return [{"displayName": n["politicas"], "name": "projects/1/locations/us-central1/ragCorpora/11"}]
    monkeypatch.setattr(preparar, "RagEngineProject", Falso)
    assert preparar.main(["--variables"]) == 0
    salida = capsys.readouterr().out
    assert "RAG_CORPUS_POLITICAS=" in salida and "RAG_CORPUS_REPORTES" not in salida


def test_variables_avisa_si_los_corpus_no_existen(monkeypatch, capsys):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "mi-proyecto")

    class Falso:
        def __init__(self, *_): pass
        def list_corpora(self): return []
    monkeypatch.setattr(preparar, "RagEngineProject", Falso)
    assert preparar.main(["--variables"]) == 1
    assert "No existe todavía el corpus de políticas" in capsys.readouterr().err
