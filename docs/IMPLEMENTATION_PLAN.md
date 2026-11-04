# Plan de implementación — Cursos Abiertos

Modalidad individual. Este documento reúne el alcance de la Instancia B, el trabajo pendiente del MVP y la evidencia del ciclo de pruebas e infraestructura. El scaffold inicial se publicó como `v0.1.0`.

## 1. Alcance y fases

El MVP P0 comprende las historias HU-01 a HU-12 del PRD: catálogo y ficha, identidad y verificación de correo, recuperación de contraseña, límite de intentos, aportes de cursos, revisión administrativa, roadmap privado y progreso. Quedan fuera los roadmaps públicos, un worker separado, la carga de videos y la edición de categorías.

- **Instancia A.** Revisar y versionar la documentación, conservar las fuentes originales y solicitar la aprobación docente.
- **Instancia B.** Implementar las historias P0 y comprobar sus recorridos en la interfaz.
- **Continuidad.** Incorporar pruebas automatizadas, imágenes de múltiples etapas, exclusiones de Docker, ejecución sin privilegios, caché y healthchecks.

La Instancia B se completa cuando una persona puede clonar el repositorio en un entorno limpio, seguir el README, aplicar migraciones, cargar datos de prueba y recorrer las historias P0 desde la interfaz. PostgreSQL debe conservar los datos al reiniciar. Los recorridos de correo requieren un entorno de prueba como Mailpit. La verificación del scaffold y las pruebas del ciclo acreditan los puntos registrados en este plan.

## 2. Estado y trabajo por módulo

Las horas corresponden a estimaciones iniciales.

| Módulo | Estado actual | Tareas y criterios de aceptación |
| --- | --- | --- |
| A — Documentación | Correcciones integradas por el PR #1 | A1. Conservar originales y revisar archivos, nombres, enlaces y diff (1–2 h). A2. Contrastar historias, pantallas, API y tablas y registrar la revisión en un PR (1–2 h). |
| M0 — Base e infraestructura | Stack, Compose y migración inicial verificados | 0.1. Registrar versiones, estructura y lockfiles (1 h). 0.2. Levantar BD, API e interfaz siguiendo el README (2 h). 0.3. Migrar una base vacía con las restricciones del modelo (3 h). 0.4. Cargar categorías, cursos y cuentas de demo sin duplicar datos al repetir el seed (1 h, pendiente). |
| M1 — Identidad y correo | Validación de JWT, sesiones revocables, identidad y CSRF comprobadas por pruebas HTTP | 1.1. Registrar una cuenta de estudiante y su roadmap en una transacción, con correo único y contraseña hasheada (2 h). 1.2. Verificar correo y permitir reenvío, invalidando el token anterior (3 h). 1.3. Completar login y logout con cookie JWT y revocación (3 h). 1.4. Aplicar límite de intentos persistente y responder 429 con Retry-After (2 h). 1.5. Recuperar contraseña con token de un solo uso y revocar sesiones previas (3 h). |
| M2 — Catálogo | Listado de publicados, búsqueda, paginación, filtro de categoría en API y estados de interfaz verificados | 2.1. Completar ficha y listado paginado de categorías (2 h). 2.2. Completar ficha, filtros en URL y navegación móvil (3 h). 2.3. Revisar tokens, adaptación y paginación en los listados (2 h). |
| M3 — Aportes y revisión | API de borradores, envío a revisión, aprobación y rechazo verificada | 3.1. Completar el CRUD HTTP de autor, con propiedad derivada de la sesión, 404 para aportes ajenos y 409 para duplicados (3 h). 3.2. Incorporar formularios y consulta de aportes propios (3 h). 3.3. Completar la cola paginada y la interfaz administrativa, con motivo de rechazo y prohibición de autorrevisión (3 h). 3.4. Completar edición y archivo de publicaciones, conservar referencias del roadmap y gestionar conflictos de versión (1 h). |
| M4 — Roadmap | Reglas y pruebas unitarias verificadas | 4.1. Integrar agregado y retiro de cursos, privacidad, límite de 100 y validación de duplicados (2 h). 4.2. Persistir el orden global incluso entre páginas (2 h). 4.3. Implementar progreso, siguiente curso disponible y avisos en la interfaz (3 h). |
| M5 — Integración y entrega | Clon limpio del scaffold y arranque del ciclo verificados | 5.1. Completar la matriz de aceptación P0 (3 h). 5.2. Verificar instalación limpia y persistencia tras reiniciar con el flujo completo (2 h). 5.3. Revisar teclado, contraste, anchos de 360/768/1440 px y coherencia de documentación, API e interfaz (2 h). |

El `GET /health` actual comprueba que el proceso HTTP responde. La consulta del catálogo a través de Nginx comprueba también el acceso a PostgreSQL. Queda pendiente el contrato de salud de base de datos previsto en BackendSchema.

## 3. Ejecución y seguimiento

Organizar el tablero por historias HU-01 a HU-12. Cada issue debe registrar requisitos, aceptación, dependencias, subtareas, rama o commit y evidencia. Usar los estados Pendiente, En curso, En revisión y Terminado, con una tarea principal en curso.

Las ramas de trabajo parten de `dev` y se integran mediante PR hacia `dev`. El flujo reserva `main` para releases con changelog y tag anotado. El historial conserva commits previos que no cumplen Conventional Commits y merges accidentales hacia `main`.

## 4. Estrategia de pruebas y aceptación

Las pruebas unitarias comprueban reglas puras. La integración del backend usa PostgreSQL de testing y esquemas temporales. Las pruebas del hook simulan `fetch` para comprobar el estado del frontend. Los recorridos HTTP por Nginx y el arranque con Compose complementan esas pruebas.

| Historias | Requisitos y reglas | Evidencia de aceptación del MVP |
| --- | --- | --- |
| HU-01 y HU-02 | RF-06/13, RN-01, RNF-02/03 | Catálogo, filtros, ficha y páginas. Los borradores permanecen fuera del catálogo. |
| HU-03 y HU-11 | RF-01/02/03/12, RN-13, RNF-01 | Registro, correo de verificación, confirmación, login y logout. Una cuenta sin verificar queda sin acceso. |
| HU-04 | RF-04, RNF-01/07 | Cambio de contraseña, rechazo de token reutilizado y revocación de sesiones anteriores. |
| HU-05 | RF-05 | Respuesta 429 con Retry-After y conservación del contador tras reiniciar la API. |
| HU-06, HU-07 y HU-12 | RF-07/08/09, RN-02/04/07/08/10 | Aporte, rechazo, corrección, edición y archivo. Un usuario ajeno recibe 404. |
| HU-08 y HU-10 | RF-10/11, RN-03/05/09/11/12 | Privacidad con dos cuentas, orden entre páginas, duplicados, progreso y avisos de indisponibilidad. |
| HU-09 | RF-09, RN-01/06 | Un administrador distinto del autor aprueba y el curso aparece en el catálogo. El rechazo exige motivo. |
| Todas | RNF-04/05/06/09 | Clon limpio, estructura por dominio, teclado, contraste y logs sin secretos. |

Registrar resultados reales y pasos reproducibles. Usar cuentas de demo, ocultar credenciales y registrar la URL fuente al comprobar un enlace.

## 5. Evidencia del scaffold

| Ticket | Resultado |
| --- | --- |
| T1 — Estructura y configuración | PR #2, merge `1154ffa`. |
| T2 — Backend mínimo | PR #3, merge `97e0e5a`. |
| T3 — Frontend mínimo | PR #4, merge `26e1cc4`. |
| T4 — Docker Compose | PR #5 y corrección en PR #6, merge `fcf87cc`. |
| T5 — Verificación y publicación | Clon limpio de `dev` verificado. Release `v0.1.0` integrado en `main` mediante PR #7. |

En el clon limpio se creó `.env` desde el ejemplo y se levantaron los servicios con `docker compose -p cursos-verificacion-v010 up -d --build`. Se verificaron los tres contenedores en estado `Up`, el backend con HTTP 200 en `/health` y el frontend accesible con el catálogo inicial vacío.

## 6. Evidencia del ciclo de clase

| Ticket | Resultado y trazabilidad |
| --- | --- |
| T1 — Reglas de cursos | 153 pruebas unitarias aprobadas y 97 % de cobertura del módulo con ramas. PR #8. |
| T2 — Roadmap | 35 pruebas aprobadas y 100 % de cobertura de líneas y ramas del módulo. PR #9. |
| T3 — Revisión de aportes | 33 pruebas aprobadas y 100 % de cobertura de líneas y ramas del módulo. PR #10. |
| T4 — Repositorio de cursos | 33 pruebas de integración con PostgreSQL. Creación, consulta, paginación, búsqueda, filtros, actualización y baja lógica. Trabajo recuperado en `dev` por el PR #15. |
| T5 — Flujo HTTP | 30 pruebas de sesiones y 26 de aportes. Se comprobó autorización, revisión, catálogo y CSRF. PR #16. |
| T6 — Hook del catálogo | 23 pruebas aprobadas, lint y build correctos. Cobertura de `useCursos.js`: 97,67 % de líneas y 88,13 % de ramas. PR #19. |
| T7 — Imagen del backend | Múltiples etapas, Uvicorn como `appuser` con UID 10001, `uv` ausente del runtime y contenedor saludable. **Parcial:** 273.969.071 bytes (273,97 MB) frente al objetivo de menos de 100 MB. PR #20. |
| T8 — Contextos Docker | Se reconstruyeron ambas imágenes y se verificó la exclusión de cachés de Python y de la prueba del hook del frontend. PR #22. |
| T9 — Nginx | Build con Node.js 24, runtime Alpine Slim, fallback SPA, proxy, headers y caché de assets con hash. Imagen de 20.896.193 bytes (20,90 MB), por debajo de 30 MB. PR #23. |
| Corrección — Migraciones | Revisión `0001_initial` aplicada y `alembic check` sin diferencias. El catálogo pasó a HTTP 200 a través de Nginx. Suite de backend: 312 pruebas aprobadas y 92 % de cobertura de `app` con ramas. PR #24. |
| T10 — Healthchecks | PostgreSQL con `pg_isready`, backend con el healthcheck de su Dockerfile y Nginx con `/health`. Tres servicios `healthy` y catálogo HTTP 200. PR #25. |
| T11 — Cierre | Changelog, plan y retrospectiva integrados en `dev` mediante PR #27, merge `053c86b`. |

### Retrospectiva

- Ejecutar pruebas antes de abrir cada PR permitió detectar errores antes de integrar.
- PostgreSQL de testing permitió verificar persistencia y migraciones con datos aislados.
- Los merges accidentales hacia main llevaron a verificar la rama base antes de fusionar.
- La prueba del catálogo por Nginx reveló que faltaban las tablas de desarrollo y motivó la migración inicial.
- La medición de la imagen del backend dejó registrado el objetivo de tamaño pendiente.
