# Flujo de Git — GitHub Flow individual

## Elección y ramas

Se elige GitHub Flow porque el trabajo es individual y permite cambios pequeños con revisión visible, sin ramas de releases innecesarias. main contiene lo revisado. Ramas `docs/<tema>`, `feat/<tema>`, `fix/<tema>`, `test/<tema>` y `docker/<tema>`. En esta corrección ya existe `docs/modificaciones-consigna`: usarla, no crear otra ni sobrescribirla.

## Ciclo de cambio

Ticket o tarea del plan → rama desde main actualizado → commits específicos → push de la rama → PR → autorrevisión documentada → merge commit a main. Un solo trabajo funcional principal en curso. Sin otro integrante disponible, la autora realiza la autorrevisión: no se inventa aprobación de terceros. El docente aprueba la fase por correo, no se presume que revise cada PR.

Antes del merge verificar diferencias, rutas, enlaces, datos secretos y aceptación. PR incluye qué cambió, motivo, requisitos/historias, comprobación efectuada y limitaciones. Usar merge commit para conservar evidencia de rama; su mensaje también convencional, por ejemplo `docs: merge assignment corrections`. Después confirmar que main remoto contiene la entrega; copiar su SHA y mensaje al correo. Borrar rama fusionada es opcional.

## Commits

Formato `tipo: descripción concreta`: docs, feat, fix, test, refactor, chore, docker. Ejemplo `docs: define contribution review lifecycle`. Evitar wip/cambios y tipo con mayúscula o sin espacio. No juntar funciones distintas ni versionar .env, dependencias instaladas o archivos privados. No crear fuentes, manifests ni locks antes de APROBADO + T1.

## Incumplimientos históricos

La revisión observó `3d36477 Initial commit` (README/.gitignore) y `8fec062 Feat:Agrego la documentacion requerida para el analisis del dominio`. No cumplen el formato adoptado; tampoco el primero conserva la SPEC original. La historia existente se conserva. Agregar ahora el original deja trazabilidad a partir de esta corrección, sin cumplir retroactivamente la regla. Informar ambos puntos y pedir instrucciones al docente; no forzar push ni reescribir historia sin acuerdo.

## Tablero previsto

Pendiente, En curso, En revisión, Terminado. WIP máximo una funcionalidad principal, porque es individual. Issues HU-01 a HU-12 con RF/RN/RNF, criterios, tareas y evidencia esperada. Su creación se registra solo cuando ocurra; este documento no afirma issues ni tablero creados.
