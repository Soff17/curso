# Gemini Enterprise Agent Platform – Programa Equipo BI

Material del instructor y entregables de referencia para el programa de **Consultoría y Acompañamiento** (6 semanas, 4 h/semana) para 30 personas organizadas en 5 células de 6.

Fuente: `Cronograma de Consultoria y Acompañamiento - Equipo BI v2.pdf` (Key Prediction 2026).

## Estructura

| Carpeta | Contenido |
|---|---|
| `docs/00-analisis-programa.md` | Análisis del cronograma, supuestos, riesgos y preguntas abiertas |
| `docs/01-plan-instructor.md` | Agenda hora por hora de las 6 semanas (2 h teórico-práctica + 2 h tutoría) |
| `docs/02-rubricas.md` | Rúbricas de evaluación por módulo y para el Capstone |
| `docs/03-setup-gcp.md` | Checklist de preparación de entorno (GCP, APIs, IAM, cuentas) |
| `data/` | Datos sintéticos financieros (políticas, esquema, seed SQLite) |
| `shared/` | Configuración común (modelo, settings) |
| `modulo1_adk_a2a/` | M1: ADK Code-First + A2A (Supervisor ↔ Presupuestos). **Incluye `SESION_TEORICA.md` (guía de la sesión teórica) , `SESION_PRACTICA.md` (guía de la práctica) y `notebooks/` (práctica de 2 h)** |
| `modulo2_rag_reranking/` | M2: RAG financiero + Two-Stage Retrieval (K=20 → N=3) |
| `modulo3_sql_bigquery/` | M3: Text-to-SQL con RAG de metadata, SQL Server/BigQuery, híbrido |
| `modulo4_ml_multimodal_bi/` | M4: ML por Function Calling, Gemini Vision, Tableau API |
| `modulo5_agentops/` | M5: Evaluación (Faithfulness), trazabilidad, DLP, CI/CD gate |
| `capstone/` | Demo Day: orquestador multiagente "División Norte Q3" |

Los módulos 4-5 contienen `GUIA_INSTRUCTOR.md` (objetivos, guion, demos, errores comunes), `LAB_CELULAS.md` (enunciado para los alumnos), `PASO_A_PASO.md` y `src/` + `tests/` con la solución de referencia. Los módulos 1, 2 y 3 ya están consolidados en `SESION_TEORICA.md` y `SESION_PRACTICA.md`, más `COMANDOS.md` en los módulos 1 y 2 (el del módulo 3 está pendiente). Los archivos anteriores del módulo 1 están en `modulo1_adk_a2a/_anteriores/`.

## Arranque rápido

```powershell
cd GeminiAgentsBI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python data/seed_data.py          # genera data/finanzas.db
pytest                            # tests offline (sin credenciales de GCP)
```

Todo el código tiene **modo offline** (SQLite, TF-IDF, reranker léxico, modelos stub) para ensayar sin GCP; el modo cloud se activa con variables de entorno (ver `.env.example`).

## Aviso importante

Las APIs de ADK, A2A y Agent Platform (antes Vertex AI) cambian con rapidez. Los agentes se verificaron con **google-adk 2.11.0** (construcción, descubrimiento en `adk web`, agent card A2A, workflows); las respuestas del LLM, Tableau, SQL Server/BigQuery reales, Ranking API, DLP y el despliegue **no se han ejecutado**. Ver `docs/05-nombres-actuales.md` y `docs/03-setup-gcp.md`. Los datos son 100 % sintéticos.
