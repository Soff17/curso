# Lab Módulo 4 – Agente ML & BI

## Objetivo
Un agente que invoca **vía A2A** el modelo interno de forecasting, extrae la gráfica de Tableau mediante su API y genera un **diagnóstico** que integra el análisis visual y el resultado del modelo.

## Requisitos
1. Levantar `ml_service` (`uvicorn ml_service.app:app --port 8080`) y consumirlo con Function Calling (docstrings claros, payload validado por Pydantic).
2. Exponer el agente ML como servidor A2A (ver patrón del M1) y que el agente BI lo llame de forma remota.
3. `obtener_vista_tableau`: autenticación con PAT, descarga de imagen y CSV subyacente (o stub).
4. Gemini Vision: preguntar por tendencia, picos y anomalías de la imagen.
5. El diagnóstico debe indicar **si la gráfica confirma o contradice** el modelo.
6. Looker Studio: describir (sin código) cómo alimentar el mismo dashboard desde BigQuery y capturar la imagen.

## Criterios
- Timeouts y errores de red devueltos como dato estructurado.
- El LLM nunca calcula el pronóstico; solo lo interpreta.
- Los secretos (PAT) salen de variables de entorno / Secret Manager, no del repo.
