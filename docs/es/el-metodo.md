# El método: un núcleo, islas por proyecto y puentes fijos

Cómo mantener ordenado un cerebro mientras crece, en una página. Los programas que lo hacen cumplir están en [los programas](los-programas.md); cómo medir que funciona, en [la prueba de las diez tareas](prueba-de-diez-tareas.md). Versión en inglés: [the method](../the-method.md).

## El problema

Un cerebro que crece se vuelve una bola. Cada página nueva enlaza a lo que tiene cerca, los programas que "conectan" enlazan todo con todo, y un día el dibujo es una mancha donde no se distingue qué es de quién ni por dónde se entra. Le pasa igual a una persona que mira el grafo y a una IA que busca qué leer.

Casi todo el daño sale de los propios arreglos. Los típicos: una página-lista que enlaza cada elemento "para que nada quede en texto plano"; un enlace que todas las páginas tienen idéntico (no dice nada); etiquetas convertidas en enlaces a la página genérica que explica la etiqueta; enlaces de plantilla que atan cada proyecto a cada tema. Todos suman líneas y restan sentido.

## La idea

- **Un núcleo** con lo que vale para todos los proyectos: cómo funciona cada canal, principios con su fuente, cómo hacemos las cosas.
- **Una isla por proyecto**, con todo lo suyo adentro.
- **Puentes fijos:** cada isla llega al núcleo por las mismas pocas puertas, y además cita la página concreta que de verdad usa.

Ocho principios lo sostienen:

1. **La carpeta dice la capa.** No se mueven ni se marcan páginas para ordenar.
2. **Los proyectos citan al núcleo; el núcleo no cita a los proyectos a mano.**
3. **Cada proyecto es una isla con dos puertas:** su portada y su página de marketing.
4. **Se entra por tarea** ("vas a hacer X, lee Y"), con una sola tabla: `rutas-por-tarea.md`.
5. **Un enlace debe decir algo.** Lo que saldría igual en todas las páginas es texto, no enlace.
6. **La historia registra y no se dibuja.** Nadie navega por bitácoras.
7. **Lo que se puede deducir lo escribe un programa,** y una regla que no hace fallar un control no es regla: una instrucción escrita no es un control.
8. **Subir sin mudar:** cuando algo de un proyecto sirve a todos, lo general se escribe en una página nueva del núcleo; la del proyecto se queda y la cita.

La prueba del núcleo: si mañana se borra la carpeta de un proyecto, nada del núcleo se rompe; y el núcleo se puede copiar a otro negocio sin borrar nombres propios.

## Las capas

La capa de una página sale de su carpeta y de su `tipo`. No se escribe en la página.

| Capa | Qué vive | Dónde |
|---|---|---|
| Puerta | Por dónde se entra y qué leer para cada tarea | `AGENTS.md`, `index.md`, `rutas-por-tarea.md` |
| Núcleo | Lo que vale para todos los proyectos | `conocimiento/` |
| Islas | Todo lo de un proyecto | `proyectos/<proyecto>/` |
| Empresa | Decisiones de la empresa, lo que espera por el dueño | `empresa/` |
| Fuentes | Los documentos crudos; no se reescriben | `fuentes/` |
| Historia | Lo que pasó, no lo que es verdad hoy: bitácoras, buzones, pendientes, revisiones, propuestas | Se reconoce por el `tipo` de la página, no por su nombre |
| Sistema y listados | Reglas, plantillas, programas e índices generados | `_sistema/` y las páginas `*-indice` |

## La regla de enlaces

Se enlaza hacia lo más estable.

| Desde → hacia | Regla |
|---|---|
| Isla → núcleo | Permitido. Dos formas: los puentes fijos de la portada, y la cita a la página concreta que se usa (un canal, un principio) |
| Isla → fuentes, empresa | Permitido |
| Isla → otra isla | No. Se deja una línea en el buzón de la otra, o lo común sube al núcleo |
| Núcleo → fuentes | Permitido, a un documento que existe en `fuentes/`. Si la fuente vive en otro lado, se nombra como texto |
| Núcleo → empresa | Solo a decisiones |
| Núcleo → isla | Nunca a mano. Lo escribe un programa en un bloque "Dónde se aplica", y solo si una página viva de ese proyecto cita esa página del núcleo |
| Núcleo → historia | No. Una propuesta aprobada se convierte en una página nueva del núcleo |
| Historia → cualquiera | Permitido: es un registro. No cuenta ni se dibuja |
| Cualquiera → historia | Solo la de su propio proyecto o zona (un proyecto puede enlazar su bitácora y su buzón). Una excepción, un puente fijo: la página de "pendientes" del dueño |

En cinco frases: los proyectos citan al núcleo; el núcleo no cita a los proyectos a mano; una isla no enlaza a otra isla; la historia registra y no se dibuja; un enlace debe decir algo. `check.py` falla en cada una.

## Los bloques generados

Una página es escrita a mano o escrita por un programa. Cuando un programa necesita poner algo dentro de una página escrita a mano, usa dos marcas:

```text
<!-- brain:links:start -->
...lo que escribe el programa...
<!-- brain:links:end -->
```

Lo que está entre las marcas se puede borrar y volver a generar sin perder nada; lo que está fuera es de quien lo escribió. Nadie edita dentro del bloque: la próxima corrida lo revierte. **El programa se niega a escribir si falta la marca de fin**: adivinar dónde termina un bloque borraría texto escrito a mano (el control y el conector lo detectan). Los bloques tienen nombre, así que una página puede llevar más de uno sin que se pisen.

## Las partes de un proyecto

Una isla grande se dibuja dispersa si cada carpeta cuelga por su lado. Por eso cada carpeta de un proyecto es una **parte** con una **página central** que reúne todas sus páginas, y la portada del proyecto enlaza cada centro, con cuántas páginas tiene. Así cualquier página viva del proyecto queda a dos saltos como máximo de su portada. El centro es una página que escribiste tú (llamada `<proyecto>-<carpeta>`, `<carpeta>` o `README`, o la única página `indice` de la carpeta) o, si no hay, una que genera el conector. Una carpeta nueva queda amarrada la próxima vez que corre el conector, y el control falla si una carpeta no tiene centro o si una página viva queda a más de dos saltos.

## Rutas por tarea

`rutas-por-tarea.md` es la única tabla "antes de hacer X, lee Y". Una fila por tarea: qué leer, en orden, y qué tener en cuenta. Es lo que permite que una IA que nunca vio tu cerebro encuentre las decisiones que aplican sin que se lo recuerdes. Dos cosas la mantienen cierta: el control falla si una ruta apunta a una página que no existe, y avisa si las reglas de arranque (`AGENTS.md`, `_sistema/global.md`) dejan de nombrarla (`checks.required_reads` en `config.json`). Una versión corta de la tabla vive en `_sistema/global.md`, que toda sesión carga. Agrega una fila cada vez que una tarea le cueste a una IA más de lo debido encontrar el camino.

## Abrir un proyecto, de forma repetible

1. Lo decide el dueño. Mientras sea solo una idea basta la portada, y el proyecto se marca `parked`.
2. `python -I _sistema/scripts/new_project.py . <carpeta> "<Nombre>"` crea sus páginas desde las plantillas, lo registra en `config.json`, agrega su fila a `index.md` y corre el conector. Con `--check` muestra qué haría.
3. La portada recibe sus puentes fijos: rutas por tarea, conocimiento compartido, lo que espera por el dueño y su propio buzón. Nunca enlaza a otro proyecto.
4. Corre `check.py`.

## Cómo saber si funciona bien

"La mejor versión" no se puede confirmar; lo que se puede es medir seis condiciones. El objetivo de fondo: que el dueño no tenga que recordarle a una IA lo que ya está decidido.

| Condición | Qué significa | Cómo se mide |
|---|---|---|
| Se encuentra | Lo importante está a pocos pasos de donde empieza la IA | Saltos desde cada portada hasta las páginas clave (`check.py`) |
| Se lee sin pedirlo | Las reglas de arranque y las skills mandan a esas páginas | `checks.required_reads` de `config.json` (`check.py` avisa si falta alguna) |
| Se aplica | La IA usa lo decidido en su trabajo | La [prueba de las diez tareas](prueba-de-diez-tareas.md): sesiones nuevas, sin recordatorios, contando las reglas respetadas |
| Dice lo correcto | No hay dos páginas que se contradigan | Contradicciones abiertas y páginas que contradicen una decisión vigente (`check.py` avisa si una decisión "vigente" ya fue reemplazada) |
| Se sostiene | Al crecer no se desordena | Roturas provocadas que el control detecta; un proyecto nuevo queda conectado solo (`test_brain.py`) |
| Cuesta poco y sirve en todas las IA | Las instrucciones de arranque no crecen, y lo mismo funciona en Claude, Codex, Kimi, Gemini... | Tamaño de las reglas de arranque, que no debe subir de una revisión a otra; reglas y lecturas en archivos que todas las IA leen, no en funciones de una sola herramienta |

Dos límites: ninguna estructura garantiza que una IA aplique una regla que leyó, por eso se mide el resultado y no solo el orden; y mandar a leer más páginas mejora el cumplimiento pero cuesta más en cada sesión, así que se busca el punto donde leer más ya no mejora.

## Los errores que cometimos y qué enseñan

1. **Una página con cientos de enlaces en el centro.** Para que las funciones de una app dejaran de ser texto plano se creó una página-lista que enlazaba cada principio que lee cada función. Con eso casi todos los pares de principios quedaron pegados por un vecino común. *Una lista que enlaza todo no es un mapa.* El cableado de un proyecto va en su isla, y enlaza a los temas, no a cada principio.
2. **Muchas páginas apuntando a un solo índice de fuentes.** La fuente vivía en otro repo, y para que no quedara en texto plano todos los principios enlazaron un índice. El índice pasó a ser la página más grande del grafo. *Un enlace que todas las páginas tienen no dice nada; si la fuente no está en el cerebro, se deja como texto.*
3. **Los mismos enlaces de plantilla en todos los proyectos.** Un bloque puso en la página de marketing de cada proyecto los mismos temas y canales, y en cada tema un enlace de vuelta a cada proyecto. Todos los proyectos se veían iguales en el dibujo, y como cada enlace tenía su espejo, quitar un solo sentido no quitaba ni una línea. *El enlace entre un proyecto y un tema existe solo si ese proyecto de verdad lo usa: se genera como espejo de las citas reales, no de una lista.*
4. **Etiquetas que no eran enlaces.** Las fichas de contenido llevaban el gancho o el tipo como texto, y el arreglo las apuntó a la página genérica que explica el campo. *Una etiqueta se convierte en enlace a su concepto concreto, por programa; nunca a la página genérica del campo.*
5. **Reglas que solo existían en prosa.** Se provocaron cinco roturas en una copia y la revisión semanal siguió en verde en todas. *Principio 7: lo que importa lo comprueba un programa que falla, no un informe que alguien lee los lunes.*
6. **Páginas de entrada que decían lo contrario de lo decidido.** Varias páginas seguían diciendo algo que una decisión posterior había cambiado, y las dos decisiones viejas seguían como vigentes. *Cuando una decisión reemplaza a otra, el mismo día se marca la vieja como reemplazada y se corrige la frase en las páginas por las que se entra.*

## Lo que no se hace

- No se mueven ni se renombran páginas vivas para ordenar: las citan skills y repos de código por su ruta.
- No se borran bitácoras ni índices generados (páginas quedarían sin entrada): se ocultan en las vistas del grafo.
- No se corre el conector dentro del guardado automático ni antes de cada commit: escribe páginas, y eso debe ser un acto deliberado.
- No se edita la configuración del grafo de Obsidian con Obsidian abierto: la reescribe con cada zoom.

## Los importadores son un patrón opcional

En nuestro propio cerebro, una sección del núcleo se regenera desde una fuente que vive en otro lado (un mapa de conocimiento que exporta una app, un curso documentado). Esos programas no están en esta plantilla porque dependen del formato de la fuente, pero el patrón viaja: **validar antes de escribir** (un tema o una etiqueta desconocidos detienen todo sin tocar un archivo), **escribir todo de una vez, ya con sus conexiones**, llamar al conector al final y guardar una huella de la parte escrita a mano de cada página que se escribe entera, para notar después que alguien la editó a mano. Si tienes una fuente así, construye el importador sobre `brain_lib.py` y registra sus tipos de página en `config.json`.
