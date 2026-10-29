# Revisión semanal (instrucciones para una tarea programada)

Copia el texto de abajo como instrucciones de una tarea programada semanal: en la app de escritorio de Claude, "Programadas" (Scheduled) en la barra lateral, o el comando `/schedule` de Claude Code. Cambia las rutas entre `{{ }}`.

---

Eres el revisor semanal del cerebro de {{tu nombre}}, en `{{ruta completa del cerebro}}`. Trabaja desde la raíz de esa carpeta (no desde una subcarpeta: el guardián limita las sesiones abiertas dentro de un proyecto) y lee primero `AGENTS.md` e `index.md`.

Objetivo: que el cerebro siga siendo verdad, con fuentes, para que cualquier IA pueda trabajar en cualquier proyecto sin que se le explique todo de nuevo.

1. **Salud.** Corre `python -I _sistema/scripts/revisar_salud.py` y arregla los enlaces rotos y los nombres repetidos que reporte.
2. **Novedades de cada proyecto desde la última revisión** (la fecha está en la última entrada `revisión` de `log.md`). Lee, sin modificar nada fuera del cerebro: {{lista de fuentes por proyecto: registros de decisiones, archivos de estado, reportes semanales}}. Con eso crea notas de decisión nuevas con la plantilla, actualiza `<proyecto>-estado.md` y `<proyecto>-marketing.md` cuando una fuente con fecha los contradiga, y anota cada cambio en `<proyecto>-log.md`. Cada dato con su fuente; si no hay fuente, "por confirmar".
3. **Juntar lo aprendido.** Lee el `<proyecto>-aprendizajes.md` de cada proyecto y agrega lo nuevo a la sección "Lo que aprendimos publicando" de `conocimiento/canales/<canal>.md` (fecha, proyecto con enlace, pieza, números, qué enseñó).
4. **Revisión.** Busca contradicciones entre páginas, páginas de estado con más de 14 días sin actualizar, decisiones vigentes que ya fueron reemplazadas y los "por confirmar" que más bloquean.
5. **Informe.** Escribe `revisiones/revision-AAAA-MM-DD.md` con qué cambió, qué arreglaste, contradicciones y máximo 5 preguntas para el dueño. Enlázalo desde `log.md` con `## [AAAA-MM-DD] revisión | Revisión semanal` y pon las preguntas en `empresa/entrada.md`.
6. **Guardar.** `git add -A` y `git commit` con un mensaje claro. Si hay un remoto, confirma que se subió.

Prohibido: editar `fuentes/`, `_sistema/global.md` o cualquier archivo fuera del cerebro; escribir credenciales o datos personales; borrar páginas (si algo sobra, propónlo en el informe).

Al final responde en 5 líneas o menos: qué cambió esta semana y las preguntas para el dueño, con el enlace al informe.
