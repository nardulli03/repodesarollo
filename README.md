# Cursos Abiertos

## Cómo levantar

Requisitos:

- Git.
- Docker Desktop iniciado con contenedores Linux.
- Docker Compose.
- Puertos 5432, 8000 y 5173 disponibles.

Desde PowerShell:

```powershell
git clone https://github.com/nardulli03/repodesarollo.git
cd repodesarollo
git switch dev
Copy-Item .env.example .env
docker compose up --build
```

Estas instrucciones corresponden al scaffold integrado en dev
después del merge del ticket T4. El release v0.1.0 todavía está pendiente.

La primera ejecución descarga las imágenes e instala las dependencias.
Mantener la terminal abierta mientras se utilizan los servicios.

Si el repositorio ya está clonado, no repetir el clone.
Si .env ya existe, revisar su configuración antes de reemplazarlo.

### Accesos

| Servicio | Dirección |
| --- | --- |
| Frontend | http://localhost:5173 |
| Estado del backend | http://localhost:8000/health |
| Documentación de la API | http://localhost:8000/docs |
| Listado de cursos | http://localhost:8000/api/v1/courses |
| PostgreSQL desde la computadora | localhost:5432 |

El frontend debe mostrar “Todavía no hay cursos publicados”.
El endpoint de cursos devuelve una colección vacía con formato paginado.

### Verificación

En otra terminal, desde la raíz del repositorio:

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8000/health
```

Los servicios postgres, backend y frontend deben aparecer en estado Up.

GET /health debe devolver:

```json
{"status":"ok"}
```

Este endpoint confirma que la API responde; todavía no verifica
la conexión con PostgreSQL.

### Detener los servicios

Desde otra terminal ubicada en la raíz:

```powershell
docker compose down
```

El volumen de PostgreSQL se conserva. No agregar -v si se quieren
mantener sus datos.

### Aplicar cambios de código

En este scaffold no se configuraron volúmenes para sincronizar
el código local con los contenedores. Después de modificar archivos:

```powershell
docker compose up --build
```

## Descripción del producto

Cursos Abiertos es una webapp de comunidad de cursos gratuitos.
Los usuarios aportan recursos de distintas plataformas y declaran
si los tomaron. Un administrador valida los aportes antes de
incorporarlos al catálogo comunitario.

Cada usuario organiza su aprendizaje en un roadmap personal y privado.

- Materia: Desarrollo de Software, sección S34.
- Institución: UTN Facultad Regional La Plata.
- Ciclo lectivo: 2026.
- Modalidad: individual.
- Repositorio: https://github.com/nardulli03/repodesarollo

## Estado actual

El ticket docente del 27/10/2026 habilitó el desarrollo
del scaffold mínimo.

| Ticket | Estado |
| --- | --- |
| T1: estructura y configuración inicial | Integrado en dev |
| T2: backend mínimo | Integrado en dev |
| T3: frontend mínimo | Integrado en dev |
| T4: Docker Compose de desarrollo | Verificado localmente; pendiente de integración |
| T5: release v0.1.0 | Pendiente |

Verificaciones realizadas durante el desarrollo:

- Backend local con GET /health y GET /api/v1/courses.
- Frontend conectado al endpoint de cursos.
- Estados de carga, error y catálogo vacío.
- pnpm lint sin errores y pnpm build correcto durante T3.
- Tres servicios Docker en estado Up.
- GET /health respondió {"status":"ok"} dentro del entorno Docker.
- Frontend accesible desde http://localhost:5173.

### Límites del scaffold

El catálogo todavía devuelve datos vacíos.
PostgreSQL está ejecutándose y DATABASE_URL está configurada,
pero el backend no realiza consultas a la base.

Todavía no están implementados:

- Registro, login con JWT y verificación de correo.
- Recuperación de contraseña y rate limit.
- CRUD de cursos y validación de aportes.
- Roadmap personal y progreso.

Estas funcionalidades pertenecen al desarrollo posterior del MVP.
No se presenta el scaffold como la aplicación completa.

Los Dockerfiles son simples, sin multi-stage ni healthchecks.
Las pruebas automatizadas y mejoras de imágenes quedan para
los tickets correspondientes.

## Stack

- Frontend: React 19, Vite y pnpm.
- Backend: FastAPI, uv y Uvicorn.
- Base de datos: PostgreSQL 18.6.
- Infraestructura de desarrollo: Docker y Docker Compose.

Las versiones verificadas y decisiones técnicas se registran
en [TRD.md](docs/TRD.md).

## Desarrollo local sin Docker

Esta alternativa requiere Python, uv, Node.js y pnpm.
Las versiones utilizadas se encuentran en el TRD.

### Backend

Desde la raíz del repositorio:

```powershell
cd backend
uv sync --locked
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

En otra terminal, desde la raíz:

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

El proxy de Vite utiliza http://127.0.0.1:8000 por defecto.
En Docker, BACKEND_INTERNAL_URL lo dirige a http://backend:8000.

Detener los servidores locales antes de iniciar Compose
si utilizan los mismos puertos.

## Configuración y dependencias

- .env.example contiene valores de ejemplo para desarrollo.
- .env contiene la configuración local y no se versiona.
- Las credenciales de ejemplo no deben utilizarse en producción.
- backend/uv.lock y frontend/pnpm-lock.yaml se versionan.
- .venv, node_modules, dist y las cachés de Python no se versionan.

## Documentación

| Documento | Contenido |
| --- | --- |
| [SPEC](docs/SPEC.md) | Alcance, origen y decisiones del producto |
| [PRD](docs/PRD.md) | Personas, historias, requisitos y aceptación |
| [TRD](docs/TRD.md) | Arquitectura, stack y decisiones técnicas |
| [UX-UI](docs/UX-UI.md) | Tokens, componentes, estados y adaptación |
| [APPFlow](docs/APPFlow.md) | Pantallas, navegación y relación con API |
| [BackendSchema](docs/BackendSchema.md) | Modelo de datos y contratos previstos |
| [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) | Tareas, dependencias y evidencia |
| [Git Workflow](docs/GIT_WORKFLOW.md) | Ramas, commits, revisión y releases |
| [Autoevaluación](docs/RUBRICA.md) | Apoyo complementario; no es rúbrica oficial |
| [SPEC oficial](docs/referencias/SPEC.md) | Especificación recibida sin modificaciones |
| [Borrador del aula](docs/referencias/SPEC-borrador-clase-2026-10-20.md) | Antecedente de la especificación |

Los documentos describen el producto objetivo.
El apartado “Estado actual” identifica lo efectivamente implementado.
Los criterios futuros no se presentan como pruebas ejecutadas.

## Flujo de trabajo

Desde los tickets del 27/10/2026:

1. Las ramas de trabajo nacen desde dev.
2. Cada ticket se integra mediante pull request hacia dev.
3. main recibe releases desde dev, con CHANGELOG actualizado
   y tag anotado vX.Y.Z.

Se utilizan commits convencionales y autorrevisión por tratarse
de un trabajo individual.

Detalle en [GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).
El historial previo se conserva; no se afirma cumplimiento retroactivo.

## Tests unitarios de cursos
Desde la raíz:

```powershell
cd backend
uv sync --locked
uv run python -m pytest tests/test_cursos_unit.py -q --cov=app.cursos.rules --cov-branch --cov-report=term-missing
```

Resultado verificado: 153 tests aprobados y 97 % de cobertura
del módulo app.cursos.rules, incluyendo ramas.

### Pruebas del backend con PostgreSQL
Requiere Docker Desktop iniciado y uv instalado.

```powershell
docker compose -p cursos-tests -f docker-compose.test.yml up -d --wait
cd backend
uv sync --locked
$env:TEST_DATABASE_URL = "postgresql+psycopg://cursos_test:cursos_test_local@127.0.0.1:5433/cursos_test"
uv run python -m pytest tests -q --cov=app --cov-branch --cov-report=term-missing
```

Las credenciales son exclusivas de testing local. Las pruebas crean
tablas en un esquema temporal dentro de cursos_test; no ejecutan
migraciones sobre la base de desarrollo.

Para eliminar el contenedor de pruebas, desde backend:

```powershell
docker compose -p cursos-tests -f ../docker-compose.test.yml down
```

