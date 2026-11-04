

# Changelog

Los cambios relevantes del proyecto se registran en este archivo.

## [Unreleased]
- Reglas puras de validación y transiciones de cursos.
- 153 casos unitarios con pytest y patrón AAA.
- pytest y pytest-cov como dependencias de desarrollo.
- Reglas de roadmap para agregar cursos publicados, evitar duplicados,
  limitar a 100 cursos, reordenar y quitar cursos conservando el progreso
  de los restantes.
- 35 pruebas unitarias de roadmap, con cobertura de líneas y ramas del 100%.
- Reglas de revisión de aportes: administrador obligatorio, prohibición
  de auto-revisión, estado en revisión, motivo de rechazo y confirmación
  del enlace para aprobar.
- 33 pruebas unitarias de revisión de aportes, con cobertura de líneas
  y ramas del 100%.
  - Persistencia de cursos con SQLAlchemy y Psycopg: creación, consulta,
  catálogo paginado, búsqueda, filtro por categoría, actualización parcial
  y baja lógica.
- PostgreSQL exclusivo para pruebas mediante docker-compose.test.yml.
- 33 pruebas de integración con PostgreSQL, esquemas temporales y rollback.
- Validación de JWT en cookie y sesiones revocables en PostgreSQL.
- Consulta de identidad mediante GET /api/v1/auth/me.
- Creación de borradores, envío a revisión y aprobación o rechazo
  por un administrador distinto del autor.
- Registro de decisiones de revisión y control de versión.
- Protección CSRF con token firmado, cookie, header y Origin.
- 30 pruebas de sesiones y 26 del flujo HTTP de aportes.
- Hook useCursos con carga, errores, paginación, filtros y refetch.
- 23 pruebas con Vitest y Testing Library, incluyendo cancelación
  y protección frente a respuestas antiguas.
- Búsqueda y navegación entre páginas en el catálogo.
- Backend con Dockerfile de dos etapas, dependencias sin herramientas
  de desarrollo, ejecución como appuser y healthcheck HTTP.
- Imagen verificada: 273.969.071 bytes. El objetivo de menos de 100 MB
  todavía no se cumple.
- Archivos .dockerignore para backend y frontend que excluyen entornos
  locales, cachés, pruebas, reportes, variables de entorno y logs.
- Configuración de Nginx con fallback SPA, proxy /api, headers de
  seguridad, healthcheck HTTP y caché para assets con hash.
- Migración inicial de Alembic para usuarios, categorías, cursos,
  sesiones y revisiones.
- Dos pruebas de migraciones sobre esquemas temporales de cursos_test.

### Fixed
- Error DATABASE_UNAVAILABLE del catálogo causado por la ausencia
  de tablas en la base de desarrollo.


## [v0.1.0] - 2026-10-31



### Added
- Estructura inicial de backend y frontend organizada por dominios.
- Plantilla de variables de entorno para desarrollo.
- Backend mínimo con FastAPI: GET /health y GET /api/v1/courses.
- Listado vacío de cursos con formato paginado.
- Frontend React que consulta GET /api/v1/courses mediante proxy de Vite.
- Pantalla de catálogo con estados de carga, error y lista vacía.
- Estilos base mobile-first.
- Dockerfiles simples para backend y frontend.
- Docker Compose con PostgreSQL 18.6, backend y frontend.
- Volumen persistente para PostgreSQL.

### Changed
- Proxy de Vite configurable para comunicarse con el backend en Docker.
- Instrucciones de arranque con Docker Compose en el README.
- El catálogo consulta PostgreSQL y muestra únicamente cursos publicados,
con paginación, búsqueda y filtro por categoría.
- El catálogo utiliza useCursos y permite reintentar sin recargar la página.
- Frontend compilado con Node 24 y servido desde Nginx Alpine Slim.
- Compose conserva localhost:5173 y lo conecta al puerto 80 de Nginx.