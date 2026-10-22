# Rúbrica propuesta de evaluación

Versión 1.1. Elaborada para el proyecto repodesarrolo de Desarrollo de Software. Es una propuesta de evaluación y autoevaluación; no es una rúbrica oficial de la cátedra. Fecha, integrantes, alojamiento y escala oficial de aprobación continúan pendientes.

## 1. Uso de la rúbrica
Se proponen dos instancias independientes: evaluación de la documentación inicial y evaluación de la aplicación final. Cada instancia suma 100 puntos; no se suman entre sí ni se presume una ponderación entre entregas. En este momento solo corresponde evaluar documentación. La aplicación no implementada no recibe puntos por funcionalidades que únicamente están especificadas.

Para cada criterio se asigna un nivel y se multiplica el peso por su factor. Registrar evidencia y una justificación breve. Si hay cumplimiento entre niveles, elegir el nivel inferior hasta aportar la evidencia faltante; no otorgar puntaje por una afirmación sin verificación.

| Nivel | Factor | Interpretación |
| --- | --- | --- |
| Completo | 1.00 | Evidencia suficiente de todos los elementos exigidos y sin contradicciones materiales. |
| Adecuado | 0.75 | Elementos principales correctos; omisiones menores que no impiden entender o usar la solución. |
| Parcial | 0.50 | Cumple parte del criterio, pero faltan elementos relevantes o evidencia suficiente. |
| Insuficiente | 0.00 | Ausente, incorrecto o contradice un requisito esencial del criterio. |

Puntaje de criterio = peso × factor. Total = suma de puntajes, con máximo 100. Ejemplo: un criterio de 20 puntos en nivel Adecuado recibe 15. Si se desea expresar una nota sobre 10, dividir el total por 10; esto no define por sí solo la condición oficial de aprobación.

## 2. Instancia A — Documentación inicial, 100 puntos

| Criterio | Peso | Qué se evalúa | Evidencia de cumplimiento completo |
| --- | ---: | --- | --- |
| SPEC: alcance y reglas | 20 | Objetivo, actores, permisos, requisitos funcionales/no funcionales, límites y casos difíciles. | RF identificados; CRUD propio y global diferenciados; JWT y email obligatorios; criterios medibles y reglas coherentes. |
| PRD: definición del producto | 15 | Problema, valor, usuarios, prioridades, historias y aceptación. | Historias que describen resultados observables, alcance P0 explícito y supuestos distinguidos de requisitos confirmados. |
| TRD: solución técnica | 20 | Stack exigido, arquitectura, decisiones, seguridad y operación. | React 19/Vite/pnpm, FastAPI/uv, PostgreSQL y Compose; JWT con claims, validación, almacenamiento, expiración/revocación; verificación, recuperación y rate limit definidos. |
| UX/UI | 10 | Jerarquía, Material claro, formularios, accesibilidad y estados de pantalla. | Descripción de pantallas públicas, personales, de autor y admin; mensajes claros; carga/error/vacío; foco y teclado. |
| Appflow | 10 | Rutas, navegación, permisos, retornos y alternativas. | Registro-verificación-login, CRUD propio, recuperación, roadmap y manejo de sesión vencida sin rutas sin salida. |
| Backend schema y API | 15 | Entidades, relaciones, constraints, contratos y concurrencia. | Propietario inmutable, email_verified_at, jti revocable, tokens separados, contratos de autor y protección de recursos ajenos. |
| Plan y trazabilidad | 10 | Secuencia, dependencias, esfuerzo, riesgos, pruebas y definición de terminado. | Cada requisito esencial tiene una prueba identificable; estimación revisada y condiciones de cierre verificables. |
| **Total** | **100** | | |

Errores que impiden considerar completo el criterio correspondiente: CRUD descrito como exclusivamente administrativo; JWT omitido o confundido con cifrado de contraseña; verificación tratada como opcional; backend sin validación de propietario; contradicciones entre roles, rutas y contratos. Deben corregirse antes de tomar esa parte como lista para implementar.

No se otorgan puntos extra por cantidad de páginas. Se valora precisión, coherencia, decisiones justificadas y posibilidad de comprobar el cumplimiento. No se exige código para esta instancia textual.

## 3. Instancia B — Aplicación final, 100 puntos

| Criterio | Peso | Evidencia necesaria para nivel Completo |
| --- | ---: | --- |
| Documentación actual y trazabilidad | 10 | Los archivos coinciden con la implementación, instalación y limitaciones; requisitos enlazados a pruebas o demostración. |
| CRUD de cursos y autorización | 20 | Estudiante verificado crea, consulta, edita, publica y archiva propios; segundo autor no accede a sus borradores ni los modifica; admin gestiona todos; validaciones y bajas lógicas funcionan. |
| Autenticación, verificación y seguridad | 20 | Registro, correo real de prueba, reenvío, login JWT, expiración, logout/revocación, recuperación y rate limit; tokens alterados o usados rechazados; hash seguro y CSRF con cookies. |
| Roadmaps y progreso | 15 | Orden de pasos, validación de publicación, inmutabilidad, seguimiento, abandono, curso compartido, conteo y siguiente paso correctos. |
| Modelo y persistencia | 10 | Migraciones reproducibles, relaciones y restricciones correctas, transacciones de operaciones críticas y ausencia de pérdida de integridad. |
| UX/UI y navegación | 10 | Material claro, navegación pública/personal/autor/admin, adaptación de pantallas, mensajes útiles, teclado/foco y estados de error. |
| Infraestructura y reproducibilidad | 10 | Docker Compose arranca una copia limpia; dependencias listas y migraciones aplicadas; variables documentadas; volumen persistente y restauración demostrada. |
| Pruebas y calidad técnica | 5 | Tests relevantes ejecutados, evidencias de casos críticos, tipos/lint y build correctos; código organizado y sin secretos versionados. |
| **Total** | **100** | |

El CRUD completo debe demostrarse desde la interfaz y API, con persistencia después de recargar. Manipular registros manualmente en PostgreSQL no sustituye una operación faltante. Mostrar un JWT en pantalla o generarlo sin validarlo en endpoints privados tampoco acredita autenticación.

## 4. Condiciones esenciales que se informan aparte del puntaje
Indicar explícitamente “Cumple” o “No cumple” para: stack obligatorio; CRUD de autor y administración; JWT; verificación de correo; recuperación; rate limit; roadmap; persistencia; arranque reproducible. Un promedio alto en otras categorías no debe ocultar una condición obligatoria faltante. La cátedra debe decidir si alguna condición constituye requisito excluyente; esta propuesta no inventa una regla oficial de desaprobación.

Casos críticos de seguridad a demostrar: autor B no modifica curso del autor A; JWT alterado y expirado fallan; usuario sin email verificado no recibe JWT; token de confirmación/reset no se usa dos veces; cerrar sesión o recuperar contraseña revoca acceso. Su incumplimiento impide asignar nivel Completo al criterio afectado y requiere registrar la limitación.

## 5. Planilla textual de evaluación
Para cada fila registrar: instancia; criterio; peso; nivel; factor; puntaje obtenido; archivo, prueba o recorrido observado; observación y corrección pendiente. Cerrar con total y lista de condiciones esenciales no cumplidas. Mantener separadas evaluación documental y funcional.

Para la defensa, pedir al estudiante que explique: qué diferencia autenticación de autorización; para qué sirve JWT y por qué su firma no cifra sus datos; dónde se valida la propiedad de un curso; por qué recuperación no verifica email; cómo se evita duplicar seguimientos; cómo se conserva integridad si se publica un roadmap mientras se archiva un curso. Evaluar explicaciones dentro de los criterios correspondientes, sin agregar puntos por fuera de 100.
