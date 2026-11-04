# Changelog

Los cambios relevantes de Cursos Abiertos se registran en este archivo.

## [Unreleased]

### Added

- Reglas de validación y transiciones de cursos, con 153 pruebas unitarias de pytest escritas con el patrón Arrange, Act, Assert.
- Reglas del roadmap para agregar cursos publicados, evitar duplicados, limitar la lista a 100 cursos, reordenarlos y quitarlos conservando el progreso de los restantes. Las 35 pruebas unitarias alcanzaron el 100 % de cobertura de líneas y ramas del módulo.
- Reglas de revisión de aportes para verificar el rol de administrador, impedir la autorrevisión, comprobar el estado del aporte y exigir un motivo de rechazo o la confirmación del enlace para aprobar. Las 33 pruebas unitarias alcanzaron el 100 % de cobertura de líneas y ramas del módulo.
- Persistencia de cursos con SQLAlchemy y Psycopg. Incluye creación, consulta, búsqueda, filtro por categoría, paginación, actualización parcial y baja lógica.
- PostgreSQL de testing mediante `docker-compose.test.yml` y 33 pruebas de integración del repositorio con esquemas temporales y rollback.
- Validación de JWT en cookie, sesiones revocables en PostgreSQL, consulta de identidad mediante `GET /api/v1/auth/me` y protección CSRF.
- Flujo HTTP de creación de borradores, envío a revisión, aprobación y rechazo. Incluye control de versión y registro de las decisiones. Se verificó con 30 pruebas de sesiones y 26 pruebas del flujo de aportes.
- Hook `useCursos` con estados de carga y error, filtros, paginación, reintento y cancelación de solicitudes. Se verificó con 23 pruebas de Vitest y Testing Library.
- Migración inicial de Alembic para usuarios, categorías, cursos, sesiones y revisiones, con dos pruebas en esquemas temporales de `cursos_test`.

### Changed

- El catálogo consulta PostgreSQL, muestra cursos publicados y permite buscar, cambiar de página y reintentar sin recargar la interfaz.
- El backend utiliza una imagen de dos etapas, ejecuta Uvicorn como `appuser` e incorpora un healthcheck HTTP. La imagen medida en T7 pesó **273.969.071 bytes (273,97 MB)**. Sigue pendiente el objetivo de menos de 100 MB.
- Los archivos `.dockerignore` del backend y el frontend excluyen entornos locales, cachés, pruebas, reportes, archivos `.env` y logs del contexto de construcción.
- El frontend se compila con Node.js 24 y se sirve con Nginx Alpine Slim. Nginx incluye fallback para la SPA, proxy de `/api`, headers de seguridad, endpoint `/health` y caché para assets con hash. La imagen medida en T9 pesó **20,90 MB**, por debajo del objetivo de 30 MB.
- Docker Compose mantiene el acceso al frontend en `localhost:5173` y lo dirige al puerto 80 de Nginx. El backend espera a que PostgreSQL esté saludable y Nginx espera a que lo esté el backend. Se verificaron los tres servicios en estado `healthy`.

### Fixed

- Se corrigió el error `DATABASE_UNAVAILABLE` que provocaba la falta de tablas en la base de desarrollo. Después de aplicar la migración inicial, el catálogo volvió a responder HTTP 200 a través de Nginx.

## [v0.1.0] - 2026-10-31

### Added

- Estructura inicial del backend y el frontend organizada por dominios.
- Plantilla de variables de entorno para desarrollo.
- Backend mínimo con FastAPI y los endpoints `GET /health` y `GET /api/v1/courses`. El listado de cursos devolvía una colección vacía con formato paginado.
- Catálogo inicial en React con estados de carga, error y lista vacía, estilos adaptables y proxy de Vite para comunicarse con el backend.
- Dockerfiles iniciales y configuración de Docker Compose para PostgreSQL 18.6, backend y frontend, con volumen persistente para PostgreSQL.
- Instrucciones de arranque con Docker Compose en el README.
