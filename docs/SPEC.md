# SPEC — Especificación del sistema

Versión 1.1. Estado: propuesta inicial. Producto: Cursos Abiertos. Repositorio previsto: repodesarrolo.

## 1. Objetivo y límites del sistema

Permitir que una persona encuentre cursos gratuitos, consulte su información y siga un recorrido ordenado con avance persistente. Permitir que estudiantes autores mantengan sus propios cursos y que un administrador gestione todo el catálogo y los roadmaps. Incluir registro, inicio y cierre de sesión, recuperación de contraseña y límites de solicitudes en operaciones sensibles.

El sistema administra recursos educativos y progreso declarado por el usuario; no verifica la aprobación real en la plataforma externa. No es un LMS completo. La gratuidad se refiere al acceso al contenido principal del curso; un certificado externo opcional puede tener costo y debe aclararse en la ficha. No se admitirán recursos cuyo contenido principal requiera pago, tarjeta o una prueba temporal de pago.

## 2. Glosario

| Término | Definición |
| --- | --- |
| Curso | Recurso externo gratuito con título, descripción, proveedor, categoría, nivel, idioma, duración estimada y URL. |
| Roadmap | Secuencia lineal de uno o más cursos obligatorios para una meta de aprendizaje. |
| Paso | Asociación de un curso a una posición dentro de un roadmap. |
| Seguimiento | Asociación entre estudiante y roadmap para consultarlo en su panel. No inscribe en el proveedor externo. |
| Progreso | Estado manual de un estudiante para un curso, compartido entre todos sus roadmaps. |
| Publicación | Acción que vuelve visible un recurso validado. |
| Archivado | Baja lógica: deja de ofrecerse a nuevos usuarios y conserva relaciones históricas. |
| Sesión | Credencial temporal revocable de un usuario autenticado. |

## 3. Actores y permisos

Visitante: consulta cursos y roadmaps publicados, busca, filtra, se registra, inicia sesión y solicita recuperación.

Estudiante: conserva los permisos públicos y, después de verificar su email e iniciar sesión con JWT, puede consultar su perfil, seguir o abandonar roadmaps, modificar su propio progreso y crear, consultar, editar, publicar y archivar cursos propios. Actúa como autor sin un rol adicional. No modifica cursos ajenos, categorías ni roadmaps.

Administrador: conserva los permisos de estudiante y gestiona cursos, categorías y roadmaps. No puede leer contraseñas, tokens ni progreso privado ajeno a través de la API. La primera cuenta administrativa se aprovisiona mediante una tarea controlada de operación; no hay formulario público para asignar roles.

Servicio de correo: entrega mensajes de recuperación. Su indisponibilidad no debe revelar si una cuenta existe.

| Operación | Visitante | Estudiante | Administrador |
| --- | --- | --- | --- |
| Consultar catálogo publicado | Sí | Sí | Sí |
| Ver borradores | No | Solo propios | Sí |
| CRUD de cursos | No | Solo propios y email verificado | Todos |
| Gestionar categorías y roadmaps | No | No | Sí |
| Seguir roadmap | No | Propio | Propio |
| Cambiar progreso | No | Propio | Propio |
| Recuperar contraseña | Sí | Sí | Sí |
| Asignar roles por API | No | No | No |

## 4. Alcance de la primera entrega

Incluye autenticación JWT, verificación obligatoria de correo, recuperación por correo, rate limit, catálogo con búsqueda y filtros, detalle de cursos, CRUD de autor y administrativo, roadmaps lineales, seguimiento personal, progreso manual, diseño adaptable y entorno reproducible con Docker Compose.

Quedan fuera: pagos, videos propios, evaluaciones, certificados, comentarios, puntuaciones, recomendaciones por IA, login social, MFA, carga de archivos, edición del perfil, cambio de email, administración pública de usuarios y aplicación móvil nativa. La verificación de email es obligatoria antes de emitir un JWT de acceso o habilitar funciones privadas. El roadmap no bloquea el acceso a pasos posteriores; su orden es una recomendación.

## 5. Requisitos funcionales

### Autenticación

- RF-01 Registro. Aceptar nombre visible, email, contraseña y confirmación en la interfaz. Validar en servidor; crear estudiante activo con email sin verificar y encolar un enlace de verificación; responder de manera genérica tanto si el email ya existía como si se crea. No iniciar sesión automáticamente.
- RF-02 Login. Validar email y contraseña; exigir email verificado y emitir JWT firmado de acceso en cookie protegida. Credenciales inválidas, usuario inexistente o inactivo producen el mismo mensaje. Solo tras validar correctamente la contraseña se puede devolver EMAIL_NOT_VERIFIED para una cuenta pendiente.
- RF-03 Sesión. Mantener identidad durante la navegación y recarga; consultar la sesión actual y revocarla al cerrar sesión. JWT con expiración absoluta de 15 minutos, sin refresh token en esta entrega. Al vencer requiere nuevo login. La sesión asociada al jti permite revocación inmediata.
- RF-04 Recuperación. Solicitar email, responder mensaje uniforme y enviar un enlace solamente a cuentas activas existentes. El enlace vence a los 30 minutos y sirve una sola vez.
- RF-05 Restablecimiento. Validar token, nueva contraseña y política vigente; cambiar el hash, consumir todos los tokens pendientes de la cuenta y revocar todas sus sesiones de forma atómica. No iniciar sesión automáticamente.
- RF-06 Rate limit. Aplicar límites compartidos entre procesos; devolver 429 y Retry-After cuando corresponde. No establecer bloqueos permanentes por fallos de autenticación.

### Cursos y categorías

- RF-07 Listar cursos publicados, con paginación y orden determinista.
- RF-08 Buscar por título o proveedor y combinar filtros de categoría, nivel e idioma. Conservar consulta y filtros en la URL.
- RF-09 Consultar ficha con descripción completa, requisitos previos, duración estimada, gratuidad, proveedor y enlace externo.
- RF-10 Crear curso en borrador, modificarlo, publicarlo y archivarlo mediante permisos de propietario verificado o de administrador.
- RF-11 Impedir la publicación de cursos incompletos y el archivado de cursos presentes en cualquier roadmap que haya sido publicado.
- RF-12 Crear, listar y renombrar categorías; eliminar únicamente categorías sin cursos asociados. Una categoría por curso; máximo 100 categorías en esta versión.

### Roadmaps

- RF-13 Listar y consultar roadmaps publicados, mostrando objetivo, nivel y cursos ordenados.
- RF-14 Crear y editar roadmaps en borrador, agregando, quitando y ordenando pasos.
- RF-15 Publicar únicamente roadmaps con al menos un curso, sin cursos repetidos y con todos sus cursos publicados.
- RF-16 Mantener inmutables el contenido y los pasos después de publicar. El administrador puede archivarlos. Para otra edición se deberá crear un roadmap nuevo; no se requiere duplicación automática.
- RF-17 Seguir un roadmap publicado de forma idempotente y mostrarlo en “Mi aprendizaje”.
- RF-18 Abandonar el seguimiento con confirmación; conservar el progreso individual de cursos.
- RF-19 Marcar un curso publicado como no iniciado, en curso o completado. La operación es propia e idempotente; puede realizarse desde su ficha aunque no se siga un roadmap.
- RF-20 Calcular el avance de un roadmap: cantidad de cursos completados dividida por total de pasos, multiplicada por 100. Mostrar entero redondeado y fracción exacta; la finalización se decide por el conteo, nunca por el porcentaje redondeado.
- RF-21 Recomendar el primer paso no completado en orden. Si todos están completos, mostrar “Roadmap completado”.
- RF-22 Conservar el acceso al detalle de un roadmap archivado para quien ya lo seguía; impedir nuevos seguimientos. Un visitante obtiene 404.

## 6. Reglas de negocio

- RN-01 Todo curso publicado ofrece acceso gratuito al contenido principal. La comprobación es editorial y manual; no se consulta automáticamente la URL externa desde el backend.
- RN-02 Un email normalizado identifica una única cuenta. En este producto se recortan espacios y se compara toda la dirección sin distinción entre mayúsculas y minúsculas. No se eliminan puntos ni sufijos de proveedor.
- RN-03 El rol, estado de verificación y propietario se obtienen de la base de datos; nunca se aceptan como permisos desde el cliente. JWT identifica al usuario; cada escritura de curso exige created_by igual al usuario actual o rol admin.
- RN-04 Curso: borrador pasa a publicado o archivado; publicado admite edición o archivado sujeto a RN-08; archivado es terminal. No hay recuperación desde la interfaz en el MVP.
- RN-05 Roadmap: borrador pasa a publicado o archivado; publicado solo pasa a archivado. Sus pasos quedan congelados desde la primera publicación.
- RN-06 Dentro de cada roadmap las posiciones son consecutivas desde 1 y los cursos no se repiten. Un curso sí puede aparecer en diferentes roadmaps.
- RN-07 El progreso es por pareja usuario-curso. Completar un curso actualiza el porcentaje de todos los roadmaps propios que lo contienen. Si luego vuelve a “en curso”, esos porcentajes también disminuyen.
- RN-08 Un curso referenciado por un roadmap publicado o archivado que fue publicado no puede archivarse. Un borrador que referencia un curso posteriormente archivado debe corregirse antes de publicarse.
- RN-09 Seguir un roadmap no reinicia cursos completados. Abandonarlo no borra progreso; volver a seguirlo recupera el avance actual si continúa publicado.
- RN-10 Los cursos no tienen precio editable. La condición de gratuito y la nota sobre certificados son campos de validación editorial.
- RN-11 Un registro duplicado no cambia nombre, contraseña ni estado de la cuenta existente.
- RN-12 Desactivar una cuenta mediante operación interna revoca sus sesiones. La API valida el estado actual en cada solicitud autenticada.
- RN-13 Enlaces externos se abren por acción del usuario; no se ejecuta HTML proporcionado por administradores. Las descripciones son texto plano.

## 7. Validación y límites
Nombre visible: 2–80 caracteres después de recortar espacios. Email: formato válido, máximo 254 caracteres. Contraseña: 15–128 caracteres, sin recortar, sin reglas arbitrarias de símbolos; permitir pegar y usar gestores. Confirmación solo en frontend; no persistirla. Rechazar contraseñas muy comunes usando una lista local mantenida como dependencia/dato de seguridad; no enviar contraseñas a servicios externos.

Curso: título 3–150, resumen 20–300, descripción 50–10000, proveedor 2–100, requisitos previos hasta 2000 caracteres; URL HTTPS de hasta 2048; duración entre 1 y 100000 minutos, estimada; nivel entre inicial, intermedio y avanzado; idioma mediante código permitido por la aplicación, inicialmente es, en y pt. Categoría obligatoria al publicar.

Roadmap: título 3–150, resumen 20–300, objetivo 20–3000; máximo 50 pasos. Borradores pueden omitir los datos editoriales exigidos para publicar, pero cualquier campo presente debe respetar tipo y longitud. Todo borrador requiere título; título y slug se generan sin colisión. Los contratos distinguen campos nulos de cadenas vacías.

Páginas de resultados: 20 elementos por defecto, mínimo 1 y máximo 100; página desde 1; búsqueda hasta 100 caracteres. Payload JSON máximo 256 KiB; excederlo produce 413.

## 8. Requisitos no funcionales
| ID | Requisito y criterio verificable |
| --- | --- |
| RNF-01 Seguridad | JWT firmado y validado, email verificado, autorización por propietario en backend, hashing Argon2id, cookies HttpOnly, CSRF, consultas parametrizadas y secretos fuera de Git. |
| RNF-02 Accesibilidad | Objetivo WCAG 2.2 AA en pantallas del alcance: teclado, foco, etiquetas, contraste y mensajes asociados. No afirmar certificación sin auditoría. |
| RNF-03 Adaptabilidad | Utilizable a 360, 768 y 1440 px sin desbordes horizontales del contenido principal. |
| RNF-04 Rendimiento | Objetivo p95 de API menor a 500 ms para catálogo con 10000 cursos y 20 clientes concurrentes en entorno de referencia documentado. Excluye SMTP y hashing; login p95 menor a 1500 ms. Medir, no presumir cumplimiento. |
| RNF-05 Integridad | Restricciones y transacciones impiden duplicados, pasos inválidos y uso doble de tokens bajo concurrencia. |
| RNF-06 Reproducibilidad | Clon limpio y variables documentadas permiten levantar frontend, backend, migraciones y PostgreSQL con Docker Compose. |
| RNF-07 Mantenibilidad | Separación por responsabilidades, tipos, migraciones versionadas y validaciones compartidas por caso de uso. |
| RNF-08 Observabilidad | Logs estructurados con request_id, estado y duración; sin credenciales, cookies ni token de recuperación. |
| RNF-09 Recuperabilidad | Backup y restauración probados antes de la entrega. Objetivos académicos: RPO 24 h y RTO 4 h; requieren procedimiento y medición. |

## 9. Casos límite obligatorios

Email duplicado concurrente; token vencido, usado o inválido; doble clic en publicar; dos administradores editando; curso archivado durante edición de roadmap; dos resets simultáneos; pérdida de conexión tras guardar; cuenta sin permisos; intento de modificar progreso ajeno; limitación por IP compartida; correo retrasado; roadmap sin pasos; porcentaje redondeado que parece completo aunque falten cursos; enlace externo roto.

Las respuestas y la recuperación de cada caso se especifican en BACKEND_SCHEMA, APPFLOW y el plan de pruebas. La ausencia de conectividad no debe confirmar un guardado que no se conoce.

## 10. Condición de aceptación global

La entrega se considera completa cuando los RF del alcance cuentan con evidencia de aceptación, los casos de seguridad críticos pasan, la navegación no contiene acciones sin salida, el sistema se inicia desde cero con migraciones y datos de demostración, y la documentación coincide con la aplicación. Esta documentación define esa meta; no certifica que ya esté implementada.

## 11. Requisitos confirmados en la revisión 1.1

- RF-23 Verificar correo. Al registrarse, crear email_verified_at nulo y enviar un enlace de verificación de un solo uso, válido por 24 horas. Confirmar desde la interfaz mediante POST protegido con CSRF; una lectura GET del enlace nunca activa la cuenta por sí sola. Consumir token y establecer email_verified_at en la misma transacción, sin emitir JWT automáticamente.
- RF-24 Reenviar verificación. Solicitar email y responder 202 genérico para cuentas nuevas, existentes, verificadas o inexistentes. Para una cuenta pendiente, emitir un token nuevo e invalidar los previos. Límites: 10 solicitudes por IP/hora y 3 por email/hora; límite de email suprime envío conservando 202.
- RF-25 CRUD propio. Todo estudiante con correo verificado puede crear y publicar cursos propios con las mismas validaciones editoriales que administración. created_by se fija desde JWT validado y es inmutable. El listado privado “Mis cursos creados” incluye todos sus estados. Leer un borrador ajeno o intentar modificar un curso ajeno devuelve 404. El administrador conserva gestión global.
- RN-14 Recuperar contraseña no verifica el email. Una cuenta pendiente puede recuperar su contraseña, pero sigue sin poder ingresar hasta completar la verificación.
- RN-15 Los tokens de verificación, recuperación y JWT tienen propósitos separados y no son intercambiables. JWT no transporta contraseñas ni secretos y su firma no cifra el contenido.
- RN-16 Tanto autores como administradores respetan bloqueos de archivado por roadmaps y control de versión; ser propietario no permite romper integridad.

La rúbrica propuesta y su relación con evidencias están en docs/RUBRICA.md. Estos tres requisitos confirmados sustituyen los supuestos anteriores de CRUD exclusivamente administrativo, sesión opaca y verificación de email diferida.
