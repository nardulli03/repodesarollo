

# Changelog

Los cambios relevantes del proyecto se registran en este archivo.

## [Unreleased]

## [v0.1.0] - 2026-10-31

### Added

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