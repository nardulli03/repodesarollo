# UX/UI — Diseño textual de la experiencia

Versión 1.1. Referencias funcionales: SPEC.md y PRD.md. Este documento describe la interfaz, sin imágenes ni código.

## 1. Principios

Búsqueda visible, pocas decisiones simultáneas y navegación consistente. Explorar no requiere cuenta. El registro se solicita cuando una persona intenta conservar seguimiento o progreso. Cada acción indica su resultado y ofrece una salida razonable ante errores.

La inspiración en google.com se expresa con fondo claro, espacio en blanco, buscador destacado y jerarquía simple. La inspiración Material se expresa con componentes consistentes, estados visibles y controles accesibles. Usar identidad propia “Cursos Abiertos”, sin logos ni textos que sugieran afiliación a Google.

## 2. Arquitectura de información

Áreas públicas: Inicio, Cursos, Detalle de curso, Roadmaps, Detalle de roadmap, Iniciar sesión, Crear cuenta, Recuperar contraseña y Restablecer contraseña.

Área personal: Mi aprendizaje, Mis cursos creados y Mi cuenta de solo lectura. Mis cursos creados permite alta, edición, publicación y baja de cursos propios. Los detalles de cursos y roadmaps incorporan controles personales si hay sesión.

Área administrativa: listado, creación y edición de cursos; categorías; listado, creación y edición de roadmaps. La navegación administrativa tiene encabezado explícito y salida al sitio público.

El menú principal ofrece Cursos y Roadmaps. Sin sesión muestra “Iniciar sesión” y “Crear cuenta”; con sesión muestra “Mi aprendizaje” y un menú de cuenta. Administración aparece solo para ese rol. Ocultar enlaces no sustituye validación del backend.

## 3. Sistema visual propuesto

| Token | Valor inicial | Uso |
| --- | --- | --- |
| Fondo | #FFFFFF | Pantallas y superficie principal. |
| Superficie secundaria | #F8F9FA | Secciones y paneles sutiles. |
| Texto principal | #202124 | Títulos y contenido. |
| Texto secundario | #5F6368 | Ayudas y metadata; comprobar contraste en su contexto. |
| Primario | #1A73E8 | Botón principal y selección. Para texto pequeño usar #174EA6. |
| Texto sobre botón primario | #FFFFFF | Usar fondo #174EA6 si el contraste del estado original no alcanza. |
| Error | #B3261E | Mensajes y bordes de error con icono y texto. |
| Éxito | #146C2E | Confirmaciones legibles, acompañadas de texto. |
| Borde decorativo | #DADCE0 | Separadores; controles esenciales usan borde con contraste verificado. |

Los valores son un punto de partida, no evidencia de accesibilidad. Medir contraste real: 4.5:1 para texto normal, 3:1 para texto grande y componentes relevantes. El tema definitivo debe corregir cualquier combinación que falle.

Tipografía: Roboto alojada localmente, con fallback system-ui. Cuerpo 16 px, interlineado 1.5; ayudas no menores a 14 px; título de pantalla 28–36 px adaptable. Espaciado sobre escala de 4 y 8 px. Contenido general hasta 1200 px; formularios de acceso hasta 440 px; formularios editoriales hasta 900 px. Radio de tarjetas 12 px, inputs 8 px y buscador principal redondeado. Elevación moderada; evitar sombras como único límite de control.

Botones de interacción frecuente con altura de 44–48 px. Foco visible de al menos 2 px con contraste suficiente. Un solo botón primario dominante por bloque. La jerarquía distingue acción principal, secundaria y destructiva. No depender exclusivamente de color, icono ni hover.

## 4. Componentes compartidos

Header con marca textual, navegación y cuenta. Breadcrumb en detalles y administración. Buscador con etiqueta accesible y botón “Buscar”. Tarjeta de curso con título, proveedor, nivel, idioma, duración y categoría. Tarjeta de roadmap con objetivo y cantidad de cursos; si se sigue, fracción y porcentaje.

Inputs con label permanente, ayuda y error asociado. Etiquetas de estado para Borrador, Publicado y Archivado. Snackbar para avisos secundarios; los errores de formulario permanecen también junto a campos o al inicio del formulario. Diálogo de confirmación con título concreto, consecuencia y botones “Cancelar” y acción específica. Nunca usar solamente “Aceptar”.

Paginación con nombres accesibles; indicador de progreso con valor numérico y “X de Y cursos”. Controles para ordenar pasos con botones “Subir” y “Bajar”; arrastrar puede agregarse como mejora, pero no es la única interacción. Estado de carga con texto y skeleton; no anunciar cada elemento decorativo al lector de pantalla.

## 5. Especificación por pantalla

### Inicio

Encabezado, título “Encontrá tu próximo curso gratuito”, subtítulo corto y buscador central. Acciones “Buscar cursos” y “Explorar roadmaps”. Debajo, hasta seis roadmaps destacados provenientes del listado publicado, sin algoritmo de recomendación. Si no hay datos, invitar al catálogo; no simular contenido. El foco inicial no debe abrir automáticamente el teclado en móvil.

### Catálogo de cursos

Título, buscador superior con consulta actual, filtros de categoría/nivel/idioma, contador de resultados, orden y tarjetas. En escritorio, filtros en lateral o fila; en móvil, botón “Filtros” abre panel con etiquetas y acciones “Aplicar” y “Limpiar”. Al aplicar vuelve a página 1. Cambios confirmados quedan en query string; volver desde una ficha conserva los filtros.

Carga: skeleton conservando distribución. Vacío: “No encontramos cursos con estos filtros” y acción para limpiarlos. Error: “No pudimos cargar los cursos” y botón de reintento. Nunca mostrar vacío como sustituto de error.

### Detalle de curso

Breadcrumb, título, resumen, proveedor, nivel, idioma, categoría, duración estimada, descripción, requisitos y nota de certificado. Acción principal “Ir al curso”, identificada como enlace externo. Un panel secundario permite seleccionar el progreso personal; sin sesión ofrece “Iniciá sesión para guardar tu avance”. El cambio de estado muestra “Guardando…” y solo se confirma al recibir respuesta.

La duración no se presenta como fecha de finalización. La etiqueta “Gratis” no equivale a certificado gratuito. Si un enlace externo falla, la plataforma conserva la ficha; no se inventa acceso alternativo.

### Catálogo y detalle de roadmaps

Listado con título, objetivo resumido, nivel y cantidad de pasos. Detalle con descripción de la meta, progreso si hay sesión y lista numerada de cursos. Cada paso muestra título, duración, nivel, enlace interno y estado propio.

Botón principal “Seguir roadmap” para quien no lo sigue; sin sesión redirige a login con destino seguro. No ejecuta automáticamente la acción después del login: retorna al detalle y el usuario confirma. Si ya lo sigue, “Continuar aprendizaje” lleva al primer curso no completado. Si terminó, muestra “Roadmap completado” y deja consultar todos los cursos. “Dejar de seguir” es secundario y abre confirmación.

Para un roadmap archivado previamente seguido, mostrar banner: “Este roadmap fue archivado. Podés consultar tu recorrido y conservar tu avance”. El backend permite la vista a su seguidor. No mostrar botón de nuevo seguimiento. No hay bloqueo de pasos futuros: el orden es sugerido.

### Registro

Título “Crear cuenta”; campos nombre, email, contraseña y confirmación; ayuda de política; mostrar/ocultar contraseña con nombre accesible. No pedir rol ni datos no necesarios. Botón “Crear cuenta”; enlace a login. Evitar reenviar por doble clic durante la solicitud.

Después de 202, mensaje: “Revisá tu correo para completar el registro. Si ya tenías una cuenta, podés iniciar sesión o recuperar el acceso”. Agregar acceso a “Reenviar verificación”. Ofrecer ambas acciones sin afirmar que se creó una cuenta específica. Este compromiso de anti-enumeración se mantiene en UI y API.

### Login

Email, contraseña, acción “Iniciar sesión”, enlace “Olvidé mi contraseña” y acceso a registro. Error unificado: “Email o contraseña incorrectos”. Ante límite: “Se alcanzó el límite de intentos. Probá nuevamente en X segundos”. No revelar si la cuenta está desactivada. Solo con contraseña correcta y email pendiente, mostrar “Confirmá tu correo para iniciar sesión” y un enlace al reenvío de verificación.

Al autenticar se consulta el destino interno permitido; si no existe, Mi aprendizaje. Mantener email ante error; no persistir contraseñas. Un 503 indica indisponibilidad, sin transformarlo en credenciales incorrectas.

### Recuperación

Un campo email y botón “Enviar enlace”. Respuesta: “Si existe una cuenta activa con ese email, vas a recibir instrucciones para recuperar el acceso”. No mostrar token ni email de destino recuperado desde el servidor. Permitir volver a login. La espera por IP incluye Retry-After; la supresión por email conserva el mensaje genérico.

### Restablecimiento

Capturar el fragmento de URL en memoria y limpiarlo del historial. Mostrar nueva contraseña y confirmación, con la misma política. Si no hay token, mostrar enlace inválido y permitir nueva solicitud. Tras éxito: “Contraseña actualizada. Iniciá sesión con tu nueva contraseña”. Token usado, vencido o alterado: “El enlace no es válido o ya venció”. Nunca iniciar sesión automáticamente.

### Mi aprendizaje

Tarjetas de roadmaps seguidos con avance y siguiente paso. Opcionalmente ordenar por fecha de seguimiento más reciente, que será el criterio inicial. Cada tarjeta permite continuar y acceder al detalle. Sin seguimientos: explicar qué es un roadmap y ofrecer explorar. El progreso de cursos sin seguimiento permanece en sus fichas; una biblioteca independiente de cursos queda fuera de alcance.

### Mi cuenta

Nombre, email, tipo de cuenta y acción de cerrar sesión. Aclarar que no existe edición de perfil en esta versión. Mostrar “Correo verificado” cuando email_verified_at tenga valor; no inventar ese estado. No mostrar IDs internos ni información de sesiones de otros dispositivos.

### Administración de cursos y categorías

Tabla con título, proveedor, estado, actualización y acciones. En móvil, tarjetas o tabla con desplazamiento contenido y etiquetas accesibles. Filtros por estado y búsqueda. Acciones: nuevo, editar, publicar cuando corresponda y archivar. Los archivados son de consulta.

Formulario en secciones: identificación; contenido; nivel/idioma/duración; categoría y enlace; revisión de gratuidad. Guardar borrador y publicar son acciones diferentes. Mostrar campos faltantes antes de publicar. Un 409 por dependencia al archivar informa que el curso pertenece a un roadmap publicado y ofrece ir a su consulta administrativa. Un conflicto de edición conserva el texto local y ofrece recargar la versión vigente, advirtiendo que se descartará el borrador local.

Categorías: listado, nuevo nombre, renombrar y eliminar si no tiene cursos. Error de dependencia explica por qué no se puede eliminar.

### Administración de roadmaps

Formulario con título, resumen, objetivo y nivel. Editor de pasos con selector de cursos publicados, numeración y botones para mover o quitar. “Guardar borrador” no publica. “Publicar” muestra confirmación: “Después de publicar no vas a poder modificar el contenido ni el orden”. Un roadmap publicado muestra solo lectura y opción archivar. No insinuar que archivarlo habilita edición.

## 6. Estados y recuperación

401: sesión vencida, limpiar datos privados y llevar a login con retorno seguro. 403: pantalla de permisos sin cerrar sesión válida. 404: recurso no disponible y enlaces a catálogo. 409: explicar conflicto y ofrecer revisión. 422: errores junto a campos y resumen enfocable. 429: espera y reintento explícito. 503 o desconexión: conservar formulario no secreto en memoria y permitir reintentar.

Si la respuesta de una escritura se pierde, indicar “No pudimos confirmar el resultado”. Reconsultar antes de repetir altas; los reintentos de progreso y seguimiento son idempotentes. Advertir al salir de formularios editoriales con cambios; no depender de persistirlos en almacenamiento local. Para publicaciones y archivados se deshabilita temporalmente el botón mientras hay una solicitud, manteniendo protección de servidor.

## 7. Accesibilidad y adaptación

Un h1 por pantalla; estructura semántica con header, nav, main y footer. Enlace para saltar al contenido. Formularios con label y autocomplete correctos: email, current-password y new-password. No deshabilitar pegado. Al navegar, actualizar título y mover foco al encabezado principal cuando corresponda; al cerrar un diálogo, devolverlo al control que lo abrió.

Diálogos con foco contenido y cierre por Escape salvo operación ya enviada. Errores anunciados con región apropiada; estados de guardado con aria-live moderado. Respetar prefers-reduced-motion. Verificar zoom de 200% y reflujo a 320 px además de los tamaños de entrega. Gráficos de progreso siempre tienen equivalencia textual.

## 8. Validación propuesta

Prueba con cinco personas: encontrar un curso inicial en español; registrarse y verificar correo; recuperar contraseña; seguir un roadmap; completar un curso; retomar; abandonar un seguimiento. Prueba administrativa separada: crear borrador, publicar, editar y provocar un archivado bloqueado. Registrar tarea, éxito, tiempo y dificultad sin recolectar contraseñas reales.

La revisión automática de accesibilidad complementa teclado, lector de pantalla y contraste manual; no reemplaza estas verificaciones. La identidad visual se considera provisional hasta validar legibilidad y navegación.

## 9. Pantallas añadidas en revisión 1.1

**Verificar correo:** al abrir /verificar-correo#token=valor, capturar token en memoria y limpiar fragmento. Mostrar botón “Confirmar correo”; no enviar la confirmación automáticamente al cargar. Éxito: “Correo confirmado. Ya podés iniciar sesión”. Enlace inválido, usado o vencido: mensaje uniforme y acceso a “Reenviar verificación”. No mostrar JWT al usuario.

**Reenviar verificación:** campo email, botón “Enviar enlace” y respuesta genérica: “Si tu cuenta necesita verificación, vas a recibir un nuevo enlace”. Mostrar espera solo para cuota pública de IP. Explicar que un nuevo enlace reemplaza al anterior.

**Mis cursos creados:** disponible para estudiantes verificados y administradores sobre sus propios recursos. Listado con estados, búsqueda y acción “Crear curso”. Formulario y validación iguales a los de administración de cursos; propietario asignado automáticamente, sin selector editable. Editar, publicar y archivar solo propios; categoría se elige del listado existente, sin permitir crear categorías. Vacío: “Todavía no creaste cursos” y acción de alta. No mezclar esta pantalla con Mi aprendizaje, que representa cursos estudiados.

Las operaciones bloqueadas por dependencia de roadmap muestran la misma explicación para autor y admin. Una respuesta 404 por ID ajeno informa “Curso no disponible” sin exponer el título o autor privado. El header autenticado agrega “Mis cursos creados”. La caducidad de JWT a los 15 minutos solicita login de nuevo y conserva solo destino interno y texto no secreto en memoria si la pantalla aún está montada; no promete guardado automático.
