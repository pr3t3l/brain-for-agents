# Cerebro para agentes

**Un solo lugar donde Claude Code, Codex y tú guardan todo lo que saben de tus proyectos, que se mantiene al día solo y que ninguna IA puede desordenar.**

[English version](README.en.md)

Si trabajas con varias IA en varios proyectos, ya conoces el problema: cada chat empieza de cero, le vuelves a explicar todo, las decisiones quedan enterradas en conversaciones que nadie vuelve a leer, y cada herramienta guarda su propia "memoria" en un lugar distinto.

Este repo es la plantilla y la guía de cómo lo resolví para mi empresa, con varios productos en paralelo y agentes de Claude Code y Codex trabajando a la vez. Está pensado para que cualquiera lo copie en una tarde.

## La idea de la que parte

Andrej Karpathy publicó [el patrón "LLM Wiki"](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): en vez de que la IA busque en tus documentos cada vez, la IA **escribe y mantiene una wiki en Markdown**. Tiene tres capas (fuentes crudas que no se tocan, páginas que la IA mantiene y un archivo de reglas), tres rutinas (ingerir, consultar, revisar) y un índice y una bitácora. Obsidian sirve para mirarla. Lee el original: es corto y muy bueno.

## Lo que este repo le agrega

El patrón de Karpathy está pensado para **una wiki, una persona y una IA**. Al usarlo con varios proyectos y varios agentes a la vez, aparecieron problemas que el patrón no resuelve. Esto es lo que les agregamos:

| Problema real | Lo que hace este cerebro |
|---|---|
| Cada IA arranca sin saber nada | **Reglas globales** que Claude Code y Codex cargan en **todas** las sesiones, en cualquier carpeta, y que se copian solas desde el cerebro en cada commit |
| Un chat de un proyecto escribe en otro proyecto | **Guardián:** un hook de Claude Code que bloquea cualquier escritura en la carpeta de otro proyecto |
| "Anótalo al final de la sesión", pero las sesiones nunca se cierran | **Escribir en el momento**, y un **aviso** que le recuerda a la IA anotar cuando cambió archivos y no anotó nada |
| Las decisiones de cada proyecto quedan sueltas | **Una nota por decisión**, en la carpeta de su proyecto, y **una tabla en vivo** (Obsidian Bases) que las junta todas |
| Muchas páginas llamadas `index` o `marketing` en Obsidian | **Nombres únicos:** cada página lleva el nombre de su proyecto |
| Nadie revisa que la wiki siga siendo verdad | **Revisión semanal** programada que contrasta con las fuentes, arregla y te deja máximo 5 preguntas |
| Si se daña el computador, se pierde | **Respaldo en GitHub** con cada commit |
| Lo que aprende un proyecto no le sirve a otro | **Aprendizajes por proyecto** que la revisión semanal junta por canal |

No es "mejor que Karpathy": es su idea, más la capa de operación que hace falta cuando hay varios proyectos y varios agentes trabajando a la vez.

## Cómo se ve

```text
cerebro/                         ← una bóveda de Obsidian y un repo de git (privado)
  AGENTS.md  CLAUDE.md           ← las reglas del cerebro
  index.md   log.md              ← la portada y la bitácora
  decisiones.base                ← tabla en vivo con todas las decisiones
  _sistema/
    global.md                    ← reglas que TODA IA carga en cualquier carpeta
    config.json                  ← dónde viven tus proyectos
    plantillas/  scripts/  revision-semanal.md
  conocimiento/                  ← lo que sirve a todos: canales, principios con fuente
  fuentes/                       ← documentos crudos, no se editan
  proyectos/
    tienda/                      ← un proyecto: tienda.md, tienda-estado.md, tienda-marketing.md,
      decisiones/                  tienda-aprendizajes.md, tienda-fuentes.md, tienda-log.md
  empresa/   entrada.md          ← lo que cruza proyectos y el buzón de avisos
  revisiones/                    ← informes semanales
```

El código **no** vive aquí. Cada proyecto sigue en su propia carpeta y su propio repo; el cerebro guarda lo que sabemos, decidimos y aprendemos.

## Instalarlo (unos 20 minutos)

Necesitas Python 3.11 o más nuevo, git, y Claude Code y/o Codex. Obsidian es opcional, solo para mirar.

1. **Copia la plantilla** a donde quieras tu cerebro, por ejemplo `Documentos/cerebro`:
   ```bash
   git clone https://github.com/pr3t3l/cerebro-para-agentes.git
   cp -r cerebro-para-agentes/plantilla ~/Documentos/cerebro
   ```
2. **Edita `_sistema/config.json`:** en `carpetas_de_proyectos`, la carpeta donde viven tus proyectos (cada subcarpeta es un proyecto). Si tienes una carpeta de empresa, ponla en `carpetas_de_empresa`.
3. **Edita `_sistema/global.md`:** quién eres, tus proyectos, la ruta del cerebro y tus prohibiciones. Es lo que toda IA va a leer siempre, así que mantenlo corto.
4. **Prueba los guardianes:** `python -I _sistema/scripts/probar_guardianes.py` debe decir `TODO BIEN`.
5. **Instala:** primero `python -I _sistema/scripts/instalar.py --dry-run` para ver qué va a cambiar, y luego sin `--dry-run`. Respalda cada archivo que toca (`*.antes-del-cerebro`).
6. **Respaldo (recomendado):** crea un repo **privado** en GitHub y conéctalo (`git remote add origin ...`). Desde ahí cada commit se sube solo.
7. **Revisión semanal (recomendado):** crea una tarea programada con el texto de `_sistema/revision-semanal.md`.
8. Abre la carpeta como bóveda en Obsidian, borra el proyecto de ejemplo `proyectos/tienda` y crea el tuyo.

Abre una sesión **nueva** de Claude Code o Codex: las reglas globales se cargan al iniciar.

## Cómo se usa en el día a día

**Abre el chat donde está lo que vas a cambiar:**

| Qué vas a hacer | Abre el chat en |
|---|---|
| Programar o arreglar un proyecto | La carpeta del código del proyecto |
| Marketing o decisiones de **un** proyecto | `cerebro/proyectos/<proyecto>` |
| Algo que cruza varios proyectos | La raíz del cerebro |

Trabaja normal. Cuando decidas algo o llegue un número, la IA lo anota en ese momento. Si se le olvida, el aviso se lo recuerda. Cada semana, la revisión pone todo al día y te deja sus preguntas.

## Más

- [Cómo funciona por dentro](docs/como-funciona.md), con sus límites honestos.
- [Preguntas frecuentes](docs/preguntas.md): todas las que me hice armándolo.

## Créditos y licencia

Idea base: [LLM Wiki de Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Armado por Alfredo Pretel (Pretel Ventures) con Claude Code. Licencia MIT: úsalo, cópialo y mejóralo.
