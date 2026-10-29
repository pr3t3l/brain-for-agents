# Preguntas frecuentes

Estas son las preguntas que me hice mientras lo armaba, con las respuestas que encontramos probando.

## Sobre la idea

**¿Qué es la técnica "LLM Wiki" de Karpathy?**
Que la IA no busque en tus documentos cada vez, sino que escriba y mantenga una wiki en Markdown que crece con cada fuente nueva. Tiene tres capas (fuentes crudas, páginas que mantiene la IA y reglas), tres rutinas (ingerir, consultar, revisar) y un índice y una bitácora. [El original](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

**¿Para qué sirve Obsidian aquí?**
Para mirar. El cerebro es una carpeta con archivos Markdown; Obsidian la muestra con enlaces, un mapa de conexiones y tablas. La IA no necesita Obsidian: lee y escribe los archivos directamente.

**¿Qué es Graphify? ¿Es una app como Obsidian?**
No. Es un programa de línea de comandos que convierte una carpeta de código en un mapa de conocimiento (archivos HTML que abres en el navegador, más un reporte). Sirve para el **código** ("¿qué archivo hace esto y qué se rompe si lo cambio?"). El cerebro sirve para **lo que sabemos y decidimos**. Se complementan.

## Sobre la estructura

**¿Un cerebro global para toda la empresa o uno por proyecto?**
Uno solo para todo, con una carpeta por proyecto. Así los proyectos se pueden enlazar entre sí, ves todas las decisiones en una tabla y hay un solo repo que respaldar. Si algún día un proyecto tiene socios, su carpeta se separa sin romper nada.

**Pero si uso un cerebro global, ¿no tengo que abrir todos los chats desde ahí?**
No. Las reglas globales se cargan en todas las sesiones, abras donde abras. Abres el chat en tu proyecto y la IA igual sabe dónde está el cerebro.

**¿Y si un chat escribe en el proyecto equivocado?**
Las IA siguen bien las reglas, pero no lo dejamos a la confianza: el guardián bloquea cualquier escritura de Claude en la carpeta de otro proyecto. Si un trabajo afecta a otro proyecto, la IA deja una línea en su buzón (`entrada.md`).

**¿Por qué no poner el conocimiento dentro del repo de cada proyecto?**
Porque se copia en cada worktree y vive en ramas: una decisión escrita en una rama no la ve nadie hasta que se une. Lo que cambia junto con el código va en el código; lo que sabemos va en el cerebro.

**Mi bóveda de Obsidian se ve llena de puntos sueltos. ¿Por qué?**
Probablemente abriste como bóveda una carpeta de código: worktrees, `node_modules`, archivos generados. Excluirlos ayuda, pero lo que queda muestra la verdad: los documentos casi no se enlazan entre sí. Un cerebro aparte, con enlaces `[[...]]`, se ve como un mapa conectado.

**Tengo muchas páginas llamadas `index`, `marketing` o `log`. ¿Las renombro?**
Sí. Obsidian muestra el nombre del archivo en pestañas, búsquedas y el mapa. La regla: cada página empieza con el nombre de su proyecto (`tienda.md`, `tienda-marketing.md`), y solo `index.md` y `log.md` de la raíz usan esos nombres.

**Cada proyecto tiene sus propias decisiones. ¿Cómo las veo todas juntas?**
Cada decisión es una nota en la carpeta de su proyecto, y `decisiones.base` (Obsidian Bases) las muestra todas en una tabla agrupada por proyecto. Crece sola.

## Sobre Claude Code y Codex

**¿Claude Code lee los `CLAUDE.md` de las carpetas de arriba? ¿Hasta dónde?**
Sí, hasta la raíz del disco: de `C:\...\proyectos\tienda\app` leería los de `app`, `tienda`, `proyectos`, y así hasta `C:\`. Aunque cada proyecto sea su propio repo.

**¿Y Codex?**
Codex se detiene en la raíz del repo. Por eso las reglas globales van en `~/.codex/AGENTS.md`, que siempre se carga.

**¿Cuándo abro el chat en el cerebro y cuándo en el proyecto?**
Donde está lo que vas a cambiar. ¿Código? En la carpeta del proyecto. ¿Marketing o decisiones de un proyecto? En `cerebro/proyectos/<proyecto>`. ¿Algo que cruza proyectos? En la raíz del cerebro.

**¿Las sesiones que ya tenía abiertas toman las reglas nuevas?**
El guardián y el aviso sí, porque la configuración de Claude Code se aplica en vivo. Las reglas globales no: se leen al iniciar la sesión. Abre una nueva, o dile a la vieja que lea `cerebro/_sistema/global.md`.

## Sobre mantenerlo al día

**Me dicen "actualiza al cerrar la sesión", pero yo nunca cierro sesiones: las uso hasta que se compactan o fallan.**
Por eso la regla es **anotar en el momento**: cuando decides algo, cuando se termina una tarea o cuando llegan números. Y el aviso se lo recuerda a la IA si se le pasó.

**¿Dónde se aplican las reglas?**
`cerebro/AGENTS.md`, en las sesiones abiertas dentro del cerebro. `_sistema/global.md` (copiado a tus archivos personales), en todas las sesiones. El guardián y el aviso, en `~/.claude/settings.json`.

**¿Cómo sabe el aviso que editaste archivos, o que ya anotaste? ¿Lee la conversación?**
Lee el archivo donde Claude Code guarda la conversación, pero sin IA: busca las líneas de "editó tal archivo" desde tu último mensaje. Si alguna está en la carpeta del proyecto en el cerebro, ya anotaste.

**¿Cuándo salta el aviso? ¿Siempre?**
No. Solo si se cumplen cuatro cosas a la vez: el chat es de un proyecto, en esa respuesta se editaron archivos del proyecto, no se anotó nada en el cerebro y no avisó en los últimos 30 minutos.

**¿Los scripts gastan tokens?**
Correrlos, no: son Python local. Gasta un poco cuando el guardián bloquea o el aviso salta, las reglas globales al iniciar cada sesión, y sobre todo la revisión semanal.

**¿Se va desactualizando?**
Para eso está la revisión semanal: contrasta con las fuentes de cada proyecto, actualiza, junta lo aprendido y te deja máximo 5 preguntas.

## Sobre servidores y trabajo

**¿Necesito un servidor o un MCP propio para la memoria?**
Para empezar, no. Yo tenía un servidor con base de datos y búsqueda por significado, y se fue quedando atrás: la IA tenía que acordarse de llamarlo, y faltaban proyectos. El Markdown en git se carga solo, va en el mismo commit que el cambio y no cuesta nada. Un servidor solo agrega búsqueda por significado o acceso desde el teléfono, y para leerlo desde el teléfono basta GitHub.

**¿Puedo usar lo mismo en mi trabajo de empleado?**
El método, sí. Los datos, no los mezcles: arma un segundo cerebro con la misma plantilla, en un lugar que tu empleador permita. Lo que se comparte son las técnicas, no la información.
