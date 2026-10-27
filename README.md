Cursos Abiertos

## Cómo levantar

Scaffold en construcción. Las instrucciones de ejecución
se completarán y verificarán en el ticket T4.

Todavía no están implementados el backend, el frontend
ni Docker Compose.

## Estado del desarrollo
El ticket docente del 27/10/2026 habilita el desarrollo
del scaffold mínimo.

- T1: estructura y configuración inicial en preparación.
- T2: backend mínimo pendiente.
- T3: frontend mínimo pendiente.
- T4: Docker Compose de desarrollo pendiente.
- T5: release v0.1.0 pendiente.

## Flujo de trabajo vigente
Las ramas de trabajo nacen desde dev y se integran en dev.
main recibe únicamente releases desde dev, con CHANGELOG
actualizado y tag vX.Y.Z.

Detalle en [GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).

Webapp de comunidad de cursos gratuitos: los usuarios aportan recursos de distintas plataformas; después de una revisión, los cursos integran el catálogo comunitario y cada persona organiza su roadmap privado.

Materia: Desarrollo de Software, sección S34, UTN FR La Plata, 2026. Modalidad: individual.
Repositorio: https://github.com/nardulli03/repodesarollo
Estado: Instancia A en corrección documental. Sin aprobación docente ni T1 registrados en esta documentación. No se afirma implementación ni ejecución de pruebas.
Rama de correcciones creada: docs/modificaciones-consigna. 

Qué hace
Permite consultar el catálogo sin cuenta, registrarse, verificar correo e iniciar sesión con JWT. Un usuario verificado aporta cursos, declara si los tomó y consulta sus estados de revisión. Un administrador valida o rechaza aportes. Cada usuario gestiona un roadmap personal: agrega cursos publicados, los ordena, los quita y registra avance. Incluye recuperación de contraseña y rate limit de login.

Stack
React 19 + Vite + pnpm; FastAPI + uv; PostgreSQL 18.6 exigido por la SPEC; Docker y Docker Compose en desarrollo. Las versiones exactas resueltas y comprobadas se registrarán en [TRD](docs/TRD.md). No se declaran instalaciones que no se realizaron.

Documentación
[SPEC](docs/SPEC.md)	Refinamiento, alcance, origen y decisiones.
[PRD](docs/PRD.md)	Personas, historias, aceptación, requisitos y reglas.
[TRD](docs/TRD.md)	Arquitectura, stack, seguridad y decisiones técnicas.
[UX-UI](docs/UX-UI.md)	Tokens, componentes, estados y adaptación.
[APPFlow](docs/APPFlow.md)	Pantallas, navegación y relación con API.
[BackendSchema](docs/BackendSchema.md)	Datos, relaciones, estados y contratos.
[IMPLEMENTATION_PLAN](docs/IMPLEMENTATION_PLAN.md)	Módulos, tareas, dependencias y evidencia.
[GIT_WORKFLOW](docs/GIT_WORKFLOW.md)	Ramas, revisión, merge y commits.
[SPEC oficial recibida](docs/referencias/SPEC.md)	Copia sin modificaciones del adjunto del 21/10.
[Borrador del aula](docs/referencias/SPEC-borrador-clase-2026-10-20.md)	Antecedente sin modificaciones; no reemplaza la SPEC oficial.

Cómo revisar
Leer SPEC → PRD → TRD → UX-UI → APPFlow → BackendSchema → plan. GitHub renderiza Markdown y Mermaid. Comprobar que pantallas, endpoints, requisitos e historias coincidan. La checklist oficial no fue incluida entre los adjuntos disponibles: la revisión por plantillas no se presenta como checklist oficial completada.
Estado de las instancias
Instancia	Estado documentado	Condición de cierre
A: documentación	Correcciones preparadas; pendiente subir y solicitar revisión	Aprobación explícita del repo entero y recepción del T1.
B: MVP	Pendiente de aprobación y T1	Clon limpio, seguir README y docker compose up; historias P0 operativas desde UI.
Continuidad del 27/10	Planificada; no se afirma realizada	Tickets de pruebas y mejoras Docker según docente.


Las fechas originales del correo son 23/10/2026 para A y 26/10/2026 para B. Esta revisión se prepara el 27/10/2026; no altera plazos ni presupone prórroga. Si aún falta aprobación, corresponde recuperar la Instancia A según el correo.
Versionado
GitHub Flow individual: rama por cambio coherente, commits convencionales, PR con autorrevisión y merge commit hacia main. Detalle en [GIT_WORKFLOW](docs/GIT_WORKFLOW.md). El historial existente no cumple la exigencia de SPEC original en primer commit ni la convención en todos los mensajes; se conserva y se solicita al docente cómo regularizarlo. No se inventa cumplimiento retroactivo.

Ejecución futura
Todavía no hay comandos de ejecución comprobados de una aplicación. En B este apartado se reemplazará por requisitos, variables sin secretos, comandos exactos de arranque/migración/seed, URLs, buzón local y datos de demostración. No generar fuentes, manifests ni lockfiles antes de la autorización docente.

Fuentes y decisiones
La consigna y SPEC oficial son la fuente del alcance obligatorio. Las plantillas orientan secciones y profundidad. JWT y verificación de correo se mantienen por requerimiento previo de la estudiante, no porque la SPEC oficial los imponga. La rúbrica previa de 100 puntos es únicamente autoevaluación opcional; no determina la aprobación docente.