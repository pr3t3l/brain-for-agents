# El cerebro y los mapas de código: dos memorias, anidadas

El cerebro responde **"¿qué sabemos y qué decidimos?"**. Un mapa de código responde **"¿en qué parte del código pasa esto, y qué se rompe si lo cambio?"**. Son memorias distintas, y cada una vive en su lugar. Las reglas globales las unen, así que todo agente sabe que existen las dos.

```text
reglas globales (~/.claude/CLAUDE.md, ~/.codex/AGENTS.md)   ← se cargan en todas las sesiones, en cualquier carpeta
 │   "el cerebro está aquí; si el repo tiene mapa de código, úsalo primero y mantenlo al día"
 │
 ├── cerebro/                               ← conocimiento y decisiones (Markdown, su propio repo)
 │     proyectos/tienda/tienda-fuentes.md      dice dónde está el repo del proyecto y su mapa
 │
 └── Proyectos/tienda/                      ← el repo propio del proyecto
       AGENTS.md                               cómo consultar su mapa y cuándo reconstruirlo
       graphify-out/                           el mapa del código: se reconstruye, nunca se edita a mano
```

## Por qué dos, y no un solo mapa gigante

- **El código cambia cada hora; las decisiones no.** El mapa de código se reconstruye desde el código. El cerebro lo escribe la IA en el momento en que se decide o se aprende algo.
- **Los mapas de código son baratos y exactos.** [Graphify](https://github.com/safishamsi/graphify) lee el código con tree-sitter (sin llamar a ningún modelo), así que reconstruir un mapa de solo código no gasta tokens.
- **No corras Graphify sobre el cerebro.** Graphify también puede leer documentos, pero lo hace con Claude (gasta tokens), y los enlaces `[[...]]` del cerebro ya forman el mapa que ves en Obsidian. Pasarle tus notas duplica el cerebro.
- **Cada mapa se queda con su código.** Se reconstruye dentro del repo del proyecto, así que cada rama y cada worktree tiene el mapa de su propio código.

## Montar el mapa de un proyecto (unos 10 minutos)

1. Instala Graphify (Python 3.10+):
   ```bash
   pip install graphifyy && graphify install
   ```
   En Windows, si el control de aplicaciones bloquea el `graphify.exe` que genera, córrelo como `python -m graphify …`.
2. En el repo del proyecto, construye un mapa **solo de código**:
   ```bash
   python -m graphify extract . --code-only
   ```
   (Dentro de Claude Code también puedes usar `/graphify .`.) Crea `graphify-out/` con `graph.json`, `graph.html` (un mapa interactivo que abres en el navegador) y `GRAPH_REPORT.md`.
3. Agrega `graphify-out/` al `.gitignore` del repo: el mapa se regenera, no se guarda en git. Agrega un `.graphifyignore` para registros, reportes de QA y cualquier cosa grande o privada.
4. Mantenlo al día. Corre `graphify update .` después de cambios grandes de código (solo código, no gasta tokens), o instala su hook de git (`graphify hook install`) para que se reconstruya en cada commit.
5. Avísales a los agentes. Agrega tres líneas al `AGENTS.md` del repo:
   ```markdown
   ## Mapa del código
   Para "¿dónde está esto?" y "¿qué se rompe si lo cambio?", consulta el mapa de Graphify antes de buscar a mano:
   `python -m graphify explain <SimboloExacto> --graph graphify-out/graph.json` o `affected <SimboloExacto> --depth 1`.
   Las conexiones son pistas, no pruebas: lee el código y corre las pruebas. Reconstrúyelo después de cambios grandes.
   ```
6. Anota el mapa en la página del proyecto en el cerebro (`<proyecto>-fuentes.md`), para que un agente que trabaje desde el cerebro también sepa que existe.

Las reglas globales de `plantilla/_sistema/global.md` ya traen la instrucción general ("si el repo tiene `MAPS.md` o `graphify-out/`, úsalo primero y sigue sus reglas"); los pasos 5 y 6 agregan el detalle de cada proyecto.

## Consejos del uso real

- **Pregunta primero con símbolos exactos** (`explain prepareOrder`, `affected prepareOrder --depth 1`). Las preguntas amplias arrastran cientos de nodos.
- **Las conexiones del mapa son pistas, no pruebas** de lo que pasa al ejecutar. Lee el código y corre las pruebas.
- **Fija la versión de Graphify** en un pequeño script, para que todos los agentes obtengan el mismo mapa.
- **El instalador de Graphify agrega una línea a `~/.claude/CLAUDE.md`.** No hay problema: la sincronización del cerebro solo reemplaza su propio bloque en ese archivo (entre las marcas `brain:global-copy`) y conserva todo lo demás.

## Más allá: varios mapas que se revisan solos

En nuestro producto más grande, el mapa de código es uno de cuatro mapas enlazados entre sí: **código** (Graphify), **datos** (dónde se guarda cada dato del negocio y qué paso lo usa), **contratos de las llamadas a la IA** (qué recibe cada llamada y qué debe devolver) y **conocimiento** (principios de la investigación, cada uno con su pasaje fuente y su huella). Un comando muestra, para una llamada a la IA, sus principios, sus datos, su código y lo que se rompería. Dos reglas los mantienen verdaderos:

- **Cada cambio actualiza su mapa en el mismo commit.** Si un commit cambia el prompt o los campos de una llamada, actualiza su contrato, o dice por qué el contrato sigue valiendo.
- **Una revisión de frescura corre en la integración continua y en un hook de Claude Code.** Falla cuando un mapa ya no coincide con el código.

No necesitas eso para empezar. Un cerebro y un mapa de Graphify por repo te llevan casi todo el camino.
