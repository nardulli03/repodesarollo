# TRD — Diseño y requisitos técnicos

Versión 1.1. Estado: arquitectura propuesta, sin implementación. Ver reglas en SPEC.md y contratos en docs/BACKEND_SCHEMA.md.

## 1. Arquitectura general

Monorepositorio con frontend, backend, infraestructura y documentación. El frontend es una SPA React 19 compilada por Vite. FastAPI expone una API REST JSON versionada bajo /api/v1. PostgreSQL conserva datos de dominio, sesiones, límites de solicitudes y cola de correos. Un worker del mismo proyecto backend procesa correo pendiente.

En desarrollo, Vite atiende el navegador y redirige /api al backend. En despliegue, un servidor web entrega los archivos estáticos y actúa como proxy de /api. La SPA y API usan un mismo origen visible para el navegador. PostgreSQL y SMTP no se exponen directamente al público. El backend no descarga ni ejecuta contenido desde las URLs de cursos.

Una solicitud recorre proxy, middleware de tamaño/origen/rate limit, router FastAPI, validación Pydantic, autorización, servicio de caso de uso y repositorio SQLAlchemy. El servicio define la transacción; el repositorio no confirma commits ocultos. Un middleware asigna request_id y registra duración sin secretos.

## 2. Stack y gestión de versiones

| Capa | Elección | Justificación |
| --- | --- | --- |
| UI | React 19 + TypeScript | Componentes, tipos y coherencia de contratos. |
| Herramientas frontend | Vite + pnpm | Desarrollo y build; dependencias reproducibles con pnpm-lock.yaml. |
| Navegación | React Router | Rutas públicas, privadas y administrativas. |
| Componentes | Material UI compatible con React 19 | Diseño Material claro, controles y foco consistentes. |
| Datos remotos | TanStack Query | Caché, invalidación y estados de consultas. |
| Formularios | React Hook Form y Zod | Validación de UX; el servidor sigue siendo autoritativo. |
| API | FastAPI + Pydantic 2 | Validación, contratos y OpenAPI. |
| Python | 3.12 como base propuesta; uv | Entorno y uv.lock reproducibles. |
| Persistencia | PostgreSQL 18, SQLAlchemy 2 y psycopg 3 | Modelo relacional y transacciones. |
| Migraciones | Alembic | Evolución explícita del esquema. |
| Contraseñas | pwdlib con Argon2id | Hash de contraseña con sal y parámetros calibrados. |
| Tokens de acceso | PyJWT | Emisión y validación de JWT HS256, claims y expiración. |
| Infraestructura | Docker + Docker Compose v2 | Arranque reproducible de servicios. |
| Calidad | ESLint, TypeScript, Ruff, pytest, Vitest y Playwright | Verificaciones estáticas, integración y recorridos críticos. |

Las versiones exactas de Vite, Node LTS, pnpm y librerías se resuelven al iniciar la implementación y se fijan en manifests, lockfiles y versiones de herramientas. Comprobar requisitos de Node y peer dependencies; no usar etiquetas flotantes latest en entrega. React y React DOM deben pertenecer a la misma versión 19.x. uv es gestor; Uvicorn es el servidor ASGI: no son equivalentes.

Se propone acceso SQLAlchemy síncrono para reducir complejidad del proyecto. Los handlers con I/O síncrono se ejecutan como endpoints síncronos en el pool de FastAPI; no bloquear el event loop desde funciones async. El hashing y SMTP tampoco deben ejecutarse directamente en el event loop. La concurrencia y el tamaño del pool se miden antes de ajustar procesos.

## 3. Organización conceptual del repositorio

- Raíz: SPEC.md, PRD.md, TRD.md y README.md.
- docs: UX_UI.md, APPFLOW.md, BACKEND_SCHEMA.md e IMPLEMENTATION_PLAN.md.
- frontend: fuentes organizadas en app, features, shared y pruebas. Features: auth, courses, roadmaps, learning y admin.
- backend: app con api, core, schemas, models, repositories, services y worker; migrations y tests separados.
- infra: archivos Docker, configuración del proxy y procedimientos operativos.

Los routers traducen HTTP; los schemas validan entrada y salida; services implementan reglas; models representan persistencia. No concentrar seguridad y reglas en componentes de interfaz ni en un archivo único de endpoints.

## 4. Autenticación mediante JWT obligatorio

Decisión ADR-01 revisada por requisito confirmado: usar JSON Web Token (JWT) firmado como credencial de acceso. JWT es un formato que transporta claims verificables, como identificador de usuario, emisión y vencimiento. El backend valida la firma para detectar alteraciones. El contenido de un JWT firmado es legible: no contiene contraseña, claves privadas, email ni datos personales innecesarios; firmar no significa cifrar.

Ejemplo de uso: al ingresar con contraseña correcta y correo verificado, FastAPI emite JWT. Cuando el estudiante intenta editar un curso, el navegador envía el JWT en cookie; FastAPI valida firma, vigencia y sesión asociada, obtiene al usuario actual y comprueba que sea propietario o administrador. JWT responde quién se autenticó; la política de autorización decide qué puede modificar.

Claims obligatorios: sub (UUID de usuario como string), jti (UUID aleatorio único de sesión), iss (emisor configurado), aud (API de Cursos Abiertos), iat, nbf y exp. Duración: 15 minutos, margen de reloj máximo 30 segundos. Header typ=at+jwt; algoritmo permitido exclusivamente HS256 con secreto aleatorio de al menos 32 bytes. PyJWT valida algoritmo explícito, firma, issuer, audience, fechas, tipos y presencia de claims; rechazar alg=none, algoritmos alternativos y tokens con propósito diferente. No seguir URLs de claves indicadas por el cliente.

El secreto JWT_SIGNING_KEY vive fuera de Git y del frontend; JWT_ISSUER y JWT_AUDIENCE se fijan por entorno. Rotación planificada invalida tokens anteriores y exige login. Si se necesitara coexistencia de claves, implementar primero un registro de claves kid permitido y política explícita; no inferir claves desde el token.

Cookie de producción: __Host-access_token, HttpOnly, Secure, SameSite=Lax, Path=/, sin Domain y Max-Age de 900 segundos. En HTTP local usar nombre diferente y Secure desactivado solo por configuración de desarrollo. JWT no se devuelve en JSON ni se guarda en localStorage o sessionStorage. La elección de cookie exige protección CSRF, descrita a continuación.

Mantener sessions con id igual al jti, user_id, created_at, expires_at y revoked_at. Cada petición privada valida también esa fila y el estado actual de usuario/email/rol. Esto permite logout inmediato y revocación al restablecer contraseña, a costa de consultar PostgreSQL: no se promete una arquitectura completamente stateless. JWT inválido o revocado: 401. No implementar refresh token en esta entrega; al vencer se solicita login y se conserva únicamente el destino interno, no contraseñas ni formularios sensibles.

Login crea una nueva fila y un JWT. Logout revoca el jti y elimina cookie con los mismos atributos. El rol se consulta en base; no se acepta el rol del cliente como autorización. Un estudiante verificado puede crear cursos y modificar solo los propios mediante la condición created_by igual a sub; el administrador puede gestionar todos. La propiedad es inmutable. Categorías y roadmaps siguen reservados a administración.

CSRF: todas las operaciones que cambian estado requieren Origin dentro de la lista exacta de orígenes permitidos y un header X-CSRF-Token. GET /auth/csrf entrega un token firmado, vinculado a una cookie __Host-csrf no HttpOnly de producción, con nonce, fecha y vencimiento de 12 horas. El cliente solo lo mantiene en memoria y lo renueva al recibir CSRF_EXPIRED. El servidor comprueba firma, expiración y correspondencia con la cookie en tiempo constante. Se aplica también a login, registro y recuperación. El JWT de acceso usa otra cookie HttpOnly independiente.

El proxy elimina encabezados Forwarded/X-Forwarded-For del cliente y establece sus propios valores. La API solo confía en proxies configurados. CORS no reemplaza CSRF: en mismo origen no se necesita habilitarlo; para una separación futura, solo orígenes explícitos y credenciales, nunca comodín. Solicitudes mutantes sin Origin o token se rechazan; herramientas operativas deben obtener el CSRF y enviar el origen autorizado.

## 5. Registro y contraseñas

Se normaliza email según RN-02 y se valida longitud. El registro ignora intentos de enviar role mediante rechazo de campos desconocidos. El insert y la restricción UNIQUE resuelven carreras; una colisión recibe la misma respuesta 202 que una creación. Siempre se ejecuta un hash equivalente para reducir diferencias de tiempo evidentes. Una cuenta nueva queda activa pero con email_verified_at nulo, y se encola verificación en la misma transacción.

Política: 15–128 caracteres y rechazo de contraseñas comunes. No truncar ni transformar contraseñas. pwdlib/Argon2id con parámetros explícitos, calibrados en la máquina de referencia y registrados en la configuración técnica de implementación; revisar hashes al iniciar sesión y actualizar parámetros cuando sea necesario. No desarrollar criptografía propia.

Login inexistente verifica contra un hash ficticio fijo generado con parámetros equivalentes. Mensaje único para usuario inexistente, inactivo o password incorrecta. Solo después de contraseña correcta, una cuenta pendiente recibe 403 EMAIL_NOT_VERIFIED, sin JWT. No se garantiza tiempo idéntico a nivel de red; se evita la salida temprana y se evalúan diferencias observables. Nunca registrar cuerpos de autenticación.

## 6. Recuperación de contraseña

Solicitud válida devuelve siempre 202 con mensaje genérico. Para una cuenta activa, genera 32 bytes aleatorios, almacena hash SHA-256 con expiración de 30 minutos e invalida tokens anteriores de la cuenta, en una transacción. El link se construye desde APP_PUBLIC_URL configurada, nunca desde Host recibido.

El correo se encola en PostgreSQL dentro de la misma transacción. Para enviarlo posteriormente se requiere temporalmente el token original: el payload de correo se guarda cifrado con una biblioteca AEAD mantenida, por ejemplo AES-GCM mediante cryptography, usando nonce único y clave exclusiva fuera de la base. Solo la tabla de verificación conserva el hash; no guardar token legible en tablas, logs ni backups sin cifrar. El secreto de cifrado no debe compartir valor con la clave CSRF o HMAC de límites.

El worker reclama mensajes con bloqueo y SKIP LOCKED, usa SMTP con timeout de 10 segundos y TLS en producción, registra intentos y elimina el payload cifrado después de entrega o vencimiento. Realiza como máximo 3 intentos totales: el inicial y dos reintentos a los 30 y 120 segundos después del fallo anterior, siempre antes de vencer el token. Un lease de 60 segundos permite recuperar trabajos de un worker caído. SMTP no garantiza exactamente una entrega: un reintento puede duplicar correo, pero el token solo puede consumirse una vez. Un token sustituido puede producir un enlace inválido recibido tarde; la pantalla permite pedir otro.

La URL propuesta lleva token en fragmento: /restablecer-contrasena#token=valor. El frontend lo captura en memoria y limpia el fragmento con reemplazo del historial antes de consultar la API. Así no se envía en el request inicial ni en Referer. Referrer-Policy: no-referrer y ausencia de scripts de terceros en esta pantalla. Recargar después de limpiar exige reabrir el enlace del correo. No se guarda token en almacenamiento web.

Restablecer adquiere bloqueo de la fila de usuario y token en orden consistente, valida no vencido/no consumido y actualiza contraseña, consume todos los tokens y revoca sesiones dentro de la misma transacción. El login adquiere el mismo bloqueo antes de crear sesión y verifica el hash vigente para impedir sesiones basadas en una contraseña vieja que terminaron de validarse durante un reset. Toda operación de hash bajo contención debe acotar tiempos; medir y mantener la transacción lo más corta posible.

## 7. Rate limiting sin Redis

Decisión ADR-02: usar PostgreSQL con contadores de ventana fija y operaciones atómicas. Se elige por escala académica y stack limitado. Contadores en memoria por proceso no cumplen el requisito compartido. Una futura escala mayor justificaría Redis u otra solución especializada.

| Operación | Límite por IP | Segundo límite |
| --- | --- | --- |
| Login | 20 intentos / 15 min | 5 fallos / email normalizado / 15 min |
| Registro | 10 solicitudes / hora | 3 solicitudes / email / hora |
| Solicitar recuperación | 10 solicitudes / hora | 3 solicitudes / email / hora |
| Restablecer contraseña | 10 intentos / 15 min | 5 intentos / hash de token / 15 min |
| API general | 120 solicitudes / minuto / IP | 300 solicitudes / minuto / usuario autenticado |

Todos los límites se aplican también a cuentas inexistentes. La clave de cuenta es HMAC del email normalizado, no el email legible; IP se seudonimiza con otra clave o propósito HMAC. Clave de token a partir del hash, nunca token bruto. IPv6 se agrupa por /64 para dificultar rotación trivial; explicar que redes compartidas pueden recibir límite conjunto.

Se usan ventanas UTC alineadas al reloj PostgreSQL, definidas por política y clave. INSERT con conflicto y actualización condicional permite consumir cuota solo mientras el contador está bajo el máximo. Cada admisión se confirma independientemente de la transacción de negocio: un rollback del login no devuelve cuota. Claves y políticas múltiples se evalúan en orden fijo. Si se consume una cuota y otra deniega, la primera no se reintegra; es una limitación conservadora deliberada.

El límite de fallos de login se consulta antes de verificar y se incrementa de forma atómica al fallar; antes de responder a otro fallo se vuelve a comprobar. La carrera máxima queda acotada por el límite de intentos por IP; no se afirma un corte global exacto de cinco verificaciones concurrentes. Los contadores no se eliminan al login exitoso para evitar carreras; expiran por ventana.

Para registro y solicitud de recuperación, el límite por email se aplica internamente: suprime creación adicional o correo y devuelve 202 genérico. El límite por IP sí devuelve 429. Login devuelve 429 por límite de cuenta con idéntica política para emails existentes e inexistentes. Reset devuelve un error de token unificado o 429 por cuota de intentos. Retry-After expresa segundos hasta el fin de la ventana más restrictiva que produjo el rechazo público.

Una ventana fija permite una ráfaga cerca del cambio de ventana; documentarlo como límite del diseño. Limpieza horaria borra contadores expirados hace más de 24 horas. Si no puede consultarse el limitador, operaciones sensibles fallan con 503; no continuar sin protección. Aplicar límite de tamaño antes del parsing y rate limit antes del hashing costoso.

## 8. Datos, transacciones y concurrencia

PostgreSQL es la fuente de verdad. UUID para identificadores, timestamps con zona en UTC, restricciones UNIQUE/FK/CHECK y valores permitidos controlados. Migraciones Alembic; no crear tablas automáticamente al iniciar la API. Ver BACKEND_SCHEMA.md.

Cursos y roadmaps tienen versión entera. PATCH, publicación, reemplazo de pasos y DELETE administrativos envían expected_version. La actualización condiciona versión y estado; si falla produce 409. Publicar roadmap y archivar curso bloquean las filas de cursos en orden UUID y revalidan referencias/estados, evitando que ambas acciones rompan invariantes concurrentemente. La publicación y sus pasos se confirman juntos.

Seguir y progreso usan UNIQUE por usuario/recurso e inserciones idempotentes. El usuario se extrae siempre de sesión. Para progreso se acepta la última escritura confirmada de ese usuario, documentada en la interfaz si hay dos pestañas. No se almacena porcentaje para evitar datos derivados desactualizados.

## 9. Frontend y contrato HTTP

Estado remoto en TanStack Query; estado efímero de formularios en sus componentes; identidad obtenida de /auth/me. Consultas privadas incluyen identidad en clave de caché. Logout y cambio de usuario limpian caché privada. No aplicar reintentos automáticos de mutaciones no idempotentes. Una respuesta 401 invalida la sesión local; 403 conserva sesión y muestra permisos insuficientes; 409 ofrece recargar; 429 muestra espera; 503 ofrece reintentar más tarde.

Se invalida catálogo tras CRUD, listas y detalle después de seguimiento, y todas las consultas de progreso/roadmaps propios al cambiar un curso. No confirmar visualmente una operación hasta respuesta del servidor para evitar rollback complejo en el MVP. Se puede cancelar búsqueda anterior al cambiar filtros y aplicar debounce de 300 ms.

Texto plano como contenido; no usar HTML sin sanitizar ni dangerouslySetInnerHTML. Enlaces externos con noopener y noreferrer. Validar next como ruta interna permitida: empieza por una sola barra, sin esquema ni doble barra y pertenece a una ruta de la aplicación.

## 10. Infraestructura y configuración

Servicios de Compose: web, api, db, migrate, mail-worker y smtp-dev opcional de desarrollo. En desarrollo web usa Vite con proxy; en producción usa build estático y reverse proxy. No ejecutar servidor de desarrollo como entrega pública.

db tiene healthcheck. migrate espera db saludable y finaliza con éxito antes de que api y worker arranquen. No alcanza con ordenar contenedores: comprobar disponibilidad real. Volumen persistente para PostgreSQL; red interna para db; reinicios controlados; api y worker sin root. PostgreSQL no publica puerto en producción.

Variables documentadas: APP_ENV, APP_PUBLIC_URL, ALLOWED_ORIGINS, DATABASE_URL, JWT_SIGNING_KEY, JWT_ISSUER, JWT_AUDIENCE, CSRF_SIGNING_KEY, RATE_LIMIT_HMAC_KEY, MAIL_ENCRYPTION_KEY, SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM, SMTP_TLS y LOG_LEVEL. Backend define ACCESS_TOKEN_TTL_SECONDS=900, VERIFY_EMAIL_TTL_SECONDS=86400 y RESET_TTL_SECONDS=1800 como parámetros controlados. Frontend usa VITE_API_BASE_URL=/api/v1; todo prefijo VITE_ es público y no debe contener secretos.

.env.example futuro contiene nombres y placeholders; .env real se excluye de Git. Los secretos se suministran por entorno o archivos montados. Producción exige claves de alta entropía y HTTPS. Rotación de MAIL_ENCRYPTION_KEY requiere procesar o invalidar mensajes pendientes; rotación de CSRF invalida tokens de formulario; rotación de HMAC reinicia cuotas, por lo que debe planificarse.

## 11. Operación, privacidad y disponibilidad

Logs JSON: timestamp, nivel, request_id, ruta normalizada, método, estado, duración, identificador de usuario cuando corresponda y código de error. Excluir cuerpos de autenticación, cookies, headers CSRF, emails completos y fragmentos/tokens. El proxy no registra datos sensibles. No registrar query strings indiscriminadamente. Eventos administrativos guardan auditoría mínima sin snapshots de datos secretos.

GET /health/live informa proceso vivo sin datos internos. GET /health/ready verifica PostgreSQL y migración esperada; no expone credenciales. El estado SMTP se observa en el worker y no bloquea el catálogo. Un error de base devuelve 503 y no confirma escrituras.

Retención propuesta: sesiones y tokens vencidos se purgan después de 24 horas; contadores después de 24 horas; payload de correo al enviar o vencer; metadata de outbox durante 7 días y auditoría administrativa 90 días; logs operativos 14 días. Una tarea periódica del worker realiza mantenimiento con lock para evitar ejecución duplicada. Backups cifrados diarios con retención propuesta de 7 días; acceso restringido y prueba de restauración. Los periodos son decisiones de operación del proyecto, no una declaración de cumplimiento normativo.

El MVP no incorpora borrado de cuenta por interfaz. Una eventual solicitud requiere procedimiento manual documentado y revisión de datos relacionados antes de exponer la aplicación como servicio real. No prometer privacidad legal certificada ni disponibilidad sin métricas.

## 12. Pruebas y decisiones pendientes

Tests unitarios para porcentajes, validaciones y reglas; integración con PostgreSQL real para constraints, permisos, límites y carreras; pruebas de UI y E2E para recorridos críticos. SQLite no reemplaza pruebas de restricciones y bloqueos PostgreSQL. CI instala dependencias con locks, verifica tipos/lint, tests y builds.

ADRs: ADR-01 JWT obligatorio con registro revocable de jti; ADR-02 límites en PostgreSQL; ADR-03 catálogo externo; ADR-04 roadmaps publicados inmutables; ADR-05 UI Material clara; ADR-06 acceso síncrono a datos para simplificar. Revisar estos compromisos solo con impacto explícito en requisitos, esquema y pruebas. Pendientes: proveedor SMTP, host de despliegue, requisitos docentes adicionales y versiones menores exactas al iniciar.

## 13. Verificación obligatoria de email

Registro crea usuario pendiente y un token aleatorio de 32 bytes independiente del JWT y del reset. Almacenar su SHA-256 en email_verification_tokens con expiración de 24 horas. Encolar correo cifrado usando el mismo mecanismo de outbox, con propósito verify_email y referencia explícita al token correspondiente. Reenvío invalida los previos bajo lock de usuario y conserva respuesta genérica para cualquier email; no cambia credenciales de cuentas existentes.

Enlace: /verificar-correo#token=valor. La SPA captura el fragmento y lo limpia; el usuario elige “Confirmar correo”, que envía POST con CSRF. Un GET o un escáner de correo no consume el token. Bajo lock de usuario/token, validar propósito, expiración y no consumo; establecer email_verified_at, consumir tokens de verificación y confirmar atómicamente. No emitir JWT automáticamente. Un enlace usado/vencido/alterado devuelve INVALID_VERIFICATION_TOKEN uniforme. Un nuevo intento de login puede continuar luego de confirmar.

Una cuenta no verificada no obtiene JWT ni acceso a CRUD, seguimiento o progreso. Un reset de contraseña no marca el correo como verificado. Cuentas administrativas también deben verificar su email; solo datos de pruebas aislados pueden tener verificación precargada con advertencia explícita de que no valida el flujo real.

Rate limit adicional: reenvío 10/IP/hora y 3/email/hora con supresión genérica por email; confirmación 10/IP/15 min y 5/hash de token/15 min. Se aplican también a tokens/emails inexistentes. Correo inicial comparte cuotas de registro. Payloads de outbox se eliminan al enviar o vencer; metadata de tokens y referencias se purga coordinadamente como en recuperación. No reutilizar JWT de acceso como token de verificación.

## 14. Autorización de autor

Todas las operaciones de autor derivan propietario de JWT validado y sesión vigente; no aceptan owner_id o created_by del cuerpo. GET de listados privados filtra antes de paginar por created_by; no filtra en navegador tras obtener todo. GET/PATCH/publicar/DELETE por ID aplican propietario en consulta, devuelven 404 para cursos ajenos y mantienen validaciones/versiones de administración. Las rutas /admin continúan exigiendo admin y no se abren a estudiantes por este cambio. Auditoría registra tanto autores como administradores.
