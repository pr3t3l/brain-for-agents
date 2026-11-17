# Reglas globales para cualquier IA (Claude Code y Codex)

Este archivo se carga en todas las sesiones, en cualquier carpeta. Mantenlo corto: los detalles viven en el cerebro. Cambia todo lo que está entre `{{ }}`.

## Quién soy y qué hago
Soy {{tu nombre}}. Mis proyectos: {{proyecto 1 (qué es)}}, {{proyecto 2 (qué es)}}. Hoy la prioridad es {{tu prioridad}}.

## Dónde está todo lo que sabemos
- **El cerebro:** `{{ruta completa del cerebro}}`. Empieza por `index.md` y, si trabajas en un proyecto, por `proyectos/<proyecto>/<proyecto>.md` y `<proyecto>-estado.md`.
- **Conocimiento compartido:** `conocimiento/conocimiento.md`.
- **El código** de cada proyecto vive en `{{carpeta de proyectos}}`. El cerebro no tiene código.
- **Mapas del código:** si el repo donde trabajas tiene `MAPS.md` o una carpeta `graphify-out/`, consúltalos antes de buscar a mano ("¿qué archivo hace esto y qué se rompe si lo cambio?") y sigue las reglas de su `AGENTS.md` para mantenerlos al día. Si el repo no dice nada, después de cambios grandes de código corre `graphify update .` (solo código, no gasta tokens).

## Antes de hacer esto, lee esto
Antes de cualquier tarea, abre `rutas-por-tarea.md` en el cerebro: una fila por tarea, con qué leer y en qué orden. La versión corta:

| Vas a… | Lee primero |
|---|---|
| Hacer marketing o contenido | `conocimiento/conocimiento.md` y luego `<proyecto>-marketing.md` del proyecto |
| Plantear un post o una campaña | el principio del gancho y la página del canal en `conocimiento/`, antes de escribir |
| Escribir o revisar código | la portada del proyecto y el mapa de código del repo; cita la regla que aplicas |
| Tomar o anotar una decisión | `_sistema/plantillas/decision.md`; nunca edites una decisión vieja, crea una nueva |
| Abrir un proyecto nuevo | `rutas-por-tarea.md` y luego `python -I _sistema/scripts/new_project.py` |
| Cualquier otra cosa, o si dudas | `rutas-por-tarea.md` y luego `index.md` |

## Cómo trabajar conmigo
- {{cómo quieres que te hablen; por ejemplo: claro, sin jerga}}.
- Si en esta sesión decido algo, se termina una tarea o llegan números, **anótalo en ese momento** en el cerebro, en la carpeta del proyecto con el que estás trabajando, siguiendo `AGENTS.md` del cerebro. No esperes al final: mis sesiones no se cierran.
- Escribe solo en la carpeta del proyecto con el que estás trabajando. Si algo afecta a otro proyecto o a la empresa, deja una línea en su `entrada.md`.
- Nunca inventes datos, cifras ni promesas. Si no hay fuente, escribe "por confirmar".

## Prohibido
- Escribir credenciales, llaves, números de cuenta o datos personales en archivos.
- {{tus prohibiciones; por ejemplo: publicar en mis redes sin mi OK}}.
