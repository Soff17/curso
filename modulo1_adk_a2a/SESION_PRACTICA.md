# Módulo 1 · SESIÓN PRÁCTICA (tutoría de 2 h) — Guía del instructor

**Formato:** 5 células de 6 personas trabajando en `notebooks/practica_alumnos.ipynb`; tú proyectas `notebooks/practica_instructor.ipynb` (resuelto). Mientras trabajan, haces **code review** por célula.
La explicación de los conceptos tiene su propia guía: **`SESION_TEORICA.md`**.

**Contenido de esta guía:** Antes de la clase · El lab (qué se entrega) · Línea de tiempo · Guion por parte (0 a 8) · Code review · Contingencias · Problemas fuera del notebook · Lo no probado.

---
## Antes de la clase (día anterior)
- [ ] `. .\env.ps1` y `python -m pytest modulo1_adk_a2a -q` → **22 passed** (no llaman a Gemini: herramienta, contrato, cableado de ADK, agent card y estructura del árbol de agentes). *(Verificado: 22 passed.)*
- [ ] Ejecuta `notebooks/practica_instructor.ipynb` completo (Run All): debe terminar en **🎓 ENTREGABLE LISTO**. Usa Gemini real (modo enterprise) y consume tokens: una corrida completa cuesta centavos (estimación), así que hazla **una sola vez**, no en bucle.
- [ ] Los dos notebooks tienen **la misma estructura**: `practica_alumnos.ipynb` (con TODO) y `practica_instructor.ipynb` (con las respuestas). Ya no hay script que los genere: **si cambias uno, aplica el mismo cambio al otro**.
- [ ] Puerto **8001 libre** (`netstat -ano | findstr 8001`), y el **8002** si harás el reto opcional 5.4 (`netstat -ano | findstr 8002`); instala Jupyter: `pip install jupyterlab` y `jupyter lab modulo1_adk_a2a/notebooks` (o abre el `.ipynb` en VS Code con el kernel del `.venv`).
- [ ] Credenciales de **todos** los alumnos probadas antes: `gcloud auth application-default login`, y en su `.env` `GOOGLE_CLOUD_PROJECT=<ID del proyecto>` y `MODEL_NAME=gemini-2.5-flash`. **El notebook siempre usa Gemini en modo enterprise**; no hay modo sin Gemini (si falla algo, ver *Contingencias*).
- [ ] Presupuesto: crea una **alerta de presupuesto** en Facturación antes de la clase (el consumo por alumno es bajo, pero son 30).
- [ ] Alumnos con el entorno instalado y la Parte 0 ejecutada (`PREREQUISITOS_ALUMNOS.md`). Permisos, cuota, carpeta a entregar y cronograma para los organizadores: `PREREQUISITOS_ORGANIZADORES.md`.

## El lab: qué se entrega
**Objetivo:** dos agentes en Python. El Supervisor recibe una solicitud amplia y delega por A2A al Especialista en Presupuestos, **manteniendo el estado de la conversación**.

**Requisitos:**
1. Contratos Pydantic para petición y respuesta (validación estricta de división y trimestre).
2. Herramienta `consultar_presupuesto` tipada, con docstring (el LLM la lee) y errores estructurados.
3. `especialista_presupuestos` y `supervisor_finanzas` con `description` clara (el router decide por ella).
4. Delegación local (`sub_agents`) **y** remota (servidor A2A).
5. Seguimiento: "¿Cómo va Norte en Q3?" → "¿Y en Q2?" (sin repetir la división).
6. Pruebas `pytest` de contratos y delegación (se pide como mejora en el code review).

**Criterios de aceptación:**
- Las cifras citadas coinciden con `data/finanzas.db`.
- Una petición inválida la rechaza el contrato, no el LLM.
- El supervisor no calcula presupuestos por sí mismo.

**Entrega:** notebook ejecutado (con el 🎓 visible) + repositorio de la célula + demo de 5 min (rúbrica en `docs/02-rubricas.md`).
**Extensión (opcional):** tercer especialista (Cuentas por Cobrar) y un test de `pytest` que verifique la delegación.

## Línea de tiempo
| Hora | Parte | Tema |
|---|---|---|
| 0:00–0:10 | 0 | Setup |
| 0:10–0:25 | 1 | Herramienta y contratos |
| 0:25–0:45 | 2 | Primer agente |
| 0:45–1:05 | 3 | Supervisor y delegación |
| 1:05–1:15 | 4 | Estado |
| 1:15–1:30 | 5 | A2A (5.4 opcional: +10 min, solo si sobra tiempo) |
| 1:30–1:40 | 6 | Workflows |
| 1:40–1:50 | 7 | Reto Tesorería |
| 1:50–2:00 | 8 | Autoevaluación |

---
## Preparación de la sala y reglas de juego

**Antes de empezar (5 min antes de que lleguen):**
- Proyecta `practica_instructor.ipynb` **ya ejecutado hasta la Parte 0** (para ir al ritmo del grupo, no por delante).
- Ten abierta una terminal en la raíz del proyecto y la consola de Google Cloud en otra pestaña.
- Define cómo sabrás quién está atascado: **semáforo** (vaso/papel verde = voy bien, rojo = necesito ayuda) o reacción en el chat. Evita preguntar "¿todos bien?": nadie responde que no.

**Reglas que dices al inicio (2 min):**
> "Esto es una **práctica guiada**, no una clase: aquí se equivocan, y los errores son parte del aprendizaje. Trabajan **en parejas dentro de la célula**: una persona escribe, la otra lee y cuestiona; **rotan en cada parte**. Ejecutan las celdas **en orden**, con Shift+Enter. Donde vean `# TODO`, completan el código. Al final de cada parte hay un **checkpoint**: no avancen hasta verlo. Si se atoran más de **3 minutos**, pongan el semáforo en rojo y voy; antes, pregunten a su compañero y a su célula.
> Mientras trabajan, voy a rotar por las células para hacer **code review**: les voy a pedir que me expliquen *por qué* escribieron lo que escribieron, no solo que funcione."

**Mapa de tiempos y checkpoints**
| Hora | Parte | Checkpoint (lo que todos deben tener) |
|---|---|---|
| 0:00 | 0 Setup | Ven `google-adk: 2.11.x` y "Modelo en uso" |
| 0:10 | 1 Herramienta y contratos | Ejercicios 1 y 2 con resultado |
| 0:25 | 2 Primer agente | El agente responde y ven 🔧📥🤖 |
| 0:45 | 3 Supervisor | Ven el `transfer_to_agent` |
| 1:05 | 4 Estado | Ven que otra sesión no recuerda |
| 1:15 | 5 A2A | La agent card se imprime y el supervisor remoto responde *(5.4 opcional: el supervisor enruta a dos remotos)* |
| 1:30 | 6 Workflows | Ven las claves del estado |
| 1:40 | 7 Reto Tesorería | El control pasa de Tesorería a Presupuestos |
| 1:50 | 8 Autoevaluación | 5 ✅ |

**Rotación del code review (10 min por célula; mientras el resto trabaja):**
| Slot | Célula | Mientras ellos están en… |
|---|---|---|
| 0:30–0:40 | 1 | Parte 2 |
| 0:40–0:50 | 2 | Parte 2–3 |
| 0:50–1:00 | 3 | Parte 3 |
| 1:00–1:10 | 4 | Parte 3–4 |
| 1:30–1:40 | 5 | Parte 6 |

---
## Apertura (2 min)

**🎤 Dices:**
> "Al final de hoy tienen que poder demostrar **tres cosas**: que un agente usa una **herramienta** en lugar de inventar números, que un **supervisor delega** a un especialista **y recuerda** la conversación, y que ese especialista puede vivir **como un servicio aparte** por A2A. El notebook los lleva paso a paso; yo les voy a ir diciendo qué tienen que **ver** en cada paso. Si lo que ven no coincide con lo que digo, **esa es la pista**: me llaman."

**🛠 Haces:** abre el notebook y muestra la tabla de partes y tiempos.

---
## Parte 0 · Preparación (10 min)

**🎤 Dices (al empezar):**
> "La Parte 0 no tiene nada de agentes: solo deja el entorno listo. La primera celda **encuentra la raíz del proyecto**, la agrega a las rutas de Python y carga el archivo `.env`. Si el proyecto no tiene datos, los genera solo. La última línea imprime la **versión de ADK**: quiero que todos vean `2.11` o la que hayan instalado."

**🎤 Dices (celda del modelo):**
> "Esta celda **configura el modelo**: siempre **Gemini en modo enterprise**, con el proyecto de su `.env` y las credenciales de `gcloud` que ya hicieron. **No llama a ningún modelo**: solo verifica que haya proyecto y credenciales, así que no cuesta nada. Si falta algo, se detiene y les dice qué hacer. Fíjense en el nombre del modelo: es una **versión concreta** (`gemini-2.5-flash`), no un alias, para que los resultados sean reproducibles."

**🎤 Dices (por qué importamos de `src`):**
> "Habrán notado que la primera celda agrega dos carpetas a las rutas de Python. Python solo importa de paquetes instalados o de carpetas que le indiquemos, y nuestro código reutilizable está en `src`. De ahí salen **cinco piezas** que usaremos: la **herramienta** (`tools.py`), el **contrato** (`contracts.py`), el **helper que imprime los eventos** (`eventos.py`), la **simulación del protocolo A2A** (`a2a_local.py`) y el **servidor A2A** (`a2a_server.py`). Los **agentes** los van a escribir ustedes. Y si luego quieren hacer los suyos, **no necesitan nada de eso**: les dejé la plantilla mínima en la guía teórica."
> *(Qué es cada archivo, la plantilla de un agente propio y cómo sería `preguntar` sin el helper: `SESION_TEORICA.md`, sección 9.)*

**🛠 Haces:** ejecuta las celdas 1 y 2 en el proyector. Pregunta quién ve un error de proyecto o de credenciales (la propia celda dice qué hacer).

**👀 Deben ver:**
```
RAIZ: C:\...\GeminiAgentsBI
google-adk: 2.11.0
Proyecto: <tu-id-de-proyecto> | Región: us-central1 | Modelo: gemini-2.5-flash
```

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `ModuleNotFoundError: google.adk` | El notebook usa otro Python (kernel equivocado) | Arriba a la derecha: *Seleccionar kernel* → el `.venv` del proyecto |
| `StopIteration` al buscar RAIZ | Abrieron el notebook desde fuera del proyecto | Abrir la carpeta `GeminiAgentsBI` completa en VS Code/Jupyter |
| `No module named dotenv` / `nbformat` | Faltó `pip install -r requirements.txt` | Instalarlo y **reiniciar el kernel** |
| `RuntimeError: Falta GOOGLE_CLOUD_PROJECT` | `.env` sin proyecto o con el valor `tu-proyecto` | Poner el **ID** del proyecto (no el nombre) y reiniciar el kernel |
| `RuntimeError: No hay credenciales` | No hicieron el login de gcloud | En terminal: `gcloud auth application-default login` |
| `404 NOT_FOUND ... Publisher model ... gemini-flash-latest` | `MODEL_NAME` con un alias que no existe en Agent Platform | `MODEL_NAME=gemini-2.5-flash` |
| `403 ... API has not been used in project ...` | Cuota/API apuntando a otro proyecto | `gcloud auth application-default set-quota-project <ID>`; revisar que la API esté habilitada en el proyecto del curso |

**✅ Checkpoint:** todos ven la versión de ADK y el modelo en uso. **No sigas hasta que todas las células lo tengan.**

---
## Parte 1 · Herramienta tipada y contratos (15 min)

**🎤 Dices (celda de la herramienta):**
> "Ejecuten esta celda y miren la **primera línea**: `(division: str, trimestre: str, categoria: str = '') -> dict`. Eso, más el texto que imprime debajo, es **todo lo que el modelo ve de esta función**. No ve el código. Por eso el docstring no es adorno: es la **instrucción de uso**. Después llamamos a la herramienta *directamente*, sin modelo, para confirmar que funciona. **Siempre prueben la herramienta sola antes de dársela a un agente**: si falla aquí, el agente nunca va a funcionar."

**👀 Deben ver:**
```
(division: str, trimestre: str, categoria: str = '') -> dict
Consulta presupuesto vs ejecutado de una división y trimestre. ...
ok Norte 2026-Q3 → desviación 25.3 %
  Viaticos     presup    47,000  ejec    68,150
  Consultoria  presup    78,000  ejec   124,800
  Tecnologia   presup    55,000  ejec    57,750
  Marketing    presup    56,000  ejec    58,800
  Servicios    presup    68,000  ejec    71,400
```
**🎤 Dices:** "Fíjense que Norte excede por **25.3 %**, sobre todo en **Consultoría** y **Viáticos**. Esa es la historia del caso que vamos a resolver."

### Ejercicio 1 (5 min)
**🎤 Dices:** "Consulten **Sur, 2026-Q1, solo Tecnologia**. Tienen tres argumentos; el tercero es opcional."
**Respuesta:** `consultar_presupuesto("Sur", "2026-Q1", "Tecnologia")` → `ok`, presupuestado 55,000, ejecutado 48,541.37, desviación **−11.74 %**.
**🎤 Dices (momento didáctico, si alguien escribe la categoría con tilde):**
> "¿Alguien escribió *Tecnología* con tilde? Ahora **funciona** —normalizamos tildes y mayúsculas—, porque un modelo en español escribirá 'Tecnología' o 'viáticos' y la base guarda 'Tecnologia'. Prueben *'Comida'*: la herramienta **no revienta**; devuelve un **error como dato** con las categorías válidas. Eso es importante: el modelo puede **leer el error y corregirse**."
```python
consultar_presupuesto("Sur","2026-Q1","Comida")   # → {'status': 'error', 'message': "Categoría inválida 'Comida'. Válidas: Viaticos, Consultoria, ..."}
```

### Contratos (celda de Pydantic) y Ejercicio 2 (5 min)
**🎤 Dices:**
> "Ahora la validación. Esta petición es válida y la imprime. Esta otra pide la división **'Marte'**: va a **fallar antes de llegar a ningún modelo**. ¿Por qué lo hacemos en código y no le pedimos al modelo 'valida la entrada'? Porque un modelo se puede equivocar o convencer; el código no. **Lo que puedes validar con código, valídalo con código.**"

**👀 Deben ver:**
```
division='Norte' trimestre='2026-Q3' categoria=None
❌ rechazado: Input should be 'Norte', 'Sur', 'Centro' or 'Occidente'
```
**Ejercicio 2 (trimestre `2026-Q5`) — Respuesta:**
```python
try:
    BudgetRequest(division="Norte", trimestre="2026-Q5")
except ValidationError as e:
    print("❌ rechazado:", e.errors()[0]["msg"])
```
**👀 Ven:** `❌ rechazado: String should match pattern '^\d{4}-Q[1-4]$'`

**❓ Preguntas (pídelas en voz alta y espera 10 s):**
1. "¿Qué parte de esta función es la 'interfaz' con el modelo?" → *nombre + tipos + docstring.*
2. "¿Qué pasa si el trimestre fuera `2026-Q5` y no tuviéramos el contrato?" → *la BD respondería 'sin datos' y el modelo podría inventar una explicación.*

**⚠️ Errores:**
- `NameError: BudgetRequest` → se saltaron una celda; ejecutar en orden. `...` (Ellipsis) en `r1 = ...` → olvidaron completar el TODO.
- **Ejercicio 2 con `division="Marte"` (error real que ocurrió al probar el notebook):** si copian la celda de arriba y solo cambian el trimestre, el mensaje que ven es `Input should be 'Norte', 'Sur', ...` y **parece que funcionó**, pero rechazó por la *división*, no por el trimestre. La prueba válida usa `division="Norte"` y debe mostrar `String should match pattern '^\d{4}-Q[1-4]$'`. Díselo así: *"¿Qué campo rechazó? Lean el mensaje."*

**🔬 Lo que se obtuvo al ejecutarlo (Gemini real, proyecto de prueba):**
- Ejercicio 1 con `"Tecnología"` (con tilde) **sí funcionó**: `ok [{'categoria': 'Tecnologia', ...}] → desviación -11.74 %`. Es la normalización del contrato en acción.
- Si el modelo escribe una categoría inexistente, la herramienta no revienta: devuelve un error como dato con las categorías válidas, y el modelo puede leerlo y corregirse.

**✅ Checkpoint:** ven el −11.74 % y el rechazo de `2026-Q5`.

---
## Parte 2 · Tu primer agente (20 min)

**🎤 Dices (antes de que escriban):**
> "Van a escribir su **primer agente**. Piensen en tres cosas: **modelo, descripción, instrucción**. Les doy 5 minutos para completar los dos TODO. Les recuerdo la diferencia: la **descripción** dice *qué es* el agente —la leerá el supervisor para decidir si le delega—; la **instrucción** dice *cómo debe trabajar* —la lee el propio agente—. En la instrucción pongan reglas **concretas y verificables**: 'usa siempre la herramienta', 'nunca inventes cifras', 'reporta esto'. Una instrucción de una línea como 'sé útil' es una instrucción vacía."

**🛠 Haces:** recorre las mesas durante los 5 min. Elige **una descripción buena y una mala** de alumnos (con permiso) y compáralas en pantalla.

| ❌ Descripción vaga | ✅ Descripción útil |
|---|---|
| "Agente de finanzas" | "Especialista en presupuestos: consulta presupuesto vs ejecutado por división, trimestre y categoría, y calcula desviaciones." |
| "Ayuda con datos" | (dice **qué hace**, **con qué insumos** y **qué entrega**) |

**🎤 Dices (celda de ejecución):**
> "Ahora ejecútenlo. Miren la salida: tres símbolos. **🔧** es que el agente *decidió llamar a una herramienta* y con qué argumentos. **📥** es lo que la herramienta *devolvió*. **🤖** es la *respuesta final*. Este es el **rastro de eventos**: cuando algo falle en el futuro, empiecen por aquí."

**👀 Deben ver:**
```
👤 ¿Cómo va la división Norte en 2026-Q3?
   🔧 [especialista_presupuestos] llama consultar_presupuesto({'division': 'Norte', 'trimestre': '2026-Q3'})
   📥 [especialista_presupuestos] resultado de consultar_presupuesto: {'status': 'ok', 'division': 'Norte', ...
🤖 [especialista_presupuestos] La división Norte en 2026-Q3 tiene un presupuesto total de 304000 y ha ejecutado 380900, lo que representa una desviación del 25.3%. Las dos categorías con mayor exceso son Consultoria y Viaticos.
```
(La redacción de Gemini cambia en cada corrida, pero **las cifras deben ser 304,000 / 380,900 / +25.3 %**.)

**🔬 Lo que se obtuvo al ejecutarlo — el antes y después de la `instruction` (úsalo como demo):**

| | Con `instruction="TODO: ..."` (sin reglas) | Con la instrucción completa |
|---|---|---|
| ¿Llamó a la herramienta? | Sí (🔧 📥) | Sí (🔧 📥) |
| Qué respondió | Totales **y las 5 categorías** con presupuestado/ejecutado de cada una | Totales, desviación y **solo las 2 categorías con mayor exceso** (Consultoría +46,800 y Viáticos +21,150) |

**🎤 Dices:** "Mismo agente, misma pregunta, mismos datos. Lo único que cambió fue la **instrucción**, y cambió **lo que reporta**. La instrucción no es adorno: es el procedimiento que el agente sigue. Y fíjense que **las cifras no cambiaron**: vienen de la base, no del modelo."

**🔬 Otras observaciones reales:**
- Con la `description` y la `instruction` todavía en "TODO", el agente **igual funcionó** (Gemini llamó la herramienta por sí solo). Eso **no significa que esté bien**: sin reglas claras, el comportamiento depende del humor del modelo. Por eso se completan.
- Si debajo de la respuesta aparece **el mismo texto otra vez entre comillas**, el kernel tiene cargada una versión vieja del helper `eventos.py`: reiniciar el kernel (o `importlib.reload`).

**❓ Preguntas de discusión (2 min) y respuestas:**
1. "¿Qué evento demuestra que el agente usó la herramienta en vez de inventar?" → *el 🔧 y el 📥.*
2. "¿Dónde viven las cifras: en el prompt o en la base de datos?" → *en la base; el modelo no las memoriza.*
3. "¿Qué pasa si la instrucción **no** dice 'usa siempre la herramienta'?" → Pruébalo: borra esa frase, vuelve a preguntar y observa si responde *sin* el 🔧. Si lo hace, esa respuesta **no tiene respaldo** en la base. (Gemini suele llamar la herramienta de todos modos, pero **no está garantizado**: por eso la instrucción debe ser explícita.)

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `NameError: presupuestos_agent` | No ejecutaron la celda de definición | Ejecutarla; luego la de `preguntar` |
| `ValidationError ... Node name '...' must be a valid Python identifier` | El `name` del agente tiene espacios (o caracteres raros) | Usar solo letras, números y `_` (p. ej. `especialista_presupuestos`) |
| `PermissionDenied` / 403 / 429 | Credenciales, API no habilitada o cuota | Revisar `gcloud auth application-default login`, el proyecto y la cuota; si es 429, esperar un minuto y reintentar |
| La respuesta no menciona la herramienta (Gemini) | Instrucción débil | Mejorar la instrucción: "Usa SIEMPRE la herramienta..." |
| La respuesta sale dos veces (la segunda entre comillas) | El kernel tiene la versión anterior de `eventos.py` | Reiniciar el kernel y ejecutar desde la Parte 0 |

**✅ Checkpoint:** ven 🔧 📥 🤖 y la cifra +25.3 %.

---
## Parte 3 · Supervisor y delegación (20 min)

**🎤 Dices (antes de escribir):**
> "Ahora crean un **supervisor**. Su trabajo **no es calcular presupuestos**: es *decidir a quién delegar*. Lo hace leyendo las **descripciones** de sus sub-agentes. Por eso la descripción que escribieron en la parte anterior ya **importa de verdad**. Escriban la instrucción del supervisor y pasen al especialista en `sub_agents`."

**🛠 Haces:** da 5 min. Mientras tanto, empieza la rotación de code review.

**🎤 Dices (al ejecutar):**
> "Miren el **primer evento**: `transfer_to_agent`. El supervisor **no responde**; llama a una función especial que **le pasa el control** al especialista. Después, el especialista hace lo de antes: herramienta, resultado, respuesta. Vean también que el resultado de la transferencia dice `{'result': None}`: **es normal**. Transferir no devuelve un dato; devuelve el control."

**👀 Deben ver:**
```
👤 ¿Cómo va la división Norte en 2026-Q3?
   🔧 [supervisor_finanzas] llama transfer_to_agent({'agent_name': 'especialista_presupuestos'})
   📥 [supervisor_finanzas] resultado de transfer_to_agent: {'result': None}
   🔧 [especialista_presupuestos] llama consultar_presupuesto({'division': 'Norte', 'trimestre': '2026-Q3'})
   📥 [especialista_presupuestos] resultado de consultar_presupuesto: {...
🤖 [especialista_presupuestos] ... ejecutado 380,900 (+25.3%) ...
```
**🛠 Haces (demo opcional de 3 min):** abre `adk web` (comandos y lectura del diagrama en la sección **"Cómo probar y leer `adk web`"**, justo después de esta parte), elige `finanzas_agents` y haz la misma pregunta: es **el mismo flujo, en visual**.

**🔬 Lo que se obtuvo al ejecutarlo:**
- **Con la `instruction` del supervisor aún en "TODO" (y un solo especialista), igual delegó.** Razón: ADK agrega por su cuenta las reglas de transferencia, y con un único candidato la elección es obvia. La `description` y la `instruction` empiezan a decidir cuando hay **dos o más** especialistas (Parte 7).
- **Repetir la celda con el mismo `session_id` no muestra los eventos.** Segunda ejecución con `s1`: solo apareció `👤 ... 🤖 ...`, sin `transfer_to_agent` ni 🔧. La conversación **continuó**, la respuesta ya estaba en el historial y ADK mandó el mensaje directo al último agente que respondió. Cambiar a un id nuevo (`s2`) devolvió el flujo completo. **Díselo a los alumnos** antes de que repitan la celda.
- **Responde el especialista, no el supervisor.** El `🤖` final lleva `[especialista_presupuestos]`: el supervisor solo enrutó.
- Del log de `adk web`: la delegación usó **3 llamadas al modelo** (≈15 s en total con `gemini-2.5-flash`): decidir la transferencia, decidir usar la herramienta y redactar la respuesta. Delegar tiene un **costo** (una llamada extra, más latencia y tokens); úsalo cuando el enrutamiento aporte valor.

**❓ Preguntas:**
1. "¿Quién eligió al especialista: un `if` en el código o el modelo?" → *el modelo, leyendo la `description`.*
2. "Si cambiamos la descripción del especialista por 'agente de datos', ¿qué creen que pasa?" → *puede que el supervisor no delegue o delegue mal. Pruébenlo: cambien la descripción, vuelvan a preguntar y comparen.*

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `sub_agents=[]` y el supervisor responde solo | Olvidaron el TODO | Agregar `presupuestos_agent` |
| `already has a parent agent` | Reutilizaron un agente que ya tiene padre | `presupuestos_agent.clone()` (lo ven formalmente en la Parte 7) |
| No aparece `transfer_to_agent` | El especialista no está en `sub_agents` o el modelo respondió directo (Gemini) | Revisar `sub_agents` y mejorar la `instruction` del supervisor |
| Aparecen avisos amarillos | Avisos de ADK (experimental/obsoleto) | "Son avisos, no errores." |
| Al repetir la celda no aparece `transfer_to_agent` ni 🔧, solo la respuesta | Mismo `session_id`: la conversación continúa y la respuesta ya estaba en el historial | Usar un `session_id` nuevo (`s2`) o reiniciar el kernel |
| `already has a parent agent` al volver a ejecutar la celda del supervisor | `presupuestos_agent` ya quedó asignado al supervisor anterior | Volver a ejecutar también la celda que define `presupuestos_agent`, o usar `.clone()` |

**✅ Checkpoint:** ven `transfer_to_agent` y la cifra.

---
## Cómo probar y leer `adk web` (la vista visual de la Parte 3)

**🛠 Pasos (en una terminal aparte, no en el notebook):**
```powershell
cd "C:\Users\Sofia Donlucas\Documents\Visual\GeminiAgentsBI"
. .\env.ps1
adk web --port 8501 modulo1_adk_a2a/src
```
Abre **http://127.0.0.1:8501**, elige **`finanzas_agents`** (arriba a la izquierda) y escribe `¿Cómo va la división Norte en 2026-Q3?`. Para terminar: `Ctrl + C` en la terminal.

> **Por qué `--port 8501` y `env.ps1`:** en la máquina de prueba Windows **reserva el puerto 8000** (el que usa `adk web` por defecto; da `Errno 13`), y sin `env.ps1` el código no encuentra el paquete `shared`. Elige `finanzas_agents`, **no** `supervisor_remoto_app`: ese necesita además el servidor A2A de la Parte 5.

### Cómo leer lo que aparece (resultado real)
**Panel derecho, pestaña *Events* (se hace clic en cada evento para ver el detalle):**
| # | Qué se ve | Qué significa |
|---|---|---|
| #1 | Tu pregunta | Entrada del usuario |
| #2 | `transfer_to_agent("especialista_presupuestos")` | El **supervisor decide delegar**: el modelo respondió con *una llamada a función*, no con texto |
| #3 | `✓ transfer_to_agent` y `supervisor_finanzas → especialista_presupuestos` | El control **pasó** al especialista (por eso el resultado es `None`: se transfiere el control, no un dato) |
| #4 | `consultar_presupuesto` (con el aviso ⚠ "Performance") | El **especialista decide usar la herramienta** |
| #5 | `✓ consultar_presupuesto` | Lo que **devolvió la herramienta** (los datos de la base) |
| #6 | Respuesta de texto | El **modelo redacta** con esos datos: 304000 / 380900 / 25.3 % y las 2 categorías |

**Panel izquierdo, el grafo:** `supervisor_finanzas → especialista_presupuestos → consultar_presupuesto`. *(Con el proyecto migrado a `src` el supervisor tiene **dos** especialistas, y el grafo muestra también la rama de `especialista_tesoreria`: en gris si no participó, en verde si ya intervino en la sesión. Verificado en `adk web`.)*
- Es el **mapa de la arquitectura** de esa ejecución.
- Los nodos verdes son los que **participaron**; la herramienta aparece en gris punteado porque es una *herramienta*, no un agente.
- Al avanzar de evento (flechas "Event 6 of 6") se ilumina el nodo activo.

**🎤 Dices:** "Este diagrama es la delegación que vimos en texto. Arriba, el supervisor, que **no calcula nada**; en medio, el especialista; abajo, la herramienta que va a la base. Cada flecha es una decisión que tomó **el modelo**, no un `if` mío."

### Qué devolvió el modelo en cada llamada (análisis)
En el log del servidor se ven **tres peticiones a `gemini-2.5-flash`** (`backend: VERTEX_AI`, región `us-central1`, tu proyecto en la URL) y las tres respondieron `200 OK`:

| Llamada | Quién | Qué devolvió el modelo | Duración aprox. |
|---|---|---|---|
| 1 | Supervisor | **No texto**: una llamada a función `transfer_to_agent(agent_name="especialista_presupuestos")` | ~6 s |
| 2 | Especialista | **No texto**: una llamada a función `consultar_presupuesto(division="Norte", trimestre="2026-Q3")` | ~5 s |
| 3 | Especialista | **Texto final**, redactado con el resultado de la herramienta | ~3 s |

Qué extraer de ahí:
1. **El modelo no hace los cálculos ni consulta la base**: pide ejecutar herramientas (llamadas 1 y 2) y solo redacta al final (llamada 3). Las cifras salen de la base de datos.
2. **Las cifras son estables; la redacción no.** En la misma práctica el modelo escribió "Consultoria / Viaticos" (sin tilde, como en la base) en una corrida y "Consultoría / Viáticos" en otra; a veces `304000`, a veces `304,000`. Es **no determinismo de redacción**: por eso las pruebas comparan **cifras**, no texto exacto (Módulo 5).
3. **Costo de delegar:** una pregunta = 3 llamadas (≈14–15 s). Un agente único habría necesitado solo 2.

### El aviso ⚠ "Performance" (evento #4)
Es esta línea del log: `App "finanzas_agents" can transfer between agents but has no context_cache_config...`. Significa que, **al transferir, cambian las instrucciones y herramientas y el prompt se reenvía sin caché**. Es una **sugerencia de optimización** (configurar `context_cache_config`), **no un error**. Con prompts cortos como el nuestro no importa; en producción con prompts largos sí (tema de costos del Módulo 5).

### Ruido normal en el log (se puede ignorar)
`GET /dev-ui/prism-dark.css 404` (estilo que falta en la interfaz), `UserWarning [EXPERIMENTAL] ...` (funciones experimentales de ADK) y la carpeta **`.adk/session.db`** que `adk web` crea dentro de cada agente (no subirla a Git).

### Para probar el estado visualmente
1. Sin cerrar, escribe `¿Y en 2026-Q2?`: responde sobre **Norte** sin pedir la división (misma sesión).
2. Pulsa **New Session** y repite la pregunta: ahora **pide la división** (otra sesión = otra conversación).

### Si algo falla en `adk web`
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `Errno 13 ... bind on address ('127.0.0.1', 8000)` | Windows reserva el puerto 8000 | `adk web --port 8501 modulo1_adk_a2a/src` |
| `500` y en la terminal `No module named 'shared'` | No se ejecutó `. .\env.ps1` en esa terminal | Detener con `Ctrl + C`, ejecutar `. .\env.ps1` y relanzar |
| `supervisor_remoto_app` no responde (solo aparece tu pregunta, sin error) | El servidor A2A no corre, o **el puerto 8001 lo tiene otro proceso** (p. ej. un `adk web --port 8001`). El supervisor llama a `localhost:8001`, recibe un 404 y se queda mudo | Liberar el 8001, levantar `uvicorn finanzas_agents.a2a_server:a2a_app --port 8001` (con `env.ps1`) y dejar `adk web` en el 8501 |
| El agente no aparece en el selector | Carpeta equivocada | Pasar la carpeta que **contiene** los paquetes: `modulo1_adk_a2a/src` |

---
## Parte 4 · Estado de la conversación (10 min)

**🎤 Dices:**
> "Ahora la pregunta de seguimiento: **'¿Y en 2026-Q2?'** —sin decir la división—. Primero en la **misma sesión**. Después en **otra sesión**. Antes de ejecutar, apuesten: ¿qué creen que va a pasar en cada caso?"

**🛠 Haces:** deja 20 segundos de apuestas (que levanten la mano) y ejecuta las dos celdas.

> ⚠️ **"Misma sesión" = el mismo `session_id` que usaron en la Parte 3.** Si en la Parte 3 cambiaron el id (por ejemplo a `s2` para ver de nuevo los eventos), en esta primera celda deben poner **ese mismo id**; con otro, el supervisor no conocerá la división. (Tras reiniciar el kernel, las sesiones anteriores desaparecen: son `InMemory`.)

**👀 Deben ver (misma sesión):**
```
👤 ¿Y en 2026-Q2?
   🔧 [especialista_presupuestos] llama consultar_presupuesto({'division': 'Norte', 'trimestre': '2026-Q2'})
   📥 ...
🤖 [especialista_presupuestos] En 2026-Q2, la división Norte tuvo un presupuesto total de 318000 y ejecutó 294364.01 ... desviación del -7.43% ...
```
**👀 Deben ver (otra sesión):**
```
👤 ¿Y en 2026-Q2?
   🔧 [supervisor_finanzas] llama transfer_to_agent(...)
🤖 [especialista_presupuestos] Por favor, especifica la división para la cual deseas consultar el presupuesto ...
```
**🎤 Dices (dos observaciones):**
> "Primera: en la misma sesión **sabe que es Norte**, porque **la conversación se guarda en la sesión** y se le reenvía al modelo cada vez. En la otra sesión no hay historial: **empieza de cero**.
> Segunda, miren con atención: en la **misma sesión no hubo transferencia**. La pregunta de seguimiento fue **directo al especialista**, porque en ADK la conversación continúa con **el último agente que respondió**. No es un error: es el comportamiento por defecto."
> *(El texto cambia en cada corrida, pero lo importante —si recuerda o no— se mantiene.)*

**🔬 Lo que se obtuvo al ejecutarlo (Gemini real, `s2` y `s3`) — análisis:**

| | Misma sesión (`s2`) | Otra sesión (`s3`) |
|---|---|---|
| Eventos | 🔧 `consultar_presupuesto` → 📥 → 🤖 (**sin** `transfer_to_agent`) | 🔧 `transfer_to_agent` → 📥 `{'result': None}` → 🤖 (**sin** herramienta) |
| Quién respondió | `especialista_presupuestos` | `especialista_presupuestos` |
| Qué hizo el modelo | Dedujo que "Norte" venía del turno anterior y llamó la herramienta con `division='Norte', trimestre='2026-Q2'` | No tenía división en su historial, **no la adivinó** y la pidió: *"Necesito saber la división para consultar el presupuesto. ¿Para qué división…?"* |
| Cifras | 318000 / 294364.01 / −7.43 % (coinciden con la base) | — (no hubo consulta) |

Qué extraer de ahí:
1. **La "memoria" es el historial de la sesión.** En `s2` el modelo recibió los turnos anteriores (la pregunta de Q3, la llamada a la herramienta y su respuesta) junto con la nueva pregunta. En `s3` el historial estaba vacío. No hay una variable "división" guardada: **el contexto viaja en la conversación**.
2. **Sin historial, el agente pregunta en vez de inventar.** Es el comportamiento que queremos: la instrucción dice "si falta división o trimestre, pídelos" y lo cumplió.
3. **Misma sesión = una llamada menos.** Al no haber transferencia, no intervino el modelo del supervisor: la pregunta fue directo al especialista.
4. **Una instrucción ambigua da respuestas variables.** La instrucción pide "las 2 categorías con **mayor exceso**", pero en Q2 Norte no excedió en ninguna categoría. Gemini lo manejó diciendo que *no hubo categorías con exceso*; en otras corridas de prueba habló de "mayor déficit" o de las categorías "más cercanas al presupuesto". **Misma pregunta, misma instrucción, distintas interpretaciones**. Mejora de instrucción para comentar en clase: *"Si ninguna categoría excede el presupuesto, indícalo explícitamente."*
5. **Verifica cifras, no redacción.** La redacción cambió respecto a otras corridas ("Por favor, especifica la división…" vs "Necesito saber la división…") y las cifras no.

> Si debajo de cada respuesta ven el texto repetido entre comillas, es el helper `eventos.py` viejo cargado en el kernel: reiniciar el kernel.

**🧪 Experimento de no determinismo (opcional, 3 min):** repite la pregunta solo como **'¿Y en Q2?'** (sin año) en 3 sesiones nuevas. En mis pruebas, **2 de 3 veces** Gemini dedujo 2026 y **1 de 3** preguntó *"¿de qué año?"*. Misma entrada, caminos distintos: por eso en el Módulo 5 se miden **tasas de éxito**, no un solo intento. (Cada intento cuesta unos pocos tokens.)

**❓ Preguntas:**
1. "¿Por qué la otra sesión pide la división?" → *no hay historial; el modelo no tiene memoria propia.*
2. "¿Qué componente guarda la conversación?" → *el `SessionService`; aquí en memoria, en producción una base de datos o Agent Runtime Sessions.*
3. "Si reinicio el notebook, ¿se conserva la sesión?" → *No: es `InMemory`.*

**⚠️ Errores:** nada que arreglar; si la sesión "recuerda" cuando no debería, usaron el mismo `session_id` por error (revisen el nombre).

**✅ Checkpoint:** entienden la diferencia entre ambas respuestas (pídele a una persona que lo explique con sus palabras).

---
## Parte 5 · A2A (15 min)

### 5.1 Protocolo sin red (3 min)
**🎤 Dices:**
> "Antes de usar red de verdad, miremos el **protocolo desnudo**: una simulación en proceso, sin modelo. Tiene **tres momentos**: el *handshake* —el supervisor pregunta qué sabe hacer el especialista—, el *envío de un mensaje tipado*, y el *estado que se conserva entre turnos*."

**👀 Deben ver:**
```
handshake → AgentCard(name='especialista_presupuestos', skills=['presupuesto'])
Norte 2026-Q3: presupuestado 304,000, ejecutado 380,900 (+25.3%).
Norte 2026-Q2: presupuestado 318,000, ejecutado 294,364 (-7.4%).
estado → {'sesion1': {'division': 'Norte', 'trimestre': '2026-Q2', 'anio': '2026', 'ultima_desviacion': -7.43}}
```

### 5.2 A2A real (12 min)
**🎤 Dices (antes de la celda del servidor):**
> "Esta celda **levanta un servidor** con el especialista en el puerto **8001**, como un **proceso aparte**. Luego pide su **agent card** por HTTP. Por eso no necesitan una segunda terminal: el notebook la lanza por ustedes. Si Windows les pregunta por el **firewall**, permitan en **redes privadas**."
**👀 Deben ver:** `Agent card → especialista_presupuestos | Especialista en presupuestos: consulta presupuesto vs ejecutado por di ...` (puede tardar unos segundos).

**🎤 Dices (celda del `RemoteA2aAgent`, TODO):**
> "Ahora el supervisor. Fíjense: el especialista remoto se declara **casi igual** que uno local —`name`, `description`—, pero en vez de un agente le damos **la dirección de su agent card**. El supervisor **no sabe ni le importa** que vive en otro proceso."
**Respuestas TODO:** `agent_card=URL_CARD` y `sub_agents=[especialista_remoto]`.

**👀 Deben ver (la misma historia de eventos que la Parte 3):**
```
   🔧 [supervisor_remoto] llama transfer_to_agent({'agent_name': 'especialista_presupuestos'})
   🔧 [especialista_presupuestos] llama consultar_presupuesto({...})      ← ¡esto se ejecutó en el puerto 8001!
   📥 [especialista_presupuestos] resultado de consultar_presupuesto: {...
🤖 [especialista_presupuestos] ... ejecutado 380,900 (+25.3%) ...
```
**🎤 Dices:** "Misma pregunta, mismo resultado, pero **la herramienta corrió en otro proceso**. Eso es A2A."

**🔬 Lo que se obtuvo al ejecutarlo (Gemini real) — análisis:**

*5.1 (sin red):* `handshake → AgentCard(name='especialista_presupuestos', skills=['presupuesto'])` y el estado conserva `division: Norte` entre turnos. Es el protocolo "desnudo": descubrir, enviar un mensaje tipado y mantener contexto.

*5.2 (por red):* se completaron los dos TODO (`agent_card=URL_CARD`, `sub_agents=[especialista_remoto]`) y la delegación funcionó.

| | Local (Parte 3) | Remoto por A2A (Parte 5) |
|---|---|---|
| Eventos | `transfer_to_agent` → `consultar_presupuesto` → respuesta | **Los mismos** |
| Dónde corrió `consultar_presupuesto` | Mismo proceso del notebook | **Otro proceso** (servidor en el puerto 8001) |
| Forma del resultado 📥 | `{'status': 'ok', 'division': 'Norte', 'trimestre': ..., 'lineas': ...}` | `{'trimestre': ..., 'total_presupuestado': 304000.0, 'division': 'Norte', 'lineas': ...}` |
| Cifras de la respuesta | 304000 / 380900 / 25.3 % | 304,000 / 380,900 / 25.3 % |

Qué extraer de ahí:
1. **Para el supervisor, "remoto" se ve igual que "local".** El `RemoteA2aAgent` se comporta como un sub-agente más: los eventos son los mismos. Lo que cambia es **dónde vive** el especialista, y el contrato que los une es la **agent card**.
2. **La forma del resultado cambió: es la evidencia de que cruzó el límite del proceso.** En el resultado remoto las claves vienen en otro orden y **ya no aparece `status`**. Por qué se pierde `status` en ese trayecto **no está verificado**; la observación útil es: *por red los datos se serializan y se reempaquetan, así que no se debe asumir que el consumidor ve exactamente el mismo diccionario*. Es la razón de peso para tener **contratos de datos** (Pydantic) entre agentes.
3. **Las cifras son las mismas; la redacción no.** La respuesta remota usó separador de miles (`380,900`) y la local no (`380900`): no determinismo de redacción, no un error de A2A.
4. **Responde el especialista, no el supervisor.** El `🤖` final sigue siendo `[especialista_presupuestos]`: el supervisor solo enrutó, igual que en local.
5. **El servidor es un proceso vivo que alguien tiene que apagar.** La celda `servidor.terminate()` imprime `servidor A2A detenido`; si se reinicia el kernel sin ejecutarla, el puerto 8001 queda ocupado (ver tabla de errores).

> Si debajo de la respuesta ven el texto repetido entre comillas: es el helper `eventos.py` viejo cargado en el kernel; reiniciar el kernel.

**🧪 Experimento (3 min, muy recomendable):**
> "Apaguemos el servidor —la celda 'Cierra el servidor'— y **vuelvan a preguntar**. ¿Qué creen que va a pasar?"
**Resultado real:** **no hay error visible**: el agente devuelve una **respuesta vacía**. *(Se comprobó en una prueba temporal con un modelo de reglas que ya no está en el proyecto; **con Gemini real no se ha ejecutado**, confírmalo antes de la clase.)* Para repetirlo usa un `session_id` nuevo.
**🎤 Dices:**
> "¿Lo vieron? **No explotó. Simplemente no contestó.** Una **falla silenciosa**. En un sistema financiero eso es peligroso, porque nadie se entera. Por eso en la semana cinco vemos **observabilidad y evaluación**: para detectar lo que no hace ruido."
*(Para repetir la Parte 5.2 después de este experimento hay que volver a ejecutar la celda que levanta el servidor.)*

### 5.3 Experimento: ¿el estado también viaja por A2A? (resultado real, Gemini)
Se ejecutan dos celdas **antes de cerrar el servidor**: el seguimiento `¿Y en 2026-Q2?` en la **misma sesión** (`a2a1`) y en una **sesión nueva** (`a2a2`) como control.

| | Misma sesión (`a2a1`) | Sesión nueva (`a2a2`, control) |
|---|---|---|
| Eventos | `supervisor_remoto` → `transfer_to_agent` → `consultar_presupuesto(Norte, 2026-Q2)` → respuesta | `transfer_to_agent` → respuesta, **sin herramienta** |
| Qué respondió | Norte 2026-Q2: presupuestado 318000, ejecutado 294364.01, desviación −7.43 %. *"No hay categorías con exceso, ya que la desviación es negativa"* | *"Necesito saber la división (Norte, Sur, Centro u Occidente) para poder consultar el presupuesto"* |

Qué extraer de ahí:
1. **Sí: el estado se conserva a través de A2A.** En la misma sesión la pregunta sin división se resolvió como Norte; en la sesión nueva no, y se pidió la división. Con eso, el entregable del PDF (delegar por A2A **manteniendo el estado**) queda comprobado también por la ruta remota.
2. **Una diferencia con la ruta local:** con el supervisor local, el seguimiento fue **directo al especialista** (sin `transfer_to_agent`); con el remoto, el supervisor **volvió a transferir**. La causa de esa diferencia **no está verificada**.
3. **El mecanismo exacto no está determinado.** No se sabe si el contexto llegó porque el supervisor envía el historial al agente remoto o porque el servidor A2A guarda su propia sesión. Para saberlo habría que inspeccionar los mensajes A2A. En la práctica **no hizo falta configurar nada** (no se usó `full_history_when_stateless`).
4. **Es una sola corrida con Gemini**, y el modelo es no determinista: confírmalo antes de afirmarlo en clase.
5. En esta corrida el modelo interpretó bien la instrucción ambigua ("las 2 categorías con mayor exceso") y dijo que no hubo excesos; en otras corridas la interpretó distinto (ver Parte 4).

**🎤 Dices:** "Antes de este experimento teníamos una duda razonable: ¿qué pasa con la memoria cuando el especialista vive en otro servicio? Probamos las dos cosas: **misma sesión**, y **sesión nueva** como control. La primera recordó que hablábamos de Norte; la segunda no. Eso es lo que esperaríamos de un sistema bien armado: el estado viaja con la sesión, aunque el especialista esté en otro proceso."

#### 5.3b Qué viaja realmente por la red (observado con ADK 2.12.0; opcional, 2 min)
**Por qué importa:** en `adk web` (agentes `supervisor_remoto_app` y `supervisor_router_app`) la respuesta del especialista aparece **dos veces**: un bloque gris **THOUGHT** y debajo el mensaje final con el mismo texto. En el notebook no se nota, porque `preguntar` solo imprime la respuesta final. Alguien lo va a preguntar.

**Qué se observó** (una pregunta directa al servidor del 8001, con streaming, sin supervisor; una sola corrida):

| # | Evento A2A | Contenido |
|---|---|---|
| 1 | Task creada | estado `SUBMITTED` |
| 2 | `statusUpdate` | `WORKING` |
| 3 | `statusUpdate` `WORKING` | llamada a `consultar_presupuesto(Norte, 2026-Q3)` |
| 4 | `statusUpdate` `WORKING` | resultado de la herramienta |
| 5 | `statusUpdate` `WORKING` | **el texto final de la respuesta** |
| 6 | `artifactUpdate` (`lastChunk: true`) | **el mismo texto final** |
| 7 | `statusUpdate` | `COMPLETED` |

Qué extraer de ahí:
1. **El especialista responde con una Task, no con un Message suelto.** Pasa por `SUBMITTED → WORKING → COMPLETED` y entrega la respuesta como **artefacto**. Es el caso "Task" de la diapositiva 26.
2. **El texto llega dos veces: en el evento 5 (dentro de un `WORKING`) y en el 6 (artefacto).** El cliente `RemoteA2aAgent` marca como *thought* todo lo que llega en `SUBMITTED`/`WORKING` (está en el código de ADK, `a2a/agent/_remote_a2a_agent.py`). Eso explica el bloque gris. No es un error de nuestro proyecto.
3. **Sin streaming** (`SendMessage`) la respuesta es una sola Task `COMPLETED` con el texto **una vez** en `artifacts`; la pregunta y las llamadas a la herramienta quedan en `history`. No se revisó si `history` repite el texto.
4. **Pista sobre el contexto de sesión (5.3):** en los metadatos del servidor, `adk_session_id` es igual al `contextId` de la Task, y `adk_user_id` es `A2A_USER_<contextId>`. Es decir, el servidor guarda **su propia sesión identificada por `contextId`**. Esto apoya la segunda hipótesis del punto 3 de 5.3, pero **no la demuestra**: en esta prueba no se envió un `contextId` propio para comprobar que se reutiliza.

**🎤 Dices:**
> "Si usan `adk web`, van a ver la respuesta dos veces: una gris, que dice THOUGHT, y otra normal. No es un error. Lo que pasa es que el especialista no contesta con un mensaje suelto, sino con una **Task**: va pasando por estados, `working` y luego `completed`, y entrega el resultado como **artefacto**. El texto viaja primero dentro del estado `working`, que ADK pinta en gris, y después como resultado final. Es justo la diferencia entre Message y Task de la que hablamos en teoría."

**⚠️ Límites:** una sola pregunta con Gemini, solo con ADK 2.12.0 (no se probó con 2.11.0). Las cifras salieron bien, pero en el evento 5 el modelo agregó diferencias calculadas por él (`Consultoria (46800)`, `Viaticos (21150)`), que la herramienta no devuelve.

### 5.4 Reto opcional: router con dos especialistas remotos (10 min, solo si sobra tiempo)
**Para qué:** el cronograma pide los patrones Supervisor/Router-Worker y hand-off **sobre A2A**. Hasta 5.3 el supervisor tenía **un** especialista remoto; aquí tiene **dos** y decide a cuál transferir según el dominio de la pregunta. Hazlo como **demo tuya** si el grupo va justo de tiempo, o como reto para las células que terminen rápido.

**🎤 Dices (antes de la celda del segundo servidor):**
> "Ahora publicamos **Tesorería** como segundo servidor A2A, en el puerto **8002**. El de Presupuestos sigue en el 8001. Son **dos servicios independientes**, y el supervisor los consume por red. Ojo con algo: un agente remoto es una **caja negra**. Tesorería no ve el árbol del supervisor, así que **quien decide a quién pasar el control es el supervisor**, no los especialistas entre sí. En la Parte 7 Tesorería transfería directo a Presupuestos; aquí eso no es posible."

**Dónde queda en el proyecto:** el servidor de Tesorería (`a2a_app_tesoreria`) y el `supervisor_router` están en `src/finanzas_agents/a2a_server.py`, y `supervisor_router_app` los expone en `adk web` (necesita los dos servidores). El notebook arranca el 8002 con `uvicorn finanzas_agents.a2a_server:a2a_app_tesoreria`, igual que el 8001.

**Respuestas TODO (versión alumnos):** `agent_card=URL_CARD_TES` y `sub_agents=[presupuestos_rem, tesoreria_rem]`; en la `instruction` del supervisor, mencionar a los dos especialistas por su `name`.

**👀 Deben ver:**
```
Agent card → especialista_tesoreria | Flujo de caja, liquidez y pagos.
👤 ¿Cuál es la posición de liquidez?
   🔧 [supervisor_router] llama transfer_to_agent({'agent_name': 'especialista_tesoreria'})
🤖 [especialista_tesoreria] ... no tengo acceso a los datos ... (pide la información que necesitaría)
👤 ¿y el presupuesto de Norte en 2026-Q3?
   🔧 [supervisor_router] llama transfer_to_agent({'agent_name': 'especialista_presupuestos'})
   🔧 [especialista_presupuestos] llama consultar_presupuesto({...})      ← corrió en el puerto 8001
🤖 [especialista_presupuestos] ... 304,000 / 380,900 / +25.3 % ...
```
**Lo que se observó (Gemini real, 2 corridas del instructor):** en las dos, el supervisor transfirió primero a Tesorería y, en la pregunta siguiente de la **misma sesión**, **volvió a transferir** a Presupuestos. Es decir, el control pasó de un especialista remoto al otro **según el dominio**, mediado por el supervisor.

**🎤 Dices:** "Fíjense en quién transfiere: en el log dice `[supervisor_router] llama transfer_to_agent`. El especialista de Tesorería **no devolvió el control**; lo retomó el supervisor. Es el patrón **Router-Worker** sobre A2A. El hand-off directo entre especialistas, el de la Parte 7, solo funciona entre agentes **del mismo árbol**."

**Qué extraer:**
1. **Router-Worker sobre A2A con dos workers** funciona con la misma mecánica que local: `sub_agents` + `transfer_to_agent`; cambia que cada worker vive en su servidor.
2. **Un `RemoteA2aAgent` por especialista** (un agente solo puede tener un padre): no reutilices los de la 5.2.
3. **Dos servidores, dos puertos:** hay que apagar ambos (la celda "Cierra el servidor de Tesorería" y la de la 5.2).
4. **Las cifras pueden salir mal en una corrida.** En una de las corridas del instructor, Presupuestos redactó **304,000,000 / 380,900,000** (multiplicadas por mil) aunque la herramienta devolvió 304000 / 380900. Se agregó a la `instruction` de `presupuestos_agent` en `agent.py` la cláusula *"reporta las cifras EXACTAMENTE como las devuelve la herramienta, sin multiplicarlas"*; **no se ha vuelto a probar con Gemini si desaparece**: repítelo un par de veces antes de la clase. Si reaparece, es un buen ejemplo de por qué en el Módulo 5 se mide la **fidelidad** de las cifras.
5. **Qué no se probó:** que Tesorería (remoto) devuelva el control al supervisor sin pasar por él, un hand-off entre dos remotos sin supervisor, ni autenticación entre servidores.

**⚠️ Errores:**
| Síntoma | Causa | Qué hacer |
|---|---|---|
| `AssertionError: El servidor A2A no arrancó` | Puerto 8001 ocupado, `uvicorn` no instalado, o tardó | `netstat -ano \| findstr 8001`; `pip install uvicorn`; reintentar la celda |
| Puerto ocupado tras reiniciar el kernel | El proceso del servidor quedó vivo | `netstat -ano \| findstr 8001` → anotar el PID → `taskkill /PID <pid> /F` |
| Windows pide permiso de firewall y no lo conceden | Bloquea el puerto | Permitir en redes privadas, o ejecutar el servidor en una terminal y comentar la celda |
| `RemoteA2aAgent` marca error de parámetros | API experimental/cambió | Ver https://adk.dev/a2a/quickstart-consuming/ (parámetro `use_legacy`) |
| Respuesta vacía sin haber apagado el servidor | El servidor murió o la celda del servidor no se ejecutó | Volver a ejecutar la celda del servidor y esperar la agent card |
| Ejecutaron dos veces la celda del servidor | Segundo proceso no puede abrir 8001 | Cerrar el primero (`servidor.terminate()`) y relanzar |
| `AssertionError: El servidor de Tesorería no arrancó` (5.4) | Puerto 8002 ocupado o servidor lento | `netstat -ano \| findstr 8002`; `taskkill /PID <pid> /F`; reintentar la celda |
| El supervisor del 5.4 se queda mudo | El servidor del 8001 o del 8002 no está corriendo | Ejecutar primero la celda de la 5.2 y luego la del 8002; ver las dos agent cards |

**✅ Checkpoint:** ven la agent card y la respuesta del supervisor remoto. **Si más de la mitad de las células fallan aquí, no pierdas tiempo:** haz tú la demo en el proyector y que el resto copie el patrón (la Parte 8 solo exige la agent card).

---
## Parte 6 · Workflows y `output_key` (10 min)

**🎤 Dices:**
> "Hasta ahora **el modelo decidía** el camino. Pero si el orden ya lo conozco —primero analizo, luego redacto— no necesito que un modelo lo decida: uso un **`SequentialAgent`**, que ejecuta sus sub-agentes **en orden fijo**. Es **código determinista**: más barato, más rápido, predecible. Y fíjense en `output_key`: es el **nombre bajo el que se guarda la respuesta en el estado de la sesión**. El siguiente agente la lee con **llaves** en su instrucción: `{analisis_presupuesto}`."

**👀 Deben ver:**
```
👤 Norte 2026-Q3
   🔧 [analista_presupuesto] llama consultar_presupuesto({...})
🤖 [analista_presupuesto] ... ejecutado 380,900 (+25.3%) ...
🤖 [redactor_ejecutivo] La división Norte excedió su presupuesto en el trimestre 2026-Q3. Se presupuestaron 304,000, pero se ejecutaron 380,900 ... 25.3% ...
Estado de la sesión → ['analisis_presupuesto', 'resumen_ejecutivo']
```
**🎤 Dices:** "Miren la última línea: el **estado** tiene las dos claves. Así se pasan información los agentes sin que el usuario intervenga."
**Aviso (di esto sin dramatizar):**
> "Si ven un aviso amarillo que dice que `SequentialAgent` está **deprecated**: es correcto. En ADK 2.x ya hay una nueva forma, `Workflow`, pero estas clases siguen funcionando y son el vocabulario del curso. No es un error suyo."

**🔬 Lo que se obtuvo al ejecutarlo (Gemini real) — análisis:**

| Qué se observó | Resultado real |
|---|---|
| Orden de ejecución | `analista_presupuesto` (llama a la herramienta y responde) → `redactor_ejecutivo` (responde). **Sin `transfer_to_agent`**: el orden no lo decide un modelo |
| Estado de la sesión | `['analisis_presupuesto', 'resumen_ejecutivo']`: una clave por cada `output_key` |
| El redactor usó el análisis | Sí: escribió 3 líneas a partir de lo que dijo el analista (la llave `{analisis_presupuesto}` se sustituyó) |
| `LoopAgent` (Ejercicio 3) | Imprime `3` (`max_iterations`) |
| Avisos | `DeprecationWarning` de `SequentialAgent` y `LoopAgent` (los esperados) |

**⚠️ Hallazgo importante: el modelo multiplicó las cifras por 1000 (y el error se propagó).** En esa corrida:
```
Herramienta (la base):   presupuestado 304000      ejecutado 380900     desviación 25.3 %
🤖 analista:             "presupuesto total de 304,000,000 ... ejecutado 380,900,000 ... 25.3%"
🤖 redactor:             "presupuesto total de 304,000,000 ... ejecutado 380,900,000 ... 25.3%"
```
Qué se aprende de ahí:
1. **El modelo no es una calculadora ni una copia fiel.** Recibió `304000` y escribió `304,000,000`. El porcentaje sí era correcto porque la herramienta lo entrega ya calculado; las cifras absolutas las "reescribió" él.
2. **El error se propagó por el pipeline.** El redactor solo ve el texto del analista (por `output_key`), no la herramienta; por eso copió la cifra equivocada. **Un error aguas arriba contamina todo lo que sigue.**
3. **Los mismos datos salieron bien en otras corridas** (Partes 2, 3 y 5: 304000 / 380900). Es **no determinismo**: "a mí me funcionó" no es una prueba.
4. **Es el caso real que motiva el Módulo 5:** la métrica **Faithfulness** mide justo esto (si la respuesta es fiel a lo que devolvió la herramienta), y el *gate* de CI debe bloquear un agente así.

**🎤 Dices (úsalo con la salida de su pantalla o con ésta):**
> "Miren con cuidado las cifras. La herramienta devolvió **304 mil**; el modelo escribió **304 millones**. El porcentaje está bien, pero el monto no. ¿Cuántos de ustedes lo habrían notado si no se los señalo? **Este es el riesgo real de un agente financiero**: no es que falle de forma obvia, es que se equivoca con mucha seguridad. Y como el redactor confía en el analista, el error ahora está en dos lugares. Por eso la semana cinco es sobre **medir** si el agente es fiel a sus datos, no sobre confiar en que lo sea."

**❓ Preguntas extra:**
- "¿Qué agente falló, el analista o el redactor?" → *el analista; el redactor solo propagó.*
- "¿Cómo lo detectaría un sistema automáticamente?" → *comparando las cifras de la respuesta con las que devolvió la herramienta (Faithfulness, Módulo 5).*

**Posibles mitigaciones (sin probar; ideas para discutir):** pedir en la instrucción *"reporta las cifras exactamente como las devuelve la herramienta, sin cambiar unidades"*; validar en código que las cifras del texto coincidan con las de la herramienta; pasar al redactor los **datos** y no solo el texto del analista.
> La primera mitigación **ya está aplicada en `practica_alumnos.ipynb`** (instrucciones del analista y del redactor; la celda usa ahora la sesión `w2` para ver los eventos de nuevo), pero **aún no se ha ejecutado**: corre la celda varias veces y compara antes de afirmar que funciona.
> Esto sale de **una** corrida. No es un fallo que ocurra siempre; si en clase les sale bien, igual vale la pena mostrarla como ejemplo de lo que puede pasar.

### Ejercicio 3 (LoopAgent, 3 min)
**Respuesta:** `refinador = LoopAgent(name="refinador", sub_agents=[revisor], max_iterations=3)` → imprime `3`.
**🎤 Dices:** "El `LoopAgent` **no tiene modelo ni instrucciones propias**: solo repite a sus hijos. Se detiene al llegar a `max_iterations` **o** cuando un sub-agente decide terminar. **Siempre pongan un máximo**; un bucle sin tope es un bucle que cuesta dinero."

**❓ Preguntas:**
1. "¿Cuándo usarías un workflow en vez de un supervisor con modelo?" → *cuando el orden es fijo y conocido.*
2. "¿Cómo sabe el redactor lo que dijo el analista?" → *vía `output_key` → estado de la sesión → `{llave}`.*

**⚠️ Errores:** `KeyError`/llave vacía en la instrucción → el `output_key` del agente anterior no coincide con el `{nombre}`. `refinador = ...` sigue en `Ellipsis` → falta el TODO.

**✅ Checkpoint:** ven las dos claves en el estado y el `3` del loop. *(Si vas atrasada, esta parte se deja de tarea.)*

---
## Parte 7 · Reto: hand-off a Tesorería (10 min)

**🎤 Dices:**
> "Este es el reto. Crean un **segundo especialista** —Tesorería— y un **segundo supervisor** que conoce a los dos. Después preguntan por **liquidez** y, **en la misma sesión**, por el **presupuesto de Norte**. Quiero ver cómo el control **pasa de un especialista a otro**. Y les adelanto el obstáculo: en ADK **un agente solo puede tener un padre**. Si reutilizan `presupuestos_agent` tal cual, van a ver un error. La salida es **clonarlo**."

**🛠 Haces:** da 7 min. Deja que **fallen** con el error y que lean el mensaje; es parte del aprendizaje. Espera 2 min antes de dar la pista del `clone()`.

**👀 El error que verán (si no clonan):**
```
ValidationError: Agent `especialista_presupuestos` already has a parent agent, current parent: `supervisor_finanzas`, trying to add: `supervisor_finanzas_v2`
```
**🎤 Dices:** "Léanlo despacio: **el mensaje dice exactamente qué pasó**. Esa es la habilidad: leer el error antes de pedir ayuda."

**👀 Resultado correcto:**
```
👤 ¿Cuál es la posición de liquidez?
   🔧 [supervisor_finanzas_v2] llama transfer_to_agent({'agent_name': 'especialista_tesoreria'})
🤖 [especialista_tesoreria] Para darte la posición de liquidez, necesito saber qué información específica te interesa ...
👤 ¿y el presupuesto de Norte en 2026-Q3?
   🔧 [especialista_tesoreria] llama transfer_to_agent({'agent_name': 'especialista_presupuestos'})
   🔧 [especialista_presupuestos] llama consultar_presupuesto({'division': 'Norte', 'trimestre': '2026-Q3'})
🤖 [especialista_presupuestos] ... ejecutado 380,900 (+25.3%) ...
```
> Nota: lo que **debe** verse siempre es la **secuencia de transferencias** (supervisor → Tesorería, y luego Tesorería → Presupuestos). El **texto** de Tesorería varía entre corridas (ver análisis abajo). Si escriben solo "Q3" sin año, Gemini puede pedir el año: usen **2026-Q3**.

**🔬 Lo que se obtuvo al ejecutarlo (Gemini real) — análisis:**

| Pregunta | Eventos | Qué respondió el modelo |
|---|---|---|
| 1. "¿Cuál es la posición de liquidez?" | `supervisor_finanzas_v2` → `transfer_to_agent('especialista_tesoreria')` | Tesorería (sin herramientas) dio una **definición general** de liquidez ("capacidad de la empresa para cumplir sus obligaciones a corto plazo… activos líquidos vs pasivos a corto plazo…") y ofreció profundizar |
| 2. "¿y el presupuesto de Norte en 2026-Q3?" | `especialista_tesoreria` → `transfer_to_agent('especialista_presupuestos')` → `consultar_presupuesto` | Cifras correctas, pero con **formato europeo**: `304.000,00`, `380.900,00`, `46.800,00`, `21.150,00` |

Qué extraer de ahí:
1. **El supervisor eligió bien entre dos especialistas** leyendo sus `description`. Aquí sí decide la descripción (en la Parte 3 había uno solo).
2. **El hand-off entre especialistas ocurrió sin pasar por el supervisor.** Tesorería reconoció que la pregunta de presupuesto no era suya y transfirió **directo** a Presupuestos. Esa es la instrucción "si te preguntan por presupuesto, devuelve el control" funcionando.
3. **Un agente sin herramientas igual responde, pero con conocimiento general, no con datos de la empresa.** La definición de liquidez es de libro de texto: no inventó cifras (bien), pero un usuario podría confundirla con "la liquidez de la empresa". En otra corrida el mismo agente respondió con una pregunta aclaratoria. Es **no determinismo**.
4. **La instrucción debe decir lo que el agente NO puede hacer.** En el notebook de práctica se reforzó la de Tesorería: *"no tienes herramientas ni acceso a datos de la empresa: no des cifras ni inventes datos; si te piden un dato, explica qué información necesitarías"*. (Cambio **aún sin ejecutar**: compara con la corrida original.)
5. **El formato de los números cambia entre corridas** (`304000`, `304,000`, `304.000,00`). Las cifras son las mismas, pero **un chequeo por texto exacto puede dar falsos ❌**. Por eso la autoevaluación de la Parte 8 se amplió para aceptar `25.3`/`25,3` y `380,900`/`380.900`/`380900`.

**🎤 Dices:** "Comparen la respuesta de Tesorería con la de Presupuestos. Presupuestos tiene una **herramienta** y sus cifras salen de la base. Tesorería **no la tiene**, y lo que dice es lo que 'sabe' el modelo en general. En un sistema real, ¿quieren que un agente sin datos conteste como si los tuviera? La instrucción es donde le dicen **qué no debe hacer**."

**🎤 Dices:** "Ese `transfer_to_agent` **entre dos especialistas**, sin pasar por el supervisor, es el **hand-off jerárquico**. Tesorería reconoció que la pregunta ya no era suya y **devolvió el control**."

**❓ Preguntas:**
1. "¿Por qué hubo que clonar?" → *un agente solo puede tener un padre.*
2. "¿Qué pasaría si las descripciones de Tesorería y Presupuestos fueran casi iguales?" → *el enrutamiento se vuelve ambiguo.*

**⚠️ Errores:** además del `clone`, el `name` de Tesorería con espacios, o no usar la **misma `session_id`** en las dos preguntas (entonces no hay hand-off, son conversaciones distintas).

**✅ Checkpoint:** ven el control pasar de Tesorería a Presupuestos. *(Reto opcional si va tarde el grupo.)*

---
## Parte 8 · Autoevaluación (10 min)

**🎤 Dices:**
> "Esta celda es su **examen automático**. Comprueba cinco cosas. Quiero ver **cinco ✅**. Si alguna sale ❌, el texto les dice **a qué parte regresar**. Ojo: el chequeo de la agent card necesita que hayan hecho la Parte 5."

**👀 Deben ver:**
```
✅ Un contrato inválido se rechaza por código, no por el LLM
✅ La herramienta devuelve Norte 2026-Q3 con exceso > 15 %
✅ El supervisor delega y responde con la cifra (25.3 % / 380,900)
✅ El seguimiento conserva la división (no la vuelve a pedir)
✅ La agent card A2A se publicó

🎓 ENTREGABLE LISTO
```

| ❌ | Causa probable | Regresar a |
|---|---|---|
| Contrato | No definieron `BudgetRequest`/`ValidationError` | Parte 1 |
| Herramienta | `consultar_presupuesto` no se importó | Parte 1 |
| Delegación | `sub_agents` vacío o `supervisor` mal definido | Parte 3 |
| Seguimiento | Usaron sesiones distintas | Parte 4 |
| Agent card | No levantaron el servidor (o lo cerraron antes) | Parte 5 |
| (con Gemini) cifra o seguimiento ❌ aunque funcionó | La **redacción** del modelo cambió (p. ej. escribió "380.900") | Mira la respuesta; si es correcta, **no es un bug**, ajusta el criterio. Es una limitación del chequeo por texto |

**🎤 Dices (la lección escondida):**
> "Si con Gemini alguna prueba falla aunque la respuesta sea correcta, acaban de descubrir **por qué evaluar agentes es difícil**: la respuesta cambia de redacción cada vez. En la semana cinco veremos cómo medirlo sin depender del texto exacto."

**✅ Checkpoint final:** cada célula muestra **🎓 ENTREGABLE LISTO** (captura de pantalla para la entrega).

---
## Cierre (5 min)

**🎤 Dices:**
> "Hoy construyeron lo esencial: **una herramienta tipada, un agente, un supervisor que delega, un estado que se conserva y un especialista remoto por A2A**. Con el notebook completo ya tienen el **esqueleto del agente financiero**; en las próximas semanas le vamos a poner *documentos*, *bases de datos* y *modelos* a esos mismos especialistas.
> **Para entregar:** el notebook ejecutado (con el 🎓 visible), y el repositorio de la célula. La demo de 5 minutos: muéstrenme el Trace de una delegación y expliquen **una decisión de diseño** que tomaron.
> **Para la próxima semana:** lean el Módulo 2 —RAG—, y tráiganme una pregunta: ¿qué documentos de su empresa serían buenos candidatos para un agente?"

---
## Code review: qué preguntar (10 min por célula)

**Estructura (10 min):** 2 min ven su pantalla · 5 min preguntas · 3 min devolución con **una cosa buena y una mejora**.

**Preguntas que hacer** (obliga a explicar, no solo a mostrar):
1. "Léeme tu `description`. Si fueras el supervisor, ¿te alcanzaría para decidir?"
2. "¿Dónde está el número 380,900 en tu código? ¿Lo escribió el modelo o la base?"
3. "Quita una línea de tu `instruction`. ¿Qué crees que cambia?" *(solo con Gemini)*
4. "¿Qué pasa si el usuario pide la división 'Marte'? Muéstramelo."
5. "¿Por qué clonaste (o no) el especialista?"
6. "¿Tu `.env` está en Git?" *(debe ser **no**)*

**Checklist rápido (para tus notas):**
- [ ] `description` distinta y clara en cada agente
- [ ] La herramienta tiene tipos y docstring
- [ ] Contrato validado por código
- [ ] Errores devueltos como dato
- [ ] Sin secretos en el repo
- [ ] Nombres de agente válidos (sin espacios)
- [ ] Un test de delegación o estado (pídelo como mejora)

---
## Si algo sale mal (contingencias)
| Situación | Plan |
|---|---|
| Gemini no responde / error 429 | Esperar 1 minuto y reintentar la celda; si persiste, el instructor ejecuta en el proyector y las células siguen el flujo y completan el código hasta que se restablezca |
| Más de la mitad no pasó la Parte 0 a los 15 min | Parar y resolver el origen común (casi siempre: kernel equivocado, `.env` sin proyecto o falta de `gcloud auth application-default login`); que trabajen en parejas con **una** máquina que funcione |
| Vas 10 min atrasada a la mitad | Deja **Parte 6** y **Parte 7** como tarea; protege la 5 y la 8 |
| A2A falla masivamente | Demo tuya en el proyector; que copien el patrón; la Parte 8 solo exige la agent card |
| Un alumno terminó mucho antes | Que haga el reto extra: añadir un tercer especialista (Cuentas por Cobrar) y un test de `pytest` que verifique la delegación |
| Te preguntan algo que no sabes | "Buena pregunta; no voy a inventarlo. Lo verifico y respondo por el chat." |

---
## Problemas fuera del notebook
| Síntoma | Causa | Solución |
|---|---|---|
| `adk web` no lista el agente | Carpeta equivocada | Pásale la carpeta que **contiene** los paquetes: `adk web --port 8501 modulo1_adk_a2a/src` |
| `Errno 13` al abrir `adk web` | Windows reserva el puerto 8000 | Usar `--port 8501` |
| `No module named 'shared'` en `adk web` o `uvicorn` | Falta `. .\env.ps1` en esa terminal | Ejecutarlo antes (o iniciar el notebook, que ya lo hace) |
| `supervisor_remoto_app` mudo | Puerto 8001 ocupado por otro proceso o servidor A2A apagado | Ver la tabla de la sección "Cómo probar y leer `adk web`" |
| 404 en `/.well-known/agent-card.json` | El servidor aún arranca | Espera unos segundos; corre desde la raíz del proyecto |
| `ModuleNotFoundError: finanzas_agents` en terminal | Falta el `PYTHONPATH` | `. .\env.ps1` (el notebook ya lo configura solo) |
| Avisos `EXPERIMENTAL` / `deprecated` | ADK 2.x | Esperados; no son errores |

## Lo que no está probado
- **Corrida completa del notebook del instructor con Gemini:** ya se ejecutó una vez (0 errores y los 5 ✅ en la Parte 8, con las correcciones de las Partes 6 a 8 y el experimento 5.3). La celda de la Parte 2 que ejecuta el agente solo quedó sin correr. **Una corrida no demuestra estabilidad**: Gemini es no determinista.
- **Windows** pidiendo permiso de firewall al levantar el servidor A2A.
- **Duplicado THOUGHT en `adk web` (5.3b):** observado solo con ADK 2.12.0 y una pregunta; no se probó con 2.11.0.
- Despliegue a Agent Runtime.
