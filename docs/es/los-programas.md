# Los programas: cómo encajan el conector, el control, los ganchos y el guardado automático

Todo vive en `_sistema/scripts/` (`_system/scripts/` en la plantilla en inglés) y se corre con `python -I`, que deja fuera de la ruta de imports de Python los archivos sueltos. Son Python local: **no gastan tokens**. El método que hacen cumplir está en [el método](el-metodo.md). Versión en inglés: [the programs](../the-programs.md).

## Quién hace qué

| Programa | Qué hace | ¿Escribe? |
|---|---|---|
| `config.json` | La única lista de proyectos, tipos de página, zonas, puentes, topes y controles. Ningún programa nombra un proyecto ni una página: todo sale de aquí | (lo editas tú) |
| `brain_lib.py` | Lo que comparten los demás: leer y escribir conservando los finales de línea, el encabezado, resolver enlaces, la capa de cada página, los bloques generados | no |
| `connect.py` | **El único conector.** Escribe todos los enlaces generados: los puentes y las partes de la portada de cada proyecto, la página central de una carpeta que no tiene, y "Dónde se aplica" en las páginas del núcleo que un proyecto cita. Correrlo dos veces no cambia nada la segunda; con `--check` no escribe | sí, solo dentro de bloques |
| `check.py` | **El único control.** Solo lee; sale con 1 si se rompe una regla. Reemplaza al antiguo `health_check.py` (sus enlaces rotos, nombres repetidos, etiquetas de decisión y cuentas de "por confirmar" están aquí) | no |
| `new_project.py` | Abre un proyecto: páginas desde las plantillas, lo registra en `config.json`, agrega su fila a `index.md`, corre el conector | sí |
| `apply_views.py` | Pone en el grafo de Obsidian los colores por capa y por proyecto, el filtro por defecto y un marcador por vista, desde `_sistema/obsidian/views.json` y `config.json`. Solo con Obsidian cerrado | `.obsidian/` |
| `autosave.py` | Mantiene la carpeta y el remoto iguales: guarda lo que quedó sin guardar, baja y sube. Corre el control antes y nunca deja que una falla detenga el guardado | git |
| `_sistema/hooks/pre-commit` | Corre `check.py`; frena el commit mientras falle | no |
| `_sistema/hooks/post-commit` | Corre `sync_global.py` y sube en segundo plano | `~/.claude`, `~/.codex` |
| `sync_global.py`, `install.py`, `guardian.py`, `reminder.py`, `paths.py` | Las reglas globales, el instalador, el guardián y el aviso, como en [cómo funciona por dentro](como-funciona.md) | ver ahí |
| `test_brain.py`, `test_guards.py` | Las pruebas, sobre copias temporales; tu cerebro y tu HOME real nunca se tocan | no |

## Cómo encajan las piezas

```text
tú o una IA editan una página
        │
        ▼
 connect.py   ← se corre al crear una página o una carpeta (nunca automático: escribe páginas)
        │
        ▼
 git commit ──► gancho pre-commit ──► check.py ──falla──► el commit no entra; quien lo ve lo arregla,
        │                                                   aunque la falla venga de otra sesión
        ▼ pasa
 gancho post-commit ──► sync_global.py (global.md → ~/.claude/CLAUDE.md y ~/.codex/AGENTS.md) ──► subir

 cada 10 minutos: autosave.py ──► guarda lo que quedó sin guardar (con BRAIN_AUTOSAVE=1 el gancho lo deja pasar),
                                  corre check.py y escribe las fallas en el mensaje del commit ──► bajar ──► subir
 cada semana: la revisión corre check.py y connect.py y lee los avisos
```

El punto delicado es el guardado automático. El gancho frena a personas e IA porque una página rota que entra se vuelve problema de todos; el guardado automático no debe frenar porque perder trabajo es peor que guardar una página que rompe una regla. Por eso deja pasar el gancho con una variable de entorno, corre el control por su cuenta y escribe las fallas en el mensaje de su commit y en `.git/brain-autosave.log`. La próxima sesión las ve en su primer commit y las arregla.

## El control, regla por regla

**Falla** (salida 1): un bloque generado sin su marca de fin; un enlace roto (desde una página de historia solo avisa); una ruta por tarea que no existe; un puente fijo a una página que no existe; un enlace a mano de isla a isla, de núcleo a isla, de núcleo a historia, de núcleo a empresa (salvo decisiones) o a la historia de otra zona; un enlace del núcleo a la historia dentro de un bloque generado; una página a mano con más de `max_links_hand` enlaces; más de `max_cite_decision` páginas del núcleo enlazando la misma decisión; una carpeta de proyecto sin registrar, o un proyecto registrado sin sus páginas o carpetas mínimas; una carpeta de proyecto sin página central; una página viva a más de `hops` saltos de su portada; una decisión sin su etiqueta de encabezado; dos páginas con el mismo nombre (salvo decisiones, buzones y fuentes crudas).

**Avisa** (salida 0): correr el conector cambiaría algo; una página clave a más de `hops` saltos de una portada; un mismo enlace en casi todas las páginas de un grupo; una página de estado de más de una pantalla; una bitácora que pasa su tope; una página con un tipo que `config.json` no conoce; una decisión "vigente" ya reemplazada por otra; un archivo de arranque que ya no nombra una lectura obligatoria; enlaces congelados que ya no existen; copias de trabajo dentro del cerebro.

Cada mensaje trae la página, la regla y cómo se arregla. Los enlaces que ya rompían una regla el día que la adoptas van en `checks.frozen` de `config.json`: el control falla solo si aparece uno nuevo, y avisa cuando uno congelado ya no hace falta.

`test_brain.py` provoca las roturas (un marcador dañado, un enlace de isla a isla, de núcleo a isla, de núcleo a historia, una ruta por tarea rota, un proyecto sin registrar, una decisión sin etiqueta, una página con demasiados enlaces, una carpeta sin centro) y verifica que el control falla en cada una, que el conector se niega a tocar una página dañada, que reconstruir desde cero da el mismo cerebro y que un proyecto nuevo sale conectado y con 0 fallas. Un control que nunca se vio fallar no es un control.

## La configuración

| Clave | Qué es |
|---|---|
| `layout` | Las palabras que dependen del idioma: nombres de carpetas, la etiqueta de decisión, las claves del encabezado (`type`/`tipo`...). Por eso los mismos scripts sirven en los dos idiomas |
| `projects` | `{carpeta: {name, marketing, parked}}`. `parked` es una idea: solo se le exige la portada |
| `project_pages` | Las páginas mínimas de un proyecto y la plantilla de cada una |
| `types` | Los tipos de página válidos; cuáles son historia; en cuáles ningún programa escribe |
| `zones`, `root_pages` | Carpeta → capa (isla, núcleo, empresa, fuentes, historia, sistema) |
| `raw` | Carpetas de documentos crudos: ningún programa escribe en ellas y el control no les pide nada |
| `parts` | Cómo se elige o se genera la página central de cada carpeta de un proyecto |
| `bridges` | Los puentes fijos de la portada de cada proyecto |
| `cited` | Lo que una portada muestra que cita del núcleo, y las páginas del núcleo que reciben "Dónde se aplica" |
| `limits` | Topes: enlaces por página, saltos, tamaños |
| `checks` | Página de rutas por tarea, páginas clave, lecturas obligatorias, enlaces congelados |

Para agregar un proyecto: `new_project.py`. Para agregar un puente fijo: una línea en `bridges`. Para soportar otra herramienta de IA: una línea en `TARGETS` de `sync_global.py`.

## Ganchos y guardado automático, paso a paso

- **Activar los ganchos** (lo hace el instalador): `git config core.hooksPath _sistema/hooks`. Viven en el cerebro, así que se versionan con él. Si ya usas `core.hooksPath` para otra cosa, el instalador no lo toca y te avisa.
- **Los ganchos son scripts de shell:** `.gitattributes` les fuerza finales de línea LF para que un checkout en Windows no los rompa. Encuentran Python como `python3` o `python`.
- **Programar el guardado automático** cada 10 minutos: en Windows, el Programador de tareas con la acción `python -I <cerebro>\_sistema\scripts\autosave.py`; en macOS o Linux, cron: `*/10 * * * * python3 -I <cerebro>/_sistema/scripts/autosave.py`. Necesita un remoto (`git remote add origin ...`) para subir; sin uno guarda en local y lo dice. Pruébalo primero con `--dry-run`.
- Nunca guarda archivos con nombre de llave o credencial (`.env`, `*.pem`, `*.key`, `*secret*`, `*token*`...), no hace nada mientras otro comando de git corre, y si al bajar hay un choque deshace la unión y lo escribe en su registro en vez de forzar nada.
- `.gitattributes` hace que git una por unión las bitácoras y los buzones, así que dos sesiones que agregan al final a la vez conservan las dos entradas.

## Las vistas del grafo

La historia registra y no se dibuja, así que las vistas la esconden. `views.json` tiene un color por capa, un color por proyecto (los nuevos toman uno de `spare_colors`) y cinco vistas: todo el cerebro, un mapa limpio, el núcleo compartido, una por proyecto y solo historia. `python -I _sistema/scripts/apply_views.py . --all` las escribe en `.obsidian/graph.json` y en los marcadores; `--dry-run` dice qué cambiaría. Se niega a escribir si Obsidian está abierto o si no puede saberlo.

## Por qué los scripts están una vez por plantilla, idénticos

El repo trae dos plantillas completas, inglés (`template/`) y español (`plantilla/`), porque copias una carpeta. Cada una tiene su `_system/scripts` (o `_sistema/scripts`), y las dos copias son **idénticas byte a byte**: todo lo que depende del idioma está en `config.json` (`layout`) y en `views.json`; los mensajes están escritos en los dos idiomas dentro de los programas. `tests/test_installer.py` falla si las copias difieren, así que editas las de inglés y las copias. Los ganchos siguen la misma regla: encuentran su propia carpeta, así que no nombran `_system` ni `_sistema`.

## Lo que no se portó, a propósito

Los importadores de nuestro propio cerebro (un programa que regenera una sección del núcleo desde la exportación de una app, otro desde un curso documentado) y las listas de contradicciones entre fuentes son específicos de esas fuentes. Se describen como patrón opcional al final de [el método](el-metodo.md).

## Límites

- El guardián y el aviso son funciones de Claude Code; el control, los ganchos y el guardado automático sirven con cualquier IA porque son git y archivos.
- El control lee enlaces Markdown (`[[...]]` y `[texto](pagina.md)`); no entiende prosa. Una página que dice lo contrario de una decisión sin enlazarla solo la atrapan la prueba de las diez tareas y la revisión semanal.
- Probado en Windows con Git Bash. Escrito también para macOS y Linux, sin probar ahí.
