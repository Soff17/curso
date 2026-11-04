# Módulo 1 · SESIÓN TEÓRICA (2 h) — Guía del instructor

**Tema:** ADK Code-First y arquitectura multi-agente A2A · **Público:** Equipo de BI (30 personas, 5 células) · **Semana 1**
La práctica con el notebook (tutoría de 2 h) tiene su propia guía: **`SESION_PRACTICA.md`**.
Verificado con **google-adk 2.11.0**. Lo que depende de Gemini real (respuestas del modelo) pruébalo tú antes de la clase.

**Presentación que acompaña esta guía:** `Modulo 1 - ADK y A2A.pptx` (33 diapositivas). Esta guía es tu **guion**: lo que dices, por qué, qué preguntar y qué responder; las diapositivas son lo que proyectas. La **sección 5 es el guion diapositiva por diapositiva**, con el "por qué" y las respuestas a dudas dentro de cada una.
Comandos, puertos y errores de entorno: **`COMANDOS.md`**. Permisos, cuota y carpeta a entregar: **`PREREQUISITOS_ORGANIZADORES.md`**.

**Contenido de esta guía:** 1. Antes de la clase · 2. Mensajes clave · 3. Línea de tiempo · 4. Ensayo previo de las demos · 5. Guion por diapositiva · 6. Frases de rescate y recortes · 7. Errores comunes y preguntas de repaso · 8. Lo que no está probado · **9. Mapa del proyecto y cómo crear tu propio agente**.

---
## 1. Antes de la clase (haz esto el día anterior)
- [ ] `. .\env.ps1` y `python -m pytest -q` → **61 passed** (todo el proyecto; ninguna llama a Gemini). *(El Módulo 1 sola se verificó con 22 passed; el total de 61 es la suma calculada de todo el proyecto, sin ejecutar completa tras los últimos cambios.)*
- [ ] `. .\env.ps1` y luego `adk web --port 8501 modulo1_adk_a2a/src` abre en http://127.0.0.1:8501 y lista `finanzas_agents` y `supervisor_remoto_app`. (**`--port 8501`**: en Windows el 8000 puede estar reservado y da `Errno 13`; **`env.ps1`**: sin él falla con `No module named 'shared'`.)
- [ ] Prueba la delegación A2A **con Gemini real** (`RemoteA2aAgent` es experimental; parámetro `use_legacy`). Puerto **8001 libre**: `netstat -ano | findstr 8001`.
- [ ] Credenciales: `GOOGLE_GENAI_USE_ENTERPRISE=TRUE` + proyecto + `gcloud auth application-default login` (o `GOOGLE_API_KEY`).
- [ ] Consola abierta en las pestañas **Model Garden** y **Agent Runtime** (nombres nuevos: ver `docs/05-nombres-actuales.md`).
- [ ] Alumnos con el entorno instalado **una semana antes** (`PREREQUISITOS_ALUMNOS.md`); permisos y cuota del proyecto resueltos (`PREREQUISITOS_ORGANIZADORES.md`).
- [ ] Presentación abierta (`Modulo 1 - ADK y A2A.pptx`; las notas del orador traen la demo de cada diapositiva) y terminal, consola, `adk web` y notebook a la mano para proyectar.

## 2. Mensajes clave (las ideas que deben llevarse)
1. **Code-First** = versionable, testeable, revisable en PR. Low-code no escala a 30 personas.
2. Un agente es: **modelo + instrucción + herramientas + (sub)agentes**. La `description` es la API pública del agente para el router.
3. **A2A no es "llamar a una función"**: es un contrato (agent card, mensajes tipados, contexto de sesión) entre sistemas de equipos distintos.
4. **Herramientas tipadas y contratos Pydantic** son la defensa contra respuestas inventadas en las interfaces: *el modelo propone, el código decide*.

## 3. Línea de tiempo
Coincide con los bloques de la presentación (los minutos suman 120).

| Hora | Min | Bloque | Diap. | Qué muestras |
|---|---|---|---|---|
| 0:00–0:08 | 8 | Apertura: el caso y el entregable | 1–3 | Caso de Norte (304,000 vs 380,900) y agenda |
| 0:08–0:26 | 18 | La plataforma y su arquitectura | 4–7 | Consola: Model Garden, Agent Runtime, Memory Bank |
| 0:26–0:46 | 20 | ADK y el entorno | 8–10 | `adk create`, `adk run` |
| 0:46–1:08 | 22 | El agente base en código | 11–17 | `tools.py`, `agent.py`, demo "Marte", `adk web` + Events, sesión y estado |
| 1:08–1:23 | 15 | Orquestación multiagente | 18–23 | `root_agent` y `sub_agents`, `transfer_to_agent`, hand-off a Tesorería, `clone()`, workflows |
| 1:23–1:40 | 17 | A2A | 24–28 | `a2a_local.py`, agent card, `supervisor_remoto_app` |
| 1:40–1:45 | 5 | Interfaces estrictas | 29 | JSON Schema de `BudgetRequest` |
| 1:45–1:52 | 7 | Qué hace un LLM cuando lo pones a trabajar | 30 | Los ejemplos reales de esta sesión |
| 1:52–2:00 | 8 | Cierre | 31–33 | 4 ideas + abrir el notebook (Parte 0) |

## 4. Ensayo previo de las demos (hazlo tú antes; esto es lo que debes ver)
Terminal en la raíz del proyecto, con `. .\env.ps1` (más comandos y soluciones de errores en `COMANDOS.md`).

| Demo | Comando / acción | Debes ver |
|---|---|---|
| Crear agente | `adk create demo_agente --model gemini-2.5-flash` y `adk run demo_agente` | Carpeta con `agent.py`, `.env`, `__init__.py` |
| Herramienta | `python -c "from finanzas_agents.tools import consultar_presupuesto as c; print(c('Norte','2026-Q3'))"` | `status: ok`, desviación ≈ **25.3 %**, 5 categorías |
| Contrato | `python -c "from finanzas_agents.contracts import BudgetRequest as B; B(division='Marte', trimestre='2026-Q3')"` | Error: `Input should be 'Norte', 'Sur', 'Centro' or 'Occidente'` |
| Esquema OpenAPI | `python -c "from finanzas_agents.contracts import BudgetRequest as B; import json; print(json.dumps(B.model_json_schema(), indent=2))"` | JSON Schema: es el contrato que se publica |
| Delegación | `. .\env.ps1` y `adk web --port 8501 modulo1_adk_a2a/src` → agente `finanzas_agents` → "¿Cómo va la división Norte en 2026-Q3?" | En **Trace**: `transfer_to_agent` → `consultar_presupuesto`; **380,900 vs 304,000 (+25.3 %)** |
| Estado | Misma sesión: "¿Y en 2026-Q2?" | No pide la división; **318,000 vs 294,364 (−7.4 %)** |
| A2A sin red | `a2a_local.py`: `Supervisor` + `BudgetWorker` (ver `SESION_PRACTICA.md`, Parte 5.1) | Handshake con `skills=['presupuesto']` y estado conservado |
| A2A real | `uvicorn finanzas_agents.a2a_server:a2a_app --port 8001` y, en otra terminal, `(Invoke-WebRequest http://localhost:8001/.well-known/agent-card.json -UseBasicParsing).Content` | JSON con `name: especialista_presupuestos` |
| Supervisor remoto | `adk web` → agente `supervisor_remoto_app` → misma pregunta | En Trace, la llamada remota al puerto 8001 |
| Hand-off a Tesorería | `adk web` → `finanzas_agents` → "¿Cuál es la posición de liquidez?" y luego "¿y el presupuesto de Norte en 2026-Q3?" (misma sesión) | `transfer_to_agent` a `especialista_tesoreria` y, en la segunda, de Tesorería a `especialista_presupuestos`. **Verificado una vez en `adk web` con el proyecto migrado (12 oct)**: la pregunta de liquidez llegó a Tesorería, que no inventó cifras, y la de presupuesto volvió a Presupuestos con las cifras correctas. Matiz: en una sesión larga la pregunta de liquidez la recibió primero el último agente (Presupuestos) y este la transfirió a Tesorería; en una sesión nueva el primer paso es supervisor → Tesorería |
| Workflows | `python -c "from finanzas_agents import workflows as w; print([a.name for a in w.pipeline_secuencial.sub_agents], w.refinador.max_iterations, w.analista.output_key)"` | `['analista_presupuesto', 'redactor_ejecutivo'] 3 analisis_presupuesto` |
| Ejecución por código | `python -m finanzas_agents.run_programmatic` (necesita Gemini) | Dos respuestas; la segunda conserva la división (misma sesión) |

> **Nota de ADK 2.x:** `SequentialAgent`, `ParallelAgent` y `LoopAgent` funcionan pero están **marcados como obsoletos** a favor de `Workflow` (que hoy no puede ser sub-agente de un `LlmAgent`). Avísalo; son el vocabulario del curso.

---
## 5. Guion por diapositiva
Archivo: `Modulo 1 - ADK y A2A.pptx` (33 diapositivas). Aquí está **qué decir en cada una**, casi literal (adáptalo a tu voz).
**Cómo leerlo:** **🛠** = qué haces (demo o comando) · **🎤** = qué decir · **💡** = por qué se hace así (para que puedas defenderlo si preguntan) · **❓** = pregunta para el grupo · **⚠️** = dudas probables y cómo responderlas.
**Tono:** el público es Equipo de BI: conocen SQL, modelos de datos y tableros, pero probablemente no agentes. Ancla cada concepto a algo que ya conocen.
**Fuentes:** lo marcado *(video)* viene de tus apuntes de los videos: dilo como "según Google" y confírmalo antes de usarlo como cifra.

---
### Apertura (0:00–0:08)

**Diap. 1 · Portada**
🛠 Presenta el programa y confirma las 5 células de trabajo. Si quieres, proyecta la tabla de 6 semanas de `docs/00-analisis-programa.md`.
> "Bienvenidos al Módulo 1 de las seis semanas. Hoy aprendemos a **construir agentes en código con ADK** y a hacer que **hablen entre ellos con A2A**. Trabajarán en **células de seis**: cada una entrega algo funcionando cada semana y en la semana seis cada una presenta su agente."

💡 Mostrar el destino desde el minuto uno da sentido a cada semana.

**Diap. 2 · El caso: la división Norte**
> "Antes de las cifras, ¿de qué va todo esto? Un **agente de IA** es un programa que usa un modelo de lenguaje para **entender una pregunta escrita en lenguaje normal**, **decidir qué hacer** y **usar herramientas** —consultar una base de datos, llamar a una API— para responder. No solo conversa: **actúa sobre sus datos**.
> Piensen en lo que hace hoy un analista de BI cuando le preguntan *'¿por qué excedió la división Norte su presupuesto?'*: entra a varios sistemas, cruza tablas, calcula desviaciones y arma la explicación. Lo que vamos a construir en estas seis semanas es un **asistente financiero hecho de varios agentes**, cada uno especialista en algo —presupuestos, tesorería—, que haga ese trabajo y **diga de dónde sale cada cifra**.
> Para practicar usamos una empresa de ejemplo con **datos sintéticos**, es decir, inventados; no hay información real. Un ejemplo del tipo de respuesta que buscamos: la división Norte presupuestó **304,000** en el tercer trimestre y ejecutó **380,900**, una desviación de **+25.3 %**, con **Consultoría** (+46,800) y **Viáticos** (+21,150) como las categorías con más exceso.
> La meta al final del programa es que el asistente conteste: *'¿Por qué la división Norte excedió su presupuesto operacional en Q3 y cuál es el riesgo de impago proyectado?'*. Cada semana agregamos una pieza: hoy, construir agentes y hacer que hablen entre ellos; después documentos (RAG), bases de datos (SQL), machine learning y, al final, cómo evaluarlos, vigilarlos y desplegarlos."

💡 La diapositiva muestra el caso, pero el grupo necesita primero entender **qué es un agente y para qué sirve en su trabajo**. Con la definición y el ejemplo del analista, las cifras dejan de ser datos sueltos y pasan a ser el tipo de respuesta que queremos.
❓ "¿Quién ha usado ChatGPT o Gemini para algo de trabajo? ¿Y quién le ha dado acceso a una base de datos real?" *(Muchos lo primero, casi nadie lo segundo: ese hueco es el curso.)*

**Diap. 3 · Agenda**
> "Son dos horas y ocho bloques: la plataforma, ADK y el entorno, el agente base, la orquestación, A2A, interfaces estrictas, qué hace un modelo cuando lo pones a trabajar, y el cierre. Las demos van dentro de los bloques. Después hay una **práctica de dos horas** con un notebook, y cada célula entrega un supervisor que delega a un especialista de presupuestos por A2A."

---
### La plataforma (0:08–0:26)

**Diap. 4 · Divisor: La plataforma**
> "Primero el mapa: qué ofrece la plataforma antes de escribir una línea de código."

**Diap. 5 · Gemini Enterprise Agent Platform**
🛠 En la consola de Google Cloud: Plataforma de agentes → Modelos → **Model Garden**; luego **Agent Runtime**, **Memory Bank** y **Sessions**. Dibuja en la pizarra: `usuario → Agent Runtime (agente ADK) → herramientas MCP / otros agentes A2A → modelos`, con Sessions y Memory Bank al lado y la gobernanza rodeándolo.
> "Piensen en un agente como **un empleado nuevo muy capaz**: tiene un **cerebro** (el modelo, por ejemplo Gemini), un **manual de puestos** (las instrucciones) y **acceso a ciertos sistemas** (las herramientas: una base de datos, una API). Lo que cambia es que este empleado no se cansa y puede atender a cientos de personas a la vez.
> La plataforma se llamaba **Vertex AI**; ahora es **Gemini Enterprise Agent Platform**. El **Model Garden** es el catálogo de modelos. El **Agent Runtime** (antes *Agent Engine*) es la 'oficina' donde vive y escala el agente desplegado *(video: arranques en frío de menos de un segundo y tareas de hasta siete días)*. **Sessions** es el cuaderno de la conversación y **Memory Bank** el archivo de lo que sabemos de cada usuario, para no preguntar lo mismo cada vez. Hay también un entorno aislado, un *sandbox*, por si el agente tiene que ejecutar código.
> Un detalle práctico: la API sigue llamándose `aiplatform.googleapis.com` y la CLI sigue siendo `gcloud`. Si vieron tutoriales con los nombres viejos, es lo mismo, renombrado."

💡 A un equipo de BI le sirve una analogía de organización (empleado, manual, sistemas) más que una lista de servicios. El aviso de nombres evita que alguien se frustre al no encontrar "Vertex AI" en la consola.
⚠️ *"¿Solo sirve en Google Cloud?"* → "El agente es código; se puede desplegar en Agent Runtime, Cloud Run, GKE o en su propia infraestructura. Lo gobernado y administrado de punta a punta es la plataforma de Google."
⚠️ *"¿Cuánto cuesta?"* → "No les voy a dar una cifra que no puedo sustentar: depende del modelo y de los tokens. En el Módulo 5 aprendemos a medirlo."

**Diap. 6 · Ciclo de vida de un agente**
> "La plataforma resuelve **cuatro problemas del ciclo de vida** de ese empleado. **Uno, construirlo:** ADK en código, **Agent Studio** si prefieren un constructor visual (se puede exportar a código ADK), y `agents-cli` para automatizar crear, evaluar y desplegar. **Dos, conectarlo:** **MCP** para herramientas externas y **A2A** para otros agentes. **Tres, desplegarlo y escalarlo:** Agent Runtime, Cloud Run o GKE. **Cuatro, gobernarlo:** lo que en una empresa serían el gafete, los permisos y la auditoría: **identidad** de cada agente, un **registro**, un **gateway** que audita, y herramientas de **evaluación y simulación** *(video)*.
> Hoy trabajamos **Construir y Conectar**. Desplegar y Gobernar son el **Módulo 5**; por eso van en lila."

💡 Presentar los cuatro problemas explica *por qué existe cada servicio* y deja sembrado el Módulo 5 desde la primera clase.

**Diap. 7 · Low-code frente a code-first**
> "Pueden armar un agente sin código en Agent Studio, y es excelente para prototipar. Pero **en este curso vamos a código**: se **versiona** en Git, se **revisa** en un pull request, se **prueba** automáticamente y se **reproduce** igual en desarrollo y producción. Treinta personas no pueden mantener un agente hecho a clics. Y no es una puerta de un solo sentido: lo visual se puede exportar a código ADK *(según tus apuntes)*."

❓ "En BI, ¿versionan sus tableros y modelos? ¿Qué pasa cuando alguien cambia algo y nadie sabe qué?" *(Conecta con code-first.)*

---
### ADK y el entorno (0:26–0:46)

**Diap. 8 · Divisor: ADK y el entorno**
> "Ahora sí, el kit con el que vamos a construir."

**Diap. 9 · Agent Development Kit (ADK)**
> "Hasta ahora hablamos de la plataforma. Ahora, **¿con qué construimos el agente?** Un agente no es solo un modelo: alrededor del modelo hay que programar muchas cosas —las instrucciones, las herramientas que puede usar, la memoria de la conversación, cómo se pasa el control a otro agente, cómo se ejecuta y se prueba—. Hacer todo eso a mano, cada vez, es lento y cada equipo lo haría distinto.
> **ADK (Agent Development Kit) es un kit de desarrollo que ya trae esas piezas resueltas.** Piensen en lo que un framework web hace por una aplicación web: ustedes escriben la lógica de su negocio y el kit se encarga de la parte repetitiva. Con ADK escriben *qué hace* el agente y él se encarga de llamar al modelo, ejecutar las herramientas, guardar la conversación y exponer el agente en consola, en una web o como servicio.
> Para qué lo usamos en este programa: **todo lo que construyamos las seis semanas —agentes con documentos, con bases de datos, con modelos de ML— se escribe con ADK**, así que es la base común del curso.
> Datos para ubicarlo: es **código abierto**, con versiones para Python, TypeScript, Java y Go; está optimizado para Gemini, pero es **agnóstico**: acepta otros modelos y se despliega donde quieran. Un agente se define **por configuración** (un archivo YAML) o **por código**. La configuración es más corta; el código da **control fino** y permite orquestar con condicionales, ciclos y funciones. Nosotros usamos código.
> Hay tres tipos de agente: los **basados en modelo**, los de **flujo de trabajo** (Sequential, Parallel, Loop) y los **personalizados**. Y lo **único obligatorio** es una variable llamada `root_agent`."

⚠️ *"¿Tenemos que usar Gemini?"* → "ADK está optimizado para Gemini, pero acepta otros modelos *(video)*. En el curso usamos Gemini por simplicidad."
💡 El grupo suele confundir "el modelo" con "el agente". Esta diapositiva debe dejar claro que el modelo es solo una pieza y que ADK es lo que arma el resto. Si quedan con una sola idea: **ADK = el kit que nos ahorra construir la infraestructura del agente**.
❓ "Si tuvieran que construir un agente desde cero sin ADK, ¿qué cosas tendrían que programar además de llamar al modelo?" *(Guardar el historial, ejecutar herramientas, validar datos, exponerlo como servicio. Eso es lo que el kit ya trae.)*

**Diap. 10 · Entorno y autenticación**
> "Antes de escribir el primer agente hay que resolver dos cosas, y por eso esta diapositiva viene ahora. **Primera: dónde vive el código** —qué se instala y cómo se organiza una carpeta de agente—. **Segunda: cómo sabe Google que somos nosotros**. El agente llama a Gemini, y Gemini es un servicio de Google Cloud que **cobra por uso y solo responde a quien tenga permiso**. Sin autenticación, el agente más bien escrito no puede ni contestar un 'hola'.
> Además, **casi todos los errores de la primera hora de la práctica vienen de aquí**: credenciales sin iniciar, proyecto equivocado, modelo que no existe. Por eso lo vemos con calma una vez, para que cuando falle algo sepan en dónde mirar."
🛠 `adk --version`, `adk create demo_agente --model gemini-2.5-flash` y `adk run demo_agente`. Abre la carpeta generada: `agent.py`, `.env`, `__init__.py`.
> "Instalar es `pip install google-adk`, con `[a2a]` para A2A. `adk create` genera la **estructura mínima**: tres archivos. `agent.py` define el agente, `.env` guarda credenciales y proyecto, `__init__.py` lo hace paquete. Todo lo demás (ejecutar en consola, abrir la web, desplegar) busca la variable `root_agent`.
> Para autenticar hay **dos caminos**: una clave de **AI Studio** en `GOOGLE_API_KEY` (rápida, para pruebas) o **credenciales de Google Cloud**, que es la que usamos: `gcloud auth application-default login`, con `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`, el **ID** del proyecto y la región. Elegimos Google Cloud porque es lo que usaría su empresa: el consumo queda en **un proyecto con permisos y facturación controlados**, no en una clave personal. Esa variable antes se llamaba `GOOGLE_GENAI_USE_VERTEXAI`; si un tutorial usa la vieja, es por eso.
> **El `.env` jamás se sube a Git.** Y el modelo va con **versión concreta**, `gemini-2.5-flash`: el alias `gemini-flash-latest` dio error 404 en nuestro proyecto, y un alias puede cambiar de modelo sin avisar."

💡 Que el alumno *vea* los tres archivos desmitifica "el agente": es un programa pequeño de Python. La autenticación se explica con su motivo (cobro y permisos) para que no parezca burocracia previa. La regla del `.env` previene el error de seguridad más común. La versión concreta hace comparables las evaluaciones del Módulo 5.
❓ "¿Por qué creen que ADK pide un nombre fijo, `root_agent`, en vez de buscar 'el primer agente que encuentre'?" *(Una convención permite que CLI, web y despliegue funcionen sin configuración y evita ambigüedad con varios agentes.)*
⚠️ *"¿Por qué `gemini-2.5-flash`?"* → "Es rápido y económico, y **probado en nuestro proyecto**."
⚠️ *"¿Por qué no usamos solo una clave de AI Studio, que es más fácil?"* → "Sirve para probar, pero la clave es personal y el consumo no queda bajo el control del proyecto. Para trabajo de empresa se usan credenciales de Google Cloud."

---
### El agente base en código (0:46–1:08)

**Diap. 11 · Divisor: El agente base**
> "Veamos qué hay dentro de un agente y por qué cada pieza importa."

**Diap. 12 · Anatomía de un agente**
🛠 Abre `src/finanzas_agents/agent.py`.
> "Un agente tiene cuatro piezas: **modelo, descripción, instrucción y herramientas**, más un nombre. El **nombre** es su identidad: el supervisor lo usa para delegar. Es un programa pequeño de Python; no hay magia."

**Diap. 13 · `description` frente a `instruction`**
> "Esta diferencia es sutil y **es la que más fallos causa**. La **`description`** es *qué es* el agente: su cargo en el directorio de la empresa, 'Flujo de caja, liquidez y pagos'. **La leen los otros agentes** para decidir si le delegan una tarea. La **`instruction`** es *cómo debe lograr su objetivo*: su manual de procedimientos, 'no inventes cifras'. **La lee el propio modelo.**
> Si la descripción es vaga, el supervisor nunca delega o delega mal. Si la instrucción es vaga, el agente improvisa."

💡 El binomio *description/instruction* previene buena parte de los fallos de los labs.

**Diap. 14 · Herramientas tipadas**
🛠 Abre `src/finanzas_agents/tools.py`.
> "Una herramienta es una **función de Python normal**, pero el modelo **no ve su código**: solo ve el **nombre, los tipos y el docstring**. Por eso el docstring no es adorno: es lo que lee para decidir cuándo usarla y con qué argumentos. Una herramienta sin docstring se usa con argumentos inventados.
> Los errores se devuelven **como dato**, `status: error`, no como excepción, para que el modelo los lea y corrija. Y la idea de diseño más importante del curso: **el modelo decide *cuándo* llamar la herramienta; el sistema decide *qué número* devuelve.** Las cifras vienen de la base de datos, no de la 'memoria' del modelo. Un número inventado en finanzas no es un error de redacción, es un riesgo."

> "**¿Y dónde entra Pydantic?** Dentro de la herramienta, en su **primera línea**. Mira el orden: el modelo llama a `consultar_presupuesto(division, trimestre)` con textos sueltos; lo primero que hace la función es **armar un `BudgetRequest`** (el contrato de Pydantic), y ahí se valida. Si la división no existe o el trimestre viene mal escrito, Pydantic lanza el error, la herramienta lo atrapa y lo devuelve como `status: error`. Solo si pasa la validación se consulta la base. O sea: **Pydantic es el filtro de entrada de la herramienta**; en la siguiente diapositiva lo vemos en detalle."
> *(Mapa para decirlo rápido: modelo → herramienta → **contrato Pydantic valida** → base de datos → respuesta. Pydantic queda entre la herramienta y los datos.)*

❓ "Si el modelo nunca ve el código de la herramienta, ¿qué parte del diseño es su interfaz con el modelo?" *(Nombre, tipos y docstring.)*
⚠️ *"¿Y si el modelo llama la herramienta con un argumento equivocado?"* → "Por eso los tipos y el contrato: la herramienta devuelve un **error estructurado**, el modelo lo lee y puede corregir."
⚠️ *"¿Y si inventa números en su respuesta final?"* → "Es un riesgo real y no se elimina con el prompt. Se **mide** con Faithfulness (Módulo 5) y se **bloquea el despliegue** si baja. No prometo que no ocurra: prometo que lo detectamos."

**Diap. 15 · Contratos con Pydantic**
🛠 `python -c "from finanzas_agents.contracts import BudgetRequest as B; B(division='Marte', trimestre='2026-Q3')"` *(Error: `Input should be 'Norte', 'Sur', 'Centro' or 'Occidente'`.)*
> "Pedí la división 'Marte' y **falló antes de llegar al modelo**. Eso es un **contrato**: una validación en código que dice qué es aceptable. ¿Por qué no decirle al modelo 'valida la entrada'? Porque a un modelo se le puede *convencer*, se puede *equivocar* y su respuesta *varía*. El código no. **Lo que se puede validar con código, se valida con código.**
> Además, el contrato normaliza: el modelo escribirá 'Tecnología' o 'viáticos', y la base guarda 'Tecnologia'. **El modelo propone, el código decide.**"

💡 Mostrar el rechazo de "Marte" convierte "validación" en algo tangible.

**Diap. 16 · Formas de ejecutar un agente**
🛠 `. .\env.ps1` y `adk web --port 8501 modulo1_adk_a2a/src` (abre http://127.0.0.1:8501). Elige `finanzas_agents` y pregunta *"¿Cómo va la división Norte en 2026-Q3?"*. Muestra la pestaña **Events** y el grafo (cómo leerlos: `SESION_PRACTICA.md`, sección *Cómo probar y leer `adk web`*).
> "Hay **cuatro formas** de ejecutar un agente: `adk run` en la consola; `adk web`, una interfaz de desarrollo; `adk api_server`, que lo expone como API; y **por código** con `Runner`. `adk web` es **solo para desarrollo**, nunca para producción.
> Miren **Events**: aparece cada paso: la pregunta, la llamada a la herramienta, el resultado, la respuesta. Va a ser su mejor amigo para depurar: cuando un agente haga algo raro, **no adivinen: lean los eventos.**"

💡 Enseñar los eventos desde temprano crea el hábito de depurar con evidencia.

**Diap. 17 · Eventos, sesión y estado**
🛠 En la misma sesión pregunta *"¿Y en 2026-Q2?"* (no pide la división). Luego pulsa **New Session** y repite la pregunta. Si quieres, muestra `run_programmatic.py` (solo leerlo).
> "Un **evento** es cada cosa que ocurre. Una **sesión** es una conversación: la misma `session_id` la continúa; una nueva empieza sin memoria.
> Y la idea que más confunde: **el modelo no tiene memoria.** Cada vez que se le llama, se le **reenvía el historial**; quien lo guarda es el **servicio de sesiones**. En `adk web` y `adk run`, ADK lo crea por nosotros; cuando llamamos al agente **por código**, hay que darle un **servicio de sesiones**, un **servicio de artefactos** (salidas que otros agentes pueden recuperar) y un **Runner**, que toma la pregunta, invoca al agente y va emitiendo eventos de forma asíncrona. En local la sesión vive en memoria y se pierde al reiniciar; en producción, el servicio de Sessions de la plataforma. La memoria de **largo plazo** es otra cosa: el Memory Bank. Y con `output_key`, la respuesta de un agente queda en el estado para el siguiente."

💡 El error conceptual número uno es creer que "el agente se acuerda". Decir *el modelo no tiene memoria* y mostrar quién la tiene evita un mes de confusión.
❓ "Si abro otra ventana con otra sesión y pregunto '¿y en Q2?', ¿qué pasa?" *(Pide la división: otra sesión = otra conversación. Muéstralo.)*
❓ "¿Dónde viven las cifras del presupuesto: en el prompt o en la base de datos?" *(En la base de datos; la herramienta las trae.)*

---
### Orquestación multiagente (1:08–1:23)

**Diap. 18 · Divisor: Orquestación multiagente**
> "Ya sabemos hacer un agente. Ahora, varios que colaboran."

**Diap. 19 · Supervisor y especialistas**
🛠 En `adk web`, abre el grafo del agente `finanzas_agents`.
> "Podríamos darle **todas** las herramientas a un solo agente gigante. No lo hacemos, por cuatro razones: con diez herramientas **se confunde más**; cada especialista tiene un **prompt corto y claro**; podemos **probar cada uno por separado**; y cada uno puede tener **solo los permisos que necesita** (lo vemos en el Módulo 5). Es el principio de un equipo humano: un gerente que enruta y especialistas que ejecutan.
> Miren el árbol: `root_agent` es el **supervisor**, con dos especialistas: **Presupuestos**, que tiene una herramienta, y **Tesorería**, que no tiene herramientas ni datos. Cada uno tiene su propia `description`."

⚠️ *"¿Y si el supervisor elige al especialista equivocado?"* → "Ocurre, sobre todo con descripciones ambiguas. Se corrige afinando las `description` y se **mide** con la 'precisión de ruta' en el Módulo 5."
⚠️ *"¿Por qué no solo un `if` en Python en vez de un supervisor?"* → "Para **dos** especialistas con reglas claras, un `if` o un workflow es mejor. El supervisor con LLM vale cuando las preguntas son **abiertas** y no se pueden enumerar las reglas."

**Diap. 20 · El supervisor en código**
🛠 Abre `src/finanzas_agents/agent.py` y baja a `root_agent` (líneas 47–59). Señala `sub_agents=[presupuestos_agent, tesoreria_agent]`.
> "Así se crea el supervisor. Es **otro `Agent` igual que los demás**, con su `name`, `model`, `description` e `instruction`; la diferencia está en una línea: **`sub_agents=[presupuestos_agent, tesoreria_agent]`**. Esa lista es la que lo convierte en supervisor. No hay ningún `if` ni código de enrutamiento: la `instruction` le dice cómo repartir ('presupuesto → especialista_presupuestos, liquidez → especialista_tesoreria') y ADK le da la capacidad de transferir. Fíjense también en el orden del archivo: **primero se definen los especialistas y al final el supervisor**, porque necesita tenerlos ya creados para recibirlos en la lista. Y `root_agent` es el nombre que ya vimos que ADK busca."
> *(Mapa: `presupuestos_agent` y `tesoreria_agent` se crean arriba → entran en `sub_agents` → `root_agent` es el supervisor.)*

**Diap. 21 · Cómo delega el supervisor**
🛠 Ahora en `adk web`: *"¿Cuál es la posición de liquidez?"* y luego, en la misma sesión, *"¿y el presupuesto de Norte en 2026-Q3?"*. Señala el evento `transfer_to_agent` y el cambio de agente.
> "El supervisor **no calcula presupuestos**. El modelo lee las **descripciones** de sus sub-agentes y llama a una función especial, **`transfer_to_agent`**: ese evento es la **delegación**. Un especialista puede devolver el control o redirigir: vean cómo **Tesorería transfiere a Presupuestos**. Se llama *hand-off jerárquico*.
> Tres cosas prácticas. **Un agente solo puede tener un padre**: si quieren reutilizar un especialista bajo otro supervisor, ADK da error y la solución es `clone()`, una copia sin padre (un empleado no puede reportar a dos jefes directos). **Delegar cuesta**: cada salto es otra llamada al modelo, con más latencia y más tokens. Y fíjense que **Tesorería no inventó cifras**: no tiene datos y su instrucción se lo prohíbe."

💡 Mencionar `clone()` ahora ahorra un error que **sí** les va a salir en el lab.
⚠️ En una sesión larga, la pregunta de liquidez puede llegar primero al último agente que respondió (Presupuestos) y de ahí transferirse a Tesorería; en una sesión nueva el primer paso es supervisor → Tesorería.

**Diap. 22 · Agentes de flujo**
🛠 Opcional (solo leerlo): `workflows.py`.
> "Hasta ahora el **modelo decide** a quién delegar. Pero a veces **el orden ya lo conocemos**: primero consulta el presupuesto, *luego* redacta el resumen. Para eso están los agentes de **flujo**: **Sequential** (uno tras otro), **Parallel** (a la vez) y **Loop** (repetir hasta una condición o `max_iterations`). No usan un LLM para decidir el orden —es **código determinista**—, así que son más **baratos, rápidos y predecibles**. Se pasan información con `output_key`: la respuesta de un agente se guarda en el estado con ese nombre y el siguiente la lee con `{nombre}` en su instrucción.
> **Regla práctica:** si el orden depende de la pregunta, que decida el modelo; si es fijo, un flujo. Y un aviso honesto: en ADK 2.x estas tres clases están marcadas como obsoletas a favor de `Workflow`. Todavía funcionan y el vocabulario es el mismo, por eso las enseñamos."


**Diap. 23 · Agentes de flujo en código**
🛠 Abre `src/finanzas_agents/workflows.py` (opcional: solo léelo en pantalla; no lo ejecutes, usa Gemini).
> "Así quedan los tres en código. Fíjense que **definir los agentes no cambia**: siguen siendo `Agent` con su `instruction`. Lo único que cambia es **la clase que los envuelve**.
> **Secuencial:** `analista` guarda su respuesta con `output_key="analisis_presupuesto"`; `redactor` la lee escribiendo `{analisis_presupuesto}` en su instrucción. Esa es la forma de pasarse información: **a través del estado de la sesión**. `SequentialAgent(sub_agents=[analista, redactor])` fija el orden.
> **Paralelo:** `ParallelAgent` con dos analistas, cada uno con **su propia clave de salida** (para que no se pisen). **Bucle:** `LoopAgent` repite al `revisor` hasta tres veces; no usa modelo propio, solo repite.
> En los tres, **el orden lo decide el código**, no un LLM. Y como ya dije, estas clases están marcadas como obsoletas en ADK 2.x a favor de `Workflow`: si buscan en la documentación, verán ese nombre."

💡 Que el grupo vea que `{analisis_presupuesto}` en una instrucción es la misma palabra que `output_key` en el otro agente les ahorra la duda más común de la Parte 6 del notebook.
⚠️ *"¿Por qué los dos analistas paralelos tienen claves distintas?"* → "Si usaran la misma, el segundo sobrescribiría al primero. Cada rama escribe en su propia clave."

---
### A2A (1:23–1:40)

**Diap. 24 · Divisor: A2A**
> "Hasta aquí, los agentes vivían en el mismo programa. ¿Y si no?"

**Diap. 25 · ¿Qué es A2A?**
> "¿Qué pasa si el especialista de **riesgos** lo construye **otro equipo**, en otro lenguaje o en otra nube? Ahí entra **A2A, Agent2Agent**: un protocolo abierto para que agentes se comuniquen **sin saber cómo están hechos por dentro**. **A2A es a los agentes lo que una API es a los sistemas**: no les importa si al otro lado hay Python, Java o Go; les importa el **contrato**.
> No es lo mismo que MCP: **MCP conecta un agente con herramientas y datos; A2A, un agente con otros agentes.** Se complementan. En ADK, `to_a2a(agente)` lo expone y `RemoteA2aAgent` lo consume; **esta última pieza es experimental** y puede cambiar. Agentes hechos con otros marcos —LangGraph, CrewAI, AG2— pueden colaborar con uno de ADK *(video)*."

⚠️ *"¿Está estable?"* → "El protocolo A2A sí; **la implementación de ADK para consumir agentes remotos está marcada como experimental**. Por eso la verificamos y la anotamos."
⚠️ *"¿Qué es MCP entonces?"* → "MCP conecta un agente con **herramientas y datos**; A2A conecta un agente con **otros agentes**."

**Diap. 26 · Agent card y flujo de A2A**
🛠 Primero, sin red: muestra `a2a_local.py`. Después: Terminal 1 `uvicorn finanzas_agents.a2a_server:a2a_app --port 8001`; Terminal 2 `(Invoke-WebRequest http://localhost:8001/.well-known/agent-card.json -UseBasicParsing).Content` (debe verse `name: especialista_presupuestos`; en PowerShell `curl` es un alias distinto). Opcional: en `adk web`, `supervisor_remoto_app` con la misma pregunta (el servidor debe estar en el **8001** y `adk web` en otro puerto, p. ej. 8501; si el 8001 lo ocupa otro proceso, el agente se queda mudo).
> "Primero, **cómo se conecta**, que son dos líneas de código, una por cada lado. Abran `a2a_server.py`. **Lado servidor:** `to_a2a(presupuestos_agent, port=8001)` toma un agente normal y lo publica como servicio, con su agent card. **Lado cliente:** `RemoteA2aAgent(..., agent_card="http://localhost:8001/.well-known/agent-card.json")` es un agente que **por dentro llama a esa URL**; el supervisor lo recibe en `sub_agents` igual que a un especialista local. Lo único que el cliente necesita saber del otro lado es **esa dirección**.
> "Ahora, qué pasa por debajo, en tres pasos. **Uno, descubrir:** el cliente pide la **agent card** con un `GET` a una dirección estándar, `/.well-known/agent-card.json`. Es una tarjeta de presentación en JSON: dice quién es el agente, qué sabe hacer, dónde está y **si exige autenticación**. A este primer intercambio se le suele llamar *handshake*, aunque en el protocolo no es un comando: es pedir la tarjeta.
> **Dos, enviar:** el cliente manda un **mensaje**. En A2A un mensaje (`Message`) tiene un identificador, un rol (usuario o agente) y su contenido en partes (`Part`: texto, datos, archivos). El agente puede responder **de inmediato con otro mensaje**, o, si el trabajo es largo, abrir una **tarea** (`Task`) con identificador y estados (por ejemplo `working`, `input-required`, `completed`).
> **Tres, continuar:** la primera vez, el **servidor** crea un **`contextId`**, que agrupa los mensajes y las tareas de una misma conversación. Para un seguimiento, el cliente **reenvía ese `contextId`**. Una tarea terminada no se reabre: el seguimiento es una **tarea nueva dentro del mismo contexto**. Eso es lo que hace nuestra pregunta '¿y en Q2?': misma conversación, trabajo nuevo, y por eso la delegación **conserva el estado**. En ADK, `RemoteA2aAgent` guarda ese `contextId` y lo reenvía por ustedes; nosotros no lo escribimos.
> Una aclaración para no confundirse: lo que vieron primero en `a2a_local.py` es una **maqueta con nombres propios**. Nuestro `A2AEnvelope` hace de mensaje y nuestro `handshake()` hace de 'pedir la tarjeta'; **esos nombres no existen en A2A real** (ahí son `Message` y la agent card). Sirven para ver el concepto sin red. Lo real es lo que corre en el puerto 8001."

⚠️ *"¿El identificador de sesión es lo que viaja por A2A?"* → "No. Nuestro `session_id` es de ADK y vive en el supervisor. Por A2A viaja un `contextId` que **genera el servidor**; ADK lo recuerda dentro de la sesión del supervisor. Lo comprobamos por resultado (la misma sesión recuerda Norte; una nueva pide la división). En los mensajes del servidor se ve que su sesión interna usa ese mismo `contextId`, pero no probamos reenviándolo a mano."
⚠️ *"¿Nuestro especialista responde con un `Message` o con una `Task`?"* → "Con una **`Task`**. Lo comprobamos mirando lo que sale del servidor del 8001: la tarea pasa por `submitted`, `working` (ahí van la llamada a la herramienta y su resultado) y `completed`, y la respuesta final llega como **artefacto**. Fue una sola pregunta con ADK 2.12.0." *(Detalle en `SESION_PRACTICA.md`, 5.3b.)*
⚠️ *"En `adk web` veo la respuesta dos veces, una en gris que dice THOUGHT. ¿Por qué?"* → "Porque es una `Task`. El texto viaja primero dentro del estado `working`, que ADK pinta en gris como *thought*, y luego otra vez como artefacto final. No es un error de nuestro proyecto." *(Observado con ADK 2.12.0; ver `SESION_PRACTICA.md`, 5.3b.)*

💡 Hacer primero la versión **sin red** deja claro el protocolo antes de que la red agregue ruido; luego la agent card real hace tangible la idea: es un JSON en una URL. Decir siempre qué es maqueta y qué es real evita que busquen `handshake()` o `A2AEnvelope` en la documentación de ADK.

**Diap. 27 · Sub-agente frente a A2A**
> "Un sub-agente vive en el mismo proceso; un agente remoto es otro servicio. A2A da independencia: despliegue propio, otro equipo, solo comparten el contrato. Pero cuesta **latencia y complejidad**. **Empiecen con sub-agentes y pasen a A2A cuando haya una razón organizacional o de escala.**
> **Una aclaración importante: tener la URL no basta.** Para que la conexión funcione hacen falta tres cosas. **Uno:** que del otro lado haya **un agente que hable A2A** y publique su agent card; una API cualquiera o una página web no sirve. **Dos:** que tengan **permiso**: la agent card dice si exige autenticación, y sin credenciales conocen la URL y aun así los rechaza. **Tres:** que **se entiendan en lo que piden**: A2A garantiza que se pueden *hablar*, no que el otro agente sepa hacer lo que necesitan; para eso es la agent card y para eso insistimos en los contratos. Resumen: **A2A resuelve el 'cómo se hablan', no el 'qué se dicen' ni el 'quién tiene permiso'.**
> El protocolo contempla estos casos: una tarea puede quedar en **`input-required`** (el agente necesita más datos) o en **`auth-required`** (hace falta autenticarse). Nosotros no probamos la autenticación, porque nuestro servidor local no la pide.
> Y una precaución: si el servidor remoto está caído, el agente puede **no avisar**. Lo observamos en pruebas con un modelo simulado que ya no está en el proyecto, así que pruébenlo en su entorno."

💡 La tabla evita que los alumnos conviertan A2A en la solución para todo. Las tres condiciones evitan la idea de que 'conectar' es solo pegar una URL.
❓ "Si tuvieran que ofrecer su agente de riesgos a *otra* área sin darles el código, ¿qué tendrían que publicar?" *(La agent card y un contrato estable.)*

**Diap. 28 · Patrón: orquestador financiero**
> "Los patrones que usaremos: **Supervisor / Router-Worker** —un Orquestador Financiero que delega sub-tareas a especialistas— y **hand-off jerárquico**, donde el control se **transfiere** entre agentes según el dominio de la consulta. En la práctica construimos **Presupuestos**, local y por A2A, y **Tesorería**, local; y en el **reto opcional 5.4** los dos especialistas van por A2A y el supervisor enruta entre ellos. **Cuentas por Cobrar y Riesgos** son la extensión: por eso van punteados."

> Para ubicar qué se practica y dónde: **Supervisor / Router-Worker** y **hand-off** funcionan con `sub_agents` y `transfer_to_agent`, tanto con especialistas **locales** (Parte 3 y Parte 7) como **remotos** por A2A (5.2 y el reto 5.4). Una diferencia que conviene decir: en local, un especialista puede **transferir directo** a otro (Tesorería a Presupuestos, sin pasar por el supervisor); por A2A, un especialista remoto es una **caja negra** que no ve el árbol del supervisor, así que **el supervisor es quien enruta** en cada pregunta. Eso lo observamos en dos corridas; no probamos un hand-off entre dos remotos sin supervisor.

💡 Esta diapositiva responde a dos puntos del cronograma a la vez (Router-Worker y hand-off). Decir qué parte es local y cuál va por A2A evita prometer más de lo que se practicó.
⚠️ *"¿Y Cuentas por Cobrar y Riesgos?"* → "Son la extensión del patrón: se agregan como un especialista más (otra `description`, otras herramientas, otro puerto si va por A2A). En esta sesión no se construyen."
⚠️ *"¿Es seguro? ¿Cualquiera puede llamar a mi agente?"* → "Por defecto, **no asuman que sí**. Autenticación y permisos se configuran; en el Módulo 5 vemos identidad del agente, IAM y el gateway. No expongan este servidor de clase fuera de su máquina."

---
### Interfaces estrictas (1:40–1:45)

**Diap. 29 · Interfaces estrictas**
🛠 `python -c "from finanzas_agents.contracts import BudgetRequest as B; import json; print(json.dumps(B.model_json_schema(), indent=2))"`. Solo mostrar; no hay práctica de esto.
> "El contrato que vimos se expresa de varias formas, según quién lo lea: **Pydantic y los type hints** validan dentro del código; **JSON Schema** describe la forma de un mensaje sin depender del lenguaje; **OpenAPI** describe una API REST completa, con rutas, entradas y salidas; y la **agent card** es el contrato de un agente A2A. Hoy no escribimos un OpenAPI: es concepto.
> La regla: **entre agentes se intercambian datos estructurados, no texto libre.** Si un agente le pasa a otro un párrafo, el segundo tiene que 'interpretarlo' y ahí vuelven los errores."

💡 Une lo que ya vieron (herramientas, contratos y agent card) en una sola idea. Es un bloque corto a propósito.
❓ "En BI, ¿qué contrato tiene hoy un tablero con la fuente de datos que lo alimenta?" *(Un esquema, una vista o un nombre de columna: es la misma idea.)*
⚠️ *"¿Vamos a escribir un OpenAPI?"* → "En esta práctica no; lo que sí verán es el JSON Schema que Pydantic genera solo."

---
### Qué hace un LLM cuando lo pones a trabajar (1:45–1:52)

**Diap. 30 · Qué hace un LLM cuando lo pones a trabajar**
Todos los ejemplos salen de las pruebas con Gemini en este proyecto.
> "Seis cosas que vimos pasar de verdad, para que no los sorprendan. **Uno:** no es determinista; una corrida no demuestra que siempre salga igual. **Dos:** puede alterar cifras: en una corrida escribió **304,000,000** donde la herramienta devolvió **304000**, y el error pasó al agente siguiente; por eso en la práctica pedimos 'copia las cifras tal cual'. **Tres:** el formato de los números cambia (380900, 380,900, 380.900): validen la **cifra**, no la redacción. **Cuatro:** una instrucción ambigua se interpreta de más de una forma. **Cinco:** sin herramientas, inventa; por eso Tesorería tiene una instrucción que le prohíbe dar cifras. **Seis:** los fallos pueden ser silenciosos si un agente remoto no responde.
> Nada de esto se arregla escribiendo mejor el prompt: se **mide** y se **vigila**. Eso es el Módulo 5."

💡 Inmuniza al grupo contra la idea de que "el agente ya sabe lo que hace" y deja sembrada la evaluación sin explicarla todavía.
❓ "Si el modelo escribió 304,000,000 en lugar de 304,000, ¿qué parte del sistema debería haberlo detectado?" *(Una validación en código sobre la cifra, no el propio modelo.)*
⚠️ *"¿Qué tan seguido pasa lo del ×1000?"* → "No lo sé: lo vimos **una vez** y no lo medimos. Por eso es un ejemplo de por qué hay que medir, no una estadística."
⚠️ *"¿La falla silenciosa con A2A es segura?"* → "Se observó con un modelo simulado que ya no está en el proyecto; preséntenlo como **precaución** y pruébenlo en su entorno."

---
### Cierre (1:52–2:00)

**Diap. 31 · Lo que debe quedarse**
> "Si se llevan **cuatro ideas** de hoy: **uno**, la `description` dice qué es el agente, y si es vaga el sistema falla. **Dos**, el modelo no tiene memoria: **el estado vive en la sesión**. **Tres**, A2A es un **contrato** entre agentes, no una llamada a función. **Cuatro**, **el modelo propone y el código decide**: el modelo decide cuándo, el sistema decide qué número."

💡 Repetir cuatro ideas al cierre mejora la retención.

**Diap. 32 · Proyecto base y siguiente paso**
> "Tienen un proyecto base en `src/finanzas_agents`: supervisor, Presupuestos y Tesorería, con pruebas y README. Ahora abran el notebook de práctica y ejecuten la **Parte 0**. En la práctica de dos horas hacemos herramienta, contratos, agentes, flujos, A2A y estado. **El entregable de cada célula** es un supervisor que delega a un especialista de presupuestos por A2A y mantiene el estado. La evaluación usa la rúbrica que les envié: funciona de extremo a extremo, calidad de código, seguridad, pruebas y documentación. El **Módulo 2** es RAG con reranking."

💡 Dejar la Parte 0 hecha evita perder los primeros 20 minutos de la práctica en problemas de entorno.

**Diap. 33 · Preguntas y respuestas**
> "¿Preguntas?" Si te quedas en blanco, usa las frases de rescate de la sección 6.

---
## 6. Frases de rescate y orden de recortes
**Frases de rescate (si te quedas en blanco o se alarga el tiempo)**
- "Eso lo vemos en la semana 5; por ahora quédense con la idea de que *se puede medir*."
- "Buena pregunta: no lo voy a inventar. Lo verifico y lo respondo en el chat."
- "Veámoslo en el Trace, que ahí está la evidencia."
- "Para el agente, la descripción es todo; para nosotros, el contrato es todo."

**Si vas corto de tiempo, recorta en este orden**
1. Workflows y agentes de flujo (diap. 22 y 23; déjalo al notebook, Parte 6).
2. Demo de `adk create` (muestra solo la estructura).
3. El detalle de Agent Runtime y la gobernanza (diap. 6; menciona solo "ahí se despliega" y lo retomas en M5).
**Nunca recortes:** `description` vs `instruction`, estado en sesión, ni la demo de la agent card.

---

## 7. Errores comunes y preguntas de repaso
**Errores que verás en las células:**
- `description` vaga → el supervisor nunca delega o delega mal.
- Herramienta sin docstring → el modelo la usa con argumentos inventados.
- Estado guardado en variables globales en lugar de la sesión.
- Confundir sub-agente (mismo proceso) con A2A (red).
- Reutilizar un agente en dos supervisores → `already has a parent agent` (solución: `clone()`).
- Dar por buena la cifra que redacta el modelo sin compararla con la de la herramienta.

**Preguntas de repaso (cierre o evaluación rápida):**
1. ¿Qué diferencia hay entre `description` e `instruction`?
2. ¿Dónde se guarda la memoria de corto plazo de una conversación? ¿Y la de largo plazo?
3. ¿Cuándo usarías `sub_agents` y cuándo A2A?
4. ¿Por qué un contrato Pydantic es mejor que pedirle al LLM "valida la entrada"?
5. ¿Qué hace `output_key` y para qué sirve un `LoopAgent` sin modelo?

## 8. Lo que no está probado (sé transparente con el grupo)
- Estabilidad: el notebook del instructor se ejecutó **una vez** con Gemini sin errores y con los 5 ✅; una corrida no garantiza que siempre salga igual (el modelo es no determinista).
- Despliegue a Agent Runtime.
- Calidad del enrutamiento con descripciones ambiguas (hazlo como demo con Gemini: es buena discusión).
- `RemoteA2aAgent` (API experimental): probado con Gemini en una corrida (delegación y seguimiento con estado por A2A), pero puede cambiar en versiones nuevas de ADK. El mecanismo por el que viaja el estado no está determinado.

---
## 9. Mapa del proyecto y cómo crear tu propio agente

Esta sección responde dos preguntas que los alumnos harán: **¿por qué existen estos archivos?** y **¿cómo hago yo uno propio?** Los fragmentos de código de esta sección se comprobaron localmente (el agente se construye, la herramienta responde y `adk` lo descubre); **no se ejecutó una llamada a Gemini con ellos**.

### 9.1 Qué es cada archivo y si lo necesitas
**Dentro de `src/finanzas_agents/`:**
| Archivo | Para qué sirve | ¿Obligatorio en un agente propio? |
|---|---|---|
| `agent.py` | Define los agentes: el supervisor (`root_agent`) con los especialistas de **Presupuestos** y **Tesorería**. ADK busca la variable **`root_agent`** | **Sí** |
| `README.md` | Mapa de archivos del proyecto, cómo ejecutarlo y cómo ampliarlo (es lo que se llevan los alumnos) | Recomendado |
| `tools.py` | Funciones que el agente puede llamar (tipadas y con docstring) | **Sí, si el agente usa herramientas** (puede ir dentro de `agent.py`) |
| `contracts.py` | Modelos Pydantic que validan los datos antes de tocar la base | Recomendado, no obligatorio |
| `eventos.py` | Helper `preguntar` / `estado`: ejecuta un agente e imprime 🔧📥🤖 | **No**: es una comodidad nuestra. ADK ya trae `adk run`, `adk web` y `Runner` |
| `a2a_server.py` | Expone un agente por A2A con `to_a2a(...)` | Solo si otros deben llamarlo por red |
| `a2a_local.py` | Simulación didáctica del protocolo A2A, sin red | No: es solo para entenderlo |
| `workflows.py` | Ejemplos de `SequentialAgent`, `ParallelAgent`, `LoopAgent` y `output_key` | No (demo) |
| `run_programmatic.py` | Ejemplo de ejecutar un agente por código con `Runner` | No (demo) |
| `__init__.py` | Marca la carpeta como paquete de Python | Sí (puede estar vacío) |
| `supervisor_remoto_app/` | Paquete para `adk web` que carga el supervisor remoto (`adk web` solo descubre `root_agent`) | No |

**Fuera de `src`:** `shared/config.py` (rutas y `MODEL_NAME`: el modelo se define ahí y en el `.env`; los agentes lo leen directamente), `data/finanzas.db` (datos sintéticos) y `.env` (proyecto y credenciales).

**🎤 Dices:** "Para que un agente funcione solo necesitan **dos cosas**: un `agent.py` con un `root_agent` y, si va a consultar algo, una herramienta. Todo lo demás que ven en `src` es **ayuda para la clase**: validar mejor, imprimir los eventos bonito, probar sin gastar tokens, o demostrar A2A. Cuando hagan el suyo, empiecen con lo mínimo y vayan agregando."

### 9.2 Por qué el notebook importa desde `src` (`sys.path`)
Python solo importa de **paquetes instalados** o de **carpetas incluidas en `sys.path`**. El notebook vive en `modulo1_adk_a2a/notebooks/` y el código reutilizable en otra carpeta, así que la **Parte 0** agrega dos rutas: la **raíz del proyecto** (para `shared.config`) y **`modulo1_adk_a2a/src`** (para `finanzas_agents`). Sin eso aparece `ModuleNotFoundError`. (La alternativa profesional es empaquetar el proyecto con `pyproject.toml` e instalarlo con `pip install -e .`; aquí se evita para no sumar otra herramienta a la clase.)

### 9.3 Plantilla mínima de un agente propio
`adk create mi_agente` genera esta estructura (también puedes crearla a mano):
```
mi_agente/
  __init__.py      # vacío
  agent.py         # define root_agent (lo único obligatorio)
  .env             # proyecto y credenciales
```
`agent.py` completo, con herramienta tipada, docstring y error como dato:
```python
from google.adk.agents import Agent


def consultar_inventario(producto: str) -> dict:
    """Devuelve las existencias de un producto.

    Args:
        producto: nombre del producto, por ejemplo 'laptop'.
    """
    datos = {"laptop": 12, "monitor": 30}
    if producto not in datos:
        return {"status": "error", "message": f"Producto '{producto}' no existe. Válidos: {list(datos)}"}
    return {"status": "ok", "producto": producto, "existencias": datos[producto]}


root_agent = Agent(
    name="asistente_inventario",                      # sin espacios
    model="gemini-2.5-flash",
    description="Responde cuántas existencias hay de un producto.",
    instruction="Usa SIEMPRE consultar_inventario; nunca inventes cifras. Si falta el producto, pídelo.",
    tools=[consultar_inventario],
)
```
`.env` (modo enterprise):
```
GOOGLE_GENAI_USE_ENTERPRISE=TRUE
GOOGLE_CLOUD_PROJECT=<ID de tu proyecto>
GOOGLE_CLOUD_LOCATION=us-central1
```
Para ejecutarlo: `adk run mi_agente` (consola) o `adk web --port 8501 <carpeta que CONTIENE a mi_agente>`.

### 9.4 Qué hace `preguntar`, en ~15 líneas (para que no sea una caja negra)
`eventos.py` no tiene magia: es el `Runner` de ADK con un poco de impresión. La versión mínima, sin los 🔧📥, es:
```python
from google.adk.runners import InMemoryRunner
from google.genai import types
from mi_agente.agent import root_agent

runner = InMemoryRunner(agent=root_agent, app_name="mi_app")


async def preguntar(texto, session_id="s1", user_id="yo"):
    if not await runner.session_service.get_session(app_name="mi_app", user_id=user_id, session_id=session_id):
        await runner.session_service.create_session(app_name="mi_app", user_id=user_id, session_id=session_id)
    mensaje = types.Content(role="user", parts=[types.Part(text=texto)])
    async for evento in runner.run_async(user_id=user_id, session_id=session_id, new_message=mensaje):
        if evento.is_final_response() and evento.content and evento.content.parts:
            print(evento.content.parts[0].text)
```
Qué hace cada pieza: el **Runner** ejecuta el agente; el **servicio de sesiones** guarda la conversación (por eso `session_id` importa); y cada acción (llamar una herramienta, transferir, responder) llega como un **evento**. `eventos.py` solo agrega los `print` de 🔧 y 📥 para verlos.

### 9.5 Exponer tu agente por A2A (si otros deben usarlo)
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
a2a_app = to_a2a(root_agent, port=8001)      # servir con: uvicorn mi_modulo:a2a_app --port 8001
```
y quien lo consuma:
```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
remoto = RemoteA2aAgent(name="asistente_inventario", description="Inventario por A2A",
                        agent_card="http://localhost:8001/.well-known/agent-card.json")
```
(Recuerda: `RemoteA2aAgent` es experimental en ADK 2.x.)

### 9.6 Orden recomendado para construir uno propio
1. **La herramienta sola**, probada como función normal (sin modelo). Si falla aquí, el agente nunca funcionará.
2. **El agente con esa herramienta** y `adk web` para ver el rastro de eventos.
3. **El contrato** (Pydantic) cuando empieces a ver datos mal formados.
4. **Un segundo agente y un supervisor**, con `description` claras (y `clone()` si reutilizas uno).
5. **A2A** solo cuando haya una razón organizacional o de escala.

**🎤 Dices (cierre):** "Todo lo que hicimos hoy cabe en un `agent.py` de 20 líneas. Lo demás —los contratos, el helper de eventos, el servidor A2A— son capas que van agregando **cuando las necesiten**, no antes."
