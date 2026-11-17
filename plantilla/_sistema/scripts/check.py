"""The check of the brain: read only. It verifies that the brain still has the shape "one core, project islands and fixed
bridges" and exits with code 1 when a rule is broken. It never writes a file. A rule that does not make this program
fail is not a rule: it is a wish.

FAILS (exit 1) when
  - a generated block has a start marker without its end marker (or the markers are otherwise damaged);
  - a link is broken (raw sources and history pages aside: history only warns), or a link of the task routes page
    points nowhere, or a fixed bridge of config.json points to a missing page;
  - a hand-written link breaks the link rule and is not in the frozen list of config.json (checks.frozen):
      island -> another island, core -> island, core -> history, core -> company (decisions aside),
      any live page -> a history page of another zone (a project may link its own log and inbox);
  - the connector wrote a link from the core to history in a generated block;
  - a hand-written page has more than `max_links_hand` outgoing links (a list that links everything is not a map);
  - more than `max_cite_decision` core pages link the same decision;
  - a folder of projects/ is not registered in config.json, a registered project (not parked) lacks its minimum pages,
    or a registered project has no folder;
  - a folder of a project has no center page, or a live page of a project is more than `hops` hops from its cover;
  - a decision lacks the header tag (layout.decision_tag);
  - two pages share a name (decisions, inboxes and raw sources aside): in Obsidian they would be one node.
WARNS (exit 0) when the connector would change something, a key page is more than `hops` hops from a project cover, one
link is the same in most pages of a group (a link must say something), a status page does not fit one screen, a log is
too big, a page has a type config.json does not know, a decision in force is said to be replaced by another one, a
required read is missing from the start rules, the frozen list keeps links that no longer exist, or a history page has
a broken link.

Usage: python -I check.py [brain folder]
Exit code: 0 no failures, 1 at least one failure.
"""
import collections
import sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I leaves the script folder off sys.path

import brain_lib as lib  # noqa: E402
import connect  # noqa: E402

SHOWN = 15  # lines shown per rule; the rest is counted


class Result:
    def __init__(self):
        self.fails, self.warns, self.fix = collections.defaultdict(list), collections.defaultdict(list), {}

    def fail(self, rule, page, msg, fix):
        self.fails[rule].append((page, msg))
        self.fix[rule] = fix

    def warn(self, rule, page, msg, fix=""):
        self.warns[rule].append((page, msg))
        if fix:
            self.fix.setdefault(rule, fix)

    def n_fails(self):
        return sum(len(v) for v in self.fails.values())

    def n_warns(self):
        return sum(len(v) for v in self.warns.values())


def run_checks(root):
    b = lib.Brain(root)
    cfg, lay, lim, chk = b.cfg, b.layout, b.cfg.get("limits", {}), b.cfg.get("checks", {})
    es = cfg.get("language") == "es"
    r = Result()

    def t(en, es_):
        return es_ if es else en

    frozen = {k: {tuple(x) for x in v} for k, v in chk.get("frozen", {}).items()}
    projects_dir = lay["projects"]

    # ---- block markers
    for rel, text in sorted(b.text.items()):
        try:
            lib.find_blocks(text)
        except lib.BlockDamaged as e:
            r.fail(t("damaged generated block", "bloque generado dañado"), rel, str(e),
                   t("put back the missing marker by hand (<!-- brain:NAME:end --> after the generated lines) and run connect.py; "
                     "no program rewrites the page while it stays damaged",
                     "pon a mano el marcador que falta (<!-- brain:NOMBRE:end --> tras lo generado) y corre connect.py; "
                     "ningún programa reescribe la página mientras siga dañada"))

    # ---- broken links
    examples = set(chk.get("example_links", []))
    others = b.others | {PurePosixPath(o).name for o in b.others}
    routes = chk.get("routes", "task-routes")
    for rel, text in sorted(b.text.items()):
        if b.is_raw(rel):
            continue
        broken = sorted({x.strip().rstrip("\\") for x in lib._WIKI.findall(text)
                         if "..." not in x and "{{" not in x and b.resolve(x) is None
                         and x.strip().rstrip("\\") not in examples and x.strip() not in others})
        if not broken:
            continue
        msg = t("links pages that do not exist: ", "enlaza páginas que no existen: ") + ", ".join(broken[:6]) + (" …" if len(broken) > 6 else "")
        if rel == routes:
            r.fail(t("task route that does not exist", "ruta por tarea que no existe"), rel, msg,
                   t("fix the row with the page's new path, or drop the row if the page is gone",
                     "corrige la fila con la ruta nueva de la página, o quítala si la página ya no existe"))
        elif b.is_history(rel):
            r.warn(t("broken link in a history page", "enlace roto en una página de historia"), rel, msg,
                   t("logs and inboxes are not rewritten: the next entry can name the new path",
                     "las bitácoras y los buzones no se reescriben: la siguiente entrada puede decir la ruta nueva"))
        else:
            r.fail(t("broken link", "enlace roto"), rel, msg,
                   t("fix the link with the page's current path, or remove it if the page was deleted",
                     "corrige el enlace con la ruta actual de la página, o quítalo si la página se borró"))

    # ---- the fixed bridges must exist
    for p, info in cfg.get("projects", {}).items():
        for br in cfg.get("bridges", []):
            target = br["page"].replace("{p}", p)
            if (br.get("only_if_marketing") and not info.get("marketing")) or info.get("parked"):
                continue
            if target not in b.text and (projects_dir + "/" + p + "/" + p) in b.text:
                r.fail(t("fixed bridge to a missing page", "puente fijo a una página que no existe"), target,
                       t(f"config.json `bridges` names it for project {p}", f"config.json `bridges` la nombra para el proyecto {p}"),
                       t("create the page or fix `bridges` in config.json", "crea la página o corrige `bridges` en config.json"))

    # ---- the link rule, on hand-written text
    always = set(chk.get("always_linkable", []))
    rules = {
        "island_to_island": (t("link from a project to another project", "enlace de un proyecto a otro"),
                             t("a project does not link another one: write the name as text, or leave a line in the other project's inbox, or move what is shared up to the core",
                               "un proyecto no enlaza a otro: escribe el nombre como texto, deja una línea en el buzón del otro, o sube lo común al núcleo")),
        "core_to_island": (t("hand-written link from the core to a project", "enlace a mano del núcleo a un proyecto"),
                           t("the core never links a project by hand: write the name as text; the generated 'Where it applies' block already shows who uses the page",
                             "el núcleo no enlaza a mano un proyecto: escribe el nombre como texto; el bloque generado 'Dónde se aplica' ya muestra quién usa la página")),
        "core_to_history": (t("link from the core to history", "enlace del núcleo a la historia"),
                            t("the core does not link logs, inboxes or reviews: quote what matters as text, or turn an approved proposal into a new page of the core",
                              "el núcleo no enlaza bitácoras, buzones ni revisiones: cita lo que importa como texto, o convierte una propuesta aprobada en una página nueva del núcleo")),
        "core_to_company": (t("link from the core to the company", "enlace del núcleo a la empresa"),
                            t("the core links only company decisions: write the rest as text",
                              "el núcleo solo enlaza decisiones de la empresa: lo demás va como texto")),
        "history_link": (t("link to a history page of another zone", "enlace a una página de historia de otra zona"),
                         t("a page links the history of its own project or zone only; the owner's 'pending' page is the fixed exception. Leave a line in that place's inbox instead",
                           "una página solo enlaza la historia de su propio proyecto o zona; 'pendientes' es la excepción fija. Deja una línea en el buzón de ese lugar")),
    }
    seen = collections.defaultdict(set)
    for rel in sorted(b.text):
        layer = b.layer(rel)
        if layer not in ("island", "core", "company") or b.is_raw(rel):
            continue
        sp = b.project(rel)
        zone_root = rel.split("/")[0]
        for d in sorted(b.links(rel, b.hand(rel))):
            dp, dl = b.project(d), b.layer(d)
            hits = []
            if sp and dp and dp != sp:
                hits.append("island_to_island")
            if layer == "core" and dp:
                hits.append("core_to_island")
            if layer == "core" and dl == "history":
                hits.append("core_to_history")
            elif dl == "history" and d not in always and not (sp and dp == sp) and not (not sp and d.split("/")[0] == zone_root):
                hits.append("history_link")
            if layer == "core" and b.zone(d) == "company" and dl != "history" and b.type(d) != "decision":
                hits.append("core_to_company")
            for h in hits:
                seen[h].add((rel, d))
                if (rel, d) not in frozen.get(h, set()):
                    r.fail(rules[h][0], rel, t(f"links {d} by hand", f"enlaza a mano {d}"), rules[h][1])
    for h in frozen:
        stale = sorted(frozen[h] - seen.get(h, set()))
        if stale:
            r.warn(t("frozen list keeps links that no longer exist", "lista congelada con enlaces que ya no existen"), None,
                   f"{h}: {len(stale)} ({stale[0][0]} -> {stale[0][1]})",
                   t("remove those rows from checks.frozen in config.json: the link is already fixed",
                     "quita esas filas de checks.frozen en config.json: el enlace ya se arregló"))

    # ---- the connector never links history from the core
    for rel in sorted(b.text):
        if b.layer(rel) != "core":
            continue
        try:
            spans = lib.find_blocks(b.text[rel])
        except lib.BlockDamaged:
            continue
        lines = b.text[rel].split("\n")
        for a, z in spans.values():
            for d in sorted(b.links(rel, "\n".join(lines[a:z + 1]))):
                if b.is_history(d):
                    r.fail(t("generated block links history from the core", "el bloque generado enlaza la historia desde el núcleo"), rel,
                           t(f"its generated block links {d}", f"su bloque generado enlaza {d}"),
                           t("fix the recipe in connect.py (or the type of the target page)", "corrige la receta en connect.py (o el tipo de la página destino)"))

    # ---- too many links
    cap = lim.get("max_links_hand", 60)
    index_page = chk.get("index_page", "index")
    for rel in sorted(b.text):
        if b.is_listing(rel) or b.is_history(rel) or b.is_raw(rel) or b.layer(rel) in ("system", "sources") or rel == index_page:
            continue
        n = len(b.links(rel, b.hand(rel)))
        if n > cap:
            r.fail(t("hand-written page with too many links", "página a mano con demasiados enlaces"), rel,
                   t(f"{n} outgoing links written by hand (cap {cap})", f"{n} enlaces de salida escritos a mano (tope {cap})"),
                   t("split the page, or leave as text what is not for navigating; if it is a list, let a program write it",
                     "parte la página, o deja como texto lo que no es para navegar; si es un listado, que lo escriba un programa"))
    cap_d = lim.get("max_cite_decision", 20)
    per_decision = collections.Counter(d for rel in b.text if b.layer(rel) == "core" for d in b.links(rel) if f"/{lay['decisions']}/" in d)
    for d, k in per_decision.most_common():
        if k > cap_d:
            r.fail(t("many core pages link the same decision", "muchas páginas del núcleo enlazan la misma decisión"), d,
                   t(f"{k} core pages link it (cap {cap_d})", f"la enlazan {k} páginas del núcleo (tope {cap_d})"),
                   t("write the rule as text in each page and link the decision once, from one rules page",
                     "la regla va como texto en cada página y la decisión se enlaza una sola vez, desde una página de reglas"))

    # ---- one link that is the same in most pages says nothing
    share, min_pages = lim.get("same_link_share", 0.8), lim.get("same_link_min_pages", 5)
    groups = collections.defaultdict(list)
    for rel in b.text:
        if b.is_live(rel) and not b.is_raw(rel) and b.layer(rel) in ("core", "island") and b.type(rel) != "decision":
            groups[(b.layer(rel), b.project(rel))].append(rel)
    for (layer, p), pages in groups.items():
        if len(pages) < min_pages:
            continue
        count = collections.Counter(d for rel in pages for d in b.links(rel, b.hand(rel)) if b.project(d) != p or p is None)
        for d, k in count.most_common(3):
            if k / len(pages) > share:
                r.warn(t("one link is the same in most pages", "un mismo enlace está en casi todas las páginas"), d,
                       t(f"{k} of {len(pages)} pages of the group link it", f"{k} de {len(pages)} páginas del grupo lo enlazan"),
                       t("a link that every page has says nothing: leave it as text, or link only where the page really uses it",
                         "un enlace que todas las páginas tienen no dice nada: déjalo como texto, o enlaza solo donde la página de verdad lo usa"))

    # ---- projects: registered, with their minimum pages, parts and hops
    registered = cfg.get("projects", {})
    base = root / projects_dir
    folders = sorted(p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")) if base.exists() else []
    for f in folders:
        if f not in registered:
            r.fail(t("project folder not registered", "carpeta de proyecto sin registrar"), f"{projects_dir}/{f}",
                   t("it is not in config.json `projects`", "no está en `projects` de config.json"),
                   t(f"run new_project.py to register it, or add it to config.json `projects`", f"corre new_project.py para registrarlo, o agrégalo a `projects` en config.json"))
    for p, info in registered.items():
        if p not in folders:
            r.fail(t("registered project without a folder", "proyecto registrado sin carpeta"), p,
                   t(f"config.json lists it but {projects_dir}/{p}/ does not exist", f"config.json lo lista pero {projects_dir}/{p}/ no existe"),
                   t("remove it from config.json `projects` or create its folder with new_project.py",
                     "quítalo de `projects` en config.json o crea su carpeta con new_project.py"))
            continue
        if info.get("parked"):
            continue
        spec = cfg.get("project_pages", {})
        need = [x["file"] for x in spec.get("always", []) + (spec.get("if_marketing", []) if info.get("marketing") else [])]
        for name in need:
            file = f"{projects_dir}/{p}/" + name.format(p=p)
            if not (root / file).exists():
                r.fail(t("project without its minimum pages", "proyecto sin sus páginas mínimas"), file,
                       t(f"{p} lacks {name.format(p=p)}", f"{p} no tiene {name.format(p=p)}"),
                       t("create it from the template (new_project.py builds them all), or mark the project `parked` in config.json",
                         "créala desde la plantilla (new_project.py las crea todas), o marca el proyecto `parked` en config.json"))
        for folder in spec.get("folders", []):
            if not (base / p / folder).is_dir():
                r.fail(t("project without its minimum folder", "proyecto sin su carpeta mínima"), f"{projects_dir}/{p}/{folder}",
                       t(f"{p} lacks the folder {folder}/", f"{p} no tiene la carpeta {folder}/"), t("create the folder", "crea la carpeta"))
        cover = f"{projects_dir}/{p}/{p}"
        if cover not in b.text:
            continue
        for f, (center, generated) in sorted(b.parts(p).items()):
            if generated and center not in b.text:
                r.fail(t("folder of a project without a center page", "carpeta de un proyecto sin página central"), f"{projects_dir}/{p}/{f}",
                       t(f"it should have {center}", f"debería tener {center}"),
                       t("run connect.py: it writes the center page and links it from the cover", "corre connect.py: escribe la página central y la enlaza desde la portada"))
        dist, frontier, hops = {cover: 0}, [cover], lim.get("hops", 2)
        while frontier:
            nxt = []
            for rel in frontier:
                if b.is_history(rel):
                    continue
                for d in b.links(rel):
                    if d not in dist:
                        dist[d] = dist[rel] + 1
                        nxt.append(d)
            frontier = nxt
        for rel in sorted(b.text):
            if rel.startswith(f"{projects_dir}/{p}/") and b.is_live(rel) and dist.get(rel, 99) > hops:
                r.fail(t("project page too far from its cover", "página de un proyecto lejos de su portada"), rel,
                       t(f"more than {hops} hops from {cover}", f"a más de {hops} saltos de {cover}"),
                       t("run connect.py (the cover lists the center of each part), or link the page from a page nearer the cover",
                         "corre connect.py (la portada lista el centro de cada parte), o enlaza la página desde una más cercana a la portada"))
        for key in chk.get("key_pages", []):
            if key in b.text and dist.get(key, 99) > hops:
                r.warn(t("key page too far from a project cover", "página clave lejos de la portada de un proyecto"), key,
                       t(f"more than {hops} hops from {cover}", f"a más de {hops} saltos de {cover}"),
                       t("add it to the fixed bridges in config.json", "agrégala a los puentes fijos en config.json"))

    # ---- decisions
    tag = lay["decision_tag"]
    for rel in sorted(b.text):
        if PurePosixPath(rel).parent.name == lay["decisions"] and not b.is_raw(rel) and b.zone(rel) in ("island", "company"):
            header = b.text[rel].split("---")[1] if b.text[rel].startswith("---") else ""
            if tag not in header:
                r.fail(t("decision without its header tag", "decisión sin la etiqueta del encabezado"), rel,
                       t(f"the header lacks '{tag}'", f"al encabezado le falta '{tag}'"),
                       t("start the note from the decision template: the decisions table finds notes by that tag",
                         "empieza la nota desde la plantilla de decisión: la tabla de decisiones encuentra las notas por esa etiqueta"))
            f = b.front(rel)
            old = f.get(lay["replaces_key"], "").strip().strip("[]|").split("|")[0].strip()
            target = b.resolve(old) if old else None
            if target and b.front(target).get(lay["status_key"]) == lay["status_current"] and f.get(lay["status_key"]) == lay["status_current"]:
                r.warn(t("a decision in force is said to be replaced", "una decisión vigente figura como reemplazada"), target,
                       t(f"{rel} replaces it, but it is still '{lay['status_current']}'", f"{rel} la reemplaza, pero sigue '{lay['status_current']}'"),
                       t(f"mark the old one '{lay['status_replaced']}' the same day", f"marca la vieja '{lay['status_replaced']}' el mismo día"))

    # ---- repeated names
    shared = {PurePosixPath(lay["inbox"]).stem}
    stems = collections.defaultdict(list)
    for rel in b.text:
        if b.is_raw(rel) or f"/{lay['decisions']}/" in rel or rel.startswith("_") or PurePosixPath(rel).name in shared:
            continue
        if b.layer(rel) == "system":
            continue
        stems[PurePosixPath(rel).name.lower()].append(rel)
    for name, pages in sorted(stems.items()):
        if len(pages) > 1:
            r.fail(t("two pages share a name", "dos páginas con el mismo nombre"), pages[0],
                   t(f"{name}: {', '.join(pages)}", f"{name}: {', '.join(pages)}"),
                   t("rename one: every page of a project starts with the project's name", "renombra una: toda página de un proyecto empieza con el nombre del proyecto"))

    # ---- warnings: size, types, start rules, connector
    for p in registered:
        status = [f"{projects_dir}/{p}/{x['file'].format(p=p)}" for x in cfg.get("project_pages", {}).get("always", []) if x.get("role") == "status"]
        for s in status:
            if s in b.text:
                kb, n = len(b.text[s].encode("utf-8")) / 1024, b.text[s].count("\n") + 1
                if kb > lim.get("status_kb", 6) or n > lim.get("status_lines", 60):
                    r.warn(t("status page does not fit one screen", "una página de estado no cabe en una pantalla"), s,
                           f"{n} {t('lines', 'líneas')}, {kb:.1f} KB", t("replace lines instead of adding: history belongs in the log", "reemplaza líneas en vez de agregar: la historia va en la bitácora"))
    for rel in b.text:
        if b.type(rel) == "log" and len(b.text[rel].encode("utf-8")) / 1024 > lim.get("log_kb", 100):
            r.warn(t("log too big", "bitácora demasiado grande"), rel, t("over the size limit", "pasa el tope de tamaño"),
                   t("move the old entries to an archive page", "pasa lo viejo a una página de archivo"))
    valid = set(cfg.get("types", {}).get("valid", []))
    for rel in sorted(b.text):
        ty = b.type(rel)
        if valid and ty and ty not in valid and not b.is_raw(rel):
            r.warn(t("page with an unknown type", "página con un tipo que no se conoce"), rel, f"{lay['type_key']}: {ty}",
                   t("use a type from config.json `types.valid`, or add it there", "usa un tipo de `types.valid` en config.json, o agrégalo ahí"))
    for file, names in chk.get("required_reads", {}).items():
        path = Path(file).expanduser() if file.startswith("~") else root / file
        if path.exists():
            text = path.read_text(encoding="utf-8")
            for n in names:
                if n not in text:
                    r.warn(t("start rules do not name a required read", "las reglas de arranque no nombran una lectura obligatoria"), file,
                           t(f"it does not mention '{n}'", f"no menciona '{n}'"),
                           t("AI sessions only read what their start rules send them to: name the page there",
                             "las sesiones de IA solo leen lo que sus reglas de arranque les mandan: nombra la página ahí"))
    if (root / ".claude" / "worktrees").exists():
        r.warn(t("working copies inside the brain", "copias de trabajo dentro del cerebro"), ".claude/worktrees", t("they show up in searches as if they were pages", "aparecen en las búsquedas como si fueran páginas"),
               t("open brain chats without a working copy", "abre los chats del cerebro sin copia de trabajo"))
    try:
        cb, refused = connect.run(root)
        mod, new, gone = cb.changed()
        if mod or new or gone:
            r.warn(t("running connect.py would change something", "correr connect.py cambiaría algo"), None,
                   t(f"{len(mod)} changed, {len(new)} new, {len(gone)} deleted (for example {(mod + new + gone)[0]})",
                     f"{len(mod)} cambiarían, {len(new)} nuevas, {len(gone)} borradas (por ejemplo {(mod + new + gone)[0]})"),
                   t("run python -I _system/scripts/connect.py", "corre python -I _sistema/scripts/connect.py"))
    except Exception as e:  # the check must still report the rest
        r.fail(t("the connector cannot run", "el conector no puede correr"), None, str(e), t("fix the error and run connect.py", "arregla el error y corre connect.py"))
    return b, r


def report(b, r):
    es = b.cfg.get("language") == "es"
    for store, label in ((r.fails, "FAIL"), (r.warns, "WARN")):
        for rule, items in store.items():
            print(f"{label} {rule} ({len(items)})")
            for page, msg in items[:SHOWN]:
                print(f"  {page + ': ' if page else ''}{msg}")
            if len(items) > SHOWN:
                print(f"  … +{len(items) - SHOWN}")
            print(f"  {'Cómo se arregla' if es else 'How to fix'}: {r.fix.get(rule, '')}")
    lay, word = b.layout, b.layout["unconfirmed"]
    counts = []
    for p in b.cfg.get("projects", {}):
        prefix = lay["projects"] + "/" + p + "/"
        counts.append(p + " " + str(sum(text.lower().count(word) for k, text in b.text.items() if k.startswith(prefix))))
    print("'" + word + "' " + ("por proyecto" if es else "per project") + ": " + ", ".join(counts))
    print(f"check: {r.n_fails()} {'fallas' if es else 'failures'}, {r.n_warns()} {'avisos' if es else 'warnings'}")


def main(argv):
    root = Path(next((a for a in argv if not a.startswith("--")), connect.DEFAULT_ROOT)).resolve()
    b, r = run_checks(root)
    report(b, r)
    return 1 if r.n_fails() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
