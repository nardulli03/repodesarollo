# Plan de implementación y verificación

Versión 1.1. Este archivo es el roadmap de construcción del software; los roadmaps de aprendizaje son una función del producto descrita en SPEC.md.

## 1. Estrategia y estimación

Construir incrementos verticales que funcionen de extremo a extremo. Primero entorno y datos; luego identidad; después catálogo, administración, roadmaps y seguimiento. No empezar extras antes de terminar el alcance P0. La fase actual es documental y no incluye ejecutar este plan.

Estimación orientativa para una persona con conocimientos iniciales/intermedios del stack: 108–164 horas netas de trabajo. Agregar reserva del 20% para aprendizaje, fallos de integración y revisión docente: aproximadamente 130–197 horas. No es una fecha comprometida; calibrar después de la primera fase. La infraestructura de correo, seguridad y concurrencia explica parte del esfuerzo.

| Fase | Horas estimadas | Depende de | Entregable revisable |
| --- | --- | --- | --- |
| 0. Revisión documental | 4–6 | Consigna | Alcance y decisiones aprobadas para trabajo. |
| 1. Entorno reproducible | 6–8 | Fase 0 | Frontend, API y PostgreSQL arrancan con Compose. |
| 2. Modelo y migraciones | 8–12 | Fase 1 | Esquema inicial y datos de demostración. |
| 3. Identidad JWT y límites | 18–28 | Fase 2 | Registro, login, CSRF, sesiones y cuotas. |
| 4. Verificación, recuperación y correo | 18–26 | Fase 3 | Outbox, worker y restablecimiento probado. |
| 5. Catálogo, CRUD propio y administrativo | 16–24 | Fases 2 y 3 | Consulta pública y administración real. |
| 6. Roadmaps y progreso | 12–18 | Fase 5 | Publicación estable y seguimiento personal. |
| 7. Integración UX y accesibilidad | 8–14 | Fases 4 a 6 | Recorridos y estados completos. |
| 8. Verificación y entrega | 18–28 | Fase 7 | Evidencia, restauración y demo final. |

Las horas incluyen pruebas de cada fase. La fase 8 integra y verifica el sistema completo; no posterga todos los tests hasta el final. Los responsables se asignan cuando se conozca el equipo. No se presupone trabajo de agentes ni incorporación de integrantes.

## 2. Fase 0 — Base documental

Revisar supuestos del README y coherencia de SPEC, PRD, TRD, UX_UI, APPFLOW y BACKEND_SCHEMA. Revisar catálogo externo e inmutabilidad de roadmaps contra la rúbrica propuesta. CRUD de estudiantes autores, JWT y verificación de correo ya están confirmados por el usuario; no volver a tratarlos como pendientes. Registrar cambios mediante decisiones breves: contexto, alternativas, decisión y consecuencias.

Crear issues por historias HU-01 a HU-10 y tareas técnicas asociadas. Cada issue referencia RF/RN/RNF, aceptación y evidencia esperada. Configurar tablero simple con Pendiente, En curso, En revisión y Terminado; limitar a una funcionalidad principal en curso por persona.

Cierre: las decisiones pendientes no impiden empezar; cualquier requisito docente que cambie el diseño queda identificado antes de construir su parte.

## 3. Fase 1 — Repositorio y entorno

Preparar estructura de frontend/backend/infra/docs. Crear Vite con React 19 y TypeScript usando pnpm; proyecto FastAPI gestionado con uv. Fijar runtimes y generar lockfiles. Configurar lint, verificación de tipos, pruebas básicas y build en integración continua.

Definir Dockerfiles, redes, volumen PostgreSQL y servicio de migraciones. Configurar proxy de mismo origen. Documentar variables en .env.example, excluyendo valores reales. Incorporar healthchecks y endpoints live/ready. Verificar que ninguna variable VITE contenga secretos.

Cierre: una copia limpia se inicia siguiendo instrucciones y la API consulta PostgreSQL. Los procesos esperan migración exitosa. No basta con que el contenedor aparezca como iniciado.

## 4. Fase 2 — Persistencia y restricciones

Implementar modelos y schemas. Primera migración con PK, FK, CHECK y UNIQUE. Separar datos demo de migraciones y tarea de aprovisionamiento admin de registro público. Incorporar factories para pruebas con PostgreSQL real.

Probar email normalizado único, progreso único, seguimiento único, pasos no repetidos, categorías restringidas y coherencia de fechas. Crear datos demo con curso compartido entre dos roadmaps para validar el cálculo posteriormente.

Cierre: migrar una base vacía funciona; reejecutar carga demo no duplica registros; restaurar una base de pruebas preserva relaciones. Credenciales administrativas no quedan versionadas.

## 5. Fase 3 — Autenticación, autorización y rate limit

Construir CSRF y verificación de Origin; registro con respuesta genérica; hashing de contraseñas; login sin enumeración obvia; JWT firmado en cookie HttpOnly de 15 minutos, claims, registro revocable de jti, me y logout. Implementar dependencias de permisos y estado activo. Proteger rutas y limpiar caché privada al cambiar sesión.

Implementar contadores PostgreSQL en transacciones independientes y claves HMAC. Usar reloj de base para ventanas y pruebas con tiempo controlado. Diferenciar cuota pública por IP de supresión interna por email en registro/recuperación. Documentar comportamiento de ventanas y redes compartidas.

Cierre: estudiante no accede a rutas administrativas y puede gestionar cursos propios después de verificar correo; rol enviado desde cliente se rechaza; no hay tokens en web storage; logout revoca; peticiones sin CSRF u origen válido se rechazan; el límite se conserva entre dos procesos de API y tras reinicio de uno.

## 6. Fase 4 — Recuperación y envío

Implementar verificación inicial obligatoria de email, reenvío uniforme, token de 24 horas y bloqueo de login pendiente. Implementar también recuperación con solicitud uniforme, token criptográfico y hash de verificación. Outbox cifrada y worker con lease, reintento y expiración. Integrar SMTP local de prueba, configurar límites y preparar variables para proveedor real.

Construir pantalla de restablecimiento con token en fragmento y limpieza del historial. Implementar transacción de consumo, cambio de contraseña y revocación. Probar la interacción con un login concurrente para que no se cree una nueva sesión con un hash antiguo después del cambio.

Cierre: recuperar funciona de extremo a extremo; token usado y vencido fallan; un token consumido en dos peticiones simultáneas cambia contraseña como máximo una vez; sesiones anteriores fallan; correo retrasado tiene salida comprensible; no hay token legible en base, logs o almacenamiento web.

## 7. Fase 5 — Cursos y categorías

Construir listados públicos, filtros en URL y detalle. Implementar categorías y CRUD administrativo con estados, versionado y auditoría. Validar gratuidad y URLs al publicar; no hacer fetch del contenido externo desde API. Crear interfaz de borrador, edición, publicación y archivo.

Probar los cuatro componentes del CRUD: alta, lectura, modificación y baja lógica. El archivo debe retirar recurso público sin borrar historial. Probar edición concurrente y categorías en uso.

Cierre: visitante consulta sin cuenta; catálogo nunca muestra borradores; estudiante verificado completa CRUD propio y recibe 404 al intentar modificar un curso ajeno; rutas administrativas devuelven 403; administrador completa CRUD desde UI; un fallo de red no aparece como vacío; se conserva búsqueda al volver.

## 8. Fase 6 — Roadmaps y aprendizaje

Implementar editor de pasos, publicación transaccional y consulta pública. Congelar metadata y composición después de publicar. Añadir archivado con acceso histórico para seguidores. Implementar PUT/DELETE de seguimiento y GET/PUT de progreso sin user_id en entrada.

Calcular conteos y siguiente paso al consultar. Invalidar consultas de todos los roadmaps personales cuando cambia un curso. Implementar navegación desde panel al siguiente curso y finalización por conteo.

Cierre: un curso compartido se refleja en varios roadmaps; abandonar conserva avance; doble seguimiento no duplica; roadmap vacío no se publica; orden con teclado funciona; carrera entre publicar y archivar no rompe el modelo.

## 9. Fase 7 — Revisión de experiencia

Aplicar sistema visual Material claro y componentes consistentes. Revisar 360, 768 y 1440 px, zoom 200%, reflujo, formularios, mensajes y diálogos. Recorrer APPFLOW con datos reales y estados vacíos/error.

Ejecutar tareas de usabilidad con compañeros sin explicar previamente dónde hacer clic. Registrar dificultades y corregir las que impiden completar P0. Verificar contraste, teclado y foco; no confiar solo en auditoría automática.

Cierre: todos los flujos tienen éxito, alternativa y salida; ningún botón promete una función fuera del alcance; no se confunde seguir un roadmap con inscribirse en un proveedor.

## 10. Fase 8 — Integración, operación y presentación

Ejecutar matriz de requisitos. Medir rendimiento con datos y entorno registrados; si falla, observar consultas e índices antes de escalar procesos. Revisar logs por secretos y comprobar headers/cookies en configuración HTTPS. Probar instalación desde copia limpia y backup/restauración.

Completar README operativo con requisitos, variables, arranque, migraciones, seeds, pruebas y problemas frecuentes. Revisar correspondencia documental con rutas y contratos reales. Preparar guion de presentación y limitaciones conocidas. No usar cuentas personales ni correos reales en la demo.

Cierre: CI pasa, demo completa, documentación actual y copia recuperable de datos. Cualquier criterio no alcanzado se comunica expresamente, sin presentarlo como cumplido.

## 11. Matriz de verificación

| Caso | Requisitos | Nivel | Resultado esperado |
| --- | --- | --- | --- |
| T-01 Registro válido y email duplicado | RF-01, RN-02 y RN-11 | Integración y E2E | Un usuario, mismo 202 genérico, cuenta existente intacta. |
| T-02 Login correcto e incorrecto | RF-02, RNF-01 | Integración | Sesión solo con credenciales válidas; error uniforme. |
| T-03 Caducidad, logout y cookie anterior | RF-03 | Integración y E2E | Petición posterior devuelve 401; UI limpia caché. |
| T-04 Solicitud de recuperación existente/inexistente | RF-04 | Integración | Mismo contrato público; solo la existente encola correo. |
| T-05 Reset usado, alterado, vencido y concurrente | RF-05, RNF-05 | Integración concurrente | Como máximo un cambio; sesiones revocadas. |
| T-06 Límites entre procesos y borde de ventana | RF-06 | Integración | Cuota compartida, Retry-After correcto y respuesta genérica por email cuando aplica. |
| T-07 Catálogo, filtros, paginación y cero resultados | RF-07 a RF-09 | Integración y E2E | Solo publicados; filtros combinados y URL restaurable. |
| T-08 CRUD y roles | RF-10, RF-25, RN-03 | Integración y E2E | Autor modifica propios; ajenos 404; administración 403 para student; admin gestiona todos. |
| T-09 Categoría en uso y nombre duplicado | RF-12 | Integración | 409 traducido; ninguna referencia rota. |
| T-10 Versiones administrativas concurrentes | RNF-05 | Integración | Segunda escritura vieja recibe 409. |
| T-11 Roadmap vacío, cursos duplicados/no publicados | RF-14 y RF-15 | Unitario e integración | Publicación rechazada; estado original intacto. |
| T-12 Archivo de curso frente a publicación | RF-11, RN-08 | Integración concurrente | Una operación falla; ningún roadmap publicado queda con curso archivado. |
| T-13 Inmutabilidad después de publicación | RF-16 | Integración | PATCH/PUT pasos rechaza cambio. |
| T-14 Seguir, repetir y abandonar | RF-17 y RF-18 | Integración y E2E | Sin duplicados; conserva progreso. |
| T-15 Compartir curso entre recorridos y reabrirlo | RF-19 a RF-21 | Unitario, integración y E2E | Conteos suben y bajan; siguiente paso correcto. |
| T-16 Archivado con seguidor y visitante | RF-22 | Integración | Seguidor consulta; visitante 404; nuevas altas no admitidas. |
| T-17 Alterar propietario o ID | RN-03, RNF-01 | Integración | user_id extra 422; no hay acceso ajeno. |
| T-18 CSRF, Origin, next y URLs peligrosas | RNF-01, RN-13 | Integración y E2E | Rechazo de mutaciones y redirecciones no permitidas. |
| T-19 Teclado, foco, contraste y reflujo | RNF-02 y RNF-03 | UI y manual | Flujos principales utilizables y mensajes perceptibles. |
| T-20 Caída SMTP, lease y expiración | RF-04, RNF-08 | Integración | Reintenta sin token legible ni correos vencidos deliberados. |
| T-21 Carga de catálogo y login | RNF-04 | Rendimiento | Reportar p95 contra metas y entorno reproducible. |
| T-22 Instalación limpia y restauración | RNF-06 y RNF-09 | Operación | Arranque y recuperación con evidencia y tiempos. |
| T-23 Revisar logs y payloads | RNF-08 | Integración y revisión | Sin contraseñas, tokens, cookies ni datos de más. |

No fijar cobertura porcentual como sustituto de casos críticos. Las pruebas concurrentes deben coordinar transacciones para provocar la carrera de forma repetible; repetir una petición rápidamente sin sincronización no demuestra ausencia de carrera.

## 12. Definición de listo y terminado

Una tarea está lista para iniciar cuando tiene objetivo, referencias documentales, dependencias conocidas y aceptación comprobable. Está terminada cuando código y documentación coinciden, se revisan permisos/validación, pasan pruebas relevantes, la UI cubre carga/error/vacío cuando aplica y el resultado puede demostrarse.

Para PRs, incluir problema concreto, comportamiento resultante, validación ejecutada y migraciones si las hay. Mantener cambios acotados por caso de uso. No mezclar secretos ni datos personales en fixtures o ejemplos. No marcar una tarea terminada por compilar si todavía falla el recorrido del usuario.

## 13. Riesgos y medidas

| Riesgo | Probabilidad/impacto estimados | Medida y respuesta |
| --- | --- | --- |
| Falta de familiaridad con uv, sesiones o migraciones | Media/alto | Incremento mínimo temprano y tiempo de aprendizaje en reserva. |
| SMTP no disponible | Media/alto para recuperación | Capturador local para pruebas y proveedor preparado antes de demo pública. |
| Stack crece por extras | Alta/alto | Congelar P0; cada extra exige impacto y nueva estimación. |
| Seguridad agregada al final | Media/alto | Construir CSRF, sesiones, permisos y cuotas antes del CRUD. |
| Inconsistencia entre documentos | Media/medio | Revisar trazabilidad en cada cambio de contrato. |
| Enlaces externos dejan de ser gratuitos | Media/medio | Revisión editorial y reconocer limitación de sustitución en roadmaps publicados. |
| Locks y límites degradan rendimiento | Media/medio | Medir pool, transacciones e índices; no esconder fallos con reintentos infinitos. |
| Base se pierde al recrear contenedores | Media/alto | Volumen persistente y restauración probada; documentar comandos destructivos por separado. |

## 14. Guion de demostración

1. Buscar un curso público y abrir su detalle.
2. Crear estudiante, verificar correo desde SMTP de pruebas, iniciar sesión con JWT y consultar perfil.
3. Seguir un roadmap y completar un curso que aparezca en otro recorrido.
4. Ver cambios de avance y siguiente paso; abandonar un seguimiento sin perder progreso.
5. Recuperar contraseña por SMTP de pruebas y demostrar revocación de una sesión previa.
6. Ingresar como administrador, crear curso, guardar borrador, publicar, editar y archivar un curso sin dependencias.
7. Crear y publicar un roadmap; mostrar rechazo a editar sus pasos y a archivar un curso que usa.
8. Demostrar CRUD propio de estudiante, 404 al intentar editar un curso ajeno, 403 en administración y 429 controlado.
9. Presentar arranque limpio, matriz de pruebas y limitaciones conocidas.

## 15. Mejoras posteriores

MFA administrativo; nuevas versiones de roadmaps; sustitución de cursos discontinuados; exportación de progreso; etiquetas múltiples; favoritos; búsqueda con ranking; limitador especializado si crece la escala. Cada mejora necesita requisitos propios, actualización del modelo y pruebas; no se considera incluida implícitamente en el MVP.

## 16. Pruebas y evaluación incorporadas en revisión 1.1

Agregar T-24 (RF-23 y RF-24): registro encola verificación, confirmación única, reenvío invalida anterior, expiración de 24 horas y GET sin efecto. T-25: contraseña correcta con email pendiente no emite JWT; reset no omite esta condición. T-26: JWT alterado, sin firma, algoritmo no permitido, issuer/audience incorrectos, expirado y jti revocado se rechazan. T-27 (RF-25): dos autores con cursos propios no pueden leer borradores ni escribir recursos del otro por ID, payload o cambios de URL; admin conserva alcance global.

Actualizar datos demo y CI para verificar autenticación, titularidad y correo. La revisión de entrega usa docs/RUBRICA.md, que suma 100 puntos y distingue evidencia documental de funciones implementadas. La estimación se incrementó por estos requisitos confirmados; no se fija fecha de entrega sin información del usuario.
