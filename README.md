# 🎓 ExamBox - Sistema de Exámenes con Docker

Sistema de exámenes en red local (LAN) donde el profesor controla el examen desde un dashboard y cada alumno trabaja en un entorno JupyterLab aislado con librerías fijas.

![ExamBox](https://img.shields.io/badge/ExamBox-v1.0-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688)

## 📋 Características

- ✅ **Entornos aislados**: Cada alumno trabaja en su propio contenedor Docker con JupyterLab
- ✅ **Control de tiempo**: Temporizador automático con extensión individual
- ✅ **Desbloqueo progresivo**: Las preguntas se desbloquean según avanza el examen
- ✅ **Entrega centralizada**: Los trabajos se comprimen y envían al servidor del profesor
- ✅ **Red aislada**: Los contenedores de alumnos no tienen acceso a Internet
- ✅ **Dashboard en vivo**: El profesor monitorea el progreso de todos los alumnos

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    RED DEL PROFESOR                      │
│  ┌─────────────────┐                                    │
│  │  exam-manager   │◄──── http://localhost:8080         │
│  │  (FastAPI + UI) │                                    │
│  └────────┬────────┘                                    │
│           │                                             │
├───────────┼─────────────────────────────────────────────┤
│           │         RED INTERNA (sin Internet)          │
│           ▼                                             │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │ student-alumno1 │  │ student-alumno2 │  ...         │
│  │   (JupyterLab)  │  │   (JupyterLab)  │              │
│  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Inicio Rápido

### Requisitos previos

- Docker Desktop instalado y funcionando
- Docker Compose v2+
- 4GB+ RAM disponible

### 1. Levantar el sistema

```bash
# Clonar/descargar el proyecto
cd docker_ipd

# Construir y levantar todo el sistema
docker compose up --build

# En Windows (alternativa si hay problemas con sockets):
docker compose -f docker-compose.dev.yml up --build
```

### 2. Acceder a las interfaces

| Interfaz | URL | Descripción |
|----------|-----|-------------|
| Panel Profesor | http://localhost:8080 | Gestión de exámenes y dashboard |
| Acceso Alumno | http://localhost:8080/student | Login de alumnos |

## 📖 Guía de Uso

### Para el Profesor

#### 1. Crear un examen

1. Accede a http://localhost:8080/professor/exams
2. Haz clic en **"Crear Examen"**
3. Rellena los datos:
   - **Nombre**: Ej. "Examen Python Final"
   - **Asignatura**: Ej. "Programación"
   - **Duración**: 60 minutos
   - **Preguntas**: 3
4. **Activa** el examen cuando esté listo

#### 2. Editar preguntas del examen

1. En la tarjeta del examen, haz clic en **"Editar Preguntas"**
2. Usa el **Editor de Preguntas** para:
   - **Añadir preguntas** con título, descripción (Markdown) e instrucciones
   - **Código inicial** que verá el alumno en cada notebook
   - **Subir PDFs** con el enunciado completo
   - **Adjuntar archivos de datos** (CSV, JSON, imágenes...)
   - Asignar **puntos** a cada pregunta
3. Haz clic en **"Generar Notebooks"** para crear los notebooks automáticamente

#### 3. Monitorear durante el examen

1. Desde el listado de exámenes, haz clic en **"Dashboard"**
2. Verás en tiempo real:
   - **Progreso General**: Distribución de alumnos por pregunta (Q1, Q2, Q3...)
   - Lista de alumnos conectados con barra de progreso
   - Estado de cada alumno (En curso / Entregado)
   - Tiempo restante individual
   - Preguntas desbloqueadas por alumno

#### 4. Acciones disponibles

| Acción | Descripción |
|--------|-------------|
| **+5 min** | Añade 5 minutos extra a un alumno |
| **🔓 Desbloquear** | Desbloquea la siguiente pregunta |
| **📤 Forzar entrega** | Fuerza la entrega de un alumno |
| **Desbloquear Todos** | Desbloquea la siguiente pregunta para todos |

#### 5. Ver entregas

1. Accede a http://localhost:8080/professor/submissions
2. Selecciona el examen
3. Descarga los ZIP de cada alumno

### Para el Alumno

1. Accede a http://localhost:8080/student
2. Selecciona el examen activo
3. Introduce tu ID y nombre completo
4. Haz clic en **"Comenzar Examen"**
5. Se abrirá JupyterLab con tu workspace
6. **Ver PDFs**: Los archivos PDF subidos por el profesor se abren directamente en JupyterLab
7. Trabaja en las preguntas desbloqueadas (Q1, Q2...)
8. Cuando termines, haz clic en **"Entregar"**

## 🧪 Demo: Simular 2 Alumnos

### Paso 1: Crear examen demo

```bash
# El sistema incluye un examen de ejemplo en data/exams/demo_python/
# Solo necesitas crear el examen desde la UI del profesor
```

1. Accede a http://localhost:8080/professor/exams
2. Crea un examen con:
   - Nombre: `Demo Python`
   - Asignatura: `Programación`
   - Duración: `30` minutos
   - Preguntas: `3`
   - Carpeta plantilla: `demo_python`
   - Carpeta materiales: `apuntes_python`
3. **Activa** el examen

### Paso 2: Simular Alumno 1

1. Abre una ventana de navegador en modo incógnito
2. Accede a http://localhost:8080/student
3. Datos:
   - Examen: `Demo Python`
   - ID: `A001`
   - Nombre: `Juan García`
4. Haz clic en "Comenzar Examen"
5. Trabaja en Q1 desde JupyterLab

### Paso 3: Simular Alumno 2

1. Abre otra ventana de navegador en modo incógnito
2. Accede a http://localhost:8080/student
3. Datos:
   - Examen: `Demo Python`
   - ID: `A002`
   - Nombre: `María López`
4. Haz clic en "Comenzar Examen"

### Paso 4: Probar funcionalidades

#### Desbloquear preguntas

1. Desde el Dashboard del profesor
2. Haz clic en **🔓** junto a un alumno para desbloquear Q2
3. O usa **"Desbloquear Siguiente (Todos)"** para todos

#### Verificar desbloqueo

1. En la ventana del alumno
2. Actualiza el explorador de archivos de JupyterLab
3. Verás aparecer la carpeta Q2

#### Añadir tiempo

1. Desde el Dashboard
2. Haz clic en **+5min** junto a un alumno
3. El temporizador del alumno se actualizará

#### Probar entrega

1. Desde la ventana de un alumno
2. Haz clic en **"Entregar"**
3. Confirma la entrega
4. Verifica en http://localhost:8080/professor/submissions

### Paso 5: Verificar entrega generada

```bash
# Las entregas se guardan en:
ls data/submissions/

# Estructura:
# data/submissions/<EXAMEN>/<ALUMNO>/<timestamp>.zip
```

El ZIP contiene:
- Todos los notebooks y archivos del workspace
- `pip_freeze.txt` con las librerías instaladas

## 📁 Estructura del Proyecto

```
docker_ipd/
├── docker-compose.yml          # Orquestación principal
├── docker-compose.dev.yml      # Versión para desarrollo/Windows
├── README.md                   # Esta documentación
│
├── exam-manager/               # Backend FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # API endpoints
│   │   ├── models.py          # Modelos SQLAlchemy
│   │   ├── schemas.py         # Schemas Pydantic
│   │   ├── database.py        # Configuración BD
│   │   └── docker_manager.py  # Gestión contenedores
│   ├── templates/             # HTML (Jinja2)
│   │   ├── index.html
│   │   ├── professor/
│   │   │   ├── exams.html
│   │   │   ├── dashboard.html
│   │   │   └── submissions.html
│   │   └── student/
│   │       ├── login.html
│   │       └── exam.html
│   └── static/
│       └── css/style.css
│
├── student-image/              # Imagen Docker alumno
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── jupyter_notebook_config.py
│   └── scripts/
│       ├── entrypoint.sh
│       ├── unlock_watcher.sh
│       └── submit.sh
│
└── data/                       # Datos persistentes
    ├── exams/                  # Plantillas de exámenes
    │   └── demo_python/
    │       ├── Q1/
    │       ├── Q2/
    │       └── Q3/
    ├── materials/              # Materiales (read-only)
    │   └── apuntes_python/
    ├── work/                   # Workspaces de alumnos
    └── submissions/            # Entregas recibidas
```

## 🔧 Configuración Avanzada

### Personalizar librerías del alumno

Edita `student-image/requirements.txt`:

```txt
# Añade las librerías que necesites
pandas==2.1.3
numpy==1.26.2
tensorflow==2.15.0
# etc.
```

Reconstruye la imagen:

```bash
docker compose build student-image-builder
```

### Crear nuevas plantillas de examen

1. Crea una carpeta en `data/exams/mi_examen/`
2. Dentro, crea subcarpetas `Q1/`, `Q2/`, `Q3/`...
3. Añade notebooks y archivos en cada pregunta
4. Usa `mi_examen` como "Carpeta plantilla" al crear el examen

### Configurar materiales

1. Crea una carpeta en `data/materials/mis_apuntes/`
2. Añade PDFs, Markdown, ejemplos...
3. Usa `mis_apuntes` como "Carpeta materiales" al crear el examen

## 🌐 Despliegue en Red LAN

Para usar en una red local con múltiples equipos:

1. **Servidor** (equipo del profesor):
   ```bash
   docker compose up --build
   ```

2. **Obtener IP del servidor**:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ip addr
   ```

3. **Clientes** (equipos de alumnos):
   - Abrir navegador
   - Acceder a `http://<IP_SERVIDOR>:8000/student`

### Ejemplo

Si la IP del servidor es `192.168.1.100`:
- Profesor: `http://192.168.1.100:8000`
- Alumnos: `http://192.168.1.100:8000/student`

## 🔒 Seguridad y Restricciones

### Red interna (sin Internet)

Los contenedores de alumnos están en una red Docker marcada como `internal: true`, lo que significa:

- ✅ Pueden comunicarse con el exam-manager
- ❌ NO pueden acceder a Internet
- ❌ NO pueden acceder a otros contenedores de alumnos

### Limitaciones de recursos

Cada contenedor de alumno tiene:
- Límite de memoria: 1GB
- Límite de CPU: 50%

### Nota importante

> ⚠️ Este sistema controla el entorno **dentro del contenedor**. No bloquea el acceso al PC del alumno fuera del navegador. Para exámenes de alta seguridad, considere software de proctoring adicional.

## 🐛 Solución de Problemas

### Error: "Cannot connect to Docker daemon"

```bash
# Asegúrate de que Docker Desktop está corriendo
# En Windows, reinicia Docker Desktop
```

### Error: Puerto 8000 en uso

```bash
# Cambia el puerto en docker-compose.yml
ports:
  - "8080:8000"  # Usa 8080 en lugar de 8000
```

### Los contenedores de alumnos no se crean

```bash
# Verifica que la imagen está construida
docker images | grep exambox-student

# Si no aparece, construye manualmente
docker compose build student-image-builder
```

### JupyterLab no carga

1. Espera 10-15 segundos después de iniciar
2. Verifica los logs del contenedor:
   ```bash
   docker logs exambox-student-<id_alumno>
   ```

## 📝 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/exams` | Lista todos los exámenes |
| POST | `/api/exams` | Crea un nuevo examen |
| POST | `/api/exams/{id}/activate` | Activa un examen |
| POST | `/api/students/register` | Registra un alumno |
| POST | `/api/students/{id}/start` | Inicia sesión de alumno |
| GET | `/api/dashboard/{exam_id}` | Datos del dashboard |
| POST | `/api/actions/add-time` | Añade tiempo extra |
| POST | `/api/actions/unlock-question` | Desbloquea pregunta |
| POST | `/api/submit/{session_id}` | Entrega examen |
| GET | `/api/submissions/{exam_id}` | Lista entregas |

## 📄 Licencia

MIT License - Proyecto educativo para prácticas de Docker.

---

**ExamBox** - Sistema de Exámenes con Docker 🐳
