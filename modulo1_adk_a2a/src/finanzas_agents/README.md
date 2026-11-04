# `finanzas_agents` · Proyecto base del Módulo 1

Es el **proyecto real** al que llegas con el notebook: el mismo árbol de agentes, ya organizado como lo mantendrías en tu repositorio. **Cópialo y amplíalo**: en los módulos siguientes agregarás herramientas (RAG, SQL, ML) a estos mismos agentes.

## Qué contiene (árbol de agentes)
```
supervisor_finanzas   (root_agent, en agent.py)
 ├── especialista_presupuestos   → herramienta consultar_presupuesto (tools.py)
 └── especialista_tesoreria      → sin herramientas (no inventa datos; devuelve el control si es de presupuesto)
```
El supervisor **no calcula nada**: lee la `description` de cada especialista y delega con `transfer_to_agent`.

## Mapa de archivos
| Archivo | Para qué sirve | ¿Obligatorio en un proyecto tuyo? |
|---|---|---|
| `agent.py` | Define los agentes. ADK busca la variable **`root_agent`** | **Sí** |
| `tools.py` | Herramientas: funciones con tipos y *docstring* (el modelo lee el docstring) | Sí, si el agente usa herramientas |
| `contracts.py` | Contratos Pydantic: validan los datos **antes** de tocar la base | Recomendado |
| `a2a_server.py` | Expone por **A2A** el especialista de presupuestos (8001) y el de tesorería (8002, reto 5.4), y define los supervisores remotos `supervisor_remoto` y `supervisor_router` | Solo si otros deben llamarlos por red |
| `a2a_local.py` | Simulación didáctica del protocolo A2A, sin red | No (para entenderlo) |
| `workflows.py` | Ejemplos de `SequentialAgent`, `ParallelAgent`, `LoopAgent` y `output_key` | No (demo) |
| `eventos.py` | Helper del notebook: ejecuta un agente e imprime los eventos 🔧📥🤖 | No (comodidad de la clase) |
| `run_programmatic.py` | Ejemplo de ejecutar un agente por código con `Runner` | No (demo) |
| `__init__.py` | Marca la carpeta como paquete (vacío) | Sí |

Fuera de esta carpeta: `shared/config.py` (rutas y `MODEL_NAME`), `data/finanzas.db` (datos sintéticos) y `.env` (proyecto y credenciales; **no se sube a Git**).

## Cómo ejecutarlo
Desde la raíz del proyecto, en una terminal (PowerShell) y con el entorno de Python activado:
```powershell
. .\env.ps1                                  # deja listo el PYTHONPATH (con el punto y el espacio)
adk run modulo1_adk_a2a/src/finanzas_agents  # consola
adk web --port 8501 modulo1_adk_a2a/src      # interfaz web: http://127.0.0.1:8501 → elige finanzas_agents
```
- `adk web` es el que se verificó en este proyecto; `adk run` con esa ruta **no se ha probado aquí** (si falla, ejecútalo desde `modulo1_adk_a2a/src` con `adk run finanzas_agents`).
- Usa `--port 8501`: en Windows el puerto 8000 (el de por defecto) puede estar reservado.
- Preguntas para probar: `¿Cómo va la división Norte en 2026-Q3?` (delega a Presupuestos) y `¿Cuál es la posición de liquidez?` (delega a Tesorería).
- Servidor A2A (opcional): `uvicorn finanzas_agents.a2a_server:a2a_app --port 8001`.
- Segundo servidor A2A (reto 5.4): `uvicorn finanzas_agents.a2a_server:a2a_app_tesoreria --port 8002`; en `adk web` elige `supervisor_router_app` (necesita los dos servidores).

## Cómo ampliarlo
1. **Agregar una herramienta:** escribe la función en `tools.py` (tipos + *docstring* + error como dato) y pásala en `tools=[...]` del agente que la use. **Pruébala sola** antes de dársela al agente.
2. **Agregar un especialista** (por ejemplo, Cuentas por Cobrar): crea el `Agent` en `agent.py`, añádelo a `sub_agents` del supervisor y **menciónalo en la instrucción del supervisor**.
3. **Reglas que ya nos mordieron:**
   - El `name` de un agente es un identificador válido (sin espacios ni tildes) y único.
   - Cada agente necesita `description` (qué *es*) e `instruction` (cómo *trabaja*).
   - **Un agente solo puede tener un padre.** Si quieres reutilizarlo bajo otro supervisor, usa `agente.clone()`.
   - Las cifras deben venir de la herramienta, no del modelo; pide en la instrucción que las reporte tal cual.
   - La respuesta del modelo **no es determinista**: valida cifras, no redacción.

## Pruebas (no llaman a ningún modelo)
```powershell
python -m pytest modulo1_adk_a2a -q
```
Cubren la herramienta, el contrato, el cableado de ADK, la agent card y la **estructura** del árbol de agentes. **No prueban el comportamiento del modelo**: para eso, ejecuta el notebook o `adk web` con Gemini.

## Qué NO es todavía
Es una base para aprender y ampliar, **no** un proyecto listo para producción: usa credenciales de usuario (en producción, cuentas de servicio con permisos mínimos), datos sintéticos en SQLite, y no está desplegado ni evaluado de forma sistemática. Eso se trabaja en los módulos siguientes (sobre todo el 5).
