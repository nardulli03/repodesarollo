

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
### Added
- Validación de JWT en cookie y sesiones revocables en PostgreSQL.
- Consulta de identidad mediante GET /api/v1/auth/me.
- Creación de borradores, envío a revisión y aprobación o rechazo
  por un administrador distinto del autor.
- Registro de decisiones de revisión y control de versión.
- Protección CSRF con token firmado, cookie, header y Origin.
- 30 pruebas de sesiones y 26 del flujo HTTP de aportes.


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