# PRD — Requisitos del producto

Versión 1.1. Fuente de alcance y reglas: SPEC.md. Estado: propuesta para primera entrega académica.

## 1. Problema y oportunidad
Una persona que busca aprender desarrollo de software encuentra cursos dispersos, dificultades para distinguir recursos gratuitos y dudas sobre qué estudiar primero. Guardar enlaces por separado no resuelve el orden ni permite recordar qué se completó. El administrador necesita mantener un catálogo confiable sin intervenir directamente en la base de datos.
La propuesta es reunir cursos gratuitos y organizarlos en roadmaps lineales, con una interfaz sencilla centrada en búsqueda y continuidad. El producto ofrece orientación y organización; no promete resultados laborales, aprobación certificada ni calidad comprobada mediante evaluaciones propias.

## 2. Usuarios y necesidades
**Estudiante principiante:** necesita identificar un punto de partida y entender requisitos previos. Debe poder explorar sin registrarse y crear una cuenta cuando quiera guardar avance.

**Estudiante que retoma:** necesita recuperar el acceso y saber cuál es su siguiente curso, incluso cuando un curso participa en más de un recorrido.

**Administrador del catálogo:** necesita cargar información coherente, revisar antes de publicar y evitar cambios que rompan recorridos existentes.

Estas personas son hipótesis de diseño; no provienen de entrevistas realizadas. 

## 3. Propuesta de valor y objetivos
1. Reducir el esfuerzo necesario para descubrir un curso adecuado.
2. Mostrar un camino concreto para alcanzar una meta de aprendizaje.
3. Conservar el progreso y facilitar retomar el estudio.
4. Mantener el catálogo mediante CRUD seguro y comprensible.
5. Demostrar una solución de extremo a extremo con tecnologías de la consigna y prácticas de ingeniería justificables.

El primer resultado valioso para un visitante es abrir la ficha de un curso apropiado. Para una persona registrada es seguir un roadmap y encontrar su siguiente paso. Para administración es publicar un curso válido sin modificar datos manualmente.

## 4. Indicadores propuestos
| Indicador | Definición | Meta inicial y medición |
| --- | --- | --- |
| Éxito de búsqueda | Participantes que encuentran un curso según una consigna sin ayuda | Al menos 4 de 5 en una prueba moderada. |
| Continuidad | Participantes que encuentran el siguiente paso de su roadmap | Al menos 4 de 5 sin explicación adicional. |
| CRUD completo | Crear, consultar, editar y archivar un curso de prueba | 100% del guion sin tocar PostgreSQL manualmente. |
| Recuperación válida | Restablecimiento con correo de prueba y acceso posterior | Funciona; enlace anterior y sesiones previas quedan inválidos. |
| Control de acceso | Intentos de acceso indebido rechazados | 100% de los casos críticos definidos. |
| Consistencia del progreso | Mismo curso completado en dos roadmaps | Ambos reflejan el avance tras reconsultar. |


## 5. Priorización de funcionalidades
Todos los elementos P0 pertenecen al MVP. El orden de construcción está en IMPLEMENTATION_PLAN.md.

| Prioridad | Funcionalidad | Valor | Requisitos |
| --- | --- | --- | --- |
| P0 | Consulta pública, búsqueda y filtros | Descubrimiento sin fricción | RF-07 a RF-09 |
| P0 | Login, registro y sesión | Identidad y persistencia | RF-01 a RF-03 |
| P0 | Recuperación y rate limit | Acceso recuperable y protección | RF-04 a RF-06 |
| P0 | CRUD de cursos propios, administración global y categorías | Mantenimiento del catálogo | RF-10 a RF-12 |
| P0 | Roadmaps y publicación controlada | Orden pedagógico estable | RF-13 a RF-16 |
| P0 | Seguimiento y progreso | Continuidad personal | RF-17 a RF-22 |
| P0 | UX adaptable, errores y accesibilidad | Uso comprensible | RNF-02 y RNF-03 |
| P0 | Verificación y reenvío de correo | Acreditar control de la dirección antes del acceso | RF-23 y RF-24 |
| P1 posterior | Nueva edición o copia de roadmap | Evolución sin alterar historial | Fuera de MVP |
| P2 posterior | Favoritos, etiquetas múltiples y recomendaciones | Personalización | Fuera de MVP |

## 6. Historias y criterios de aceptación

### HU-01 — Explorar y buscar

Como visitante quiero buscar cursos para encontrar recursos adecuados a mi nivel.

- Dado un catálogo con cursos publicados, al buscar “React” se muestran coincidencias de título o proveedor, sin distinguir mayúsculas, y nunca borradores o archivados.
- Al combinar nivel y categoría se aplican ambos filtros y se vuelve a la primera página.
- Al recargar o compartir la URL se conserva la búsqueda.
- Si no hay resultados se muestran la consulta actual y una acción para limpiar filtros.
- Un fallo de API muestra reintento y conserva la consulta; no aparece como “sin resultados”.

### HU-02 — Consultar un curso

Como visitante quiero conocer contenido, requisitos y duración para decidir si me sirve.

- La ficha muestra todos los campos públicos y la condición de gratuidad, incluida cualquier nota de certificado externo.
- “Ir al curso” abre la URL HTTPS externa y advierte visualmente que se sale del sitio.
- Una URL con slug inexistente o no público produce una pantalla 404 comprensible.
- El botón externo no marca el curso como completado.

### HU-03 — Registrarme e ingresar

Como estudiante quiero crear mi cuenta e iniciar sesión para conservar el avance.

- Un registro válido crea exclusivamente una cuenta de estudiante. Un email duplicado no modifica la cuenta anterior.
- La respuesta de registro es genérica en ambos casos; se indica revisar el correo, verificarlo e iniciar sesión. Se ofrecen reenvío y recuperación sin revelar existencia de cuenta.
- Contraseña y confirmación diferentes impiden el envío desde la interfaz.
- Un login correcto de una cuenta verificada emite JWT y lleva al destino interno solicitado o a Mi aprendizaje. Con contraseña válida y email pendiente se pide completar verificación, sin emitir JWT.
- Un login incorrecto no revela si existe la cuenta; una contraseña errónea nunca crea una sesión.
- Al recargar se conserva una sesión vigente; al cerrar sesión, otra petición con la cookie anterior falla.

### HU-04 — Recuperar acceso

Como persona que olvidó su contraseña quiero obtener un enlace seguro.

- Con email existente o inexistente se muestra el mismo mensaje y estado 202, sujeto a límites de abuso por IP.
- Con enlace válido y contraseña aceptable se confirma el cambio y se ofrece login.
- Token vencido, usado o alterado muestra un mensaje unificado y acceso a solicitar otro enlace.
- Dos envíos simultáneos con un mismo token permiten como máximo un cambio.
- Tras restablecer, ninguna sesión anterior puede consultar información privada.

### HU-05 — Recibir un límite comprensible

Como usuario quiero saber cuándo reintentar si envío demasiadas solicitudes.

- Un límite público por IP devuelve 429 y segundos de espera en Retry-After.
- La interfaz muestra espera estimada sin perder email ni demás datos no secretos; no persiste contraseñas.
- Los envíos inhibidos internamente por cuenta en registro o recuperación conservan respuesta genérica para no permitir enumeración.
- Después de la ventana se puede volver a intentar. No existe bloqueo permanente de la cuenta.

### HU-06 — Crear y publicar cursos

Como estudiante autor o administrador quiero preparar un curso antes de ofrecerlo públicamente.

- Guardar un título válido crea un borrador visible para su autor en Mis cursos creados y para administración.
- Publicar exige campos completos, categoría válida, URL permitida y confirmación editorial de gratuidad.
- Un estudiante verificado puede crear y editar cursos propios. Si intenta leer o modificar un curso ajeno por rutas de autor recibe 404. Las rutas administrativas continúan reservadas a admin.
- Si otro administrador editó la misma versión, se informa conflicto y se evita sobrescribir cambios.
- Una vez publicado se encuentra desde el catálogo.

### HU-07 — Editar y dar de baja

Como autor de un curso o administrador quiero corregir información y retirar recursos sin romper relaciones.

- Editar un curso publicado mantiene las validaciones exigidas para publicación.
- Archivar solicita confirmación y retira el curso del catálogo público.
- Si un roadmap que fue publicado lo utiliza, se devuelve 409 y se explica qué asociación impide archivarlo.
- Repetir el archivado con la versión vigente o tras reconsultar no duplica efectos ni borra datos históricos.
- No hay eliminación física de cursos desde la aplicación.

### HU-08 — Construir un roadmap

Como administrador quiero ordenar cursos para proponer una secuencia de aprendizaje.

- Puedo agregar, quitar y mover pasos en un borrador, también con teclado.
- Un curso repetido, posiciones incompletas o más de 50 pasos producen validación.
- No puedo publicar un recorrido vacío ni con cursos no publicados.
- Después de publicar puedo consultarlo y archivarlo, pero no cambiar sus contenidos ni pasos.
- Si hay un conflicto concurrente al publicar, la operación se rechaza completamente.

### HU-09 — Seguir y abandonar un roadmap

Como estudiante quiero guardar un recorrido en mi panel.

- Seguir un roadmap publicado lo agrega una sola vez aunque repita la solicitud.
- Si ya hay cursos completados, el porcentaje inicial los incluye.
- Abandonar requiere confirmación y retira el seguimiento, sin reiniciar progreso.
- No puedo seguir un roadmap archivado; si ya lo seguía puedo consultar su detalle con etiqueta “Archivado”.

### HU-10 — Registrar avance y retomar

Como estudiante quiero registrar lo estudiado y encontrar mi siguiente paso.

- Cada curso admite no iniciado, en curso y completado, con confirmación visual tras respuesta del servidor.
- El progreso de otra persona no puede consultarse ni modificarse cambiando identificadores.
- Dos roadmaps que comparten un curso actualizan sus conteos al completar o reabrir ese curso.
- El siguiente paso es el primero no completado. Todos los pasos siguen accesibles.
- Si todos están completos, aparece el estado final sin sugerir un siguiente curso.

## 7. Contenido y experiencia

La página inicial prioriza un buscador central con acceso al catálogo y a roadmaps. La estética es clara, con mucho espacio, texto legible y azul como acción principal. La referencia a Google define sencillez, jerarquía y rapidez de lectura; no autoriza copiar logos ni crear apariencia de afiliación.

Los textos usan español consistente: “Iniciar sesión”, “Crear cuenta”, “Recuperar contraseña”, “Seguir roadmap” y “Mi aprendizaje”. En campos editoriales se explica qué falta antes de publicar. Los errores no deben exponer stack traces, nombres de tablas ni detalles internos.

## 8. Restricciones y compromisos
El equipo debe completar React 19 con Vite/pnpm, FastAPI con uv, PostgreSQL y Docker Compose. No se agrega Redis, plataforma de videos ni servicio de identidad para el MVP. SMTP es la dependencia externa mínima para recuperación real; puede simularse de forma controlada en desarrollo.

La inmutabilidad de roadmaps publicados sacrifica edición inmediata a cambio de conservar la secuencia. El seguimiento es manual para evitar integraciones con proveedores y sus credenciales. El JWT de 15 minutos, sin refresh token en el MVP, requiere volver a iniciar sesión al vencer. La verificación de correo agrega un paso necesario antes del primer acceso.

## 9. Riesgos de producto y validación
Cursos retirados o que dejan de ser gratuitos: revisión manual periódica y corrección de enlace o selección editorial; si ya están en un roadmap publicado, no se promete archivado libre. La sustitución de cursos en recorridos publicados requerirá una política de versiones futura. En la entrega se utilizarán enlaces previamente revisados.

Catálogo vacío: datos de demostración realistas con fuentes y fechas de revisión. Roadmaps poco claros: probar orden, objetivo y requisitos con compañeros. Scope excesivo: no incorporar P1 antes de terminar criterios P0. Confusión sobre inscripción externa: indicar que seguir aquí no registra al usuario en el proveedor.

## 10. Entrega y evidencia
Demostrar un recorrido público, uno autenticado, una verificación y recuperación reales en correo de pruebas, CRUD propio de estudiante y CRUD administrativo. Adjuntar resultados de pruebas, matriz de requisitos, procedimiento de instalación y limitaciones conocidas. Las capturas futuras serán evidencia de una implementación posterior; esta entrega documental permanece exclusivamente en texto.

## 11. Historias incorporadas en revisión 1.1
### HU-11 — Verificar el correo

Como estudiante quiero confirmar mi dirección para activar el acceso privado.

- El registro envía verificación a una cuenta nueva y mantiene respuesta pública uniforme.
- Con contraseña correcta y email pendiente, login devuelve 403 EMAIL_NOT_VERIFIED y no entrega JWT.
- El enlace válido activa el email tras una confirmación explícita y conduce a login.
- Tokens alterados, usados o vencidos muestran un error uniforme y opción de reenviar.
- El reenvío invalida enlaces anteriores; no cambia la contraseña ni verifica una cuenta inexistente.
- Recuperar contraseña no omite la verificación requerida.

### HU-12 — Gestionar mis cursos creados
Como estudiante con correo verificado quiero administrar los cursos que aporté.

- Mis cursos creados muestra solo los propios, incluidos borradores y archivados.
- Puedo crear, consultar, editar, publicar y archivar los propios con las reglas comunes.
- No puedo alterar created_by mediante cuerpo, URL o claim enviado sin firma válida.
- Un segundo estudiante no puede consultar mis borradores ni cambiar mis cursos.
- No obtengo acceso a categorías ni a edición de roadmaps por crear cursos.

La priorización incorpora RF-23 a RF-25 en P0. La rúbrica de evaluación propuesta se encuentra en docs/RUBRICA.md y no presupone aprobación oficial docente.
