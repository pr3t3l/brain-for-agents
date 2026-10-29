# Cómo funciona por dentro

## 1. Tres capas, como en el patrón de Karpathy

- **Fuentes** (`fuentes/`): documentos crudos (artículos, cursos, investigaciones). La IA los lee y los cita; nunca los edita.
- **Páginas** (`proyectos/`, `conocimiento/`, `empresa/`): lo que la IA escribe y mantiene. Cada dato lleva su fuente o dice "por confirmar".
- **Reglas** (`AGENTS.md` del cerebro y `_sistema/global.md`): cómo se trabaja.

## 2. Por qué el cerebro vive separado del código

Lo primero que intenté fue poner el conocimiento dentro del repo de cada proyecto. Tiene dos problemas:

- **Se copia muchas veces.** Si trabajas con worktrees (una copia del repo por cada agente o rama), cada documento aparece tantas veces como worktrees tengas. En mi caso, una bóveda de Obsidian sobre la carpeta de código tenía unas 39.000 notas, casi todas copias o librerías.
- **Vive en ramas.** Una decisión escrita en una rama no la ve nadie hasta que esa rama se une a la principal.

La regla que salió de ahí: **lo que cambia junto con el código va en el código** (mapas del código, contratos, specs que verifica la integración continua); **lo que sabemos o decidimos va en el cerebro**.

## 3. Cómo cargan las reglas Claude Code y Codex

Esto lo comprobé con pruebas, no solo leyendo la documentación:

- **Claude Code** lee los `CLAUDE.md` de la carpeta donde abres la sesión **y de todas las carpetas de arriba, hasta la raíz del disco**, aunque haya repos en medio. Además lee siempre `~/.claude/CLAUDE.md`, abras donde abras.
- **Codex** lee `~/.codex/AGENTS.md` y luego los `AGENTS.md` desde la **raíz del repo** hasta tu carpeta. **No sube más allá de la raíz del repo.** Lo probé con dos carpetas: una "empresa" con una palabra secreta y un repo "proyecto" adentro con otra. Codex solo vio la del proyecto.

Por eso las reglas globales van en los dos archivos personales (`~/.claude/CLAUDE.md` y `~/.codex/AGENTS.md`), que se cargan siempre. Para no mantener dos copias a mano, la verdad vive en `cerebro/_sistema/global.md` y un hook de git (`post-commit`) la copia a los dos lugares cada vez que guardas el cerebro.

Dentro del cerebro, `CLAUDE.md` contiene solo `@AGENTS.md`: así Claude y Codex leen el mismo archivo de reglas.

## 4. El guardián

Es un hook `PreToolUse` de Claude Code (`_sistema/scripts/guardian.py`). Antes de cada escritura de Claude, mira dos datos: **en qué carpeta se abrió la sesión** y **qué archivo quiere escribir**.

- Si el archivo no está en el cerebro: deja pasar (solo vigila el cerebro).
- Si la sesión se abrió en un proyecto (su carpeta de código o `cerebro/proyectos/<proyecto>`): solo deja escribir en `cerebro/proyectos/<proyecto>/` y en cualquier `entrada.md`.
- Si se abrió en una carpeta de empresa o en `cerebro/empresa`: solo en `cerebro/empresa/`.
- Si se abrió en la raíz del cerebro o en cualquier otro lado: sin límite.

Cuando bloquea, Claude recibe la razón y la propuesta: "deja una línea en el `entrada.md` de ese lugar".

## 5. El aviso

Es un hook `Stop` de Claude Code (`_sistema/scripts/reminder.py`), que corre al terminar cada respuesta. Claude Code guarda cada conversación como un archivo en tu disco y le pasa al hook su ubicación. El script, **sin usar ningún modelo**:

1. busca tu último mensaje;
2. lista los archivos que Claude editó desde ahí;
3. si editó archivos del proyecto y ninguno en `cerebro/proyectos/<proyecto>/`, le devuelve a Claude un recordatorio;
4. si no hubo una decisión, una tarea terminada o números, Claude termina sin hacer nada.

Salta como máximo una vez cada 30 minutos por sesión, solo en sesiones de proyecto, y nunca dos veces seguidas en el mismo final de respuesta.

## 6. Decisiones como notas y una tabla en vivo

Cada decisión es un archivo con datos arriba (`tipo: decision`, `proyecto`, `fecha`, `estado`, `fuente`). `decisiones.base` es una vista de Obsidian Bases que muestra todas las notas con `tipo: decision`, agrupadas por proyecto. Crece sola: cada decisión nueva aparece en la tabla.

Una decisión nunca se edita: si cambia, se crea otra y la vieja se marca `reemplazada`.

## 7. La revisión semanal

Es una tarea programada de Claude (instrucciones en `_sistema/revision-semanal.md`) que corre desde la raíz del cerebro:

- revisa la salud (enlaces rotos, nombres repetidos);
- lee las fuentes de cada proyecto y actualiza estados y decisiones;
- junta lo aprendido de cada proyecto en las páginas de canal;
- deja un informe con máximo 5 preguntas para ti;
- guarda y sube todo.

## 8. Idioma y nombres de carpetas

`_sistema/config.json` define el idioma (`language`: `es` o `en`) y los nombres de las carpetas (`layout`). Los scripts son idénticos en la plantilla en inglés (`template/`) y en la de español (`plantilla/`); solo cambia la configuración. Así puedes renombrar carpetas sin tocar código.

## 9. ¿Cuánto cuesta en tokens?

- **Los scripts no gastan tokens:** son Python en tu computador.
- **El guardián**, cuando bloquea, le pasa a Claude un mensaje de unas 50 palabras.
- **El aviso**, cuando salta, provoca una vuelta extra de Claude.
- **Las reglas globales** (unos 500 tokens) se cargan al iniciar cada sesión.
- **Lo que más gasta es la revisión semanal**, que es una sesión completa una vez por semana. Y, claro, cuando una IA lee el cerebro para trabajar, que es justamente el propósito.

## 10. Límites honestos

- **El guardián y el aviso son de Claude Code.** Codex no tiene un equivalente que haya podido confirmar: ahí la protección es la regla escrita, más `writable_roots` para que pueda escribir en el cerebro.
- **El guardián solo vigila las herramientas de edición de Claude**, no los comandos de terminal.
- **Las sesiones ya abiertas** no cargan las reglas globales hasta que abres una nueva. El guardián y el aviso sí se aplican en vivo.
- **Lo probé en Windows** (con Git Bash). Los scripts están escritos para Mac y Linux también, pero ahí no los he probado en uso real.
- **Si trabajas para un empleador**, no mezcles su información en tu cerebro personal: arma un segundo cerebro con la misma plantilla, en un lugar que tu empleador permita.
