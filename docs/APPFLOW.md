# APPFLOW — Mapa de navegación textual

Versión 1.1. Las rutas siguientes pertenecen al frontend. Los endpoints HTTP se detallan en BACKEND_SCHEMA.md. No se incluyen diagramas gráficos.

## 1. Inventario de rutas

| Ruta | Pantalla | Acceso | Salidas principales |
| --- | --- | --- | --- |
| / | Inicio | Público | Cursos, roadmaps, login y registro. |
| /cursos | Catálogo | Público | Ficha de curso, filtros, paginación. |
| /cursos/:slug | Detalle de curso | Público si publicado | Proveedor externo, login y cambio de progreso. |
| /roadmaps | Catálogo de roadmaps | Público | Detalle. |
| /roadmaps/:slug | Detalle de roadmap | Público si publicado; propio si archivado y seguido | Curso, seguir, continuar, abandonar. |
| /iniciar-sesion | Login | Público | Destino seguro, recuperación, registro. |
| /registro | Crear cuenta | Público | Confirmación genérica, verificar correo, login y recuperación. |
| /verificar-correo | Confirmación explícita; token por fragmento | Público | Login o reenvío. |
| /reenviar-verificacion | Solicitar otro enlace | Público | Confirmación genérica y login. |
| /mis-cursos | Cursos creados propios | JWT y correo verificado | Nuevo, editar, publicar, archivar. |
| /mis-cursos/nuevo | Crear curso propio | JWT y correo verificado | Guardar borrador. |
| /mis-cursos/:id/editar | Editar o consultar curso propio | JWT y propietario | Guardar, publicar o archivar según estado. |
| /recuperar-contrasena | Solicitud de recuperación | Público | Confirmación y login. |
| /restablecer-contrasena | Nueva contraseña; token recibido por fragmento | Público con token válido para confirmar | Login o nueva solicitud. |
| /mi-aprendizaje | Seguimientos propios | Sesión | Detalle y siguiente curso. |
| /mi-cuenta | Perfil de consulta | Sesión | Cerrar sesión y Mi aprendizaje. |
| /admin | Entrada de administración | Administrador | Redirige a /admin/cursos. |
| /admin/cursos | Gestión de cursos | Administrador | Nuevo, editar y consultar archivado. |
| /admin/cursos/nuevo | Alta | Administrador | Guardar borrador y volver al listado. |
| /admin/cursos/:id/editar | Edición o consulta según estado | Administrador | Guardar, publicar, archivar, volver. |
| /admin/categorias | Gestión de categorías | Administrador | Crear, renombrar y eliminar. |
| /admin/roadmaps | Gestión de roadmaps | Administrador | Nuevo y detalle administrativo. |
| /admin/roadmaps/nuevo | Alta de recorrido | Administrador | Guardar borrador. |
| /admin/roadmaps/:id/editar | Editor de borrador o lectura de publicado/archivado | Administrador | Guardar, publicar o archivar. |
| Cualquier otra | 404 | Todos | Inicio o catálogo. |

El acceso administrativo con IDs no vuelve públicos esos recursos. Las rutas de frontend no determinan autorización real; cada endpoint comprueba sesión y rol.

## 2. Flujo público de descubrimiento

1. Inicio presenta búsqueda y acceso a roadmaps.
2. Buscar lleva a /cursos?q=consulta&page=1. Los filtros se expresan como category_id, level y language; sort controla orden.
3. Elegir una tarjeta abre /cursos/:slug.
4. Ir al curso abre el recurso externo en una nueva pestaña, sin cambiar progreso ni enviar credenciales de esta aplicación al proveedor.
5. Volver al catálogo conserva filtros mediante historial y URL.

Alternativas: cero resultados permite limpiar filtros; error de red permite reintentar; slug no público muestra 404. No se redirige a login para leer un curso público.

## 3. Registro e inicio de sesión

1. Registro valida datos en cliente y obtiene un token CSRF si no lo tiene.
2. Enviar solicita alta; se bloquea doble envío en UI.
3. Respuesta 202 muestra confirmación genérica e indica revisar correo; ofrece reenvío, login o recuperación.
4. Abrir el enlace de verificación, confirmar y volver a login. Login con contraseña correcta y correo verificado recibe cookie JWT y consulta /auth/me. Si el correo sigue pendiente, no se emite JWT y se ofrece reenvío.
5. Con identidad válida, redirige al next interno permitido o /mi-aprendizaje.

Si se llegó a login al intentar seguir un roadmap, next contiene únicamente su ruta de detalle, no una acción pendiente. Después del login se vuelve a esa ficha y el usuario elige seguir. Esto evita repetir mutaciones accidentalmente y mantiene el resultado visible.

Un usuario autenticado que visita login o registro se lleva a Mi aprendizaje. Recuperación y restablecimiento siguen accesibles para permitir recuperación explícita; reset revoca también su sesión actual.

## 4. Recuperación y restablecimiento

1. Desde login se elige “Olvidé mi contraseña”.
2. Se ingresa email y se envía solicitud con CSRF.
3. Se muestra respuesta uniforme, exista o no la cuenta. Un límite de IP muestra espera; un límite interno por email conserva la respuesta uniforme.
4. El correo de una cuenta activa contiene enlace a /restablecer-contrasena con token en fragmento.
5. La SPA captura token, limpia el fragmento y solicita nueva contraseña con confirmación.
6. Confirmar envía token en cuerpo HTTPS, nueva contraseña y CSRF. El token nunca se envía en query string de API.
7. Al aceptar, informa éxito, elimina datos privados de caché y lleva a login por acción del usuario.

Token inválido, usado o vencido converge en una única pantalla con acción “Solicitar otro enlace”. Si se recarga después de limpiar el fragmento, debe reabrirse el correo. Un correo duplicado no permite dos resets. No hay login automático ni aceptación de enlaces desde dominios elegidos por el cliente.

## 5. Seguimiento y aprendizaje

1. Roadmaps muestra recorridos publicados.
2. Detalle muestra objetivo y cursos en orden.
3. “Seguir roadmap” sin sesión lleva a login con retorno seguro; con sesión ejecuta una operación idempotente.
4. El éxito muestra progreso e incorpora el recorrido a Mi aprendizaje.
5. “Continuar aprendizaje” abre la ficha del primer curso no completado.
6. El estudiante puede cambiar estado a en curso o completado. Después de confirmación se reconsultan progreso y roadmaps propios.
7. Al regresar a Mi aprendizaje se presenta el siguiente paso. Si no queda ninguno, aparece completado.

Si un curso aparece en varios roadmaps, su estado es común. El detalle lo explica con ayuda breve: “Tu avance de este curso se usa en todos tus roadmaps”. El usuario puede volver de completado a en curso; no se bloquea esa acción ni se mantiene un porcentaje ficticio.

## 6. Abandono y archivado

“Dejar de seguir” abre un diálogo con explicación de que se conserva el avance de cursos. Cancelar no realiza solicitudes; confirmar elimina únicamente el seguimiento. La pantalla queda como roadmap público si sigue publicado. Si estaba archivado, después de abandonar deja de estar autorizado su detalle y se vuelve a Mi aprendizaje con confirmación.

Si administración archiva un roadmap entre su consulta y el intento de seguimiento, el backend rechaza el seguimiento y la interfaz explica que ya no está disponible. Si ya era seguido, permanece visible en el panel con etiqueta Archivado.

## 7. Administración de cursos

1. Administración abre listado con filtros de estado.
2. Nuevo curso abre formulario mínimo con título obligatorio.
3. Guardar crea borrador y lleva a su edición con ID y versión devueltos.
4. Completar datos y guardar actualiza la versión.
5. Publicar muestra revisión y exige versión vigente; si es válido cambia estado y muestra enlace a ficha pública.
6. Editar publicado permite corregir campos con todas las validaciones editoriales. El slug permanece estable.
7. Archivar abre confirmación. Si no hay dependencias protegidas, retira del catálogo y pasa a consulta.

Validación de campos mantiene formulario y enfoca resumen. Conflicto de versión conserva texto local; ofrece cargar servidor tras aviso. Dependencia de roadmap impide archivado con explicación. Se puede abandonar un borrador sin completarlo; no se permite publicarlo incompleto. Un archivado no se revierte desde la aplicación.

## 8. Administración de roadmaps

1. Nuevo crea borrador con título.
2. Se edita objetivo, nivel y resumen.
3. Seleccionar cursos publicados agrega pasos; subir, bajar y quitar actualiza lista local.
4. Guardar pasos reemplaza la lista completa atómicamente, con versión.
5. Publicar valida de nuevo cursos, pasos y contenido, y confirma que quedará inmutable.
6. Tras publicar, el editor se transforma en consulta con botón Archivar.

Un error al guardar pasos no deja la mitad de la lista persistida. Un curso que fue archivado mientras se editaba impide publicación. Archivar conserva pasos y seguimientos previos; no habilita edición. Una nueva propuesta de recorrido se crea como otro borrador.

## 9. Sesión y restricciones de navegación

Al entrar a una ruta privada se consulta sesión. Mientras se resuelve se muestra carga, sin datos privados residuales. Sin sesión se redirige a login. Con rol insuficiente se muestra 403 y salida al sitio público.

Al recibir 401 durante una acción, se borra caché privada y se solicita login. No se reenvía automáticamente el formulario previo. Logout revoca sesión en servidor antes de confirmar; ante fallo de red no afirmar revocación. Una vez confirmado, limpiar caché, cookie mediante servidor y volver a Inicio.

El parámetro next solo acepta rutas internas conocidas; rechazar URL absoluta, doble barra, javascript y variantes codificadas que eludan normalización. El destino por defecto es Mi aprendizaje. El botón Atrás no debe recuperar datos privados de otra sesión desde caché.

## 10. Flujo de errores transversal

422: conservar datos no secretos y mostrar campos afectados. 409: reconsultar el recurso antes de proponer repetir. 429: mostrar segundos de Retry-After y habilitar reintento después de la espera. No iniciar múltiples contadores contradictorios. 503: informar indisponibilidad temporal, mantener contexto y permitir volver. Escritura con resultado desconocido: reconsultar antes de repetir.

Todas las pantallas de error ofrecen navegación útil. El usuario no debe quedar atrapado en una redirección entre login, permisos y una ruta inexistente.

## 11. Flujo de verificación obligatoria

Registro encola enlace de 24 horas. El usuario abre /verificar-correo, la SPA extrae token del fragmento y limpia la URL. El botón “Confirmar correo” realiza POST /auth/verify-email con CSRF. Éxito muestra confirmación y lleva a login por acción del usuario; no autentica automáticamente. Token vencido/usado/alterado conduce a reenvío con respuesta genérica. Un GET del enlace, incluido el de un escáner de correo, no confirma la cuenta.

Login con contraseña válida y correo pendiente devuelve EMAIL_NOT_VERIFIED y ofrece /reenviar-verificacion. Recuperar contraseña no cambia ese estado ni permite saltar la verificación. El next seguro puede acompañar estos pasos como ruta interna validada, sin ejecutar acciones pendientes después de autenticar.

## 12. Flujo de CRUD del estudiante autor

Después de verificar email e iniciar sesión, el menú ofrece /mis-cursos. Crear abre formulario y guarda propietario desde JWT, nunca desde un campo. La edición usa /me/authored-courses y conserva versión. Publicar exige los mismos datos completos que administración; archivar aplica las mismas dependencias. Un curso ajeno devuelve 404. Las categorías y los roadmaps se consultan, pero su gestión administrativa no se habilita al autor.

Si el JWT vence, volver a login y luego al destino interno permitido; no repetir escrituras automáticamente. El usuario puede estudiar y crear cursos con la misma cuenta, pero sus listados personales de aprendizaje y autoría se presentan separados y con títulos claros.
