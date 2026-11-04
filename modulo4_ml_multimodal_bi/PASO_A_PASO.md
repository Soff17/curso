# Módulo 4 – Paso a paso (ML interno, multimodalidad y BI)

Terminal en la raíz, `.venv` activo, `. .\env.ps1`.

---
## Contenido 1 – Modelos internos vía Function Calling
1. Levanta el servicio ML (stand-in de un endpoint de Agent Platform Online Inference —antes Vertex AI Prediction— o del FastAPI del equipo):
```powershell
cd modulo4_ml_multimodal_bi
uvicorn ml_service.app:app --port 8080
```
(otra terminal)
```powershell
curl http://localhost:8080/health
curl -X POST http://localhost:8080/forecast -H "Content-Type: application/json" -d '{\"serie\":[10,20,30,40],\"horizonte\":2}'
curl -X POST http://localhost:8080/credit-score -H "Content-Type: application/json" -d '{\"pct_cartera_mora\":0.33,\"dias_vencido_prom\":40,\"monto_expuesto\":900000}'
```
**Debes ver:** pronóstico 50 y 60; probabilidad de mora alta. Abre http://localhost:8080/docs (OpenAPI automático) y prueba un payload inválido (`"serie":[1,2]`) → 422.
2. Consúmelo desde herramientas del agente:
```powershell
python -c "
from bi_agents.ml_tools import pronosticar_gasto, estimar_probabilidad_mora, detectar_anomalias_gasto
print(pronosticar_gasto('Norte', 3)); print(estimar_probabilidad_mora('Norte')); print(detectar_anomalias_gasto('Norte'))"
```
**Debes ver:** histórico mensual, 3 puntos con banda `lo/hi`; probabilidad de mora de Norte ≈ 0.79 (riesgo ALTO) y Sur menor (≈ 0.49, MEDIO).
3. Modo servicio real: `AGENTS_MODE=cloud` + `ML_SERVICE_URL=http://localhost:8080` → `ml_tools._call` usa HTTP. Para un endpoint de Agent Platform (antes Vertex AI Prediction) se cambiaría esa función por `aiplatform.Endpoint(...).predict(...)`.
**Explica:** el LLM decide *cuándo* llamar; el número lo da el modelo. Docstrings y tipos = contrato de la función.

## Contenido 2 – Multimodalidad (Gemini Vision) sobre dashboards
1. Genera la imagen de prueba y analízala:
```powershell
python -c "
from bi_agents.tableau_client import obtener_vista_tableau
from bi_agents.vision import analizar_grafica
v = obtener_vista_tableau('Finanzas','GastoMensual','Norte')
open('vista_norte.png','wb').write(v['png'])
print(analizar_grafica(v['png'], 'Describe tendencia y picos.', v['serie']))"
```
Abre `vista_norte.png` (barras; la última en rojo). **Debes ver** el texto `[stub]` (offline).
2. Con Gemini real (`AGENTS_MODE=cloud`): mismo comando; el modelo describe la imagen. Prueba además con **una captura real** de un dashboard de Tableau/Looker Studio y con una pregunta concreta ("¿qué categoría destaca en el mapa de calor?").
**Explica:** la visión es buena para tendencias/anomalías cualitativas; no para leer cifras exactas de ejes → usar el CSV subyacente. Cuida PII en las capturas.

## Contenido 3 – Tableau REST API y Looker Studio
1. Tableau: crea un *Personal Access Token* (Mi cuenta → Configuración → Tokens de acceso personal). Llena `.env` (`TABLEAU_SERVER_URL`, `TABLEAU_SITE`, `TABLEAU_TOKEN_NAME`, `TABLEAU_TOKEN_VALUE`).
2. Prueba (modo cloud): `python -c "from bi_agents.tableau_client import obtener_vista_tableau as o; r=o('Finanzas','NombreRealDeLaVista','Norte'); print(r['status'], r.get('csv','')[:200])"`.
   Guarda `r['png']` y ábrelo. **Debes ver** la imagen filtrada por división y el CSV subyacente.
   > Validar contra tu versión de `tableauserverclient`: `ImageRequestOptions`, `vf()`, `populate_image/csv`; y el campo de filtro de nombre de vista.
3. Looker Studio (antes "Data Studio"): no hay SDK equivalente. Demuestra en la UI: fuente de datos BigQuery (`finanzas.presupuesto`) → informe → *Compartir → Programar entrega (PDF)*, o capturar con la Linking API. Deja claro a los alumnos la limitación.

## Contenido 4 – A2A con el modelo de forecasting
```powershell
# Terminal 1
uvicorn bi_agents.a2a_ml:a2a_app --port 8002
# Terminal 2
curl http://localhost:8002/.well-known/agent-card.json
adk web modulo4_ml_multimodal_bi/src
```
En `adk web`, para el orquestador crea un paquete con `root_agent = bi_orquestador` (de `bi_agents.a2a_ml`). Pregunta: **"¿Qué pasará con el gasto de Norte los próximos 3 meses y qué muestra la gráfica?"**
**Debes ver en el Trace:** delegación remota a `agente_forecast_remoto` (puerto 8002), llamada a `diagnosticar_division`, y una conclusión "confirma/contradice".
> Imports de A2A verificados con google-adk 2.11.0. Como en el Módulo 1, `adk web` solo descubre `root_agent`: crea un paquete (p. ej. `bi_app/agent.py` con `from bi_agents.a2a_ml import bi_orquestador as root_agent`).

---
## Entregable práctico – Diagnóstico integrado
1. `python -m pytest modulo4_ml_multimodal_bi -q` → 7 passed.
2. Ejecuta `python -c "from bi_agents.agent import diagnosticar_division as d; import json; print(json.dumps(d('Norte'), indent=2, ensure_ascii=False))"`
**Debes ver:** `forecast` con 3 puntos, `lectura_visual`, `fuente_grafica` (`stub`/`tableau`) y `consistencia`.
3. En `adk web`, el agente debe: invocar el modelo (con nombre/versión `tendencia_lineal_v1`), obtener la gráfica y redactar el diagnóstico sin inventar cifras.
4. Falla controlada: apaga `uvicorn` (modo cloud) y pregunta de nuevo → debe devolver un error estructurado, no inventar.

## Listo para dar clase si…
Tienes `ml_service` corriendo, una captura real de dashboard probada con Gemini, el PAT de Tableau validado (o el stub listo) y puedes explicar por qué la visión no sustituye al CSV.
