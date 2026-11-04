# Módulo 1 · Preguntas que pueden hacer (técnicas y no técnicas)

Guía interna para ti, no para alumnos. Sirve para el cierre de la teórica, la tutoría y el chat del grupo.

## Cómo leer las respuestas
Cada respuesta lleva una etiqueta que dice **de dónde sale**, para que no presentes como hecho algo que es criterio:

| Etiqueta | Significa |
|---|---|
| 📘 **Docs ADK** | Lo dice la documentación de `adk.dev` (consultada el 13-oct-2026; es un resumen automático de cada página, verifica el detalle antes de citar literal) |
| 🧪 **Probado** | Lo comprobamos en nuestro proyecto con `google-adk 2.11.0` |
| 🧭 **Criterio** | Práctica o heurística razonable, **no** viene de la documentación ni la medimos. Preséntala como "una regla práctica" |
| ❔ **No verificado** | No lo comprobamos; dilo así y compromete una respuesta para después |

> **Lo más importante de este archivo:** la documentación de ADK **no da cifras** para cosas como la longitud de una instrucción, cuántas herramientas dar a un agente o cómo elegir el mejor modelo. Dice "sé claro y específico" y deja el resto al diseñador. Cuando te pregunten por números, la respuesta honesta es: *"no hay un número oficial; hay un método para decidirlo"* y ese método se explica abajo.

---

## A. Preguntas no técnicas (negocio, expectativas, riesgo)

**1. ¿Un agente es lo mismo que un chatbot?**
No. Un chatbot responde con lo que "sabe" el modelo. Un agente **decide qué hacer y usa herramientas** (consultar una base, llamar una API) para responder con datos reales. En nuestro caso, las cifras salen de `finanzas.db`, no de la memoria del modelo. 🧪

**2. ¿Reemplaza al analista de BI?**
En este programa, no: automatiza la parte repetitiva (entrar a varios sistemas, cruzar tablas, armar el primer borrador de la explicación). Quien define qué preguntar, valida la respuesta y decide qué hacer con ella sigue siendo la persona. 🧭

**3. ¿Puede equivocarse o inventar cifras?**
Sí. Un modelo puede inventar o redactar mal. Se reduce haciendo que las cifras vengan **de herramientas** y no del modelo, validando entradas con contratos y **midiendo** el resultado (Módulo 5: Faithfulness). No se elimina con un prompt; se detecta y se bloquea. Lo que sí vimos: Tesorería, sin datos, no inventó cifras porque su instrucción se lo prohíbe y no tiene herramientas. 🧪

**4. ¿Cuánto cuesta usarlo?**
Se cobra por uso de Gemini (tokens de entrada y salida) y por los servicios que despliegues. En un día pesado de pruebas nuestro consumo fue ≈72 mil tokens de entrada y ≈26 mil de salida (ver `PREREQUISITOS_ORGANIZADORES.md`). **No tenemos un precio por pregunta** y los precios cambian; consúltalos en la página de precios de Agent Platform. 🧪 (consumo) / ❔ (precio)

**5. ¿Mis datos salen de la empresa? ¿Se usan para entrenar el modelo?**
Depende del contrato y de la configuración del proyecto de Google Cloud. En el curso usamos **datos sintéticos**, así que no aplica. Para datos reales, la respuesta correcta es revisar los términos de Google Cloud y la política de la empresa, y consultar con seguridad/legal. ❔ No lo verificamos. Si alguien insiste, comprométete a investigarlo para el siguiente módulo.

**6. ¿Cuándo NO conviene usar un agente?**
Cuando el proceso es siempre el mismo y se puede escribir con reglas: un `if`, una consulta SQL o un workflow fijo es más barato, rápido y predecible. El agente con LLM vale cuando las preguntas son **abiertas** y no se pueden enumerar las reglas. 📘 (previsibilidad de los workflows) + 🧭

**7. ¿Cuánto tarda en responder?**
Más que una consulta normal. En nuestras pruebas, la delegación del supervisor usó **3 llamadas al modelo** (≈15 s en total con `gemini-2.5-flash`): decidir la transferencia, decidir usar la herramienta y redactar. Cada salto de delegación suma una llamada. 🧪

**8. ¿Necesito saber programar para usar agentes?**
Para **construirlos con ADK**, sí: Python básico (funciones, diccionarios, `try/except`). Para usar uno ya hecho, no. La documentación de Google también muestra un camino donde una herramienta de IA genera el agente a partir de instrucciones (Agents CLI), pero **no lo probamos**. 🧭 / ❔

**9. ¿Por qué Google/ADK y no otro?**
En este programa la plataforma es Gemini Enterprise Agent Platform, y ADK es el kit que Google recomienda para ella. No es obligatorio: la plataforma acepta también otros frameworks (LangChain, LangGraph, AG2, LlamaIndex) y ADK acepta otros modelos. Nosotros usamos ADK + Gemini por simplicidad. 📘

**10. ¿Qué tan seguro es? ¿Cualquiera puede llamar a mi agente?**
Por defecto, **no asumas que está protegido**. La autenticación y los permisos se configuran. El servidor A2A de clase corre en `localhost` y no debe exponerse. En el Módulo 5 vemos identidad del agente, IAM y gateway. 🧪 (servidor local sin credenciales) / 📘 (seguridad, ver sección G)

**11. ¿Esto ya se usa en producción?**
No lo afirmes. Lo que tenemos es una práctica de laboratorio con datos sintéticos. Algunas piezas de ADK que usamos (`RemoteA2aAgent`) están marcadas como **experimentales**. 🧪

**12. ¿Qué pasa si Google cambia algo?**
Ya pasó varias veces en el material: Vertex AI pasó a llamarse Gemini Enterprise Agent Platform, `GOOGLE_GENAI_USE_VERTEXAI` a `GOOGLE_GENAI_USE_ENTERPRISE`, y las clases Sequential/Parallel/Loop quedaron obsoletas en ADK 2.x a favor de `Workflow`. Por eso fijamos versión (`google-adk 2.11.0`) y modelo (`gemini-2.5-flash`). 🧪

---

## B. Diseño de agentes: instrucciones, descripción y parámetros

**13. ¿Cuánto debe medir una `instruction`? ¿Hay un límite o un tamaño recomendado?**
**La documentación no da una cifra, ni mínima ni máxima.** Pide ser claro y específico ("evita la ambigüedad"), usar Markdown si es compleja, incluir ejemplos para tareas difíciles o formatos concretos, y explicar cuándo y por qué usar cada herramienta. 📘
Regla práctica (🧭, no oficial): empieza **corta** (rol, qué herramienta usar, qué no hacer, formato de salida) y **agrega una regla solo cuando veas un error real** que la justifique. Nuestras instrucciones tienen 3 a 5 frases cada una y funcionaron. Una instrucción larga no es mejor por serlo: más texto es más tokens en **cada** llamada y más reglas que pueden contradecirse.
Señales de que se pasó de larga: reglas contradictorias, el agente ignora una parte, o cuesta mucho cada llamada. Señales de que es corta: respuestas con formato inconsistente, usa mal la herramienta o inventa cuando falta un dato.

**14. ¿Y la `description`?**
Es un resumen **breve** de lo que sabe hacer el agente. Sirve sobre todo en sistemas multiagente: el supervisor la lee para decidir a quién delegar. Debe ser **lo bastante específica para distinguirlo de los demás**. 📘 Una o dos frases (🧭). Dos descripciones parecidas son la causa más común de que el supervisor elija al especialista equivocado.

**15. ¿Cuál es la diferencia entre `description` e `instruction`?**
`description` es **para otros** (el supervisor decide con ella); `instruction` es **para el propio agente** (cómo se comporta). 📘 Si escribes una instrucción buena y una descripción vaga, el agente trabaja bien pero nadie le manda tareas.

**16. ¿Puedo meter variables en la instrucción?**
Sí, con `{nombre}`: inserta el valor del estado de la sesión (es lo que usa `output_key`). **Si la variable no existe, el agente da error**; con `{nombre?}` se vuelve opcional. 📘

**17. ¿Qué es la `temperature` y cuánto pongo?**
Controla cuánta variación tiene la respuesta: valores bajos dan respuestas más estables, altos más variadas. Se ajusta con `generate_content_config` junto con `max_output_tokens`, `top_p`, `top_k` y ajustes de seguridad. 📘 Para agentes que consultan cifras, conviene **baja** (🧭); la documentación solo da `0.2` como ejemplo de código, no como recomendación. En el curso no la cambiamos.

**18. ¿Qué hace `include_contents`?**
Con `'default'` el agente recibe el historial relevante; con `'none'` solo la instrucción y el turno actual. Útil para agentes que no necesitan memoria de la conversación (más barato). 📘

**19. ¿Cuántas herramientas puedo darle a un agente?**
**La documentación no da un número.** Nuestra guía dice que con diez herramientas el modelo "se confunde más"; es una **regla práctica**, no una medida nuestra ni de Google. 🧭 Lo que sí es verificable: más herramientas implican más descripciones que el modelo lee en cada llamada y más oportunidades de elegir mal. La forma sana de decidir es partir en especialistas y **medir** la precisión de ruta (Módulo 5).

**20. ¿Cómo escribo una buena herramienta?**
Nombre descriptivo, tipos explícitos y **docstring claro** (el modelo no ve el código, solo nombre, tipos y docstring). Devuelve un diccionario con una clave `status` (`success`/`error`) y dile al agente **en la instrucción qué hacer con cada resultado**: reintentar, abandonar o pedir más datos. No incluyas `tool_context` en el docstring. 📘 Devolver errores como dato y no como excepción: 🧪

**21. ¿Puedo forzar que la respuesta tenga un formato (JSON)?**
Sí, con `output_schema` (en Python acepta modelos Pydantic, listas, `dict`). **Advertencia de la documentación:** usarlo junto con `tools` solo está soportado por ciertos modelos (menciona Gemini 3.0); con otros, ADK recurre a una herramienta `set_model_response` que puede no ser fiable. 📘 No lo probamos con `gemini-2.5-flash`. ❔

**22. ¿Puede el agente pedirme un dato que le falta?**
Sí; es una instrucción de diseño ("si falta división o trimestre, pídelos"), como hace nuestro especialista de presupuestos. 🧪

---

## C. Elegir modelo

**23. ¿Cómo decido cuál es el mejor modelo?**
**La documentación de ADK no da criterios de selección**: solo explica cómo conectar modelos (cadena directa para los de Google Cloud, conectores para otros como LiteLLM, Ollama o vLLM, y *model routing* con failover). 📘 No existe "el mejor" en abstracto; es un método:
1. **Define qué tarea** hace ese agente (consultar y resumir es distinto de razonar sobre un caso complejo).
2. **Arma 10 a 20 preguntas reales** con respuesta esperada (un *eval set*).
3. **Prueba 2 o 3 modelos** con las mismas preguntas.
4. **Compara tres cosas:** calidad (¿cifras correctas?), latencia (¿cuánto tarda?) y costo (tokens).
5. **Elige el más barato que cumpla la calidad.** 🧭
Se puede usar un modelo distinto por agente: uno rápido para el que solo enruta y uno más capaz para el que razona.

**24. ¿Por qué usamos `gemini-2.5-flash`?**
Es rápido, económico y **probado en nuestro proyecto**. 🧪 No es "el mejor"; es el que verificamos. En el proyecto de prueba también respondieron `gemini-3.5-flash`, `3.6-flash`, `3.7-flash`, `3.8-flash` y `3.1-flash-lite` (en `global`), pero no los usamos. 🧪

**25. ¿Por qué no usamos el alias `gemini-flash-latest`?**
Dio **error 404** en Agent Platform. Además, un alias puede cambiar de modelo sin avisar, y eso rompe la comparabilidad de las evaluaciones. Con clave de AI Studio sí funcionaría. 🧪

**26. ¿Puedo usar un modelo que no sea de Google?**
Sí. ADK soporta Claude, modelos alojados en Agent Platform y, con conectores, OpenAI, Ollama, vLLM, LiteLLM y otros. 📘 No probamos ninguno; el material se verificó solo con Gemini. ❔

**27. ¿Un modelo "más grande" siempre da mejores resultados?**
No necesariamente para esta tarea. Si la herramienta ya entrega los datos, el modelo solo enruta y redacta, y un modelo rápido suele alcanzar. Pero ve a la evidencia: pruébalo con tu eval set (pregunta 23). 🧭

**28. ¿Qué pasa si el modelo cambia de versión?**
Puede cambiar el comportamiento. Por eso se usan **versiones concretas** (no alias) y se re-evalúa cuando se cambia de modelo. 🧭

---

## D. Estado, sesión y memoria

**29. ¿Qué diferencia hay entre sesión, estado y memoria?**
**Sesión:** una conversación (mismo `session_id` = continúa; nueva = empieza sin memoria). **Estado:** datos guardados en la sesión (por ejemplo con `output_key`). **Memoria:** información a largo plazo entre sesiones (Memory Bank). 📘 / 🧪 (sesión y estado)

**30. ¿Cómo sabe el agente que "¿y en Q2?" se refiere a Norte?**
Por el historial de la sesión: el supervisor conserva la división de la pregunta anterior. Con otro `session_id`, esa memoria no existe. 🧪

**31. ¿Qué significan los prefijos `app:`, `user:` y `temp:` del estado?**
Sin prefijo: solo esa sesión. `user:` y `app:` amplían el alcance a un usuario o a toda la aplicación, pero **solo con un servicio de sesión persistente** (por ejemplo base de datos o el de Agent Platform). `temp:` vale solo para la invocación actual. 📘

**32. ¿Qué pasa con la conversación si reinicio el programa?**
Con el servicio en memoria (`InMemorySessionService`, el que usamos), **se pierde**. Para conservarla hay que usar un servicio persistente. 🧪

**33. La conversación se vuelve larguísima, ¿se puede reducir?**
La documentación menciona **compresión de contexto** y **caché de contexto del modelo** como funciones de ADK. No leí su detalle ni las probamos. ❔

---

## E. Multiagente y A2A

**34. ¿Cuándo uso varios agentes y cuándo uno solo?**
La documentación dice que un agente monolítico se vuelve difícil de **desarrollar, evaluar y mantener**, y que dividir da previsibilidad, fiabilidad y estructura. No dice cuándo basta uno solo. 📘 Nuestro criterio: empieza con **uno** y divide cuando las instrucciones se contradicen, las herramientas se multiplican o necesitas probar y dar permisos por separado. 🧭

**35. ¿Cuántos especialistas puede tener un supervisor?**
No hay límite documentado. Cada descripción nueva se suma a lo que el supervisor lee y puede confundir la elección. 🧭

**36. ¿Qué hago si el supervisor elige al especialista equivocado?**
Afina las `description` (casi siempre es la causa) y **mídelo** con la precisión de ruta (Módulo 5). 🧪 / 🧭

**37. ¿Por qué un agente solo puede tener un padre?**
Es una regla de ADK: un agente no puede estar bajo dos supervisores. Para reutilizarlo se usa `clone()`, que hace una copia sin padre. Es un error que sí les saldrá en el laboratorio. 🧪

**38. ¿Cuándo uso sub-agentes y cuándo A2A?**
Sub-agentes cuando todo vive en el mismo programa. A2A cuando el otro agente es de **otro equipo, otro lenguaje u otra nube** y solo comparten el contrato. A2A cuesta latencia y complejidad: empieza con sub-agentes. 🧪 / 🧭

**39. ¿Puedo conectarme a cualquier agente solo con su URL?**
No. Hacen falta tres cosas: que del otro lado haya **un agente que hable A2A** y publique su agent card; que tengas **permiso** (la agent card puede exigir autenticación); y que **se entiendan en lo que pides**. A2A resuelve el "cómo se hablan", no el "qué se dicen" ni el "quién tiene permiso". 📘 (protocolo) / ❔ (la autenticación no la probamos: nuestro servidor local no la pide)

**40. ¿Y si el servidor A2A está caído?**
Observamos que el agente puede **no avisar** y quedarse mudo (por ejemplo, si otro proceso ocupa el puerto 8001). Verifica siempre que la agent card responda. 🧪

**41. ¿Qué diferencia hay entre A2A y MCP?**
MCP conecta un agente con **herramientas y datos**; A2A conecta un agente con **otros agentes**. Se complementan. 📘

**42. ¿Cuándo uso un agente de flujo (Sequential/Parallel/Loop) y cuándo un supervisor?**
Si el orden **ya lo conoces**, un flujo: es código determinista, más barato y predecible. Si el orden **depende de la pregunta**, que decida el modelo (supervisor). En ADK 2.x esas clases aparecen como obsoletas a favor de `Workflow`. 📘 / 🧪

---

## F. Seguridad y gobierno

**43. ¿Cómo evito que alguien le haga decir o hacer cosas indebidas (prompt injection)?**
La documentación lista medidas por capas, no una sola: 📘
- **Guardrails en las herramientas:** exponer solo acciones permitidas, con parámetros que fija el desarrollador (por ejemplo, solo `SELECT` o tablas autorizadas).
- **Callbacks** como `before_tool_callback`, que validan una llamada antes de ejecutarla y pueden bloquearla.
- **Plugins** reutilizables a nivel de ejecución, como *Model Armor* o *PII Redaction*.
- **Filtros de seguridad de Gemini** y un modelo económico (tipo Flash Lite) como "juez" de entradas y salidas.
- **Identidad:** la herramienta puede usar la identidad del agente (cuenta de servicio, simple pero con un solo nivel de acceso) o la del usuario (OAuth).
En el curso aplicamos la primera idea: el **contrato** valida la entrada antes de tocar la base. 🧪 El resto lo vemos en el Módulo 5.

**44. ¿Qué es mejor, que la herramienta use la identidad del agente o la del usuario?**
Identidad del agente: más sencilla, pero todos los usuarios quedan con el mismo acceso; conviene registrar logs para atribuir acciones. Identidad del usuario: limita a lo que ese usuario puede hacer, aunque los *scopes* suelen ser más amplios de lo necesario. 📘

**45. ¿Qué pasa con datos personales (PII)?**
Hay un plugin de redacción de PII y el filtrado de Gemini. En el curso trabajamos con datos sintéticos; el Módulo 5 trata DLP. 📘

**46. ¿Puede el agente ejecutar código? ¿Es seguro?**
ADK tiene ejecución de código con sandbox, y para un ejecutor propio recomienda entornos herméticos (sin red). 📘 No usamos ejecución de código.

---

## G. Calidad y evaluación

**47. ¿Cómo sé si mi agente "está bien"?**
Con un **eval set**: preguntas reales con respuesta esperada y las herramientas que debería llamar. `adk eval <agente> <eval_set>` ejecuta la evaluación. 📘 Por defecto, `tool_trajectory_avg_score` exige **1.0** (la secuencia de herramientas debe coincidir exacta) y `response_match_score` **0.8**; se pueden cambiar en `test_config.json`. 📘 Nosotros usamos pruebas `pytest` y el Módulo 5 trabaja evaluación. No ejecutamos `adk eval`. ❔

**48. ¿Qué mide un "LLM como juez"?**
Un modelo compara la respuesta con una referencia o con una rúbrica. ADK trae criterios como `final_response_match_v2`, `hallucinations_v1` y `safety_v1`. Esos criterios requieren la Vertex Gen AI Evaluation Service API (más permisos y consumo). 📘

**49. ¿Cómo pruebo sin gastar tokens?**
Las pruebas de `pytest` del módulo (22) **no llaman a Gemini**: prueban herramienta, contrato, cableado de ADK, agent card y estructura del árbol. Lo que sí consume es ejecutar el notebook o `adk web`. 🧪

**50. ¿Cómo veo qué hizo el agente por dentro?**
En `adk web`, el grafo y la pestaña de Events muestran cada llamada a herramienta, resultado y transferencia. Para producción: Cloud Trace y logging (Módulo 5). 🧪 / 📘

---

## H. Operación y prácticas

**51. ¿Cómo se despliega un agente?**
ADK documenta despliegue en Agent Runtime, Cloud Run y GKE (`adk deploy agent_engine`, `cloud_run`, `gke`, `docker`). **No ejecutamos un despliegue real.** El Módulo 5 lo retoma. 📘 / ❔

**52. ¿Puedo usar `adk web` en producción?**
No. Es solo para desarrollo. 🧪

**53. ¿Puede el agente usar internet o buscar información actual?**
Sí, con herramientas de grounding o de búsqueda; no las usamos en el curso. 📘 / ❔

**54. ¿Cómo evito que el agente tarde mucho o gaste de más?**
Menos saltos de delegación, instrucciones concisas, `include_contents='none'` cuando no se necesita historial, y un modelo rápido para tareas simples. Mide tokens y latencia por llamada antes de optimizar. 🧭 / 📘

**55. ¿Por qué falla si me quedo sin permisos o sin cuota?**
Errores típicos: `permission denied` (faltan los roles `aiplatform.user` y `serviceusage.serviceUsageConsumer`), `404` por modelo inexistente, o proyecto equivocado. Ver `PREREQUISITOS_ALUMNOS.md` y `COMANDOS.md`. 🧪 (los roles se investigaron; no se probaron con una cuenta restringida)

---

## I. Respuestas cortas para frases que seguro escucharás

| Si dicen… | Responde |
|---|---|
| "¿Cuál es el número mágico de tokens para una instrucción?" | "No existe un número oficial. Empieza corta y agrega reglas cuando veas un error real." |
| "¿Cuál es el mejor modelo?" | "El más barato que pase tu evaluación. Se decide con datos, no con fama." |
| "Entonces, ¿para qué ADK si la CLI lo genera?" | "La CLI automatiza; entender el código te permite revisar, corregir y gobernar lo que genera." |
| "¿Esto se puede poner en producción ya?" | "El patrón sí; este laboratorio no. Faltan evaluación, seguridad y despliegue: son los módulos 4 y 5." |
| "Gemini me dio una cifra distinta a la de la base" | "Por eso las cifras salen de herramientas y se mide la fidelidad." |
| "Probé y a mí me dio otra respuesta" | "Normal: un modelo no es determinista. Por eso se evalúa con muchos casos, no con uno." |
| "¿Y si no sé qué responder?" | "No lo probamos / no está en la documentación. Lo reviso y te contesto." |

---

## Lo que esta guía NO resuelve (lista honesta)
- No hay **precios** (cámbialos por los vigentes).
- No se probó ningún modelo distinto de Gemini.
- No se probó `adk eval`, despliegue, Agents CLI ni Managed Agents.
- No se verificó la política de privacidad de datos de Google Cloud.
- La regla de "diez herramientas" y los rangos de longitud de instrucción son **criterio**, no medición.
- La documentación de `adk.dev` se leyó mediante resúmenes automáticos; las páginas largas se leyeron solo en su primera parte (instrucciones, herramientas y contexto). Antes de citar un detalle literal, ábrela.
