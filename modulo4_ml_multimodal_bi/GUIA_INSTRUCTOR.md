# Guía del instructor – Módulo 4 (Semana 4)

## Mensajes clave
1. Los modelos de ML del equipo ya existen: el agente es una **capa de interpretación y orquestación**, no un reemplazo.
2. Function Calling = contrato tipado + docstring; el modelo decide *cuándo*, el servicio decide *qué número*.
3. Multimodalidad: la imagen aporta contexto que el CSV no tiene (anotaciones, filtros visibles, formato condicional) pero **debe validarse contra datos**.
4. Seguridad: PAT con permisos mínimos; no enviar capturas con PII a ningún modelo sin DLP (ver M5).

## Estructura sugerida (2 h)
| Min | Tema |
|---|---|
| 0-30 | Endpoints de Agent Platform (antes Vertex AI Prediction) vs FastAPI; Function Calling; demo `ml_service` |
| 30-60 | Gemini Vision: prompts para dashboards (tendencia/picos/mapas de calor) |
| 60-90 | Tableau REST: auth PAT, `views`, `populate_image`, `populate_csv`, filtros `vf` |
| 90-120 | A2A con agente ML y diagnóstico integrado |

## Looker Studio ("Data Studio")
No hay SDK de extracción equivalente. Opciones: Linking API (preconfigurar reportes), fuente BigQuery y captura vía Chrome headless/PDF programado. Aclarar con el cliente antes de prometerlo.

## Errores comunes
- Pedir a la visión números exactos de ejes (poco fiable) → usar el CSV subyacente.
- No fijar `maxage`/filtros → imagen cacheada de otro contexto.
- Tratar `probabilidad_mora` como certeza.

## Antes de clase
Probar PAT de Tableau, endpoint `/health` del servicio ML y una imagen de ejemplo con Gemini.
