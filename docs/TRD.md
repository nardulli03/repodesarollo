TRD — Cursos Abiertos
Versión 2.0, 27/10/2026. Diseño previsto, sin código generado ni versiones instaladas certificadas.

1. Stack y versiones
Capa	Elección	Versión	Motivo
UI	React, Vite, pnpm	React 19; patch y herramientas pendientes de verificar	Stack fijo.
Lenguaje UI	JavaScript, React Router, CSS propio	Versiones por resolver	Evitar pendiente sobre TypeScript y dependencia visual extra.
API	FastAPI, uv, Uvicorn	Exactas pendientes; referencia FastAPI 0.158.2 de SPEC	Stack fijo; uv gestiona, Uvicorn sirve HTTP.
Datos	PostgreSQL, SQLAlchemy 2, psycopg 3, Alembic	PostgreSQL 18.6 exigido; otras exactas por resolver	Transacciones y migraciones explícitas.
Seguridad	PyJWT, pwdlib con Argon2id	Exactas por resolver	Bibliotecas mantenidas, sin criptografía propia.
Dev	Docker, Compose, Mailpit	Exactas por registrar	Entorno reproducible y correo local.
Pruebas clase	pytest, Vitest	Por resolver	Funciones puras y capas.


Antes de aprobar como versión definitiva, registrar salida real de herramientas disponibles y versiones resueltas. Después del T1, fijar dependencias en manifests y locks y registrar imagen efectiva. No confundir versión exigida, seleccionada e instalada; no usar latest como garantía de reproducibilidad. Si PostgreSQL 18.6 u otra referencia no está disponible, elevar diferencia al docente antes de reemplazarla.
2. Decisiones técnicas
ID	Tema	Alternativas	Elegida y motivo
TD-01	Autenticación	JWT, sesión opaca, proveedor externo	JWT requerido previamente, cookie HttpOnly y sesión revocable en BD; sin refresh para MVP.
TD-02	Paginación	Cursor, offset + total	page/page_size/total en todos los listados; sencillo de demostrar.
TD-03	Errores	Formatos distintos, envelope único	Envelope JSON con code/message/fields/request_id; UI consistente.
TD-04	Validar enlaces	Fetch API, automatización, revisión humana	Admin abre enlace antes de aprobar y registra fecha; evita SSRF y complejidad del MVP.
TD-05	Roadmap	Copiar metadatos, relación usuario-curso, varios recorridos	Una cabecera por usuario e items referenciados con orden/estado; aislamiento claro.
TD-06	Password	bcrypt, Argon2id	Argon2id por resistencia a ataques con uso de memoria; biblioteca, parámetros calibrados y hash incluye parámetros.
TD-07	Correo	Worker/outbox, SMTP síncrono	Envío síncrono tras commit y timeout 10 s; reenvío explícito recupera fallos. No se promete entrega garantizada.
TD-08	Frontend	TypeScript, JavaScript; MUI, CSS propio	JavaScript y CSS por tokens para reducir alcance y hacer visible mobile-first.
TD-09	Rate limit	Memoria, Redis, PostgreSQL	Contador atómico PostgreSQL compartido; sin sumar Redis.


3. Arquitectura
3.1 Responsabilidades
React presenta estados y llama a API REST /api/v1 del mismo origen mediante proxy Vite en desarrollo. Routers traducen HTTP; servicios de aplicación coordinan repositorios/transacciones; funciones puras de dominio validan reglas sin FastAPI ni SQLAlchemy; repositorios son acceso a BD. Esta separación permite probar reglas puras en clase sin confundirlas con orquestación transaccional.
```mermaid
flowchart TD
    UI[React] --> HTTP[Router del dominio]
    HTTP --> APP[Servicio de aplicación]
    APP --> RULE[Reglas puras]
    APP --> REPO[Repositorio]
    REPO --> DB[(PostgreSQL)]
```

3.2 Estructura prevista para B — no crear fuentes antes del T1
backend/
  app/
    main.py
    config.py
    identidad/  router.py, service.py, rules.py, repository.py, models.py, schemas.py
    cursos/     router.py, service.py, rules.py, repository.py, models.py, schemas.py
    aportes/    router.py, service.py, rules.py, repository.py, schemas.py
    roadmap/    router.py, service.py, rules.py, repository.py, models.py, schemas.py
    shared/     db.py, errors.py, security.py, pagination.py
  migrations/
  tests/
frontend/
  src/
    app/        router, shell, providers
    features/
      identidad/ components/, hooks/, api.js
      catalogo/  components/, hooks/, api.js
      aportes/   components/, hooks/, api.js
      revision/  components/, hooks/, api.js
      roadmap/   components/, hooks/, api.js
    shared/     components/, http.js
    styles/     tokens.css, base.css
infra/
docs/

docker-compose.yml
Aportes representa el ciclo del curso; no duplica la entidad curso en otra tabla. Las flechas entre dominios usan servicios/repositorios explícitos, no importaciones circulares. El nombre de las carpetas comunica funciones del producto.
3.3 Servicios Compose previstos
Servicio	Base	Puerto host previsto	Responsabilidad
postgres	postgres:18.6, sujeto a comprobación	Ninguno por defecto	Persistencia en volumen.
migrate	Misma imagen backend	Ninguno	Alembic antes de API; ejecución única.
backend	Python slim, versión exacta por resolver	8000 dev	API.
frontend	Node compatible con Vite elegido, exacto por resolver	5173	Vite y proxy /api.
mailpit	Imagen exacta por fijar	8025 web; SMTP 1025 interno	Capturar emails sin enviarlos a personas reales.


docker compose up deberá iniciar migración y servicios, con espera básica de BD y migración exitosa. No basta el orden de creación. Se permite healthcheck mínimo de PostgreSQL para disponibilidad; healthchecks avanzados, usuario no-root y multi-stage se trabajan en clase. No optimizar imágenes como condición P0. Seeds con comando documentado, idempotente y credenciales suministradas por entorno, nunca embebidas.

4. Convenciones
Git: [GIT_WORKFLOW](GIT_WORKFLOW.md), rama actual docs/modificaciones-consigna.

Errores: { "error": { "code": "VALIDATION_ERROR", "message": "Revisá los datos", "fields": { "title": "Campo requerido" }, "request_id": "uuid" } }. fields puede estar vacío. Los 422 de FastAPI se adaptan al envelope. 401 sesión inválida, 403 rol/CSRF/correo pendiente, 404 recurso ausente o ajeno, 409 duplicado/versión/estado incompatible, 422 campos, 429 cuota con Retry-After, 503 dependencia caída. 413 para JSON > 256 KiB. Sin stack ni SQL al cliente.
Variable	Ejemplo sin secreto	Obligatoria	Propósito
DATABASE_URL	postgresql+psycopg://usuario:CLAVE_LOCAL@postgres:5432/cursos	Sí	Conexión.
JWT_SIGNING_KEY	GENERAR_ALEATORIO_32_BYTES_MINIMO	Sí	Firma HS256.
JWT_ISSUER / JWT_AUDIENCE	cursos-abiertos / cursos-api	Sí	Validar destino/origen.
CSRF_SIGNING_KEY	GENERAR_SECRETO_DISTINTO	Sí	Firma CSRF.
RATE_LIMIT_KEY	GENERAR_SECRETO_DISTINTO	Sí	HMAC de IP/email.
APP_PUBLIC_URL	http://localhost:5173	Sí	Construcción de enlaces.
SMTP_HOST / SMTP_PORT	mailpit / 1025	Sí dev	Correo local.
SMTP_USER / SMTP_PASSWORD / SMTP_TLS	vacíos / vacío / false	Según entorno	SMTP real exige TLS.
COOKIE_SECURE	false dev; true HTTPS	Sí	Seguridad de cookies.
DEMO_ADMIN_PASSWORD / DEMO_USER_PASSWORD	DEFINIR_LOCALMENTE	Solo seed	Sin credenciales reales versionadas.
No poner secretos en VITE_*. Variables y ejemplos se crean como .env.example solo después de aprobación; .env ignorado. Logs con request_id, ruta sin token, estado/duración; no cuerpos de auth ni cookies. Captura de errores de dominio en router y fallos inesperados en middleware.

5. Restricciones verificables
Restricción	Solución	Verificación futura
Listados paginados	Envelope items/total/page/page_size, default 20, máximo 100	Todos los GET de colecciones del schema.
Mobile-first	CSS base móvil; min-width 768/1024 mejora layout	UX-UI y revisión de CSS.
Menú sándwich	Botón ARIA, panel y foco	Header, teclado y móvil.
Screaming Architecture	Árbol por dominio §3.2	Repo de B.
Material claro	Tokens y estados de UX-UI	Revisión visual.

6. Autenticación, correo y límites
JWT y autorización
JWT firmado identifica al usuario; no cifra sus claims ni reemplaza permisos. Claims sub UUID, jti UUID, iss, aud, iat, nbf, exp; solo HS256, secreto mínimo 32 bytes, vigencia 15 min, margen de reloj 30 s. Validar firma, algoritmo permitido, presencia/tipos, fechas/emisor/audiencia. Sin secretos ni password en payload. Sesión en BD asociada a jti permite logout/reset inmediato. Cada petición consulta estado actual y email verificado; rol y propietario desde BD. Sin refresh: vence y exige login.

Cookie HttpOnly, SameSite=Lax, Path=/, Secure en HTTPS; __Host-access_token en producción sin Domain, access_token_dev en HTTP local. No localStorage, ni token en URL ni JSON de login. GET csrf emite cookie firmada no HttpOnly y token para header X-CSRF-Token; servidor valida firma, cookie, vencimiento 12 h y Origin exacto permitido para toda mutación, incluso auth pública. Secretos distintos. Renovar CSRF en login/logout; no aceptar variantes de origen ni confiar encabezados de proxy arbitrarios.

Hash Argon2id, parámetros de biblioteca registrados/calibrados al implementar; no truncar contraseña ni loguearla. Login inválido uniforme y hash ficticio para cuenta inexistente. Email no verificado solo se informa después de contraseña correcta. Un registro duplicado no cambia credenciales.
Correo
Tokens opacos de 32 bytes aleatorios, solo SHA-256 persistido. Verificación 24 h, recuperación 30 min, uso único. Registro crea usuario pendiente y token; commit antes del SMTP; recuperación/reenvío invalidan anteriores dentro de transacción. Enviar fuera de transacción y con timeout: si SMTP falla, cuenta/token permanecen y la UI ofrece reenvío o nueva recuperación. Endpoints de solicitud siguen respuesta 202 genérica por privacidad, tanto para duplicados como inexistentes y fallos SMTP; no prometen entrega. Reenvío de verificación envía solo si existe y está pendiente. Registro duplicado no reenvía: usar endpoint específico. Sin cola ni worker en MVP; caída entre commit/envío requiere reintento del usuario.

Links desde APP_PUBLIC_URL configurada: /verificar-correo#token=... y /restablecer-contrasena#token=.... Capturar fragmento en memoria, limpiar historial y enviar token en body; sin terceros en pantallas. GET no consume tokens. Verificación requiere botón confirmar y no inicia sesión. Reset bloquea fila usuario, valida/consume token, cambia hash y revoca sesiones atómicamente. Login bloquea la misma fila al verificar hash vigente/crear sesión para impedir sesiones con contraseña anterior tras reset. Consumir token una sola vez bajo bloqueo; no enviar correo dentro del lock.
Rate limit compartido
Ventanas fijas UTC: login 20 intentos/IP/15 min y 10 intentos/email/15 min, contando todos los intentos para cortar concurrencia antes del hashing. Registro 10/IP/h; recuperación y reenvío 10/IP/h y 3/email/h. Supresión por email de correo devuelve 202 genérico; cuota pública excedida devuelve 429 y Retry-After en segundos. IP/email almacenados como HMAC con propósito separado. UPSERT atómico en transacción propia confirma cuota aun si negocio falla; si BD cae devuelve 503, no omite limitación. No bloquear permanentemente. No confiar X-Forwarded-For de clientes. Ventanas fijas admiten ráfagas cerca de cambio y afectan redes compartidas: limitaciones documentadas.

7. Integridad y operación
UUID, UTC, consultas parametrizadas y Pydantic rechaza campos extra. expected_version en escrituras sobre curso/roadmap; actualización condicional y 409 si desactualizado. Reordenar roadmap en una transacción bloqueando cabecera; restricción de posiciones diferible. Agregar bloquea curso y cabecera; solo publicados. Edición/archivo de curso usa bloqueo de la misma fila para resolver carrera: si cambia primero, no admite alta; si alta termina primero, conserva item con aviso. No borrar referencias.

8. Riesgos técnicos
Riesgo	Probabilidad/impacto	Mitigación
SMTP cae	Media/alto	Mailpit demo, timeout, reenvío, no afirmar entrega.
Versión exigida no disponible	Por verificar/alto	Registrar evidencia y acordar alternativa.
Alcance excesivo	Alta/alto	Un roadmap y categorías precargadas; sin worker ni extras P0.
Cambio pendiente oculta curso	Media/medio	Aviso de retirada temporal antes de editar; referencias conservadas.
Consumo concurrente o reordenación	Media/alto	Bloqueos y restricciones; integración por capas planificada.

9. Testing previsto
En B: verificaciones funcionales end-to-end manuales y clon limpio. En clase: pytest para funciones puras y PostgreSQL real para permisos, constraints/transacciones; Vitest para estados de UI. No usar SQLite como evidencia de bloqueos PostgreSQL. Detalle y cobertura objetivo en IMPLEMENTATION_PLAN. No se afirma haber ejecutado tests.

## Versiones verificadas durante T2

- Python: 3.14.6.
- uv: 0.12.1.
- FastAPI: 0.162.0.
- Uvicorn: 0.54.0.

Dependencias resueltas en backend/uv.lock.
En el scaffold, GET /health verifica que la API responde.
GET /api/v1/courses devuelve un catálogo vacío paginado.
La conexión y las consultas a PostgreSQL todavía no están implementadas.