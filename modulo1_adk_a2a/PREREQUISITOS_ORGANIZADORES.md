# Prerrequisitos para los ORGANIZADORES · Módulo 1 (sesión práctica)

> 🔒 **Documento interno. No se reparte a los alumnos.** Lo que sí reciben ellos es `PREREQUISITOS_ALUMNOS.md`.
> Aquí está lo que **tú o el administrador del proyecto** deben dejar listo para que 30 personas puedan correr la práctica.

**Leyenda:** ✅ verificado en este proyecto · 📖 respaldado por documentación, no probado aquí · ⚠️ no verificado

---
## 1. Qué necesita la práctica de tu lado (resumen)
- [ ] Un **proyecto de Google Cloud** con **facturación activa**
- [ ] La API **`aiplatform.googleapis.com`** ("Agent Platform API") habilitada
- [ ] Acceso a **Gemini** en el proyecto (✅ `gemini-2.5-flash` respondió en las regiones `us-central1` y `global` del proyecto de prueba)
- [ ] **Dos roles** asignados a cada alumno (sección 3)
- [ ] **Cuota** suficiente para 30 personas conectadas a la vez
- [ ] **Alerta de presupuesto** configurada
- [ ] **Carpeta del proyecto** preparada y lista para entregar (sección 5)
- [ ] **Una cuenta de prueba** con solo esos roles, para validar todo antes (sección 4)

## 2. El proyecto
| Dato | Detalle |
|---|---|
| **ID del proyecto** | Se entrega a los alumnos. Es el **ID**, no el nombre: pueden diferir (en las pruebas, el nombre visible y el ID eran distintos) |
| **Región** | `us-central1` (✅ probada). `global` también respondió, pero la práctica se documentó con `us-central1` |
| **Modelo** | `gemini-2.5-flash` (✅). **No** `gemini-flash-latest`: da 404 en este tipo de proyecto. También respondieron `gemini-3.5-flash`, `3.6-flash`, `3.7-flash`, `3.8-flash` y `3.1-flash-lite` en `global`, pero no se usan en la práctica |
| **Datos** | Solo sintéticos; no hay información real de la empresa |
| **¿Un proyecto compartido o uno por célula?** | Decisión tuya. Uno compartido es lo más simple; uno por célula (5) aísla fallos de cuota y costos, pero hay que repetir la configuración |

Habilitar la API (lo hace un administrador):
```powershell
gcloud services enable aiplatform.googleapis.com --project=<ID_DEL_PROYECTO>
```
⚠️ Comando estándar; no se ejecutó aquí porque la API ya estaba habilitada en el proyecto de prueba.

## 3. Permisos que necesita cada alumno
Roles **a nivel de proyecto**. **No** les des Propietario ni Editor.

| Rol | Para qué | Respaldo |
|---|---|---|
| **`roles/aiplatform.user`** (Agent Platform User) | Llamar a Gemini | 📖 Es un rol predefinido de la plataforma; la documentación de ADK pide "Agent Platform User" para producción. Lista exacta de permisos: `gcloud iam roles describe roles/aiplatform.user` |
| **`roles/serviceusage.serviceUsageConsumer`** | Que `gcloud auth application-default set-quota-project` funcione y no haya avisos o errores de cuota | 📖 La [documentación de cuotas](https://docs.cloud.google.com/docs/quotas/set-quota-project) dice que ese comando requiere `serviceusage.services.use` y que ese rol lo incluye |

La práctica **solo llama a Gemini**: no usa BigQuery, Storage ni otros servicios, así que no hacen falta más roles en el Módulo 1. Los permisos de los módulos siguientes (BigQuery, DLP, trazas, etc.) están en la plantilla `modulo5_agentops/ci/iam_least_privilege.md`.

### Asignarlos a 30 personas sin repetirlo 30 veces
1. Crea un **grupo de Google** con los correos de los alumnos.
2. Asigna los dos roles **al grupo**:
```powershell
gcloud projects add-iam-policy-binding <ID_DEL_PROYECTO> --member="group:<grupo@dominio>" --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding <ID_DEL_PROYECTO> --member="group:<grupo@dominio>" --role="roles/serviceusage.serviceUsageConsumer"
```
⚠️ No ejecutado aquí. Para un alumno suelto, cambia `group:<grupo@dominio>` por `user:<correo>`. Si el dominio de tus alumnos es de otra organización, hay que verificar que tu organización permita agregarlos (políticas de compartición de dominio): ⚠️ no probado.

### Comprobar quién tiene qué
```powershell
gcloud projects get-iam-policy <ID_DEL_PROYECTO> --flatten="bindings[].members" --filter="bindings.role:roles/aiplatform.user" --format="table(bindings.members)"
```
⚠️ No ejecutado.

## 4. Valida con una cuenta de prueba (hazlo antes de dar acceso a todos)
**Tu cuenta probablemente es de administrador**, así que si pruebas con ella no descubrirás un permiso faltante. Crea (o usa) una cuenta **con solo los dos roles de arriba** y, con ella:
1. Sigue `PREREQUISITOS_ALUMNOS.md` **desde cero**, en una máquina o perfil limpio si puedes.
2. Ejecuta la **prueba de Gemini** y las **dos primeras celdas** del notebook.
3. Ejecuta el notebook completo una vez (consume unos pocos tokens).

| Si falla con… | Falta o pasa |
|---|---|
| `PermissionDenied` | `roles/aiplatform.user` |
| `403 ... has not been used in project ...` | La cuota apunta a otro proyecto, o falta `serviceUsageConsumer` |
| `429` | Cuota agotada o demasiadas peticiones seguidas |
| `404 ... Publisher model` | `MODEL_NAME` equivocado o modelo no disponible en la región |

**Este paso no se ha hecho todavía.** Es el mayor riesgo logístico del módulo.

## 5. La carpeta que se entrega
Qué **sí** y qué **no** entregar:

| Elemento | ¿Entregar? | Por qué |
|---|---|---|
| `modulo1_adk_a2a/notebooks/practica_alumnos.ipynb` | ✅ | Es la práctica (con TODO) |
| `modulo1_adk_a2a/notebooks/practica_instructor.ipynb` | ❌ | **Tiene todas las respuestas** |
| `modulo1_adk_a2a/SESION_TEORICA.md`, `SESION_PRACTICA.md`, `PREREQUISITOS_ORGANIZADORES.md` | ❌ | Son guías del instructor (la práctica incluye respuestas y resultados esperados) |
| `modulo1_adk_a2a/PREREQUISITOS_ALUMNOS.md`, `COMANDOS.md` | ✅ | Son para el alumno |
| `modulo1_adk_a2a/_anteriores/` | ❌ | Borradores viejos |
| `.env` | ❌ | Es tuyo (tiene tu proyecto). Entrega solo `.env.example` |
| Carpetas `.adk/`, `__pycache__/`, `.venv/` | ❌ | Sesiones guardadas, cachés y entorno tuyo |
| `shared/`, `data/`, `env.ps1`, `conftest.py` | ✅ | El notebook los necesita |
| Carpetas `modulo2` a `modulo5`, `capstone`, `docs` | A tu criterio | No se usan en el Módulo 1 |

**Decisión pendiente tuya sobre `src/finanzas_agents/agent.py`:** contiene **la solución** de las Partes 2, 3 y 7 (los agentes que el alumno debe escribir en el notebook). Si la entregas desde el inicio, pueden copiarla en lugar de escribirla. El notebook los invita a compararla **al final**. Opciones: (a) entregarla al terminar la sesión; (b) entregarla desde el inicio y asumir que algunos la verán; (c) entregar una versión sin esa parte y la completa después. `tools.py`, `contracts.py`, `eventos.py`, `a2a_local.py` y `a2a_server.py` sí se necesitan desde el inicio.

Antes de comprimir, **limpia las salidas del notebook de alumnos** (en VS Code: *Borrar todas las salidas*) para no filtrar tu ID de proyecto ni respuestas.

## 6. Cuota, costo y seguimiento
- **Consumo:** es bajo por alumno, pero son 30 personas ejecutando a la vez. En un día de pruebas intensas (muchas corridas del notebook completo y varios sondeos de modelos) se consumieron ≈ 72 mil tokens de entrada y ≈ 26 mil de salida con `gemini-2.5-flash`, un costo del orden de centavos de dólar. **No tengo una medición por alumno**; la forma fiable de saberlo es medir una corrida completa con una cuenta de prueba y multiplicarla.
- **Cuota por minuto:** con 30 personas lanzando preguntas casi simultáneas es posible ver errores `429`. Revisa las cuotas de peticiones del modelo en el proyecto y, si hace falta, escalona el inicio o trabaja en parejas. ⚠️ No se probó con carga real.
- **Alerta de presupuesto:** créala en *Facturación → Presupuestos y alertas* antes de la clase.
- **Seguimiento durante la sesión:** en la consola de la plataforma hay gráficas de **tokens de entrada y de salida por día y por modelo**; sirven para ver el consumo en vivo.
- Si el costo es una preocupación, el modelo `gemini-2.5-flash` es el rápido y económico; **no cambies a modelos "Pro"** sin revisar tarifas.

## 7. Equipos de los alumnos (preguntas para hacer con anticipación)
- ¿Pueden **instalar** Python, VS Code y la CLI de Google Cloud? (equipos corporativos restringidos)
- ¿Hay **VPN o proxy** que bloquee `*.googleapis.com`? ⚠️ No probado.
- ¿Sistema operativo? El material se probó en **Windows 11 con PowerShell**; macOS y Linux no.
- ¿Pueden **abrir puertos locales** (8001 y 8501)? Windows puede pedir permiso de firewall; además el puerto 8000 suele estar reservado.

## 8. Cronograma sugerido
| Cuándo | Qué |
|---|---|
| **T-10 días** | Proyecto, API, facturación y alerta de presupuesto. Grupo de Google con los alumnos |
| **T-7 días** | Roles asignados al grupo. Envío de `PREREQUISITOS_ALUMNOS.md` y de la carpeta del proyecto |
| **T-5 días** | **Validación con la cuenta de prueba** (sección 4) |
| **T-3 días** | Cada alumno hace la **verificación** de su documento y te confirma. Recoge a quienes tengan problemas |
| **T-1 día** | Tú corres el notebook del instructor una vez con Gemini real y ensayas la sesión con el guion |
| **Día D** | Consola abierta con las gráficas de tokens; plan para quienes no hayan podido instalar (trabajar en pareja con una máquina que sí funcione) |

## 9. Plan B
- **Si Gemini falla o hay `429` masivos:** no hay modo sin Gemini en el notebook. Opciones: esperar un minuto y reintentar; que trabajen en parejas con una sola máquina; o que tú ejecutes en el proyector y ellos sigan el flujo y completen el código. Está en `SESION_PRACTICA.md` ("Si algo sale mal").
- **Si un alumno no pudo configurar su máquina:** que trabaje con un compañero. La Parte 8 (autoevaluación) puede hacerla uno por pareja.

## 10. Qué NO está verificado (resumen honesto)
- Que una **cuenta con solo los dos roles** pueda ejecutar todo (nunca se ha probado con una).
- La **carga de 30 personas** a la vez (cuota y `429`).
- Que el **entorno mínimo** de `pip` corra el notebook de punta a punta en una máquina limpia (los paquetes sí se instalaron en un entorno limpio).
- macOS, Linux y equipos con **VPN/proxy** corporativos.
- Los comandos de `gcloud` marcados ⚠️ de este documento.
