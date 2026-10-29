# Cerebro: reglas para agentes

Este es el cerebro: lo que sabemos, decidimos y aprendemos de cada proyecto. No hay código aquí. El código vive en las carpetas de proyectos de `_sistema/config.json`.

Sigue el método "LLM Wiki" de Andrej Karpathy: fuentes crudas que no se editan, páginas que la IA mantiene y estas reglas.

## Qué hay dónde

| Carpeta | Qué contiene | ¿Se edita? |
|---|---|---|
| `index.md` | La portada: un mapa de todo el cerebro | Sí, al crear o mover páginas |
| `log.md` | La bitácora general (solo se agrega al final) | Solo agregar |
| `_sistema/` | `global.md` (reglas para todas las IA), `plantillas/`, `scripts/`, `config.json` | Solo con OK del dueño |
| `conocimiento/` | Lo que sirve a todos los proyectos (por ejemplo, cómo funciona cada red social), con su fuente | Desde la raíz del cerebro |
| `fuentes/` | Copias crudas de documentos | **No.** Se leen y se citan, nunca se editan |
| `proyectos/<proyecto>/` | Todo lo de un proyecto: `<proyecto>.md` (su portada), `<proyecto>-estado.md`, `<proyecto>-marketing.md`, `<proyecto>-aprendizajes.md`, `<proyecto>-fuentes.md`, `<proyecto>-log.md` y `decisiones/` | Sí, solo desde una sesión de ese proyecto |
| `empresa/` | Lo que cruza todos los proyectos | Sí, desde una sesión de empresa; el resto solo agrega a `entrada.md` (buzón) |
| `revisiones/` | Los informes de la revisión semanal | La revisión semanal |

## Cómo trabajar

1. **Al empezar:** lee `index.md` y, del proyecto con el que trabajas, su portada (`<proyecto>.md`) y su estado (`<proyecto>-estado.md`).
2. **Escribe en el momento, no al final.** Cuando el dueño decide algo, cuando se termina una tarea o cuando llegan números, actualiza en ese mismo momento la página que corresponde y agrega una línea a `<proyecto>-log.md`. Las sesiones no se cierran: no esperes al final.
3. **Una decisión = una nota** en `proyectos/<proyecto>/decisiones/`, con la plantilla `_sistema/plantillas/decision.md`. Nunca edites una decisión vieja: si cambia, crea una nueva y marca la vieja como `reemplazada`.
4. **Cada dato con su fuente.** Escribe de dónde sale (ruta, enlace o "lo dijo el dueño el AAAA-MM-DD"). Si no hay fuente, escribe "por confirmar". Nunca inventes datos, cifras ni promesas.
5. **Escribe solo en la carpeta de tu proyecto.** Si tu trabajo afecta a otro proyecto o a la empresa, agrega una línea en el `entrada.md` de ese lugar (fecha, de dónde vienes, qué cambió, qué hay que decidir) y no toques nada más.
6. **Enlaza con `[[...]]`** usando la ruta completa (por ejemplo `[[proyectos/tienda/tienda-marketing|marketing]]`), para que el mapa de Obsidian muestre las conexiones.
7. **Nombres únicos.** Ningún archivo repite el nombre de otro (salvo las decisiones, que llevan fecha). Las páginas de un proyecto empiezan con el nombre del proyecto. Solo `index.md` y `log.md` de la raíz usan esos nombres.
8. **Formato de la bitácora:** `## [AAAA-MM-DD] tipo | título`, con tipo `decisión`, `ingesta`, `publicación`, `aprendizaje`, `revisión` o `cambio`.

## Rutinas

- **Ingerir una fuente:** guarda el original en `fuentes/` (o enlázalo si ya vive en un repo), resume lo útil en las páginas que toca y anótalo en la bitácora.
- **Consultar:** responde citando páginas. Si la respuesta vale la pena, guárdala como página nueva.
- **Lo aprendido publicando:** cada proyecto lo anota en su `<proyecto>-aprendizajes.md` (fecha, canal, pieza, números, qué enseñó). La revisión semanal lo junta en `conocimiento/canales/`.
- **Revisión semanal:** ver `_sistema/revision-semanal.md`.

## Lo que se cuida solo

- **Reglas globales:** `_sistema/global.md` se copia a `~/.claude/CLAUDE.md` y `~/.codex/AGENTS.md` después de cada commit (`_sistema/scripts/sync_global.py`). Edita solo `global.md`.
- **Guardián (Claude Code):** una sesión abierta dentro de un proyecto (en su carpeta de código o en `cerebro/proyectos/<proyecto>`) solo puede escribir en `cerebro/proyectos/<proyecto>/` y en cualquier `entrada.md`. No cubre comandos de terminal ni a Codex: ahí vale la regla 5.
- **Aviso (Claude Code):** si en una respuesta se cambiaron archivos de un proyecto y no se anotó nada, Claude recibe un recordatorio (como máximo uno cada 30 minutos por sesión).
- **Pruebas:** `python -I _sistema/scripts/test_guards.py`. **Salud:** `python -I _sistema/scripts/health_check.py`.

## Prohibido

Credenciales, llaves, contraseñas, números de cuenta o datos personales. Agrega aquí tus propias prohibiciones.
