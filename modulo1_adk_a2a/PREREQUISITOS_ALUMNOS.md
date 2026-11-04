# Antes de la sesión práctica · Módulo 1 (ADK Code-First + A2A)

Este documento te dice **qué debes tener instalado y configurado antes de la sesión**, empezando desde lo más básico. Si lo haces con calma, la práctica de 2 horas se dedica a aprender agentes y no a resolver instalaciones.

> ⏱ **Reserva entre 30 y 45 minutos** (es un estimado; depende de tu conexión y de tu equipo). Hazlo **al menos un día antes**.
> ⚠️ **Si tu equipo es corporativo y no te deja instalar programas, avisa antes de la sesión.** No esperes al día de la práctica.

---

## 0. Resumen en una lista (marca cuando lo tengas)
- [ ] Una computadora con **internet** y permiso para instalar programas
- [ ] **Python 3.11** (o 3.10+) instalado
- [ ] **Visual Studio Code** con las extensiones **Python** y **Jupyter**
- [ ] **Google Cloud CLI** (`gcloud`) instalado
- [ ] La **carpeta del proyecto** `GeminiAgentsBI` en tu equipo (te la entrega el instructor)
- [ ] Los **paquetes de Python** instalados
- [ ] Sesión iniciada en Google Cloud y el archivo **`.env`** configurado
- [ ] Verificación final hecha (sección 5)

## 1. Lo que te dará el instructor
No lo puedes conseguir tú; pídelo antes de empezar:
| Dato | Para qué sirve | Lo tengo |
|---|---|---|
| **ID del proyecto de Google Cloud** (no el nombre) | Va en tu `.env` y en los comandos de `gcloud` | ☐ |
| **Acceso a ese proyecto** con permiso para usar Gemini | Sin esto el modelo responde "permiso denegado" | ☐ |
| **La carpeta del proyecto** (`GeminiAgentsBI`) | Contiene el notebook, el código y los datos de ejemplo | ☐ |
| Tu **cuenta de Google** registrada en el proyecto | Es la que usarás al iniciar sesión | ☐ |

## 2. Requisitos de tu computadora
- **Sistema operativo:** el material se probó en **Windows 11 con PowerShell**. En macOS o Linux debería funcionar con comandos equivalentes, pero **no se ha probado**.
- **Conexión a internet** con acceso a los servicios de Google Cloud (`*.googleapis.com`). Si estás detrás de una VPN o un proxy corporativo y algo falla al conectar con Google, avísalo.
- **Permisos** para instalar programas y para abrir puertos locales (la práctica levanta un servidor en tu propia máquina).

## 3. Conocimientos previos
- **Python básico:** funciones, diccionarios, `try/except`. No necesitas dominar `async/await`: verás la palabra `await` en algunas celdas y la práctica la explica.
- **Notebooks:** saber ejecutar una celda (Shift+Enter).
- **Datos/BI básico:** entender qué es un presupuesto frente a lo ejecutado y una consulta a una base de datos.
- **No necesitas experiencia previa con IA ni con agentes.**

## 4. Instalación paso a paso

### 4.1 Python
1. Descarga **Python 3.11** desde https://www.python.org/downloads/ (el material se probó con **3.11.9**; ADK pide 3.10 o superior).
2. En el instalador de Windows, **marca la casilla "Add python.exe to PATH"** antes de instalar.
3. Abre PowerShell y comprueba:
   ```powershell
   python --version
   ```
   Debe mostrar `Python 3.11.x` (o 3.10 o superior). Si dice que no encuentra el comando, reinstala marcando la casilla del PATH.

### 4.2 Visual Studio Code
1. Instala VS Code desde https://code.visualstudio.com/.
2. Abre la pestaña de **Extensiones** e instala **Python** y **Jupyter** (las dos de Microsoft). Con ellas puedes abrir y ejecutar archivos `.ipynb`.

### 4.3 Google Cloud CLI (`gcloud`)
1. Instálala siguiendo https://cloud.google.com/sdk/docs/install.
2. Abre una **terminal nueva** y comprueba:
   ```powershell
   gcloud --version
   ```
   Debe mostrar una línea que empieza con `Google Cloud SDK`.

### 4.4 La carpeta del proyecto
1. Guarda la carpeta `GeminiAgentsBI` que te dio el instructor en un lugar sencillo (por ejemplo, `Documentos`).
2. En VS Code: **Archivo → Abrir carpeta…** y elige `GeminiAgentsBI`. **Abre la carpeta completa**, no solo el notebook: el notebook necesita encontrar los demás archivos.

### 4.5 Entorno virtual (recomendado)
Un entorno virtual mantiene los paquetes de este curso separados del resto de tu Python. En la terminal de VS Code (*Terminal → Nueva terminal*), dentro de `GeminiAgentsBI`:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
El inicio de la línea debería mostrar `(.venv)`.
Si PowerShell dice que la ejecución de scripts está deshabilitada, ejecuta primero `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (solo vale para esa terminal) y repite el comando de activación.

### 4.6 Paquetes de Python
Con el entorno activado, instala **solo lo que necesita este módulo**:
```powershell
pip install "google-adk[a2a]>=2.11.0" python-dotenv ipykernel httpx uvicorn pydantic
```
Esto instaló sin errores en un entorno limpio de Windows con Python 3.11.9. Instala además ADK 2.11 o superior, `google-genai`, FastAPI, Starlette y el SDK de A2A como dependencias.

> **No uses `pip install -r requirements.txt` salvo que el instructor te lo pida.** Ese archivo es de **todo el programa** (6 semanas) e incluye `pyodbc`, que a veces falla al instalarse en Windows.
> Si quieres ejecutar también las pruebas automáticas: `pip install pytest` (opcional).

### 4.7 Iniciar sesión en Google Cloud
En la terminal, **una vez**, y sustituyendo `<ID_DEL_PROYECTO>` por el que te dio el instructor:
```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project <ID_DEL_PROYECTO>
gcloud auth application-default set-quota-project <ID_DEL_PROYECTO>
```
- Cada uno de los dos primeros comandos **abre el navegador** para que inicies sesión con tu cuenta de Google. Usa la cuenta que el instructor registró.
- `application-default login` es el que usa el código de la práctica.
- El último comando evita avisos de cuota del proyecto equivocado.

### 4.8 El archivo `.env`
1. En la carpeta del proyecto, **copia** el archivo `.env.example` y llámalo **`.env`**.
2. Ábrelo y deja estas **tres** variables (el resto no se usa en el Módulo 1):
   ```
   GOOGLE_CLOUD_PROJECT=<ID_DEL_PROYECTO>
   GOOGLE_CLOUD_LOCATION=us-central1
   MODEL_NAME=gemini-2.5-flash
   ```
3. Cuida tres detalles:
   - Es el **ID** del proyecto, **no su nombre**.
   - `MODEL_NAME` debe ser **`gemini-2.5-flash`**. **No uses `gemini-flash-latest`**: en este tipo de proyecto da error 404.
   - **El `.env` es privado: nunca lo subas a Git ni lo compartas.**

### 4.9 Elegir el kernel del notebook
1. Abre `modulo1_adk_a2a/notebooks/practica_alumnos.ipynb`.
2. Arriba a la derecha pulsa **Seleccionar kernel** y elige el Python de **`.venv`** que creaste (aparece como `.venv`). Si no usaste entorno virtual, elige el Python donde hiciste `pip install`.

## 5. Verificación (hazla antes de la sesión)
Con la terminal en la carpeta del proyecto y el entorno activado:

| Comprobación | Comando | Debes ver |
|---|---|---|
| Python | `python --version` | `Python 3.11.x` (o 3.10 o superior) |
| ADK | `pip show google-adk` | `Version: 2.11.x` (o superior) |
| CLI de ADK | `adk --version` | un número de versión, sin error |
| gcloud | `gcloud --version` | `Google Cloud SDK ...` |
| Proyecto activo | `gcloud config get-value project` | tu `<ID_DEL_PROYECTO>` |

**Prueba de Gemini** (usa unos pocos tokens, es normal). Sustituye el ID:
```powershell
$env:GOOGLE_GENAI_USE_ENTERPRISE="TRUE"; $env:GOOGLE_CLOUD_PROJECT="<ID_DEL_PROYECTO>"; $env:GOOGLE_CLOUD_LOCATION="us-central1"
python -c "from google import genai; c=genai.Client(); print(c.models.generate_content(model='gemini-2.5-flash', contents='Di hola en una palabra').text)"
```
Debe imprimir una palabra (por ejemplo, "Hola"). Si imprime un error, mira la tabla de la sección 7.

**Prueba del notebook:** abre `practica_alumnos.ipynb`, ejecuta las **dos primeras celdas de código** (Parte 0). Debes ver:
```
RAIZ: C:\...\GeminiAgentsBI
google-adk: 2.11.x
Proyecto: <ID_DEL_PROYECTO> | Región: us-central1 | Modelo: gemini-2.5-flash
```
Con eso estás listo. (Esas dos celdas **no llaman a Gemini**: solo comprueban que haya proyecto y credenciales.)

## 6. Puertos que usa la práctica
La práctica abre servidores **solo en tu computadora**:
| Puerto | Para qué | Si falla |
|---|---|---|
| **8001** | El servidor del especialista (Parte 5) | Comprueba que esté libre: `netstat -ano | findstr 8001`. Si algo lo usa, ciérralo |
| **8002** | El servidor de Tesorería (reto opcional 5.4) | Comprueba que esté libre: `netstat -ano | findstr 8002`. Si algo lo usa, ciérralo |
| **8501** | `adk web` (interfaz visual, opcional) | Usa siempre `--port 8501` |
| ~~8000~~ | Es el puerto por defecto de `adk web`, pero **Windows puede tenerlo reservado** (da `Errno 13`) | No lo uses |

Al arrancar el servidor, **Windows puede preguntarte por el firewall**: permite el acceso en **redes privadas**.

Para `adk web` (opcional), desde una terminal en la carpeta del proyecto:
```powershell
. .\env.ps1
adk web --port 8501 modulo1_adk_a2a/src
```
y abre http://127.0.0.1:8501. (Sin `. .\env.ps1`, falla con `No module named 'shared'`).

## 7. Problemas frecuentes
| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `python` no se reconoce | Python no está en el PATH | Reinstálalo marcando "Add python.exe to PATH" |
| `ModuleNotFoundError: google.adk` en el notebook | El notebook usa otro Python | Cambia el kernel al de `.venv` (sección 4.9) |
| `StopIteration` en la primera celda | Abriste solo el notebook, no la carpeta | Abre la carpeta `GeminiAgentsBI` completa en VS Code |
| `RuntimeError: Falta GOOGLE_CLOUD_PROJECT` | `.env` sin proyecto, o con `tu-proyecto` | Pon el **ID** real y reinicia el kernel |
| `RuntimeError: No hay credenciales` | Falta el login de gcloud | `gcloud auth application-default login` |
| `404 NOT_FOUND ... Publisher model ...` | `MODEL_NAME` mal escrito o es `gemini-flash-latest` | `MODEL_NAME=gemini-2.5-flash` |
| `403 ... has not been used in project ...` | La cuota apunta a otro proyecto | `gcloud auth application-default set-quota-project <ID_DEL_PROYECTO>` |
| `PermissionDenied` | Tu cuenta no tiene permiso en el proyecto | Avisa al instructor |
| `429` / "cuota" | Muchas peticiones seguidas | Espera un minuto y reintenta |
| `pip install` falla con `pyodbc` | Instalaste `requirements.txt` completo | Usa solo la línea de la sección 4.6 |
| El navegador no se abre al iniciar sesión | Bloqueado por el equipo | Copia el enlace que muestra la terminal y ábrelo a mano |
| Cambié el `.env` y no pasa nada | El kernel tiene el valor viejo en memoria | **Reinicia el kernel** y ejecuta desde la Parte 0 |

## 8. Seguridad y buenas prácticas
- **No subas a Git ni compartas** tu archivo `.env`.
- **No compartas** la carpeta de credenciales de `gcloud` (en Windows, `%APPDATA%\gcloud`).
- Cada pregunta al modelo consume **tokens** del proyecto. La práctica usa **pocos**; aun así, no ejecutes las celdas en bucles ni las repitas sin necesidad.
- Si usas un equipo compartido, cierra tu sesión al terminar: `gcloud auth revoke` y `gcloud auth application-default revoke`.

## 9. El día de la sesión
- Laptop **cargada**, con todo lo anterior verificado.
- Abre VS Code **en la carpeta del proyecto** y deja el notebook listo con el kernel elegido.
- Si algo no funciona, ten a mano el **mensaje de error completo** (una captura sirve) para que el instructor lo resuelva rápido.
