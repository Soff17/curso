# Capstone & Demo Day (Semana 6)

## Caso
> "Analiza por qué la división Norte excedió su presupuesto operacional en Q3 y cuál es el riesgo de impago proyectado."

## Arquitectura esperada
```
Supervisor (A2A)
 ├─ Agente RAG + Reranking  → políticas de gasto, top-3 artículos, ¿exceso permitido?
 ├─ Agente SQL              → SQL Server / BigQuery, desglose contable Q3
 └─ Agente ML & BI          → modelo de mora + validación visual en Tableau
        ↓
Informe ejecutivo sin alucinaciones, con referencias exactas [R#]
```
Referencia offline: `python -m capstone_agent.report` (con `PYTHONPATH` de los módulos; ver README raíz) o `pytest capstone`.

## Plan de las 2 sesiones
**Sesión (2 h) – ensayo:** integración, checklist de abajo, ejecución de la pregunta oficial y de 2 sorpresa.
**Tutoría (2 h) – Demo Day:** 5 células × (12 min demo + 3 min arquitectura + 8 min preguntas).

## Checklist de la célula antes de presentar
- [ ] Pregunta oficial responde en < 90 s.
- [ ] Cada cifra y cada norma lleva referencia verificable.
- [ ] Reranking visible: 20 candidatos → 3 (mostrar evidencia).
- [ ] Guardrail SQL probado con un intento malicioso.
- [ ] Faithfulness medida ≥ umbral acordado; reporte adjunto.
- [ ] Trazas A2A (Cloud Trace o tracer local) mostrando las 3 delegaciones.
- [ ] PII enmascarada en logs.
- [ ] Plan B: modo offline funcionando si cae la red.

## Plantilla de presentación (10 diapositivas)
1. Problema y usuario · 2. Arquitectura A2A · 3. Datos y fuentes · 4. RAG + rerank (antes/después) · 5. SQL y guardrails · 6. ML + visión · 7. Demo en vivo · 8. Evaluación (Faithfulness, Recall, delegación) · 9. Gobernanza y costo · 10. Lecciones y siguientes pasos.

## Preguntas de jurado (banco)
- ¿Qué pasa si el modelo de mora no responde? ¿Y si Tableau devuelve otra vista?
- Muéstrame de dónde sale la cifra X. ¿Y el artículo?
- ¿Cómo evitas que el agente SQL borre datos?
- ¿Qué cambiarías para pasar a producción?
- Misma pregunta para otra división/trimestre.

Rúbrica: `docs/02-rubricas.md`.
