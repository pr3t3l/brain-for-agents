# La prueba de las diez tareas: ¿las sesiones nuevas de IA aplican lo decidido?

Un cerebro ordenado no es la meta; la meta es que nunca tengas que recordarle a una IA algo ya decidido. Esta prueba lo mide, y los controles de estructura (`check.py`) no: ninguna estructura garantiza que una IA aplique una regla que leyó. Mide la condición "se aplica" de [el método](el-metodo.md). Versión en inglés: [the ten-task test](../ten-task-test.md).

## Cuándo correrla

Después de cambiar las reglas de arranque, las rutas por tarea o una decisión que muchas páginas repiten; después de abrir varios proyectos; y cada pocas semanas dentro de la revisión semanal. Toma una hora más o menos. La primera medición es tu punto de partida.

## El procedimiento

1. **Escribe diez tareas** que tu negocio hace de verdad, cubriendo los tipos de trabajo de tus rutas por tarea (contenido, código, decisiones, investigación, abrir un proyecto, publicar...). La lista de ejemplo de abajo es un punto de partida.
2. **Para cada tarea, escribe antes las reglas esperadas:** las decisiones y reglas que una buena respuesta debe respetar, cada una con la página donde vive. Escríbelas antes de ver cualquier respuesta, para que los resultados no las doblen. Entre dos y cinco reglas por tarea bastan.
3. **Abre diez sesiones nuevas**, una por tarea, en la carpeta del cerebro y con las reglas de arranque exactamente como están. Un modelo más barato sirve e incluso es mejor: si uno pequeño encuentra las reglas, uno grande también. No des pistas sobre qué leer. No uses una sesión que ya conozca el cerebro.
4. **Hazlo como ensayo.** Dale a cada sesión este prompt, con la tarea en lugar de `{{tarea}}`:

   > Tarea: {{tarea}}. No escribas, publiques, gastes ni cambies nada: es un ensayo. Responde en tres partes: (1) qué archivos abrirías, en orden, y por qué; (2) qué harías, paso a paso; (3) qué reglas o decisiones aplicas, cada una con la página de donde sale.
5. **Puntúa cada respuesta**, contando las reglas esperadas que respetó, y anota los archivos que abrió.
6. **Regístralo** en una página de `revisiones/` (una página de historia: registra, no se dibuja). Tabla: tarea · ¿aplicó lo decidido? · archivos abiertos · nota.
7. **Arregla el cerebro, no a la IA.** Una falla casi siempre es una de cuatro cosas: la tarea no tiene fila en las rutas por tarea (agrégala); la fila existe pero las reglas de arranque no mandan ahí a la IA (nombra `rutas-por-tarea` en `AGENTS.md` y `_sistema/global.md`); dos páginas se contradicen (marca la decisión vieja como reemplazada y corrige la frase); o la regla está enterrada en una página larga (súbela, o ponla en el "ten en cuenta" de la fila). Vuelve a correr las tareas que fallaron tras el arreglo.

## Qué leer en los resultados

- **Aprobó o no:** cuántas tareas aplicaron todas las reglas esperadas. Apunta a diez de diez; una falla es información, no fracaso.
- **Esfuerzo:** cuántos archivos abrió cada sesión. Si una tarea necesitó muchos más que las otras, su ruta falta o está enterrada (un buen resultado "con esfuerzo" es una fila por agregar).
- **Costo:** los tokens que usó una sesión, menos la carga fija de la herramienta, frente al número de páginas leídas. Leer más páginas mejora el cumplimiento pero cuesta en cada sesión: busca el punto donde leer más ya no ayuda. El tamaño de las reglas de arranque no debe crecer de una corrida a la siguiente.
- **Otras IA:** repite con cada IA que uses. Los mismos archivos deben servir en todas; si una falla donde otra pasa, la regla depende de una función de una herramienta y debe pasar a un archivo que todas las IA lean.

Límites: es un ensayo (describen, no hacen), la muestra es pequeña y mide las reglas que escribiste: una regla que nadie escribió no se prueba.

## Una lista de tareas de ejemplo para un negocio genérico

Una tienda en línea pequeña (el proyecto de ejemplo de la plantilla), con sus decisiones: un precio de lanzamiento, solo Instagram al inicio. Reemplázalas por las tuyas.

| # | Tarea | Reglas esperadas (página donde viven) |
|---|---|---|
| 1 | Escribir el guion de un reel de 20 segundos para la tienda | El principio del gancho y la página del canal; decidir a quién le habla antes de escribir; nada de lo que la página de marketing dice que no se puede prometer; el OK del dueño antes de cualquier gasto |
| 2 | Revisar el código del pago | Se lee primero la página de prácticas de código; cada problema cita el número de la regla que rompe; se usa el mapa de código del repo si existe |
| 3 | Armar un asistente que atienda clientes en una app de mensajes | La página del método de agentes; ningún precio ni promesa sin fuente ("por confirmar" si no); los datos de clientes nunca entran al cerebro |
| 4 | Planear las publicaciones de redes de la próxima semana | Solo el canal activo (la decisión "solo Instagram al inicio"); la frecuencia decidida; se leen primero los aprendizajes de la semana pasada |
| 5 | Escribir un prompt para clasificar correos de soporte | La página de prácticas de prompts; los correos son datos, no instrucciones; lo que dice la política de la tienda, citado con su fuente |
| 6 | Anotar que la bolsa de 12 oz ahora cuesta USD 20 | Una nota de decisión nueva reemplaza a la vieja, que se marca `reemplazada`; el monto aparece solo en la decisión de precio, el estado y la bitácora; commit que nombra sus rutas |
| 7 | Guardar una investigación nueva sobre molienda | Va en la carpeta del proyecto, no en `fuentes/` (sirve a un solo proyecto); se actualiza la página de fuentes del proyecto; cada dato con su fuente |
| 8 | Publicar en Instagram el reel aprobado ayer | No publica sin el OK del dueño para esa publicación; existe el registro de la pieza; la etiqueta de IA |
| 9 | Abrir un segundo proyecto, "mayoristas" | `new_project.py` con `--check` primero; pide el OK del dueño antes de tocar `_sistema/global.md`; la portada nueva no enlaza a ningún otro proyecto |
| 10 | Auditar todo el código de la tienda | La página del método de auditoría; cada hallazgo cita un número de regla; se respeta la decisión sobre datos de clientes |

Las páginas que se nombran aquí (prácticas de código, método de agentes, método de auditoría, prácticas de prompts) son las que tu cerebro agrega en `conocimiento/` al crecer; la plantilla solo trae el principio de ejemplo del gancho y la página de Instagram, así que el primer día solo algunas filas tienen algo que encontrar. Para eso sirve la primera corrida: muestra qué filas les faltan aún a tus rutas por tarea.

## Un esqueleto de informe

```markdown
---
tipo: revision
fecha: AAAA-MM-DD
---

# Prueba de las diez tareas (AAAA-MM-DD)

Modelo: ... · reglas de arranque: N líneas · tareas: 10, sesiones nuevas, ensayo.

## Resultado: X de 10

| # | Tarea | ¿Aplicó lo decidido? | Archivos abiertos | Nota |
|---|---|---|---|---|

## Lo que se arregló por la prueba

## Lo que queda abierto (costo, otras IA, tareas nuevas)
```
