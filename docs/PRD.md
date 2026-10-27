PRD — Cursos Abiertos
Versión 2.0, 27/10/2026. Propuesta de producto para revisión. Fuente obligatoria: [SPEC oficial](referencias/SPEC.md).

1. Resumen ejecutivo
Los estudiantes aportan cursos gratuitos con metadatos suficientes para elegirlos. Un administrador los valida antes de incorporarlos al catálogo público. Cada usuario verificado selecciona cursos del catálogo para su roadmap privado, decide el orden y registra avance. La plataforma enlaza al proveedor externo; no imparte ni certifica cursos.

2. Objetivos y métricas
Objetivo	Verificación de aceptación futura
Descubrir cursos	Encontrar un curso por tema y categoría con filtros y paginación desde UI.
Mantener catálogo validado	Cero aportes pendientes/rechazados/archivados en consultas públicas.
Organizar aprendizaje	Dos usuarios crean listas distintas; ninguno accede ni modifica la ajena.
Completar ciclo de aporte	Autor aporta, administrador revisa y resultado se refleja en UI.
Recuperar acceso	Solicitud, correo local, cambio y login con nueva contraseña.
Utilizar desde móvil	Flujos P0 utilizables a 360 px con menú sándwich y teclado.
Son objetivos por comprobar, no resultados medidos.

3. Personas
Estudiante que organiza su aprendizaje
Contexto: cursa materias y combina recursos de distintas plataformas desde celular y computadora. Motivación: elegir cursos apropiados y ordenar su estudio. Frustraciones: enlaces dispersos, datos incompletos y pérdida del avance. Historias tipo: “quiero guardar este curso para después”; “quiero retomar el primero que no terminé”. Puede aportar recursos propios a la comunidad.
Administrador que valida aportes
Contexto: revisa recursos enviados por estudiantes en sesiones cortas. Motivación: mantener un catálogo gratuito, completo y trazable. Frustraciones: duplicados, enlaces rotos y cambios sin revisión. Historias tipo: “quiero saber qué cambió”; “quiero rechazar indicando exactamente qué corregir”. Mantiene permisos personales, pero no consulta roadmaps ajenos.

4. Historias de usuario
Cada fila es aceptación futura. Una historia terminada requiere recorrido desde UI y evidencia en el plan.
ID	Prioridad	Como / quiero / para	Criterios verificables
HU-01	P0	Visitante: buscar catálogo para descubrir cursos	Solo publicados; buscar por título/tema/proveedor sin distinguir mayúsculas; combinar categoría/nivel/idioma; páginas de 20 por defecto; filtros en URL; vacío distinto de error.
HU-02	P0	Visitante: consultar ficha para evaluar un curso	Ver todos los metadatos, gratuidad y condiciones de certificado; enlace externo identificado; 404 si no publicado; no mostrar datos privados del autor.
HU-03	P0	Persona: registrarme e ingresar para usar funciones privadas	Registro válido envía verificación; cuenta duplicada responde genérico; pendiente no obtiene JWT; verificada inicia sesión; logout invalida acceso posterior; rol no elegible.
HU-04	P0	Usuario: recuperar acceso para no perder mis datos	Solicitud genérica, enlace de 30 min, uso único, contraseña nueva y sesiones revocadas; token inválido/expirado ofrece nueva solicitud.
HU-05	P0	Persona: entender el límite de login para saber cuándo reintentar	Superar cuota devuelve 429 y espera; límite se mantiene tras reiniciar API; mismo trato para emails inexistentes; mensaje no confunde con contraseña incorrecta.
HU-06	P0	Autor: aportar curso para enriquecer catálogo	Completar campos y declaración de toma; guardar borrador o enviar a revisión; no puede aprobarse ni aparecer público sin validación; duplicado detectado.
HU-07	P0	Autor: editar o retirar mis cursos para mantenerlos	Listar propios con estados; editar propios y reenviar; cambio publicado pasa a revisión; archivado desaparece público sin borrar referencias; curso ajeno 404.
HU-08	P0	Usuario: organizar mi roadmap para decidir qué estudiar	Agregar publicado, ordenar, quitar con confirmación; sin repetidos; solo propietario; recarga conserva orden; máximo 100 cursos.
HU-09	P0	Administrador: validar aportes para mantener catálogo confiable	Pendientes paginados; detalle completo; aprobar tras comprobar enlace y gratuidad; rechazo exige motivo; autor ve resultado; versión vieja produce 409.
HU-10	P0	Usuario: registrar avance para retomar	Estados pendiente/en_curso/completado; conteo y porcentaje derivados; siguiente es primer no completado; 0 cursos muestra 0%; completado puede reabrirse.
HU-11	P0	Persona: confirmar correo para acreditar titularidad	Token 24 h, uso único, confirmación explícita sin login automático; reenvío invalida anteriores; respuesta genérica; enlace vencido ofrece reenviar.
HU-12	P0	Autor: consultar mis aportes para saber qué corregir	Listado propio paginado, filtros por estado, detalle de motivo/fecha; ajenos no visibles; autoría no editable.

HU-08/09 reemplazan el alcance previo de roadmaps públicos y seguimiento de terceros. No se conservan tareas para funciones retiradas.
5. Requisitos funcionales y validaciones
ID	Requisito	Historias
RF-01	Registrar cuenta sin asignar rol desde cliente.	HU-03
RF-02	Emitir JWT solo tras credenciales correctas y correo verificado.	HU-03
RF-03	Consultar identidad y cerrar sesión revocándola.	HU-03
RF-04	Solicitar y completar recuperación segura.	HU-04
RF-05	Aplicar rate limit al login y operaciones de correo.	HU-05
RF-06	Listar/buscar catálogo y consultar fichas públicas.	HU-01/02
RF-07	Crear/editar/listar/archivar cursos propios.	HU-06/07/12
RF-08	Registrar metadatos y declaración de toma del aportante.	HU-06
RF-09	Enviar, revisar, aprobar o rechazar un aporte.	HU-06/09/12
RF-10	Consultar roadmap propio, agregar/reordenar/quitar cursos.	HU-08
RF-11	Actualizar estado, calcular avance y siguiente curso.	HU-10
RF-12	Confirmar correo y reenviar enlace.	HU-11
RF-13	Obtener categorías paginadas de lista precargada.	HU-01/06


Contrato de metadatos
Al enviar a revisión: categoría existente; tema 2–100; título 3–150; proveedor 2–100; resumen 20–300; descripción 50–10000; URL HTTPS válida hasta 2048; idioma es/en/pt; nivel inicial/intermedio/avanzado; duración estimada 1–100000 minutos. Los campos adicionales de descubrimiento son decisión propia.
Versión: hasta 80 caracteres, o nulo con versión no informada. Año: 1900 hasta año UTC actual, o nulo si no informado. Docentes: 1–20 nombres de 2–120 caracteres, o lista vacía si explícitamente no informados. La UI permite “No informado” y explica la ausencia. Cuestionarios, examen, certificado y aval se responden sí/no, sin defaults silenciosos; si hay aval se exige organización 2–150. Sin aval, organización nula. La declaración author_has_taken exige sí/no explícito al envío; nulo solo en borrador.
Borrador requiere título; campos presentes válidos, resto puede ser nulo. Enviar o aprobar revalida todos los obligatorios. Certificado puede implicar costo externo: nota hasta 500 caracteres; obligatorio aclararlo si corresponde. El administrador rechaza datos que no puede comprobar; “no informado” solo es válido para versión, año y docentes y debe reflejar al proveedor.
Email normalizado único, máximo 254; nombre 2–80. Contraseñas 15–128 caracteres, sin recortar y con confirmación en UI. Mensajes no revelan existencia de cuenta en registro, recuperación o reenvío.
6. Requisitos no funcionales
ID	Requisito	Verificación
RNF-01	Seguridad: hashing, JWT, propiedad y no secretos en Git	Revisión de contratos, demostración de accesos ajenos rechazados.
RNF-02	Todos los listados y tablas paginados	Catálogo, categorías, propios, pendientes y roadmap; page_size 1–100, default 20.
RNF-03	Mobile-first con mejora progresiva y menú móvil	UX-UI y recorrido a 360/768/1440 px.
RNF-04	Accesibilidad	Contraste documentado, teclado, foco y errores asociados; objetivo WCAG AA, sin afirmar certificación.
RNF-05	Screaming Architecture	Estructura prevista y luego real por dominios de negocio.
RNF-06	Reproducibilidad	Clon limpio y Compose con instrucciones y seeds.
RNF-07	Integridad	Un email, un roadmap por usuario, un curso por roadmap y orden consistente.
RNF-08	Rendimiento	Objetivo API catálogo p95 < 700 ms con 1000 cursos/10 clientes, excluye hashing/SMTP; medir después.
RNF-09	Observabilidad	Request ID y estados sin tokens, contraseñas ni cookies.

7. Reglas de negocio
ID	Regla	Fuente
RN-01	Publicación solo tras aprobación de contenido principal gratuito y enlace activo.	SPEC
RN-02	Autor declara si tomó el curso; no equivale al avance de otros usuarios.	SPEC
RN-03	Un roadmap privado por usuario, hasta 100 cursos, propio y editable.	SPEC personal + decisión
RN-04	Solo autor modifica/archiva el propio; admin puede revisar y archivar cualquiera, con motivo.	Decisión
RN-05	Estados de avance manual: pendiente, en_curso, completado.	Decisión
RN-06	Admin valida; no aprueba sus propios aportes en MVP. Demo usa dos cuentas distintas.	Decisión de separación de revisión
RN-07	Editar un publicado lo devuelve a borrador y lo retira del catálogo hasta nueva aprobación; en_revision no editable.	Decisión simple, sin versionado editorial doble
RN-08	Archivado terminal, baja lógica; conserva referencias y progreso.	Decisión
RN-09	Solo se agregan publicados; si después dejan de publicarse, el roadmap conserva título/estado/avance y aviso, sin habilitar enlace externo.	Decisión
RN-10	URL normalizada global única, incluso archivada; conflicto 409. Normalizar esquema/host en minúsculas, quitar fragmento/puerto HTTPS estándar, conservar path/query.	Decisión
RN-11	Progreso por item del roadmap; quitar elimina ese avance y volver a agregar inicia pendiente. Confirmar consecuencia en UI.	Decisión de simplificación
RN-12	Posiciones consecutivas desde 1, sin cursos repetidos; reordenación afecta todo el recorrido, no solo página visible.	Decisión
RN-13	Correo verificado requerido para acceso privado; reset no saltea verificación.	Requisito previo
RN-14	Categorías precargadas, sin CRUD de categorías en MVP.	SPEC lista + decisión

8. Fuera de alcance
Ver SPEC §4. No se exige backup con RPO/RTO, auditoría de rendimiento de gran escala ni outbox cifrada/worker como entregables P0. No se reduce seguridad básica ni funciones exigidas por retirar estos extras.

9. Supuestos y decisiones
Las decisiones resuelven vacíos, no se atribuyen a la cátedra: [SPEC §8](SPEC.md). Se conserva autenticación JWT y correo por solicitud previa. Implementación individual: rol administrador es actor del producto, no otro integrante del equipo.

