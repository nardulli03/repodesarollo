
IMPLEMENTATION_PLAN — Cursos Abiertos
Versión 2.0. Modalidad individual. Tareas planificadas, ninguna se marca implementada. La aprobación por correo con T1 es condición de inicio de B.

1. MVP P0 y fases
P0 incluye HU-01..HU-12 del PRD: catálogo, ficha, registro/login/logout, recuperación, rate limit, aporte y CRUD propio, roadmap personal, revisión administrativa, progreso, verificación y consulta de aportes. Sin roadmaps públicos, worker, carga propia de videos ni categorías editables.

DoD B: en máquina limpia, clonar, seguir README, docker compose up, acceder a frontend5173/API8000/Mailpit8025 y completar las historias P0 desde UI con PostgreSQL persistente; sin errores de consola que impidan los recorridos. README debe tener comandos exactos realmente verificados, migración, seed, variables, URLs y datos locales. No se presenta este objetivo como logrado.

A: corregir documentación, versionar, pedir revisión y esperar APROBADO/T1. B: construir funcionalidades y comprobarlas manualmente. Continuidad: pruebas automatizadas, Docker multi-stage, .dockerignore, no-root, caché y healthchecks avanzados en tickets de clase. No son precondición P0 de B.


2. Módulos y dependencias
Dependencias indican prerrequisitos, no trabajo paralelo de integrantes. Una funcionalidad principal en curso.

3. Detalle por módulo
A — Revisión documental
A1: reemplazar documentos y conservar originales	Archivos/nombres/enlaces correctos; diff revisado.	1–2 h
A2: revisión cruzada y PR	Historias/pantallas/API/tablas/tareas consistentes, sin placeholders de decisiones salvo versiones verificables y datos personales.	1–2 h

M0 — Base e infraestructura, después del T1
0.1	Resolver versiones y estructura TRD	Versiones verificadas registradas; carpetas por dominio; manifests/locks del stack.	1 h

0.2	Compose y Dockerfiles mínimos	BD, migrate, API, UI, Mailpit levantan siguiendo README; API responde GET /health con 200 y confirma conexión en entorno local sin secretos.	2 h

0.3	Modelos y Alembic	Base vacía migra con tablas, FK, UNIQUE y CHECK del schema.	3 h

0.4	Seeds idempotentes	Categorías y cursos con datos reales revisados; dos cuentas diferentes para autor/admin, claves desde entorno; repetir no duplica.	1 h
GET /health es endpoint operativo público fuera de /api/v1; 200 vivo y BD disponible, 503 si BD inaccesible, sin datos de conexión. La versión definitiva y su contrato deben conservarse en BackendSchema.

M1 — Identidad, JWT y correo
1.1	Registro y hashing	Cuenta student y roadmap vacío atómicos; email único, password no legible y rol del cliente rechazado.	2 h

1.2	Verificación/reenvío y UI	Email en Mailpit, confirmar una vez, pendiente no inicia sesión, reenviar invalida anterior.	3 h

1.3	Login/me/logout, CSRF y guardas	Cookie JWT validada, acceso privado, logout revocado; falta CSRF/origen se rechaza.	3 h

1.4	Rate limit compartido	Cuota antes del hashing, 429/Retry-After; reinicio API conserva contador.	2 h

1.5	Recuperación completa	Email local, cambio, token consumido, sesiones previas inválidas, contraseña anterior falla.	3 h

M2 — Catálogo
2.1	Listados y detalle API	Publicados únicamente; categorías paginadas; filtros/orden estables.	2 h

2.2	UI catálogo/ficha/header	Búsqueda en URL, cards, ficha completa, estados y menú móvil funcional.	3 h

2.3	Tokens y adaptación base	Estilos mobile-first visibles y mejoras min-width; todos los listados conservan paginación.	2 h

M3 — Aportes y validación
3.1	CRUD de autor	Propietario desde JWT, metadatos completos y estados; ajeno404; URL duplicada409.	3 h

3.2	Formularios y propios	Guardar/editar/enviar/archivar desde UI, declaración sí/no y estado/motivo visibles.	3 h

3.3	Revisión admin	Cola paginada, aprobar tras comprobar enlace, rechazar con motivo, auto-revisión403.	3 h

3.4	Edición publicada y conflictos	Sale del catálogo al volver a borrador; roadmap conserva referencia; versión vieja409.	1 h

M4 — Roadmap personal
4.1	Agregar/quitar y privacidad	Solo publicados al agregar, sin duplicados, lista propia y límite100; usuarioB no accede a itemA.	2 h

4.2	Reordenar y paginar	Mover posición global cambia orden persistente incluso entre páginas, sin huecos.	2 h

4.3	Progreso y UI	Fracción/porcentaje y siguiente disponible correctos; quitar advierte que borra avance; no disponible bloquea actualización de estado.	3 h

M5 — Integración y entrega
5.1	Recorrer aceptación P0	Matriz §5 completada con evidencia real y problemas registrados, no solo compilación.	3 h

5.2	Instalación limpia y README	Persona sigue comandos exactos y completa flujo sin pasos implícitos; datos persisten al reiniciar.	2 h

5.3	UX/seguridad/documentación	Teclado, contraste y 360/768/1440 revisados; API, UI y docs coinciden.	2 h

4. Ejecución y tablero
Issues HU-01 a HU-12; cada uno incluye RF/RN/RNF, aceptación del PRD, subtareas de §3, dependencias, evidencia y rama/commit. Estados Pendiente/En curso/En revisión/Terminado; WIP1 por ser individual.

A1-A2	A	[ ]	docs/modificaciones-consigna; correcciones preparadas, pendiente integrar/revisar.
A3	A	[ ]	Pendiente PR/merge.
0.1-0.4	M0	[ ]	
1.1-1.5	M1	[ ]	—
2.1-2.3	M2	[ ]	—
3.1-3.4	M3	[ ]	—
4.1-4.3	M4	[ ]	—
5.1-5.3	M5	[ ]	—

Cada tarea al ejecutarse se desglosa en su fila o issue y recibe rama/commit propios o lote coherente. No marcar módulo completo por haber terminado una sola subtarea. [x] solo tras evidencia.

5. Evidencia y estrategia de testing
Aceptación funcional de B
Historias	Requisitos/reglas	Evidencia esperada, todavía no producida

HU-01/02	RF-06/13, RN-01, RNF-02/03	Capturas o registro de catálogo/filtros/ficha y páginas; borrador no visible.

HU-03/11	RF-01/02/03/12, RN-13, RNF-01	Registro→Mailpit→confirmación→JWT→logout; pending no emite acceso.

HU-04	RF-04, RNF-01/07	Reset exitoso, token repetido inválido y sesión previa rechazada.

HU-05	RF-05	429/Retry-After y conservación tras reinicio de API.

HU-06/07/12	RF-07/08/09, RN-02/04/07/08/10	Aporte completo, rechazo/corrección, ajeno404, archivo y edición publicada.

HU-08/10	RF-10/11, RN-03/05/09/11/12	Dos usuarios aislados, orden entre páginas, duplicado y progreso; no disponible con aviso.

HU-09	RF-09, RN-01/06	Admin distinto valida y curso aparece; no auto-revisión; motivo al rechazar.

Todas	RNF-04/05/06/09	Clon limpio, estructura por dominio, teclado/contraste y revisión de logs sin secretos.

Evidencias con cuentas de demo; ocultar tokens/cookies/password. La validación humana de enlaces registra URL fuente.






