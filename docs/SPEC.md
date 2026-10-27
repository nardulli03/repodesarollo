SPEC — Cursos Abiertos
Versión documental 2.0, 27/10/2026. Refinamiento de la [SPEC oficial](referencias/SPEC.md). Propuesta para revisión, sin aplicación implementada.

1. Identidad del producto
Nombre: Cursos Abiertos. Una línea: una comunidad aporta cursos gratuitos validados y cada estudiante organiza su aprendizaje en un roadmap personal.

2. Problema
Los recursos gratuitos están dispersos y sus descripciones no siempre aclaran edición, docentes, exámenes o certificados. Encontrar un enlace no alcanza para decidir si sirve para una meta de estudio.
El catálogo comunitario reúne esos metadatos. La revisión previa reduce aportes incompletos o que no ofrecen contenido gratuito. El roadmap permite decidir un orden propio y retomar el avance sin depender del historial del navegador.

3. Visión
En doce meses, la comunidad dispone de un catálogo mantenido y confiable, con aportes trazables y recorridos personales útiles. El MVP valida ese ciclo básico sin convertirse en plataforma de videos ni de certificación.

4. Alcance
Dentro
Consulta pública, búsqueda y filtros; registro, verificación de correo, JWT, logout y recuperación completa; rate limit; CRUD de cursos propios con revisión; validación administrativa; lista de categorías; un roadmap privado por usuario con incorporación de cursos publicados, orden, retiro y progreso. Entorno Docker Compose reproducible y diseño Material claro inspirado en Google.
Fuera
Roadmaps públicos/editoriales, seguimiento de recorridos de terceros, múltiples roadmaps por usuario, pagos, alojamiento de lecciones, videos o archivos, certificados propios, evaluaciones internas, comentarios, puntuaciones, IA, login social, MFA, edición de email y panel público de gestión de usuarios. Los certificados del proveedor pueden ser pagos si el contenido principal sigue siendo gratuito y se aclara.

5. Reglas de producto clave
ID	Regla	Origen

RN-01	Solo cursos gratuitos y aprobados aparecen en el catálogo.	SPEC oficial: aportes validados.

RN-02	El aportante declara explícitamente si tomó el curso.	SPEC oficial.

RN-03	Cada usuario gestiona únicamente su roadmap privado; uno por usuario en MVP.	Personal: SPEC; privacidad y cantidad: decisión de producto.

RN-04	El autor gestiona sus cursos; el administrador revisa y puede archivarlos.	CRUD previo y decisión sobre validación.

RN-05	El progreso personal no acredita aprobación externa ni se infiere de la declaración del aportante.	Decisión propia.
Detalle completo en [PRD §7].

6. Stack registrado
Capa	Requisito/selección	Versión exacta comprobada
Frontend	React 19, Vite, pnpm	Pendiente de resolución/verificación; no se inicializó la aplicación.
Backend	FastAPI, uv	Pendiente; SPEC da 0.158.2 como referencia, no como instalación realizada.
Datos	PostgreSQL 18.6 según SPEC	Pendiente de comprobar disponibilidad y ejecución.
Infra	Docker y Docker Compose	Pendiente de registrar salida real de herramientas.
Registrar versiones mediante pnpm -v, uv --version, docker --version, docker compose version y versiones efectivas de dependencias una vez autorizada la implementación. Ante indisponibilidad de una versión exigida, informar y acordar alternativa; no sustituirla silenciosamente.

7. Restricciones técnicas heredadas
Restricción	Cumplimiento previsto
Mobile-first con mejora progresiva	Base de una columna sin media queries; mejoras de layout solo con min-width. UX-UI §3.
Paginación de todas las consultas/listados y tablas	page/page_size/total en catálogo, aportes, revisión, roadmap y categorías; opciones de categorías con paginación.
Menú sándwich móvil	Header con botón accesible, panel, Escape y restitución de foco.
Screaming Architecture	Carpetas por identidad, cursos, aportes y roadmap, con capas internas. TRD §3.
Apariencia Google/Material	Valores y estados concretos en UX-UI, sin copiar marca.


8. Vacíos y decisiones
Vacío	Opciones	Decisión y motivo	Detalle
Quién valida	Automático, pares, administrador	Administrador revisa metadatos, gratuidad y enlace; viable en trabajo individual.	PRD RN-06, TRD TD-04
Cantidad de roadmaps	Uno, varios	Uno privado por usuario; alcanza para organizar cursos sin sumar gestión de múltiples listas.	PRD RN-03
Qué es catálogo personal	Copia de cursos, referencias	Referencias del roadmap al curso comunitario; evita duplicar metadatos.	BackendSchema
Edición publicada	Directa, revisión posterior	Pasa a revisión y sale temporalmente del catálogo; los roadmaps existentes conservan referencia y aviso.	PRD RN-07
Baja de cursos	Física, lógica	Archivado terminal; conserva historia y progreso.	PRD RN-08
Datos no informados	Inventar, rechazar, representar desconocido	Versión/año/docentes pueden declararse no informados; los indicadores se responden sí/no tras revisión.	PRD §5
Enlace activo	Fetch automático, revisión humana	Validador abre el enlace y registra fecha; sin fetch de URLs arbitrarias desde API.	TRD TD-04
Autenticación	Sesión opaca, JWT	JWT firmado y revocable en cookie, por requerimiento previo. Correo verificado antes de login.	TRD TD-01
Búsqueda	Texto, filtros	Texto por título/tema/proveedor y filtros categoría/nivel/idioma combinables.	PRD HU-01




