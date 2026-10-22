# Backend schema — Modelo de datos y contratos de API

Versión 1.1. Especificación textual; no incluye SQL ni código ejecutable. Reglas de referencia: SPEC.md. Seguridad e infraestructura: TRD.md.

## 1. Convenciones del modelo

Identificadores UUID generados por la aplicación; todas las fechas son timestamptz en UTC y se serializan en ISO 8601. PK identifica clave primaria; FK una referencia; UNIQUE impide duplicados. Campos obligatorios salvo indicación de nulo. Los CHECK expresan reglas de una fila; reglas entre tablas requieren servicio transaccional, no un CHECK que consulte otras tablas.

Los estados se representan mediante texto con CHECK para facilitar migraciones. Strings de entrada se recortan salvo contraseñas y tokens. Pydantic rechaza campos desconocidos en escrituras. Las salidas usan schemas explícitos y nunca serializan automáticamente todos los atributos ORM.

created_at se define al crear; updated_at se actualiza en cada cambio. Cursos, roadmaps y categorías incluyen version entero positivo, inicialmente 1. Un cambio efectivo incrementa version. No se cambia slug al editar título; se genera al crear con sufijo de unicidad, incluso si otro recurso está archivado.

## 2. Entidades y campos

### users

| Campo | Tipo lógico | Restricciones y finalidad |
| --- | --- | --- |
| id | UUID | PK. |
| email | varchar(254) | Email normalizado, UNIQUE. |
| display_name | varchar(80) | Entre 2 y 80 caracteres. |
| password_hash | text | Argon2id; nunca se devuelve. |
| role | varchar(16) | student o admin; default student. |
| is_active | boolean | Default true; no equivale a email verificado. |
| email_verified_at | timestamp o nulo | Nulo hasta confirmar el correo; obligatorio para emitir JWT. |
| password_changed_at | timestamp | Instante del último cambio. |
| created_at, updated_at | timestamp | Auditoría básica. |

No guardar confirmación de contraseña, contraseña legible ni permisos enviados por el cliente. email_verified_at se establece exclusivamente al consumir un token de verificación válido. El usuario inicial administrador se crea con credencial suministrada por un canal de operación, no incrustada en seeds.

### sessions

| Campo | Tipo lógico | Restricciones |
| --- | --- | --- |
| id | UUID | PK; mismo valor que jti del JWT. |
| user_id | UUID | FK users. |
| created_at | timestamp | Inicio. |
| expires_at | timestamp | Mayor a created_at; igual a exp del JWT, inicio + 15 minutos. |
| revoked_at | timestamp o nulo | Si tiene valor, no autoriza. |

No se necesita almacenar IP ni user agent para la funcionalidad inicial. La cookie contiene el JWT firmado y el claim jti referencia sessions.id; no se almacena el JWT completo. Una sesión solo es válida si firma y claims son válidos, no está revocada, no venció, sub coincide con user_id y el usuario sigue activo con correo verificado. Al borrar una cuenta por procedimiento interno sus sesiones pueden eliminarse en cascada; no hay endpoint público de borrado de usuario.

### password_reset_tokens

| Campo | Tipo lógico | Restricciones |
| --- | --- | --- |
| id | UUID | PK. |
| user_id | UUID | FK users. |
| token_hash | char(64) | UNIQUE. |
| created_at | timestamp | Creación. |
| expires_at | timestamp | Creación + 30 minutos. |
| consumed_at | timestamp o nulo | Consumo o invalidación por sustitución. |

La invalidez por sustitución se registra con consumed_at aunque no se haya cambiado una contraseña. No se usa para estadísticas de resets exitosos. La creación de otro token bloquea usuario e invalida los anteriores. Usuarios inexistentes no generan filas de tokens, pero sí consumen cuotas de abuso.

### categories

| Campo | Tipo lógico | Restricciones |
| --- | --- | --- |
| id | UUID | PK. |
| name | varchar(80) | Entre 2 y 80; unicidad sin distinguir mayúsculas mediante índice sobre lower(name). |
| slug | varchar(120) | UNIQUE, estable. |
| version | integer | Positivo. |
| created_at, updated_at | timestamp | Auditoría básica. |

No hay archivado de categorías. DELETE físico solo si ningún curso la referencia, incluso borradores o archivados; FK RESTRICT. El nombre se almacena recortado. Unicidad de nombre se normaliza igual en API y base.

### courses

| Campo | Tipo lógico | Restricciones |
| --- | --- | --- |
| id | UUID | PK. |
| slug | varchar(200) | UNIQUE y estable. |
| title | varchar(150) | Obligatorio desde borrador, 3–150. |
| summary | varchar(300) o nulo | 20–300 cuando está presente; obligatorio al publicar. |
| description | text o nulo | 50–10000; obligatorio al publicar. |
| prerequisites | text o nulo | Hasta 2000. |
| provider | varchar(100) o nulo | 2–100; obligatorio al publicar. |
| external_url | varchar(2048) o nulo | HTTPS, sin credenciales embebidas; obligatorio al publicar. |
| category_id | UUID o nulo | FK categories RESTRICT; obligatorio al publicar. |
| level | varchar(16) o nulo | initial, intermediate, advanced. |
| language | varchar(8) o nulo | es, en o pt en MVP. |
| duration_minutes | integer o nulo | 1–100000. |
| free_access_confirmed | boolean | Default false; debe ser true al publicar. |
| certificate_note | varchar(500) o nulo | Aclaración editorial sobre certificado externo. |
| status | varchar(16) | draft, published, archived. |
| published_at | timestamp o nulo | Fecha de primera publicación. |
| archived_at | timestamp o nulo | Fecha de baja. |
| created_by, updated_by | UUID | FK users RESTRICT; created_by es el propietario inmutable, asignado desde usuario autenticado. |
| version | integer | Positivo. |
| created_at, updated_at | timestamp | Auditoría básica. |

Los CHECK controlan rangos y coherencia de fechas/estado. Un estado published exige campos editoriales completos y published_at; archived exige archived_at. Un curso puede archivarse desde draft conservando published_at nulo. El servicio controla que archived sea terminal. El modelo no contiene precio.

### roadmaps

Campos: id UUID PK; slug varchar(200) UNIQUE; title varchar(150) obligatorio; summary varchar(300) nulo en borrador; goal text nulo, entre 20 y 3000 cuando está presente; level con los mismos valores que cursos; status draft/published/archived; published_at y archived_at nulos según estado; created_by y updated_by FK users RESTRICT; version entero positivo; created_at y updated_at.

Publicar requiere summary, goal, level y al menos un paso. Inmutabilidad incluye título, slug, resumen, objetivo, nivel y pasos; solo admite transición a archived. Los nombres del curso y su URL sí pueden corregirse desde su entidad propia, por lo que la inmutabilidad es de la composición del roadmap, no una instantánea de toda la metadata de cada curso.

### roadmap_steps

| Campo | Tipo lógico | Restricciones |
| --- | --- | --- |
| id | UUID | PK. |
| roadmap_id | UUID | FK roadmaps RESTRICT. |
| course_id | UUID | FK courses RESTRICT. |
| position | integer | Entre 1 y 50. |

UNIQUE(roadmap_id, position) y UNIQUE(roadmap_id, course_id). La consecutividad y mínimo de un paso al publicar se validan en servicio. Reemplazar pasos de borrador borra su lista anterior y crea la nueva en una transacción tras bloquear roadmap; si cualquier inserción falla se revierte todo. Para evitar colisiones durante reordenamiento se reemplaza el conjunto dentro de esa transacción, no se cambian posiciones una a una sin estrategia.

### roadmap_enrollments

Campos: id UUID PK; user_id FK users; roadmap_id FK roadmaps RESTRICT; followed_at timestamp. UNIQUE(user_id, roadmap_id). La finalización no se guarda en esta tabla: se deriva del progreso. DELETE del seguimiento elimina esta fila, sin tocar course_progress. Un procedimiento de borrado de usuario elimina sus asociaciones personales.

### course_progress

Campos: id UUID PK; user_id FK users; course_id FK courses RESTRICT; status not_started/in_progress/completed; completed_at timestamp nulo; created_at y updated_at. UNIQUE(user_id, course_id). CHECK: completed exige completed_at no nulo; los otros estados exigen completed_at nulo.

Ausencia de fila equivale a not_started. PUT not_started puede crear o conservar fila explícita. Cambiar a completed establece fecha solo al entrar en ese estado; repetir completed no reinicia fecha. Volver a in_progress borra completed_at. El progreso no equivale a aprobación verificada.

### rate_limit_buckets

Campos: policy varchar(64); subject_hash char(64); window_start timestamp; window_end timestamp; hits integer no negativo. PK compuesta (policy, subject_hash, window_start). CHECK window_end mayor a window_start. No almacenar email ni IP sin seudonimizar. La política determina la duración y el límite; no aceptar esos valores desde solicitudes.

### email_outbox

Campos: id UUID PK; purpose reset_password/verify_email; reset_token_id FK password_reset_tokens nullable y UNIQUE; verification_token_id FK email_verification_tokens nullable y UNIQUE, con borrado coordinado después de purgar outbox; CHECK de referencia única según propósito descrito en sección 13; payload_ciphertext bytea o nulo; encryption_key_id varchar(64); status pending/processing/sent/failed/expired; attempts integer entre 0 y 3; available_at timestamp; lease_until timestamp nulo; expires_at timestamp; sent_at timestamp nulo; last_error_code varchar(64) nulo; created_at y updated_at.

El payload cifrado contiene destinatario, plantilla y token temporal para envío. Se destruye al completar o vencer. No almacenar excepciones SMTP con destinatarios/tokens en last_error_code. Al purgar tokens se eliminan previamente mensajes asociados ya terminales; un token no puede quedar borrado mientras su correo sigue pendiente. La metadata terminal se conserva hasta 7 días, por lo que tokens de ambos propósitos asociados pueden conservar metadata de hash hasta completar esa ventana; no autorizar con ellos después de expirar.

### audit_events

Campos: id UUID PK; actor_id UUID FK users RESTRICT; action varchar(64); resource_type varchar(32); resource_id UUID; request_id varchar(64); created_at timestamp; metadata JSONB limitada a estado anterior/nuevo, versión e IDs de dependencias. No snapshots de contraseñas, contenido de correo ni datos de sesión. Se escribe en la misma transacción que la mutación de autor o administrativa.

## 3. Relaciones y cardinalidades

| Origen | Destino | Relación |
| --- | --- | --- |
| users | sessions y password_reset_tokens | Uno a muchos. |
| categories | courses | Uno a muchos; curso de borrador puede no tener categoría. |
| roadmaps | roadmap_steps | Uno a muchos; mínimo uno al publicar. |
| courses | roadmap_steps | Uno a muchos; resuelve muchos a muchos curso-roadmap. |
| users y roadmaps | roadmap_enrollments | Muchos a muchos. |
| users y courses | course_progress | Muchos a muchos con estado propio. |
| password_reset_tokens | email_outbox | Uno a uno en el flujo de solicitud; reset_token_id UNIQUE en outbox. |
| users | cursos, roadmaps y auditoría | Uno a muchos como actor administrativo. |

No hay FK directa entre progreso y seguimiento: un curso puede tener avance sin roadmap. Un archivado es actualización, nunca cascada de datos históricos.

## 4. Índices y consultas

- Índices de unicidad de email, slugs, token_hash y claves compuestas personales.
- sessions(user_id) y sessions(expires_at) para revocación y limpieza.
- password_reset_tokens(user_id) y expires_at para invalidación y mantenimiento.
- courses(status, created_at, id) y filtro por category_id, level o language según plan de consulta medido; no crear todos los índices posibles sin evidencia.
- roadmap_steps(course_id) para bloquear archivados y (roadmap_id, position) ya cubierto por unicidad.
- roadmap_enrollments(user_id, followed_at, id) para panel personal.
- email_outbox(status, available_at) para worker y expires_at para purga.
- rate_limit_buckets(window_end) y auditoría(created_at) para retención.

Búsqueda inicial mediante ILIKE parametrizado en title y provider, sin distinguir acentos como garantía. La comparación de acentos queda fuera del contrato inicial. Se escapan comodines % y _ para interpretar q como texto literal. ILIKE con comodín inicial puede requerir escaneo; medir con 10000 cursos y, si no alcanza la meta, agregar pg_trgm e índice GIN mediante migración y evidencia de EXPLAIN. Evitar N+1 precargando categoría y pasos en consultas acotadas.

## 5. Convenciones de API

Base /api/v1. JSON UTF-8 excepto 204 sin cuerpo. JWT firmado en cookie HttpOnly para autenticación; el transporte elegido no utiliza header Bearer. Validar claims y registro jti según TRD. Todas las mutaciones requieren CSRF y origen válido. JWT o sesión inválida: 401; sesión válida sin permiso administrativo: 403; curso ajeno en endpoint de autor: 404. Un recurso privado fuera de alcance se oculta con 404 cuando la política exige no revelar su existencia.

Respuesta de detalle: objeto explícito del recurso. Listado: items, page, page_size, total y total_pages. Si total es cero, total_pages es 0 e items está vacío. La página solicitada debe ser positiva; si supera el último número se responde lista vacía con 200 y el total real. Orden siempre añade id como desempate.

Error estándar: error contiene code estable, message seguro, details con pares field/message cuando corresponde y request_id. No incluir el campo input de errores de Pydantic si contiene contraseña, token u otros secretos. Ejemplos de códigos: VALIDATION_ERROR, AUTH_REQUIRED, INVALID_CREDENTIALS, FORBIDDEN, NOT_FOUND, VERSION_CONFLICT, RESOURCE_IN_USE, INVALID_STATE, INVALID_RESET_TOKEN, RATE_LIMITED, CSRF_INVALID y SERVICE_UNAVAILABLE.

Todos los errores, incluidos validación y fallos inesperados, se adaptan a este contrato. 400 se reserva para token de recuperación inválido y requests de semántica general inválida; 422 para campos; 409 para conflictos de negocio/versiones; 413 para tamaño; 429 para límites públicos; 503 para dependencias indisponibles; 500 para fallo inesperado con mensaje genérico y request_id.

Cache-Control: no-store en auth, datos privados y administración. El MVP también usa no-store en API pública para evitar persistir visibilidad editorial obsoleta; la caché de consultas del cliente se invalida y revalida al enfocar. Recursos estáticos con hash pueden tener caché larga. OpenAPI se genera desde contratos de implementación; documentación interactiva solo en desarrollo o protegida en despliegue.

## 6. Endpoints de autenticación

| Método y ruta | Entrada | Éxito | Regla |
| --- | --- | --- | --- |
| GET /auth/csrf | Sin cuerpo | 200 token y cookie CSRF | Público; no-store. |
| POST /auth/register | display_name, email, password | 202 mensaje genérico | Crea student; duplicado conserva misma respuesta. |
| POST /auth/login | email, password | 200 user público y Set-Cookie con JWT | Credenciales inválidas: 401; contraseña correcta y email pendiente: 403 EMAIL_NOT_VERIFIED; límites: 429. |
| GET /auth/me | Cookie JWT | 200 id, display_name, email, role, email_verified_at | 401 si no hay sesión vigente. |
| POST /auth/logout | Cookie y CSRF | 204 y borrado de cookie | Idempotente: también 204 sin sesión, con CSRF válido. |
| POST /auth/forgot-password | email | 202 mensaje genérico | La cuenta/email no se revela. |
| POST /auth/reset-password | token, new_password | 200 confirmación | Token inválido/usado/vencido: 400 uniforme. |

Las confirmaciones de contraseña se validan en UI; no son campos de API. register no devuelve id de usuario ni JWT y encola verificación para una cuenta nueva. reset-password no devuelve tokens ni usuario. CSRF inválido devuelve 403 con código específico; el cliente puede obtener un token nuevo pero no reenvía silenciosamente una mutación cuyo resultado sea desconocido.

## 7. Consultas públicas

| Método y ruta | Parámetros | Respuesta |
| --- | --- | --- |
| GET /categories | Sin filtros | Lista no paginada de categorías, límite administrativo de 100 categorías. |
| GET /courses | q, category_id, level, language, page, page_size, sort | Solo publicados. sort: newest o title; default newest. |
| GET /courses/{slug} | Slug | Curso publicado y categoría. No incorpora datos de progreso. |
| GET /roadmaps | q, level, page, page_size, sort | Solo publicados; sort newest o title. |
| GET /roadmaps/{slug} | Slug | Metadata y pasos ordenados; publicados o archivado si ya seguido por sesión actual. |

Roadmaps busca q en título, sin filtros no documentados. La respuesta pública de curso incluye id, slug, title, summary, description, prerequisites, provider, external_url, category, level, language, duration_minutes y certificate_note; status y published_at pueden exponerse como metadata editorial, nunca created_by o updated_by. La tarjeta usa un subset sin descripción larga.

Detalle de roadmap devuelve id, slug, title, summary, goal, level, status, published_at, steps y course_count. Cada paso incluye position y resumen público del curso. El avance se obtiene por endpoint personal y no se añade a respuestas públicas reutilizables.

## 8. Endpoints personales

| Método y ruta | Entrada | Éxito |
| --- | --- | --- |
| GET /me/roadmaps | page, page_size | 200 seguimientos con metadata, completed_count, total_count, progress_percent y next_course. |
| PUT /me/roadmaps/{roadmap_id} | Sin campos de dominio | 200 seguimiento actual; no duplica. Solo roadmap publicado para alta. |
| DELETE /me/roadmaps/{roadmap_id} | Sin cuerpo | 204 incluso si no existía seguimiento propio. |
| GET /me/roadmaps/{roadmap_id}/progress | Sin cuerpo | 200 conteos y estado de cada paso; exige seguimiento propio. |
| GET /me/courses/{course_id}/progress | Sin cuerpo | 200 estado propio o not_started implícito; curso publicado. |
| PUT /me/courses/{course_id}/progress | status | 200 estado actualizado; curso publicado. |

Ningún endpoint personal acepta user_id. Enviar ese campo produce 422, no cambia propietario. Intentar progreso de un curso no publicado devuelve 404. Un roadmap archivado ya seguido admite lectura de progreso; intentar crear seguimiento devuelve 409 INVALID_STATE, salvo si ya existe, caso en que PUT devuelve el seguimiento actual. DELETE no borra progreso.

next_course es el primer paso cuyo estado no sea completed; si todos terminaron es null. progress_percent se calcula con redondeo de mitad hacia arriba; completed exige completed_count igual a total_count. Total 0 no ocurre en recorridos publicados; si datos corruptos lo producen, registrar incidente y no dividir por cero.

## 9. Endpoints administrativos

Los endpoints de esta sección requieren rol admin. Las rutas equivalentes de autor se definen en la sección 13 y no conceden acceso administrativo. Los UUID de ruta se validan como tales; las rutas administrativas no aceptan slugs.

| Método y ruta | Entrada | Éxito y observaciones |
| --- | --- | --- |
| GET /admin/courses | q, status, page, page_size | 200, incluye borradores y archivados; sort updated_at descendente e id. |
| POST /admin/courses | title y campos opcionales de borrador | 201 recurso con version; Location al detalle API administrativo. |
| GET /admin/courses/{id} | ID | 200 metadata completa sin secretos de actor. |
| PATCH /admin/courses/{id} | Campos editables y expected_version | 200 versión nueva; no acepta status, slug, autores ni fechas. |
| POST /admin/courses/{id}/publish | expected_version | 200 publicado; validación completa. |
| DELETE /admin/courses/{id}?expected_version=N | Versión positiva en query | 204 archivado; 409 si dependencia protegida. |
| GET /admin/categories | Sin filtros | 200 categorías con versión. |
| POST /admin/categories | name | 201 categoría. |
| PATCH /admin/categories/{id} | name, expected_version | 200 versión nueva. |
| DELETE /admin/categories/{id}?expected_version=N | Versión | 204 si no hay cursos; si hay, 409. |
| GET /admin/roadmaps | q, status, page, page_size | 200, todos los estados. |
| POST /admin/roadmaps | title y metadata opcional | 201 borrador con versión. |
| GET /admin/roadmaps/{id} | ID | 200 detalle completo y pasos. |
| PATCH /admin/roadmaps/{id} | Metadata editable y expected_version | 200, solo draft. |
| PUT /admin/roadmaps/{id}/steps | course_ids en orden, expected_version | 200 detalle con nueva versión; solo draft. |
| POST /admin/roadmaps/{id}/publish | expected_version | 200 publicado; mínimo un paso. |
| DELETE /admin/roadmaps/{id}?expected_version=N | Versión | 204 archivado, conserva pasos y seguimientos. |

expected_version en query de DELETE evita depender de cuerpos DELETE descartados por intermediarios. Valores de versión incorrectos producen 409. Si el recurso ya está archivado, DELETE con versión actual devuelve 204 sin incremento; un reintento con versión antigua devuelve 409 y debe reconsultarse. Publicar uno ya publicado con versión actual devuelve 200 sin cambio; versión antigua es conflicto. Un archivo desde borrador y un archivo desde publicado usan la misma operación.

PUT steps recibe únicamente una lista de UUID ordenada, máximo 50; servidor asigna posiciones desde 1. Lista vacía permitida en borrador. Duplicados o UUID malformados: 422. Curso inexistente o no publicado al guardar pasos: 409 con código INVALID_COURSE_SELECTION y campos seguros, porque el selector pudo quedar obsoleto. Un borrador existente puede conservar pasos cuyo curso se archivó después, pero no publicarse así.

Errores de UNIQUE de categoría se traducen a 409 DUPLICATE_CATEGORY. Los slugs de cursos/roadmaps se generan con sufijo y reintento acotado; nunca devolver un error SQL sin traducir. No hay endpoint para asignar roles ni editar usuarios.

## 10. Operaciones transaccionales críticas

**Registro:** validar, aplicar cuotas, calcular hash, insertar con UNIQUE y confirmar; colisión conserva respuesta genérica. No devolver la excepción de integridad. Límite por email se aplica a cualquier email, no según existencia.

**Login/reset:** orden común de bloqueo de usuario antes de sesiones/tokens. Login valida el hash vigente dentro del protocolo de bloqueo; reset revoca sesiones antes de commit. Para peticiones ya autenticadas en ejecución al confirmar un reset no se promete cancelación retroactiva; las siguientes consultas de sesión serán rechazadas.

**Publicación de roadmap:** bloquear roadmap, comprobar versión y draft, leer pasos, bloquear cursos por ID ordenado, comprobar todos publicados, guardar estado y auditoría, commit. No validar cursos solamente antes de la transacción.

**Archivado de curso:** bloquear curso, comprobar versión, consultar si cualquier paso lo referencia desde roadmap con published_at no nulo, rechazar si existe, cambiar estado y auditoría. Comparte locks con publicación. Si publicación gana, archivado falla; si archivado gana, publicación falla.

**Guardar pasos:** bloquear roadmap y comprobar draft/versión; bloquear cursos ordenados para validar selección; reemplazar lista e incrementar versión. El protocolo de orden de locks se mantiene uniforme entre servicios: recurso roadmap, cuando aplique, antes de cursos ordenados; archivado de curso no adquiere lock de roadmap después de bloquear curso, evitando ciclo.

**Progreso:** UPSERT sobre user_id/course_id y fecha; consulta agregada calcula roadmaps. Si dos pestañas escriben estados diferentes, prevalece la última transacción confirmada, sin combinar estados artificialmente.

**Seguimiento frente a archivo:** creación bloquea roadmap y comprueba published; archivado bloquea el mismo roadmap. Si el seguimiento gana queda histórico; si el archivo gana no se crea. Las cuotas se confirman en transacciones separadas de estas operaciones.

## 11. Datos de demostración

Proponer seis categorías, doce cursos publicados gratuitos revisados manualmente, dos borradores y tres roadmaps con cursos compartidos. Incluir cuentas de prueba de estudiante y administrador creadas por tarea local idempotente con secretos suministrados por entorno. No distribuir contraseñas reales ni crear cuentas demo públicas en producción.

La carga de demostración es separada de las migraciones. No consultar enlaces remotos durante migración o arranque. Guardar fuente y fecha de revisión en un registro editorial documental de seeds; si después se requieren como función, agregar campos mediante cambio de alcance.

## 12. Invariantes para revisión

No existen dos cuentas con el mismo email normalizado, dos seguimientos iguales ni dos progresos iguales. No se devuelve un password_hash. Un estudiante verificado crea y gestiona sus propios cursos, pero no modifica cursos ajenos ni selecciona propietario. Un roadmap publicado nunca queda vacío ni contiene un curso archivado por una operación permitida. Un reset válido se consume una vez y revoca sesiones. Un cambio administrativo con versión vieja no sobrescribe datos. Cada una de estas condiciones requiere una prueba de integración explícita.

## 13. Contratos añadidos en revisión 1.1

### Verificación de correo

email_verification_tokens: id UUID PK, user_id FK users, token_hash char(64) UNIQUE, created_at, expires_at y consumed_at nulo. Expiración de 24 horas. Token de alta entropía, no JWT; el verificador de email nunca acepta un access token. Índices por user_id y expires_at. Registro crea token y outbox en la misma transacción; reenvío y confirmación bloquean usuario antes del token.

La tabla email_outbox se amplía: purpose reset_password/verify_email; reset_token_id pasa a nullable; agregar verification_token_id FK email_verification_tokens nullable y UNIQUE. CHECK exige exactamente la referencia que corresponde al propósito: reset_password lleva reset_token_id y ninguna verification_token_id; verify_email lleva verification_token_id y ninguna reset_token_id. El worker deriva plantilla y expiración del propósito y elimina mensajes/tokens con purga coordinada. El cifrado de payload se mantiene para ambos tipos de correo.

| Método y ruta | Entrada | Respuesta |
| --- | --- | --- |
| POST /auth/verify-email | token | 200 confirmación, sin JWT; inválido/usado/vencido 400 INVALID_VERIFICATION_TOKEN. |
| POST /auth/resend-verification | email | 202 uniforme; no revela existencia ni estado de verificación; 429 solo por cuota pública de IP. |

Ambos son públicos y requieren Origin y CSRF válidos. Token en cuerpo HTTPS, nunca query string. Verificar consume token y establece email_verified_at atómicamente; reenvío invalida los anteriores. Registro no duplica cuentas ni altera contraseñas al reenviar. Un email ya verificado conserva estado y el reenvío responde genérico sin emitir un nuevo enlace.

### CRUD de cursos del autor

| Método y ruta | Entrada | Respuesta |
| --- | --- | --- |
| GET /me/authored-courses | q, status, page, page_size | 200 solo propios, incluyendo todos los estados. |
| POST /me/authored-courses | title y campos de borrador | 201 curso propio; created_by desde sub validado. |
| GET /me/authored-courses/{id} | UUID | 200 si propio; ajeno o inexistente 404. |
| PATCH /me/authored-courses/{id} | Campos editables, expected_version | 200 versión nueva; ajeno 404. |
| POST /me/authored-courses/{id}/publish | expected_version | 200 publicado si válido y propio. |
| DELETE /me/authored-courses/{id}?expected_version=N | Versión | 204 baja lógica; 409 si dependencia o versión; ajeno 404. |

Exigen JWT vigente, usuario activo y correo verificado. Reutilizan servicios y validaciones del CRUD administrativo; los filtros de propietario ocurren en servidor antes de leer o mutar. created_by, owner_id, role, status y fechas no se aceptan como campos editables. Un administrador usa /admin para intervenir en cursos ajenos; /me siempre conserva semántica de recursos propios.

Auditoría renombrada a audit_events para cubrir ambos actores. No hay migración ejecutada todavía: estos cambios ajustan el diseño inicial. Agregar tests de firma alterada, algoritmo inválido, iss/aud incorrectos, exp vencido, jti revocado, correo pendiente y modificación ajena. Un JWT firmado válido no evita comprobar propiedad.
