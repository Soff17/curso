# Módulo 1 · Comandos de la práctica, paso a paso

Un recorrido **en orden**: desde que descargas el material hasta que corres el proyecto (`src`) y compruebas que **todo lo que hiciste en el notebook también existe ahí**.

- Todos los comandos son para **PowerShell** (Windows 11). En macOS o Linux los equivalentes **no se han probado**.
- Se ejecutan **desde la raíz del proyecto** (la carpeta `GeminiAgentsBI`), salvo que se diga otra cosa.
- **Leyenda:** 🟢 no usa Gemini (no gasta tokens) · 💸 usa Gemini (pocos tokens) · ⚠️ no verificado en este proyecto
- Los pasos **1 a 6** se hacen **antes de la sesión**. El **7** es durante la práctica. El **8** es para **después del notebook**.
- Si algo falla, ve al **paso 10**. El detalle de instalación está en `PREREQUISITOS_ALUMNOS.md`.

---
## 1. Descargar y abrir la carpeta
| Comando | Qué hace | |
|---|---|---|
| `Expand-Archive "$HOME\Downloads\GeminiAgentsBI_Modulo1_Alumnos_v3.zip" -DestinationPath "$HOME\Documents"` | Descomprime el ZIP en `Documentos` (cambia el nombre si tu archivo se llama distinto) | 🟢 |
| `cd "$HOME\Documents\GeminiAgentsBI"` | Entra a la carpeta del proyecto | 🟢 |
| `dir` | Debes ver `data`, `modulo1_adk_a2a`, `shared`, `env.ps1`, `.env.example`, `README.md` | 🟢 |
| `code .` | Abre **la carpeta completa** en VS Code ⚠️ (si no funciona: VS Code → *Archivo → Abrir carpeta…*) | 🟢 |

Abre la **carpeta completa**, no solo el notebook: necesita encontrar los demás archivos. Las siguientes terminales conviene abrirlas **dentro de VS Code** (*Terminal → Nueva terminal*), que ya queda en la carpeta correcta.

## 2. Entorno de Python
| Comando | Qué hace | |
|---|---|---|
| `python --version` | Debe decir `Python 3.11.x` (o 3.10 o superior) | 🟢 |
| `python -m venv .venv` | Crea un entorno virtual (solo la primera vez) | 🟢 |
| `.\.venv\Scripts\Activate.ps1` | Lo activa. El inicio de la línea debe mostrar `(.venv)` | 🟢 |
| `pip install "google-adk[a2a]>=2.11.0" python-dotenv ipykernel httpx uvicorn pydantic` | Instala **solo** lo que necesita este módulo | 🟢 |

- Si PowerShell dice que la ejecución de scripts está deshabilitada: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (vale solo para esa terminal) y repite la activación.
- **No uses `pip install -r requirements.txt`** salvo que el instructor lo pida: es de todo el programa e incluye `pyodbc`, que a veces falla en Windows.
- Cada **terminal nueva** necesita volver a activar el entorno (`.\.venv\Scripts\Activate.ps1`).

## 3. Iniciar sesión en Google Cloud (una sola vez por equipo)
```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project <ID_DEL_PROYECTO>
gcloud auth application-default set-quota-project <ID_DEL_PROYECTO>
```
Sustituye `<ID_DEL_PROYECTO>` por el **ID** (no el nombre) que te dio el instructor. Los dos primeros comandos abren el navegador: usa la cuenta que el instructor registró. El **segundo** es el que usa el código. 🟢

## 4. El archivo `.env`
| Comando | Qué hace | |
|---|---|---|
| `Copy-Item .env.example .env` | Crea tu `.env` a partir del ejemplo | 🟢 |
| `notepad .env` | Ábrelo y deja tu ID de proyecto en `GOOGLE_CLOUD_PROJECT` | 🟢 |

Debe quedar así (el resto no se usa en el Módulo 1):
```
GOOGLE_CLOUD_PROJECT=<ID_DEL_PROYECTO>
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_ENTERPRISE=TRUE
MODEL_NAME=gemini-2.5-flash
```
`MODEL_NAME` debe ser **`gemini-2.5-flash`**; **no** `gemini-flash-latest` (da error 404 en este tipo de proyecto). **El `.env` es privado: no lo compartas ni lo subas a Git.**

## 5. Dejar la terminal lista (en cada terminal nueva)
| Comando | Qué hace | |
|---|---|---|
| `. .\env.ps1` | Deja el `PYTHONPATH` listo para `adk web`, `uvicorn` y los scripts. **Lleva punto y espacio al inicio.** Imprime `PYTHONPATH listo para ...` | 🟢 |

Sin este paso aparece `No module named 'shared'`. **El notebook no lo necesita** (lo hace él solo); lo necesitan las terminales del paso 8.

## 6. Verificar que todo está bien (antes de la sesión)
| Comando | Debes ver | |
|---|---|---|
| `pip show google-adk` | `Version: 2.11.x` o superior | 🟢 |
| `adk --version` | un número de versión | 🟢 |
| `gcloud --version` | `Google Cloud SDK ...` | 🟢 |
| `gcloud config get-value project` | tu ID de proyecto | 🟢 |
| `gcloud auth list` | tu cuenta marcada como activa | 🟢 |

**Prueba de Gemini** (una palabra de respuesta; cambia el ID):
```powershell
$env:GOOGLE_GENAI_USE_ENTERPRISE="TRUE"; $env:GOOGLE_CLOUD_PROJECT="<ID_DEL_PROYECTO>"; $env:GOOGLE_CLOUD_LOCATION="us-central1"
python -c "from google import genai; c=genai.Client(); print(c.models.generate_content(model='gemini-2.5-flash', contents='Di hola en una palabra').text)"
```
💸 Debe imprimir una palabra, por ejemplo "Hola".

**Prueba del proyecto (sin Gemini):**
```powershell
. .\env.ps1
python -c "import finanzas_agents.agent, finanzas_agents.workflows, finanzas_agents.a2a_server; print('ok')"
```
🟢 Debe imprimir `ok` (puede mostrar avisos `[EXPERIMENTAL]`: son normales).

## 7. Durante la práctica: el notebook
1. Abre `modulo1_adk_a2a/notebooks/practica_alumnos.ipynb` (el instructor proyecta `practica_instructor.ipynb`, con las respuestas).
2. Arriba a la derecha: **Seleccionar kernel** → el Python de `.venv`.
3. Ejecuta **de arriba hacia abajo** con **Shift+Enter**. Para empezar de cero: **Reiniciar** el kernel y volver a la Parte 0 (las sesiones viven en memoria).
4. Las dos primeras celdas de código (Parte 0) **no llaman a Gemini** y deben mostrar:
```
RAIZ: C:\...\GeminiAgentsBI
google-adk: 2.11.x
Proyecto: <ID_DEL_PROYECTO> | Región: us-central1 | Modelo: gemini-2.5-flash
```

**Qué hace el notebook por ti:**
- En la **Parte 5** levanta el servidor de presupuestos en el puerto **8001**; en el **reto 5.4**, el de tesorería en el **8002**. **No los levantes además a mano.**
- Cuando termines cada servidor, ejecuta su celda de cierre (`servidor.terminate()`); si reinicias el kernel sin hacerlo, el puerto queda ocupado.

| Comando (terminal aparte) | Para qué |
|---|---|
| `netstat -ano \| findstr 8001` | Ver quién usa el 8001 (anota el PID de la última columna) |
| `netstat -ano \| findstr 8002` | Ver quién usa el 8002 |
| `netstat -ano \| findstr 8501` | Ver quién usa el 8501 (`adk web`) |
| `taskkill /PID <pid> /F` | Cerrar ese proceso (un servidor que quedó vivo) |

Cada parte del notebook usa Gemini (💸, pocos tokens) salvo las Partes 0, 1 y 5.1.

## 8. Después del notebook: correr el proyecto (`src`) y comprobar que es lo mismo
Lo que construiste celda por celda ya existe como proyecto en `modulo1_adk_a2a/src/finanzas_agents/`. Esta sección lo demuestra **pieza por pieza** y luego **todo junto**. Antes, en la terminal: `. .\env.ps1` (paso 5).

### 8.1 Pieza por pieza (🟢, sin Gemini)
| Lo que hiciste en el notebook | Dónde está en `src` | Comando que lo comprueba |
|---|---|---|
| **Parte 1:** herramienta `consultar_presupuesto` | `tools.py` | `python -c "from finanzas_agents.tools import consultar_presupuesto as c; print(c('Norte','2026-Q3'))"` → `status: ok`, desviación ≈ 25.3 % |
| **Parte 1:** contrato Pydantic que rechaza datos inválidos | `contracts.py` | `python -c "from finanzas_agents.contracts import BudgetRequest as B; B(division='Marte', trimestre='2026-Q3')"` → **debe fallar** con un mensaje claro |
| **Partes 2, 3 y 7:** especialistas y supervisor | `agent.py` | `python -c "from finanzas_agents.agent import root_agent as r; print(r.name, [a.name for a in r.sub_agents])"` → `supervisor_finanzas ['especialista_presupuestos', 'especialista_tesoreria']` |
| **Parte 4:** estado de la conversación (sesión) | `eventos.py` (`preguntar`, `estado`) | Se ve en `adk web` (8.3): una **sesión nueva** no recuerda la anterior |
| **5.1:** protocolo A2A sin red | `a2a_local.py` | `python -c "from finanzas_agents.a2a_local import Supervisor, BudgetWorker; s=Supervisor(workers={'especialista_presupuestos': BudgetWorker()}); print(s.handshake('especialista_presupuestos')); print(s.ask('s1','Norte Q3')); print(s.ask('s1','y en Q2?')); print(s.sessions)"` → agent card, Q3, Q2 sin repetir la división, y el estado |
| **5.2 y 5.3:** A2A real (presupuestos en el 8001) | `a2a_server.py` (`a2a_app`, `supervisor_remoto`) | Ver 8.2 |
| **5.4:** router con dos especialistas remotos | `a2a_server.py` (`a2a_app_tesoreria`, `supervisor_router`) | `python -c "from finanzas_agents.a2a_server import supervisor_router as r; print([a.name for a in r.sub_agents])"` → `['especialista_presupuestos', 'especialista_tesoreria']` |
| **Parte 6:** workflows y `output_key` | `workflows.py` | `python -c "from finanzas_agents import workflows as w; print([a.name for a in w.pipeline_secuencial.sub_agents], w.refinador.max_iterations, w.analista.output_key)"` → `['analista_presupuesto', 'redactor_ejecutivo'] 3 analisis_presupuesto` |

### 8.2 Los servidores A2A (dos terminales, cada una con `. .\env.ps1`)
| Terminal | Comando | Deja corriendo | |
|---|---|---|---|
| 1 | `uvicorn finanzas_agents.a2a_server:a2a_app --port 8001` | Presupuestos por A2A | 🟢 |
| 2 | `uvicorn finanzas_agents.a2a_server:a2a_app_tesoreria --port 8002` | Tesorería por A2A | 🟢 |

Comprueba las dos **agent cards** (en una tercera terminal; en PowerShell `curl` es un alias distinto, usa este comando):
```powershell
(Invoke-WebRequest http://localhost:8001/.well-known/agent-card.json -UseBasicParsing).Content
(Invoke-WebRequest http://localhost:8002/.well-known/agent-card.json -UseBasicParsing).Content
```
🟢 Deben mostrar `"name":"especialista_presupuestos"` y `"name":"especialista_tesoreria"`.
**No uses el notebook al mismo tiempo**: ocuparía esos puertos.

### 8.3 Todo junto en `adk web`
En una terminal más (con `. .\env.ps1`): `adk web --port 8501 modulo1_adk_a2a/src` → abre **http://127.0.0.1:8501** y elige un agente arriba a la izquierda. Usa **`--port 8501`**: en Windows el 8000 puede estar reservado (`Errno 13`).

| Agente en `adk web` | Qué es (parte del notebook) | Qué necesita | Pregunta de prueba (💸) |
|---|---|---|---|
| `finanzas_agents` | Supervisor con dos especialistas **locales** (Partes 3 y 7) | Nada más | `¿Cómo va la división Norte en 2026-Q3?` → Presupuestos (304000 / 380900 / 25.3 %). Luego `¿Cuál es la posición de liquidez?` → Tesorería. Luego `¿y el presupuesto de Norte en 2026-Q3?` → Tesorería **transfiere** a Presupuestos |
| `supervisor_remoto_app` | Supervisor con Presupuestos **remoto** (5.2 y 5.3) | Terminal 1 (8001) | `¿Cómo va la división Norte en 2026-Q3?` y luego `¿Y en 2026-Q2?` (misma sesión) |
| `supervisor_router_app` | Supervisor con **dos** remotos (5.4) | Terminales 1 y 2 | `¿Cuál es la posición de liquidez?` y luego `¿y el presupuesto de Norte en 2026-Q3?` (misma sesión) |

- **Qué mirar:** el grafo (izquierda) y *Events* (derecha). Debes ver `transfer_to_agent` y, después, `consultar_presupuesto`. **New Session** empieza una conversación sin memoria (es la Parte 4).
- **En `supervisor_router_app`:** primero se transfiere a `especialista_tesoreria` y, en la pregunta siguiente, el **supervisor** vuelve a transferir a `especialista_presupuestos`. Es el patrón **Router-Worker sobre A2A**.
- Si un agente remoto **no responde y no da error**, casi siempre falta un servidor (o el puerto lo usa otro proceso): paso 10.
- Los **workflows** (Parte 6) no tienen interfaz en `adk web`: se comprueban con el comando de 8.1.
- ⚠️ Esta secuencia completa **no se ha ejecutado de punta a punta** con `adk web`; sí se comprobaron por separado los servidores, las agent cards y la importación de los tres agentes.
- Otras formas de ejecutar el agente local: `adk run modulo1_adk_a2a/src/finanzas_agents` ⚠️ (si falla: `cd modulo1_adk_a2a/src` y `adk run finanzas_agents`) y `python -m finanzas_agents.run_programmatic` 💸 ⚠️ (por código con `Runner`; no se ha probado tras la migración).

### 8.4 Pruebas automáticas (solo en el proyecto completo del instructor)
| Comando | Esperado | |
|---|---|---|
| `python -m pytest modulo1_adk_a2a -q` | **24 passed** (verificado) | 🟢 |

El ZIP de alumnos **no incluye las pruebas** (son la solución). No llaman a Gemini mientras el `.env` tenga `AGENTS_MODE=offline`: cubren la herramienta, el contrato, el cableado de ADK, las agent cards y la **estructura** de los agentes, **no** el comportamiento del modelo.

## 9. Cerrar todo
1. En cada terminal con un servidor o con `adk web`: **`Ctrl + C`**.
2. Para salir del entorno virtual: `deactivate`.
3. Comprueba que no quedó nada vivo: `netstat -ano | findstr 8001` (y 8002, 8501). Si algo sigue ahí: `taskkill /PID <pid> /F`.
4. Datos de ejemplo: si borras o dañas `data\finanzas.db`, **descarga de nuevo el ZIP**. (El instructor puede regenerarla con `python data\seed_data.py`, que no viaja en el ZIP.)

## 10. Si algo falla
| Síntoma | Qué hacer |
|---|---|
| `No module named 'shared'` o `'finanzas_agents'` | Falta `. .\env.ps1` en esa terminal |
| `Errno 13 ... 8000` | Usa `--port 8501` |
| `404 NOT_FOUND ... Publisher model` | `MODEL_NAME=gemini-2.5-flash` en `.env` (no `gemini-flash-latest`) |
| `403 ... has not been used in project` | `gcloud auth application-default set-quota-project <ID>` |
| `RuntimeError: Falta GOOGLE_CLOUD_PROJECT` | El `.env` no tiene el ID real (o dice `tu-proyecto`); corrígelo y **reinicia el kernel** |
| Cambié el `.env` y no pasa nada | Reinicia el kernel o el servidor: leen el `.env` al arrancar |
| `supervisor_remoto_app` no responde | Servidor del 8001 apagado, o el 8001 lo usa otro proceso (paso 7, tabla de puertos) |
| `supervisor_router_app` no responde | Falta el servidor del 8001 **o** el del 8002: comprueba las dos agent cards |
| `AssertionError: El servidor A2A no arrancó` (notebook) | Puerto 8001 ocupado, `uvicorn` no instalado, o tardó: `netstat`, `pip install uvicorn` y reintenta |
| Windows pide permiso de firewall | Permite el acceso en **redes privadas** |
| Dos celdas del servidor ejecutadas | Segundo proceso no puede abrir el puerto: cierra el primero (`servidor.terminate()`) y relanza |

Más detalle: `PREREQUISITOS_ALUMNOS.md` (instalación), `SESION_PRACTICA.md` (guion y errores del instructor) y `src/finanzas_agents/README.md` (mapa del proyecto).
