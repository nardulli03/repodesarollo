# TRD — Cursos Abiertos

**Versión documental:** 2.1. **Actualización:** 28/10/2026.
**Repositorio:** https://github.com/nardulli03/repodesarollo
**Modalidad:**individual.

Este documento distingue el scaffold ya verificado de la arquitectura objetivo del MVP. T1–T3 están integrados en `dev`; T4 funciona localmente y está pendiente de commit, PR e integración según la evidencia disponible. No se afirma un release `v0.1.0` publicado ni una aprobación individual de toda la documentación.

El ticket docente del 27/10/2026 habilitó el scaffold mínimo: estructura, backend, frontend y Compose. Para estos tickets se excluyen tests automatizados, multi-stage, healthchecks y optimización de imágenes.

## 1. Stack y versiones

### 1.1 Versiones comprobadas durante T2 y T3

| Componente | Versión verificada | Contexto y evidencia |
| --- | --- | --- |
| Python | 3.14.6 | Entorno local Windows: `python --version`. |
| uv | 0.12.1 | Entorno local: `uv --version`; fijado también al instalar uv en la imagen backend. |
| FastAPI | 0.162.0 | Resolución de dependencias de T2. |
| Uvicorn | 0.54.0 | Resolución de dependencias de T2. |
| Node.js | 24.16.0 | Entorno local: `node --version`. |
| pnpm | 11.13.0 | Gestor de frontend; fijado también al instalarlo en la imagen frontend. |
| React | 19.3.1 | `pnpm list react react-dom vite --depth 0`. |
| React DOM | 19.3.1 | Mismo comando; coincide con React. |
| Vite | 8.3.5 | Listado de dependencias, build y log de Vite dentro de Docker. |

Frontend escrito en JavaScript/JSX y CSS propio, con ESLint. Las dependencias efectivas y transitivas quedan registradas en `backend/uv.lock` y `frontend/pnpm-lock.yaml`; no se usa `package-lock.json` como lockfile del proyecto.

### 1.2 Docker y entorno verificados durante T4

| Componente | Versión o referencia | Estado |
| --- | --- | --- |
| Docker Engine/CLI | 29.8.0 | `docker --version` y `docker info`. |
| Docker Compose | 5.5.1 | `docker compose version`. |
| Motor | Linux, contexto `desktop-linux` | Docker Desktop con WSL2. |
| PostgreSQL | Imagen `postgres:18.6` | Descargada; logs confirman PostgreSQL 18.6 y servidor listo. |
| Base backend | `python:3.14-slim` | Imagen construida y contenedor operativo. |
| Base frontend | `node:24-bookworm-slim` | Imagen construida y contenedor operativo. |

`python:3.14-slim` y `node:24-bookworm-slim` son referencias de imágenes, no mediciones del patch exacto ejecutado en el contenedor. Las versiones locales de Python y Node no se atribuyen automáticamente a esas imágenes. Los tags pueden actualizarse; para reproducibilidad estricta se fijarán patch/digest y se registrarán valores efectivos. No se afirma que ese fijado ya esté hecho.

### 1.3 Componentes previstos para etapas posteriores

| Área | Selección prevista | Estado |
| --- | --- | --- |
| Navegación SPA | React Router | Sin instalación ni rutas de aplicación implementadas. |
| Persistencia | SQLAlchemy 2, psycopg 3, Alembic | Sin instalación/versión verificada ni migraciones. |
| Seguridad | PyJWT y pwdlib con Argon2id | Diseño pendiente de implementación. |
| Correo de desarrollo | SMTP y Mailpit | Fuera del Compose mínimo de T4. |
| Pruebas | pytest, Vitest | Planificadas para tickets posteriores; no ejecutadas. |

La referencia FastAPI 0.158.2 de la SPEC era orientativa; la versión realmente resuelta es 0.162.0. Se mantiene React 19 y PostgreSQL 18.6. No se presenta una herramienta prevista como instalada.

## 2. Decisiones técnicas

| ID | Tema | Alternativas | Elección y motivo | Estado |
| --- | --- | --- | --- | --- |
| TD-01 | Autenticación | JWT, sesión opaca, proveedor externo | JWT por requisito previo; cookie HttpOnly y sesión revocable, sin refresh en MVP. | Pendiente. |
| TD-02 | Paginación | Cursor, offset + total | `page`, `page_size`, `total`, `items`; simple de consumir y demostrar. | Contrato implementado sobre colección vacía; sin consultas persistentes. |
| TD-03 | Errores API | Respuestas particulares o envelope único | Envelope con code/message/fields/request_id para MVP. | Pendiente; actualmente validaciones usan formato por defecto de FastAPI. |
| TD-04 | Validación de enlaces | Fetch en API, automática o humana | Admin abre enlace y registra revisión; evita fetch de URLs arbitrarias en servidor. | Pendiente. |
| TD-05 | Roadmap | Copias, relación usuario-curso, múltiples recorridos | Una cabecera por usuario con items referenciados, orden y progreso. | Pendiente. |
| TD-06 | Contraseñas | bcrypt, Argon2id | Argon2id con biblioteca y parámetros calibrados; no cifrado reversible. | Pendiente. |
| TD-07 | Correo | Worker/outbox o SMTP síncrono | Envío tras commit con timeout de 10 s y reenvío; reduce alcance sin prometer entrega garantizada. | Pendiente. |
| TD-08 | UI | TypeScript/JavaScript, MUI/CSS | JavaScript/JSX y CSS propio mobile-first; menos dependencias y reglas visibles. | Pantalla mínima implementada; guía completa pendiente. |
| TD-09 | Rate limit | Memoria, Redis o PostgreSQL | Contadores atómicos PostgreSQL compartidos; sin agregar Redis. | Pendiente. |
| TD-10 | Ejecución de desarrollo | Procesos locales o Compose | Tres servicios con Dockerfiles de una sola etapa; cumple ticket sin optimizaciones anticipadas. | Verificado en T4. |
| TD-11 | Proxy | URL absoluta en navegador o proxy Vite | `/api` conserva la ruta y se dirige al backend configurable por entorno. | Verificado local y Docker. |

## 3. Arquitectura

### 3.1 Arquitectura actual del scaffold

```mermaid
flowchart TD
    BROWSER["Navegador: localhost:5173"] --> FE["Frontend: Vite y React"]
    FE -->|"/api/v1/courses"| BE["Backend: FastAPI, puerto 8000"]
    BE --> EMPTY["Respuesta paginada vacía"]
    PG[("PostgreSQL 18.6: activo")]
```

No se dibuja una conexión funcional backend→base porque todavía no se implementaron consultas. Compose entrega `DATABASE_URL` al backend, pero tener esa variable no prueba una conexión.

`Catalogo.jsx` usa fetch sobre `/api/v1/courses` y muestra carga, error, catálogo vacío o lista. El backend devuelve `items: []`, `total: 0` y los parámetros de página. La página React todavía no incluye búsqueda real, menú, navegación, autenticación ni controles completos de paginación.

### 3.2 Organización por dominio

Estructura relevante existente, sin enumerar archivos de plantilla sin función de negocio:

```text
repodesarollo/
  backend/
    Dockerfile
    pyproject.toml
    uv.lock
    app/
      __init__.py
      main.py
      cursos/
        __init__.py
        router.py
      identidad/     (estructura reservada)
      aportes/       (estructura reservada)
      roadmap/       (estructura reservada)
      shared/        (estructura reservada)
  frontend/
    Dockerfile
    package.json
    pnpm-lock.yaml
    vite.config.js
    index.html
    public/
    src/
      main.jsx
      App.jsx
      index.css
      app/           (estructura reservada)
      features/
        catalogo/
          Catalogo.jsx
        identidad/   (estructura reservada)
        aportes/     (estructura reservada)
        revision/    (estructura reservada)
        roadmap/     (estructura reservada)
      shared/        (estructura reservada)
      styles/        (estructura reservada)
  docs/
  docker-compose.yml
  .env.example
  .gitignore
  CHANGELOG.md
  README.md
```

Las carpetas vacías se conservan con `.gitkeep`; eso no significa que el módulo esté implementado. Al incorporar archivos reales se pueden retirar esos marcadores. La separación por dominio corresponde a Screaming Architecture.

### 3.3 Arquitectura objetivo del MVP

React presenta estados y consume REST bajo `/api/v1`. Los routers traducen HTTP; servicios de aplicación coordinan reglas, repositorios y transacciones; funciones puras de negocio no dependen de HTTP ni BD; repositorios acceden a PostgreSQL.

```mermaid
flowchart TD
    HTTP["Router del dominio"] --> APP["Servicio de aplicación"]
    APP --> RULE["Reglas puras"]
    APP --> REPO["Repositorio"]
    REPO --> DB[(PostgreSQL)]
```

Los dominios incorporarán `service.py`, `rules.py`, `repository.py`, `models.py` y `schemas.py` según responsabilidad. Migraciones, pruebas y configuración persistente se agregarán cuando correspondan sus tickets. El frontend separará componentes, hooks y acceso API conforme crezcan los módulos. Aportes expresa el ciclo de un curso; no duplica la entidad curso. Evitar importaciones circulares entre dominios.

### 3.4 Servicios Compose implementados

| Servicio | Construcción/imagen | Dirección desde host | Responsabilidad |
| --- | --- | --- | --- |
| postgres | `postgres:18.6` | `127.0.0.1:5432` por defecto | Base activa con volumen nombrado. |
| backend | Build `./backend`, base `python:3.14-slim` | `127.0.0.1:8000` por defecto | FastAPI con /health y listado vacío. |
| frontend | Build `./frontend`, base `node:24-bookworm-slim` | `127.0.0.1:5173` por defecto | Vite, React y proxy de API. |

Volumen `postgres_data` montado en `/var/lib/postgresql`, con datos de la imagen PostgreSQL 18 dentro de su directorio de versión. No se utiliza montaje de fuentes locales ni recarga sincronizada entre host y contenedores. Tras cambiar código se reconstruye con `docker compose up --build`.

Los Dockerfiles instalan mediante lockfiles: backend `uv sync --locked --no-dev`; frontend `pnpm install --frozen-lockfile`. No se copian `.venv` ni `node_modules` del host para ejecutarlos en Linux. Backend escucha `0.0.0.0:8000` y Vite `0.0.0.0:5173` dentro de los contenedores; la publicación hacia la computadora se limita a 127.0.0.1.

`depends_on` ordena el inicio: postgres→backend→frontend. No verifica disponibilidad de la BD. El scaffold no depende todavía de consultas SQL, por lo que no se agrega espera ni healthcheck en este ticket. La disponibilidad y reintentos se resolverán al incorporar persistencia, mediante cambio documentado. Servicios migrate/Mailpit no forman parte de T4.

### 3.5 Proxy local y Docker

El navegador siempre usa `/api/v1/courses` mediante el origen de Vite. La configuración conserva `/api` sin rewrite:

- Sin variable: destino `http://127.0.0.1:8000`, para procesos locales.
- En Compose: `BACKEND_INTERNAL_URL=http://backend:8000`.

`backend` es nombre de servicio resoluble entre contenedores. Dentro de frontend, localhost apuntaría al propio contenedor, no a FastAPI. No se requiere habilitar CORS para esta comunicación por proxy. No se agrega `allowedHosts: true` ni configuración abierta innecesaria.

## 4. Convenciones y configuración

### 4.1 Flujo Git vigente

Desde el ticket del 27/10/2026: ramas `feat/T{N}-descripcion-corta` y `fix/descripcion-corta` nacen desde `dev` y se integran en `dev` mediante PR. `main` recibe releases desde `dev` con CHANGELOG y tag anotado `vX.Y.Z`. No se realizan commits directos de trabajo en main ni merges de feature directamente a main.

Detalle: [GIT_WORKFLOW.md](GIT_WORKFLOW.md). Trabajo individual con autorrevisión, commits convencionales y evidencia real; no se presenta este flujo como aplicado retroactivamente. T4 todavía no se declara mergeado y T5 todavía no se declara publicado.

### 4.2 Contratos actualmente implementados

| Método/ruta | Comportamiento actual |
| --- | --- |
| GET /health | 200 `{"status":"ok"}`; confirma que responde la API, sin revisar BD. |
| GET /api/v1/courses | 200 `{"items":[],"total":0,"page":1,"page_size":20}` con parámetros de consulta. |
| GET /docs | Documentación interactiva generada por FastAPI. |

`page` entero >=1; `page_size` entero entre 1 y 100, por defecto 20. Una entrada inválida usa actualmente 422 de FastAPI con `detail`. No están implementados filtros, consultas a BD, autenticación, permisos ni envelope propio.

El contrato objetivo de errores del MVP es:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Revisá los datos",
    "fields": {"title": "Campo requerido"},
    "request_id": "uuid"
  }
}
```

Su implementación posterior debe adaptar también 422 sin exponer stack ni SQL. Estados previstos: 401 sesión inválida, 403 permiso/CSRF/correo pendiente, 404 ausente o ajeno, 409 duplicado/versión/estado, 422 datos, 429 cuota con Retry-After, 503 dependencia caída y 413 payload >256 KiB. No se afirma que estos controles ya existan.

### 4.3 Variables del scaffold

| Variable | Ejemplo de desarrollo | Uso actual |
| --- | --- | --- |
| POSTGRES_DB | cursos_abiertos | Inicialización de base. |
| POSTGRES_USER | cursos_dev | Usuario de desarrollo. |
| POSTGRES_PASSWORD | cambiar_solo_para_desarrollo | Credencial de ejemplo, no producción. |
| POSTGRES_PORT | 5432 | Puerto publicado en host. |
| BACKEND_PORT | 8000 | Puerto publicado del backend. |
| FRONTEND_PORT | 5173 | Puerto publicado del frontend. |
| DATABASE_URL | postgresql+psycopg://cursos_dev:cambiar_solo_para_desarrollo@postgres:5432/cursos_abiertos | Entregada al backend, sin conexión implementada. |
| BACKEND_INTERNAL_URL | http://backend:8000 | Compose la establece para el proxy de Vite; fallback local 127.0.0.1:8000. |

Compose lee `.env` para interpolar variables; el ejemplo `.env.example` se versiona y `.env` permanece ignorado. La contraseña en URL y POSTGRES_PASSWORD deben coincidir. Los puertos publicados pueden cambiar, sin cambiar puertos internos ni el nombre postgres de la URL. No usar credenciales de ejemplo en producción.

### 4.4 Variables y observabilidad previstas

| Variable futura | Propósito |
| --- | --- |
| JWT_SIGNING_KEY | Secreto aleatorio mínimo32 bytes, distinto de otros. |
| JWT_ISSUER / JWT_AUDIENCE | Origen/destino permitido. |
| CSRF_SIGNING_KEY | Firma de token CSRF. |
| RATE_LIMIT_KEY | HMAC por propósito para claves de cuota. |
| APP_PUBLIC_URL | Origen configurado para enlaces de correo. |
| SMTP_HOST / SMTP_PORT | Mailpit u otro SMTP. |
| SMTP_USER / SMTP_PASSWORD / SMTP_TLS | Configuración de correo según entorno. |
| COOKIE_SECURE | False solo en HTTP local; true en HTTPS. |
| DEMO_ADMIN_PASSWORD / DEMO_USER_PASSWORD | Credenciales externas a Git para seeds. |

Estas variables no son requeridas para arrancar el scaffold actual; se incorporarán con sus módulos. Nunca poner secretos en variables VITE_*. El registro estructurado con request_id y el middleware de excepciones son diseño posterior. Actualmente se verificaron logs de arranque; no se afirma un sistema completo de observabilidad. Nunca registrar password, cookies ni tokens.

## 5. Restricciones y estado de cumplimiento

| Restricción | Estado actual | Trabajo posterior |
| --- | --- | --- |
| Paginación de listados | Endpoint vacío acepta page/page_size y devuelve envelope. | Consultas reales, todos los listados y controles de UI. |
| Mobile-first progresivo | CSS base de una columna, mejora con min-width:768px. | Resto de pantallas y breakpoints de guía. |
| Menú sándwich | No implementado en pantalla mínima. | Header accesible con foco y ARIA. |
| Screaming Architecture | Carpetas por dominio y router/componente de catálogo separados. | Servicios, repositorios y módulos reales. |
| Material claro | Fondo blanco, azul, tipografía de sistema y estados básicos. | Tokens/componentes completos, contraste y navegación. |
| Entorno Compose | Tres servicios Up; health y UI verificados. | Repetición en clon limpio antes de cerrar release. |

El scaffold no acredita cumplimiento total del MVP, accesibilidad completa ni pruebas de persistencia de negocio. La estructura reservada tampoco se presenta como funcionalidad terminada.

## 6. Autenticación, correo y límites — diseño pendiente

Estas funciones pertenecen al MVP posterior. Ninguna está implementada en T1–T4. Las bibliotecas y parámetros pendientes se registrarán al construir cada módulo.

### 6.1 JWT y autorización

JWT firmado identifica al usuario; no cifra sus claims ni reemplaza permisos. Claims sub UUID, jti UUID, iss, aud, iat, nbf, exp; solo HS256, secreto mínimo 32 bytes, vigencia 15 min, margen de reloj 30 s. Validar firma, algoritmo permitido, presencia/tipos, fechas/emisor/audiencia. Sin secretos ni password en payload. Sesión en BD asociada a jti permite logout/reset inmediato. Cada petición consulta estado actual y email verificado; rol y propietario desde BD. Sin refresh: vence y exige login.

Cookie HttpOnly, SameSite=Lax, Path=/, Secure en HTTPS; `__Host-access_token` en producción sin Domain, `access_token_dev` en HTTP local. No localStorage, ni token en URL ni JSON de login. GET csrf emite cookie firmada no HttpOnly y token para header X-CSRF-Token; servidor valida firma, cookie, vencimiento 12 h y Origin exacto permitido para toda mutación, incluso auth pública. Secretos distintos. Renovar CSRF en login/logout; no aceptar variantes de origen ni confiar encabezados de proxy arbitrarios.

Hash Argon2id, parámetros de biblioteca registrados/calibrados al implementar; no truncar contraseña ni loguearla. Login inválido uniforme y hash ficticio para cuenta inexistente. Email no verificado solo se informa después de contraseña correcta. Un registro duplicado no cambia credenciales.

### 6.2 Correo

Tokens opacos de 32 bytes aleatorios, solo SHA-256 persistido. Verificación 24 h, recuperación 30 min, uso único. Registro crea usuario pendiente y token; commit antes del SMTP; recuperación/reenvío invalidan anteriores dentro de transacción. Enviar fuera de transacción y con timeout: si SMTP falla, cuenta/token permanecen y la UI ofrece reenvío o nueva recuperación. Endpoints de solicitud siguen respuesta 202 genérica por privacidad, tanto para duplicados como inexistentes y fallos SMTP; no prometen entrega. Reenvío de verificación envía solo si existe y está pendiente. Registro duplicado no reenvía: usar endpoint específico. Sin cola ni worker en MVP; caída entre commit/envío requiere reintento del usuario.

Links desde APP_PUBLIC_URL configurada: `/verificar-correo#token=...` y `/restablecer-contrasena#token=...`. Capturar fragmento en memoria, limpiar historial y enviar token en body; sin terceros en pantallas. GET no consume tokens. Verificación requiere botón confirmar y no inicia sesión. Reset bloquea fila usuario, valida/consume token, cambia hash y revoca sesiones atómicamente. Login bloquea la misma fila al verificar hash vigente/crear sesión para impedir sesiones con contraseña anterior tras reset. Consumir token una sola vez bajo bloqueo; no enviar correo dentro del lock.

### 6.3 Rate limit compartido

Ventanas fijas UTC: login 20 intentos/IP/15 min y 10 intentos/email/15 min, contando todos los intentos para cortar concurrencia antes del hashing. Registro 10/IP/h; recuperación y reenvío 10/IP/h y 3/email/h. Supresión por email de correo devuelve 202 genérico; cuota pública excedida devuelve 429 y Retry-After en segundos. IP/email almacenados como HMAC con propósito separado. UPSERT atómico en transacción propia confirma cuota aun si negocio falla; si BD cae devuelve 503, no omite limitación. No bloquear permanentemente. No confiar X-Forwarded-For de clientes. Ventanas fijas admiten ráfagas cerca de cambio y afectan redes compartidas: limitaciones documentadas.

## 7. Integridad y operación — diseño pendiente

El scaffold aún no tiene ORM, migraciones ni operaciones persistentes. Las reglas siguientes se implementarán con los módulos de dominio.

UUID, UTC, consultas parametrizadas y Pydantic rechaza campos extra. expected_version en escrituras sobre curso/roadmap; actualización condicional y 409 si desactualizado. Reordenar roadmap en una transacción bloqueando cabecera; restricción de posiciones diferible. Agregar bloquea curso y cabecera; solo publicados. Edición/archivo de curso usa bloqueo de la misma fila para resolver carrera: si cambia primero, no admite alta; si alta termina primero, conserva item con aviso. No borrar referencias.

## 8. Riesgos técnicos

| Riesgo | Probabilidad/impacto | Mitigación |
| --- | --- | --- |
| SMTP cae | Media/alto | Mailpit demo, timeout, reenvío, no afirmar entrega. |
| Variación de imágenes base con tag de versión mayor/menor | Media/medio | Registrar versiones efectivas y fijar patch o digest al preparar una entrega reproducible definitiva. |
| Alcance excesivo | Alta/alto | Un roadmap y categorías precargadas; sin worker ni extras P0. |
| Cambio pendiente oculta curso | Media/medio | Aviso de retirada temporal antes de editar; referencias conservadas. |
| Consumo concurrente o reordenación | Media/alto | Bloqueos y restricciones; integración por capas planificada. |


## 9. Validaciones y pruebas

### 9.1 Verificaciones manuales realizadas

| Ticket | Evidencia observada | Resultado |
| --- | --- | --- |
| T2 | Instalación uv; navegador en /health y /api/v1/courses. | API mínima respondió. |
| T3 | React conectado al endpoint; estados de catálogo vacío y recuperación tras corrección de main.jsx. | Pantalla mínima operativa. |
| T3 | `pnpm lint` y `pnpm build`. | Sin errores de lint; build correcto con Vite 8.3.5. |
| T4 | `docker compose up --build`. | Imágenes frontend/backend construidas y PostgreSQL 18.6 iniciado. |
| T4 | `docker compose ps`. | backend, frontend y postgres en estado Up. |
| T4 | Navegador en http://localhost:8000/health. | `{"status":"ok"}`. |
| T4 | Navegador en http://localhost:5173. | “Cursos Abiertos” y “Todavía no hay cursos publicados”. |

Lint y build se ejecutaron durante T3; no se afirma una nueva ejecución después del cambio de proxy de T4. No se presentan como tests unitarios ni de integración automatizados. Las comprobaciones fueron sobre el entorno de trabajo de la estudiante, no todavía sobre un clon limpio independiente.

### 9.2 Pendientes del cierre T4 y release T5

- Guardar documentación actualizada y crear commit/PR de T4 hacia dev.
- Verificar T1–T4 integrados y actualizar el plan con ramas/commits reales.
- Repetir instrucciones desde clon limpio, sin depender de node_modules ni .venv locales.
- Cerrar CHANGELOG con versión y fecha real; integrar dev→main y crear tag anotado v0.1.0.
- Registrar versiones/digests efectivos si se decide fijar imágenes con precisión adicional.

El release no se antedata al 27/10: usar fecha efectiva de publicación. No marcar pruebas o tareas como realizadas si aún no tienen evidencia.

### 9.3 Estrategia posterior

pytest/AAA para reglas puras; PostgreSQL real para constraints, permisos y concurrencia; Vitest para estados/hooks. SQLite no acredita comportamiento de bloqueos PostgreSQL. Objetivos y casos se desarrollan en [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md). No se implementan tests, multi-stage ni healthchecks por adelantado como condición para aprobar el scaffold.

## Actualización de cierre del scaffold

T4 quedó integrado en dev mediante el PR #6, merge fcf87cc.
Se verificó el arranque desde un clon limpio de dev: los tres contenedores quedaron Up, /health respondió ok y el frontend mostró el catálogo vacío.
La integración en main y el tag v0.1.0 quedan pendientes
hasta ejecutar la publicación del release.