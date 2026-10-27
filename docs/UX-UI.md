UX-UI — Cursos Abiertos
Versión 2.0. Guía textual; inspiración Google/Material, sin usar marca Google. Diseño previo a implementación.

1. Principios
1. Móvil como base, mejoras progresivas al crecer pantalla.
2. Búsqueda y siguiente acción visibles, con espacio en blanco.
3. Estados de carga, vacío y error distintos y recuperables.
4. Validación y privacidad explícitas: aporte pendiente no equivale a publicado; roadmap personal no es público.
5. Accesibilidad por teclado y foco visible, no depender de color ni hover.

2. Design tokens
2.1 Paleta
Los ratios de esta tabla se calculan con luminancia relativa sRGB para los colores planos indicados; no certifican componentes todavía inexistentes. La implementación debe comprobar estados y fondos reales.
Token	Valor	Uso	Contraste sobre blanco
--color-primary	#174EA6	Botón, link, foco	7.85:1
--color-on-primary	#FFFFFF	Texto de botón	7.85:1 sobre primario
--color-background	#FFFFFF	Página	—
--color-surface	#F8F9FA	Sección secundaria	No usar como borde de control.
--color-text	#202124	Texto	16.10:1
--color-text-muted	#5F6368	Ayuda y metadata	6.05:1
--color-success	#146C2E	Éxito con texto/icono	6.53:1
--color-warning	#7A4F01	Aviso con texto/icono	7.13:1
--color-error	#B3261E	Error con texto/icono	6.54:1
--color-control-border	#747775	Borde de input	4.53:1
--color-divider	#DADCE0	Separador decorativo	Sin función esencial.

2.2 Tipografía
system-ui, Arial, sans-serif; sin descargar fuentes externas. Tokens: --text-sm 14px/1.5 metadatos, --text-base 16px/1.5 cuerpo, --text-lg 20px/1.4 sección, --text-xl 28px/1.3 título. Peso 400 normal, 600 acciones, 700 títulos. Una h1 por pantalla. Sin texto informativo menor a14px.

2.3 Espaciado y capas
Escala 4,8,12,16,24,32,48,64px (--space-1..8). Radios sm8/md12/lg24px. Sombra sm=0 1px 3px #00000026; md=0 4px 12px #00000026. Capas header100, overlay200, modal300, toast400. Contenedor max1200px, gutters16px base/24px desde768. Formulario auth max440px; aporte max800px. Acciones táctiles mínimo44px, gap8px. Foco outline3px primario, offset2px. Colores de texto de etiquetas no se aplican sobre fondos de color sin comprobar.

2.4 Variables documentales listas para implementar después del T1
:root {
  --color-primary: #174EA6;
  --color-on-primary: #FFFFFF;
  --color-background: #FFFFFF;
  --color-surface: #F8F9FA;
  --color-text: #202124;
  --color-text-muted: #5F6368;
  --color-success: #146C2E;
  --color-warning: #7A4F01;
  --color-error: #B3261E;
  --color-control-border: #747775;
  --color-divider: #DADCE0;
  --font-family-base: system-ui, Arial, sans-serif;
  --text-sm: 14px; --text-base: 16px; --text-lg: 20px; --text-xl: 28px;
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 24px; --space-6: 32px; --space-7: 48px; --space-8: 64px;
  --radius-sm: 8px; --radius-md: 12px; --radius-lg: 24px;
  --shadow-sm: 0 1px 3px #00000026;
  --shadow-md: 0 4px 12px #00000026;
  --z-header: 100; --z-overlay: 200; --z-modal: 300; --z-toast: 400;
}
3. Mobile-first con mejora progresiva
Capa	Layout y navegación
Base sin media queries	Una columna, menú sándwich, formularios apilados, tablas como cards con etiquetas y paginador, padding16px.
@media (min-width: 768px)	Dos columnas de cards, nav horizontal, padding24px; tabla semántica si cabe sin ocultar información.
@media (min-width: 1024px)	Tres columnas catálogo, filtros laterales, contenedor centrado; formularios siguen limitados.
No diseñar desktop y usar max-width para reparar móvil. Media de preferencias como prefers-reduced-motion no es breakpoint de layout. Todo control funciona sin hover/arrastre; mejoras visuales no ocultan funciones. Verificar 360/768/1440px, zoom200% y reflujo320px. Paginación permanece en todas las capas.

4. Componentes: anatomía y estados

4.1 Botones
Label explícito, padding12px16px, radio8, alto mínimo44px, icono20px opcional. Primario blanco sobre primario; secundario texto primario y borde; peligro texto error y confirmación. default/hover (subrayar o elevar)/focus-visible (outline)/active (sombra interna)/disabled (fondo surface, texto muted, sin acción)/loading (label “Guardando…” e indicador). Disabled no comunica error. Durante petición evitar doble clic; no eliminar foco.

4.2 Inputs y selectores
Label permanente, borde control1px, radio8, padding12px, ayuda14px. default/focus/filled/error/disabled; error con texto y aria-describedby, aria-invalid. Nombre y email conservados ante fallo; password no persistida. Sí/no sin preselección en indicadores y declaración del aporte. Desconocido solo donde PRD lo permite. Categorías: selector con búsqueda y “Cargar más”, consume páginas, conserva selección por id y muestra nombre por endpoint de detalle.

4.3 Card de curso
Título, categoría, tema/proveedor, edición/docentes informados y badges certificado/examen/aval con texto; acción “Ver curso” y “Agregar a mi roadmap” autenticado. default, hover, focus-within y seleccionado (“Ya está en tu roadmap”, sin duplicar). No inferir pertenencia descargando roadmaps ajenos; si la API no conoce pertenencia, agregar puede devolver duplicado y explicarlo. No mostrar indicadores como confirmados si falta fuente.

4.4 Listados y tablas
Header, contador, filtros, contenido, paginador anterior/siguiente y página actual. Loading skeleton y texto; éxito datos; vacío con acción específica; error con reintento. Aplicar filtros vuelve a página1. Cambio de página conserva filtros; lectores reciben anuncio de página cargada sin narrar cada skeleton. Columnas de revisión: título, autor visible solo al admin, fecha, estado, acciones.

4.5 Menú sándwich
Botón “Abrir menú”, aria-expanded y aria-controls. Panel cerrado/abierto con enlaces según sesión/rol. Al abrir enfocar primer enlace, contener foco si funciona como modal; cerrar por botón, Escape, click fuera o navegación; devolver foco al botón salvo cambio de ruta. Desktop presenta mismos destinos. Mi roadmap nunca aparece como recurso de otro usuario.

4.6 Modal
Título, explicación, cancelar y acción concreta; focus trap, aria-labelledby, Escape y retorno de foco. Usos: retirar curso, quitar item y editar publicado. Quitar item: “Se eliminará también tu avance en este curso”. Editar publicado: “El curso dejará de aparecer en el catálogo hasta una nueva aprobación”. In_review no ofrece edición, sí retiro.

4.7 Toast y mensajes
Éxito/info role=status, 6s; error también inline persistente y role=alert si necesita atención. No esconder motivo de rechazo ni espera del rate limit en toast temporal. Posición inferior con margen16px sin cubrir acciones. Textos: “Aporte enviado a revisión”; “Curso agregado a tu roadmap”; “No pudimos confirmar el guardado. Revisá el estado antes de repetir”.

4.8 Skeleton/vacío
Skeleton con dimensiones de card y aria-hidden; región con aria-busy y texto de carga. Vacío inicial catálogo: “Todavía no hay cursos publicados”; con filtros: “No encontramos cursos con estos filtros”, limpiar. Roadmap vacío: “Elegí un curso para empezar”, CTA catálogo. Error no se transforma en vacío.

4.9 Item de roadmap y revisión
Item: posición global, título, disponibilidad, estado de avance, botones subir/bajar/quitar. Subir/bajar se aplican a orden global aun en borde de página; no dependen de drag. No disponible conserva título/avance con aviso, sin enlace externo ni selector de avance; quitar sigue permitido. Revisión muestra metadatos, link externo, confirmación de comprobación y aprobar/rechazar; rechazo exige motivo visible al autor. Auto-revisión indica permiso insuficiente sin aprobar.

5. Layout y pantallas
Header sticky, marca propia y destinos Catálogo, Mi roadmap, Mis aportes; Revisión solo admin. Sin sesión Login/Registro. Inicio con búsqueda protagonista. Catálogo con filtros y cards; detalle con metadatos y enlace externo. Auth centrada. Aporte por secciones: identificación, edición/docentes, evaluación/certificado/aval, declaración y envío. Estado del aporte muestra motivo y acciones permitidas. Roadmap muestra fracción, porcentaje y siguiente disponible. Tabla de revisión y ficha administrativa con dos decisiones claras. Rutas y fichas completas en APPFlow.

6. Accesibilidad y comprobación futura
Contraste ratios §2; revisión en componentes reales aún pendiente. Etiquetas programáticas, alt en imágenes informativas, iconos decorativos aria-hidden, foco visible, saltar al contenido, orden lógico. Formularios con autocomplete email/current-password/new-password, permitir pegado. Cambio de ruta actualiza title y foco h1. Errores enlazados; no solo color. Reducir animación con prefers-reduced-motion. Probar teclado, menú, diálogos, paginación, reordenación, zoom y contraste. Lista de verificación documental no se marca como prueba realizada.

7. Iconografía y assets
Lucide React con versión exacta por fijar en B; iconos20px, currentColor, stroke2. Razón: set consistente y accesible acompañado de texto. Menu, X, Search, ChevronUp/Down, ExternalLink, Check y AlertCircle. Sin imágenes obligatorias ni logos de proveedores descargados sin revisar permisos. Fuente del sistema para reducir dependencias.