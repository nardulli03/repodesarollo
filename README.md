# repodesarrolo — Documentación inicial

Versión documental: 1.1. Actualización: 21 de octubre de 2026. Estado: propuesta de diseño para revisión académica; aplicación todavía no implementada.

## Propósito

Diseñar una plataforma web de cursos gratuitos que permita descubrir recursos educativos, autenticarse, recuperar el acceso y seguir recorridos de aprendizaje. El trabajo se plantea desde la perspectiva de un estudiante de Ingeniería en Sistemas de Información en la materia Desarrollo de Software: requisitos verificables, alcance realizable y decisiones técnicas justificadas.

El nombre del repositorio se conserva exactamente como fue indicado: `repodesarrolo`. Nombre provisional del producto: **Cursos Abiertos**. No se presupone acceso al repositorio remoto ni se afirma haber leído su contenido; estos archivos están preparados para incorporarse a su raíz. No se ha identificado propietario ni URL del repositorio.

## Organización y orden de lectura

| Archivo | Responsabilidad |
| --- | --- |
| [SPEC.md](SPEC.md) | Especificación integral: alcance, actores, requisitos y reglas de negocio. |
| [PRD.md](PRD.md) | Problema, valor del producto, funcionalidades, historias y aceptación. |
| [TRD.md](TRD.md) | Arquitectura, stack, seguridad, operación y decisiones técnicas. |
| [docs/UX_UI.md](docs/UX_UI.md) | Experiencia, sistema visual textual y comportamiento por pantalla. |
| [docs/APPFLOW.md](docs/APPFLOW.md) | Mapa textual de navegación, permisos y recorridos alternativos. |
| [docs/BACKEND_SCHEMA.md](docs/BACKEND_SCHEMA.md) | Modelo relacional, contratos de API, validación y transacciones. |
| [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | Fases, dependencias, pruebas, riesgos y condiciones de entrega. |
| [docs/RUBRICA.md](docs/RUBRICA.md) | Rúbrica propuesta de evaluación, ponderaciones y evidencia. |

Todos los entregables son texto Markdown. Las tablas representan contratos y relaciones; no se incluyen imágenes, prototipos ejecutables, SQL, código de aplicación ni configuración de infraestructura.

## Cómo mantener coherencia

SPEC define el comportamiento obligatorio. PRD explica su valor y aceptación. TRD define la solución y BACKEND_SCHEMA concreta sus contratos. UX_UI y APPFLOW describen cómo se presenta. IMPLEMENTATION_PLAN ordena su construcción. Si una revisión cambia una regla, deben actualizarse los documentos afectados en la misma revisión; una contradicción no se resuelve eligiendo silenciosamente un archivo.

Los identificadores RF, RN y RNF permiten relacionar requisitos con historias y pruebas. Las decisiones agregadas a la consigna están marcadas como propuestas o supuestos; no son confirmaciones del docente.

## Supuestos de trabajo
1. Requisito confirmado: el CRUD de cursos está habilitado a estudiantes autores sobre sus propios cursos y a administradores sobre todo el catálogo. El registro público crea estudiantes; el permiso de autoría se habilita al verificar su email, sin asignar un rol administrativo.
2. Los cursos se realizan en plataformas externas; aquí se almacena metadata y seguimiento manual.
3. Roadmap significa recorrido pedagógico ordenado de cursos, además del plan de implementación del proyecto, que se documenta por separado.
4. La plataforma no cobra. No se integran pagos, certificados propios ni reproducción de video.
5. La demostración es de baja escala, con un único despliegue Docker Compose y PostgreSQL compartido por los procesos de backend.
6. Requisitos confirmados: JWT obligatorio para autenticación y verificación obligatoria del correo. Se propone TypeScript para React y Material UI para la interfaz; TypeScript continúa pendiente de validación.
7. El correo se prueba con un capturador SMTP local; un entorno accesible por Internet necesita un proveedor SMTP configurado y HTTPS.

## Tecnologías exigidas

Frontend: React 19, Vite y pnpm. Backend: FastAPI y uv. Base de datos: PostgreSQL. Infraestructura: Docker y Docker Compose. UX/UI: estética Material clara con búsqueda protagonista, inspirada en la sencillez de google.com, sin copiar marca ni identidad.

## Fuentes técnicas de referencia

Se consultaron fuentes primarias para fundamentar el diseño. Los parámetros concretos de este proyecto —tiempos, umbrales, esquema y alcance— son decisiones propuestas, no valores impuestos por estas fuentes.

- React: https://react.dev/versions
- Vite: https://vite.dev/guide/
- pnpm: https://pnpm.io/installation
- uv: https://docs.astral.sh/uv/guides/projects/
- JWT, buenas prácticas: https://www.rfc-editor.org/rfc/rfc8725
- FastAPI, JWT, contraseñas y hashing: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- PostgreSQL, restricciones: https://www.postgresql.org/docs/current/ddl-constraints.html
- Docker Compose, disponibilidad y orden de arranque: https://docs.docker.com/compose/how-tos/startup-order/
- OWASP, recuperación: https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
- OWASP, sesiones: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- Material Design: https://m3.material.io/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/


