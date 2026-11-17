"""The only connector: it writes every generated link of the brain, and nothing else.

What it writes, always inside a marked block (or in a page it owns whole, marked `generated_by: connect.py`):
  * on each project cover, the block `links`: the fixed bridges to the core, what the project cites from the core, the
    parts of the project (one center page per folder, with how many pages it has) and the live pages the cover does not
    link yet;
  * the center page of a part that has none (for example `<project>-decisions`), and the removal of a generated center
    once somebody writes one by hand;
  * on each core page that a project's live pages cite (config.json `cited.applied_in`), the block `applied`:
    "Where it applies". Core -> island links exist only here, as a mirror of real citations, never by hand.

Running it twice changes nothing the second time. It refuses to write a page whose block markers are damaged (it says so
and leaves the page alone) and it never writes a page someone else changed while it was running.

Usage: python -I connect.py [brain folder] [--check]
  --check  write nothing; say what would change
Exit code: 0 done (or nothing to do), 1 a page was refused.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I leaves the script folder off sys.path

import brain_lib as lib  # noqa: E402

LINKS, APPLIED = "links", "applied"
DEFAULT_ROOT = lib.HERE.parent.parent


def say(en, es, lang):
    return es if lang == "es" else en


def wl(rel, label=None):
    return f"[[{rel}|{label}]]" if label else f"[[{rel}]]"


def plural(n, lang):
    return f"{n} " + (say("page", "página", lang) if n == 1 else say("pages", "páginas", lang))


def cited_by_project(b, p):
    """{core page: how many live pages of project `p` link it by hand}."""
    base = f"{b.layout['projects']}/{p}/"
    count = {}
    for rel in b.text:
        if rel.startswith(base) and b.is_live(rel) and not b.is_raw(rel):
            for d in b.links(rel, b.hand(rel)):
                if b.layer(d) == "core":
                    count[d] = count.get(d, 0) + 1
    return count


def render_center(b, p, name, folder, lang):
    base = f"{b.layout['projects']}/{p}/{folder}/"
    pages = sorted(r for r in b.text if r.startswith(base) and b.is_live(r))
    lines = ["---", f"{b.layout['type_key']}: {b.cfg.get('parts', {}).get('center_type', 'index')}", f"{b.layout['project_key']}: {p}", f"{lib.GEN_KEY}: {lib.GEN_VALUE}", "---", "",
             f"# {name}: {folder}", "",
             say("_Written by `connect.py`: do not edit; the next run rewrites it._",
                 "_Lo escribe `connect.py`: no lo edites; la próxima corrida lo reescribe._", lang), ""]
    for r in pages:
        f = b.front(r)
        meta = [x for x in (f.get("date") or f.get("fecha"), f.get(b.layout["status_key"])) if x]
        lines.append(f"- {wl(r, b.title(r))}" + (f" ({', '.join(meta)})" if meta else ""))
    return "\n".join(lines) + "\n"


def cover_block(b, p, info, parts, lang):
    cfg, projects = b.cfg, b.layout["projects"]
    name, cover = info["name"], f"{projects}/{p}/{p}"
    lines = [f"## {say('Core knowledge and bridges', 'Conocimiento central y puentes', lang)}", ""]
    bridges = []
    for br in cfg.get("bridges", []):
        target = br["page"].replace("{p}", p)
        if (br.get("only_if_marketing") and not info.get("marketing")) or target not in b.text:
            continue
        bridges.append(wl(target, br["text"].replace("{name}", name)))
    if bridges:
        lines += [f"**{say('Fixed bridges', 'Puentes fijos', lang)}:** " + " · ".join(bridges), ""]

    cited = cited_by_project(b, p)
    groups = []
    for g in cfg.get("cited", {}).get("groups", []):
        items = sorted((d, n) for d, n in cited.items() if d.startswith(g["path"]))
        if items:
            groups.append(f"{g['title'].lower()}: " + " · ".join(f"{wl(d, b.title(d))} ({n})" for d, n in items))
    if groups:
        lines += [f"**{say(f'What {name} cites from the core', f'Lo que {name} cita del núcleo', lang)}** "
                  + say("(in parentheses, how many pages): ", "(entre paréntesis, cuántas páginas): ", lang) + "; ".join(groups), ""]

    if parts:
        lines += [f"**{say(f'Parts of {name}', f'Partes de {name}', lang)}** "
                  + say("(each folder has one page that gathers all its pages; in parentheses, how many it has):",
                        "(cada carpeta tiene una página que reúne todas sus páginas; entre paréntesis, cuántas tiene):", lang), ""]
        for f, (center, _gen) in sorted(parts.items()):
            n = sum(1 for r in b.text if r.startswith(f"{projects}/{p}/{f}/") and b.is_live(r))
            lines.append(f"- {wl(center, f.replace('-', ' ').capitalize())} ({plural(n, lang)})")
        lines.append("")

    cover_links = b.links(cover, b.hand(cover)) if cover in b.text else set()
    base = f"{projects}/{p}/"
    centers = {c for c, _g in parts.values()}
    more = sorted(r for r in b.text if r.startswith(base) and "/" not in r[len(base):] and r != cover
                  and b.is_live(r) and r not in cover_links and r not in centers)
    if more:
        lines += [f"**{say(f'More pages of {name}', f'Más páginas de {name}', lang)}:** " + " · ".join(wl(r, b.title(r)) for r in more), ""]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def run(root):
    """Compute every generated block in memory (nothing is written). Returns (brain, refused pages)."""
    b = lib.Brain(root)
    lang, projects = b.cfg.get("language", "en"), b.layout["projects"]
    refused = {}

    def put_block(rel, lines, name):
        try:
            b.text[rel] = lib.set_block(b.text[rel], lines, name)
        except lib.BlockDamaged as e:
            refused[rel] = str(e)

    expected_centers = {}
    for p, info in b.cfg.get("projects", {}).items():
        cover = f"{projects}/{p}/{p}"
        if cover not in b.text:
            continue
        parts = b.parts(p)
        expected_centers[p] = {c for c, g in parts.values() if g}
        for f, (center, generated) in parts.items():
            if generated:
                b.set(center, render_center(b, p, info["name"], f, lang))
        put_block(cover, cover_block(b, p, info, parts, lang) if b.allows_blocks(cover) else None, LINKS)

    # generated centers that no longer apply (a hand-written center now exists, or the folder is gone)
    for rel in sorted(b.text):
        p = b.project(rel)
        if p and b.front(rel).get(lib.GEN_KEY) == lib.GEN_VALUE and rel not in expected_centers.get(p, set()):
            b.delete(rel)

    # core pages: "Where it applies", a mirror of what live project pages really cite
    applied_in = tuple(b.cfg.get("cited", {}).get("applied_in", []))
    cites = {p: cited_by_project(b, p) for p in b.cfg.get("projects", {}) if f"{projects}/{p}/{p}" in b.text}
    limit = b.cfg.get("limits", {}).get("applied_max", 10)
    for rel in sorted(b.text):
        if not applied_in or not rel.startswith(applied_in) or not b.is_live(rel) or not b.allows_blocks(rel):
            continue
        rows = [(p, c[rel]) for p, c in sorted(cites.items()) if rel in c]
        lines = None
        if rows:
            shown = " · ".join(wl(f"{projects}/{p}/{p}", b.cfg["projects"][p]["name"]) + f" ({n})" for p, n in rows[:limit])
            more = f" · … (+{len(rows) - limit})" if len(rows) > limit else ""
            lines = [f"**{say('Where it applies', 'Dónde se aplica', lang)}:** " + shown + more]
        put_block(rel, lines, APPLIED)
    return b, refused


def main(argv):
    root = next((Path(a) for a in argv if not a.startswith("--")), DEFAULT_ROOT)
    check = "--check" in argv
    b, refused = run(root.resolve())
    for rel, why in sorted(refused.items()):
        print(f"REFUSED {rel}: {why}. I did not touch that page; fix the marker by hand and run me again.")
    mod, new, gone = b.changed()
    if check:
        for rel in mod + new + gone:
            print(("would change " if rel in mod else "would create " if rel in new else "would delete ") + rel)
        print(f"connect: {len(mod) + len(new) + len(gone)} page(s) would change; nothing was written.")
        return 1 if refused else 0
    mod, new, gone, skipped = b.save()
    for rel in skipped:
        print(f"skipped {rel}: someone changed it while I was running; the next run picks it up.")
    print(f"connect: {len(mod)} changed, {len(new)} created, {len(gone)} deleted." if mod or new or gone else "connect: nothing to change.")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
