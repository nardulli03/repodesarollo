# Cursos Abiertos

Catálogo comunitario de cursos gratuitos. Los usuarios pueden aportar cursos y declarar si los tomaron. Un administrador revisa los aportes antes de publicarlos. El roadmap personal y privado forma parte del alcance del producto.

Proyecto individual de Desarrollo de Software, sección S34, UTN Facultad Regional La Plata, 2026.

## Arranque con Docker

Requisitos: Git, Docker Desktop con contenedores Linux y Docker Compose. Los puertos locales 5432, 8000 y 5173 deben estar disponibles o ajustarse en `.env`.

Si todavía no tenés una copia del repositorio:

```powershell
git clone https://github.com/nardulli03/repodesarollo.git
Set-Location repodesarollo
git switch dev
```

Desde la raíz del repositorio, prepará la configuración y levantá los servicios:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose build
docker compose up -d --wait postgres
docker compose run --rm --no-deps backend alembic upgrade head
docker compose up -d --wait backend frontend
```

Alembic aplica las migraciones pendientes antes de iniciar la API. PostgreSQL conserva sus datos en el volumen `postgres_data`. Los valores de `.env.example` son para desarrollo local. Mantené `.env` fuera de Git.

### Accesos y verificación

| Servicio | Dirección |
| --- | --- |
| Catálogo | http://localhost:5173 |
| Estado de Nginx | http://localhost:5173/health |
| API de cursos a través de Nginx | http://localhost:5173/api/v1/courses |
| Estado del backend | http://localhost:8000/health |
| Documentación interactiva de la API | http://localhost:8000/docs |
| PostgreSQL desde la computadora | `127.0.0.1:5432` |

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:5173/health
Invoke-RestMethod http://localhost:5173/api/v1/courses
```

Los tres servicios deben figurar como `healthy`. Los endpoints de estado devuelven `{"status":"ok"}` y comprueban la respuesta HTTP de cada servicio. La consulta del catálogo comprueba además el recorrido Nginx → FastAPI → PostgreSQL. En una base nueva devuelve `{"items":[],"total":0,"page":1,"page_size":20}`.

### Actualizar y detener

Después de modificar el código o incorporar una migración, repetí el bloque de arranque desde `docker compose build`. Para detener los servicios y conservar el volumen de datos:

```powershell
docker compose down
```

## Estado actual

- Catálogo público conectado a PostgreSQL. El frontend incluye búsqueda, paginación, reintento y estados de carga, error y lista vacía.
- API de borradores, envío a revisión, aprobación y rechazo. Incluye control de versión y validación de permisos.
- Validación de JWT en cookie, sesiones revocables, consulta de identidad y protección CSRF. Las pruebas crean usuarios y sesiones para verificar esos controles.
- Migración inicial de las cinco tablas implementadas y arranque de Docker Compose con healthchecks.

Quedan pendientes el registro y login de usuarios, la verificación de correo, la recuperación de contraseña y el rate limit. El roadmap cuenta con reglas y pruebas unitarias. Su integración con la API y la interfaz sigue pendiente.

La imagen del backend medida en T7 fue de **273,97 MB** frente al objetivo de menos de 100 MB. La del frontend medida en T9 fue de **20,90 MB** frente al objetivo de menos de 30 MB. El [plan de implementación](docs/IMPLEMENTATION_PLAN.md) conserva la evidencia por ticket y la retrospectiva de T11.

## Desarrollo local

Usá Python 3.14, uv, Node.js 24 y pnpm. Esta modalidad ejecuta FastAPI y Vite en tu computadora y mantiene PostgreSQL en Docker. Dejá libres los puertos de la API y Vite si ya levantaste sus contenedores.

En la raíz, prepará `.env` con el comando del apartado de Docker si todavía no existe. Luego:

```powershell
docker compose up -d --wait postgres
Set-Location backend
uv sync --locked
$env:DATABASE_URL = "postgresql+psycopg://cursos_dev:cambiar_solo_para_desarrollo@127.0.0.1:5432/cursos_abiertos"
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

Ajustá `DATABASE_URL` a las credenciales y al puerto publicados en tu configuración local. En otra terminal, desde la raíz:

```powershell
Set-Location frontend
pnpm install --frozen-lockfile
pnpm dev
```

Vite dirige `/api` a `http://127.0.0.1:8000` en desarrollo local. En Compose, Nginx envía esas solicitudes al servicio `backend`.

## Pruebas

### Backend con PostgreSQL de testing

Desde la raíz del repositorio:

```powershell
docker compose -p cursos-tests -f docker-compose.test.yml up -d --wait
Set-Location backend
uv sync --locked
$env:TEST_DATABASE_URL = "postgresql+psycopg://cursos_test:cursos_test_local@127.0.0.1:5433/cursos_test"
uv run python -m pytest tests -q --cov=app --cov-branch --cov-report=term-missing
```

Las pruebas de integración y migraciones usan esquemas temporales de `cursos_test`. La verificación del ciclo registró **312 pruebas aprobadas y 92% de cobertura de `app` con ramas**.

Para detener la base de testing desde `backend`:

```powershell
docker compose -p cursos-tests -f ../docker-compose.test.yml down
```

### Frontend

Desde la raíz del repositorio:

```powershell
Set-Location frontend
pnpm install --frozen-lockfile
pnpm test:coverage
pnpm lint
pnpm build
```

La verificación de T6 registró **23 pruebas aprobadas**, lint y build correctos. La cobertura de `useCursos.js` fue de 97,67% de líneas y 88,13% de ramas.

## Stack y documentación

React 19, Vite y pnpm en el frontend. FastAPI, Uvicorn, uv, SQLAlchemy, Psycopg y Alembic en el backend. PostgreSQL 18.6, Nginx y Docker Compose en infraestructura. El repositorio versiona `backend/uv.lock` y `frontend/pnpm-lock.yaml`.

| Documento | Contenido |
| --- | --- |
| [SPEC](docs/SPEC.md) | Alcance y decisiones del producto |
| [PRD](docs/PRD.md) | Personas, historias y criterios de aceptación |
| [TRD](docs/TRD.md) | Arquitectura y decisiones técnicas |
| [UX-UI](docs/UX-UI.md) | Componentes, estilos y estados |
| [APPFlow](docs/APPFlow.md) | Pantallas y navegación |
| [BackendSchema](docs/BackendSchema.md) | Modelo y contratos previstos |
| [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) | Tareas, evidencia y retrospectiva |
| [Git Workflow](docs/GIT_WORKFLOW.md) | Registro del flujo de trabajo |
| [Autoevaluación](docs/RUBRICA.md) | Apoyo complementario |
| [SPEC oficial](docs/referencias/SPEC.md) | Especificación recibida |
| [Borrador del aula](docs/referencias/SPEC-borrador-clase-2026-10-20.md) | Antecedente de la especificación |
| [Changelog](CHANGELOG.md) | Cambios por versión y trabajo sin publicar |

## Flujo de trabajo

Las ramas de trabajo nacen desde `dev` y se integran mediante PR con base `dev`. El flujo reserva `main` para releases desde `dev`, con changelog actualizado y tag anotado. `v0.1.0` corresponde al scaffold inicial. La evidencia del ciclo y sus desvíos quedan registrados en el plan de implementación.
