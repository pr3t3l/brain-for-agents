"""Open a project: build its minimum pages from the templates, register it in config.json, add its row to the front page
and run the connector so it is wired to the core. Nothing about the project is typed anywhere else.

Usage: python -I new_project.py <brain folder> <folder> "<Name>" [--no-marketing] [--parked] [--check]
  <folder>        the project's folder name and the start of each of its pages (lower case, digits and hyphens)
  --no-marketing  a project that does no marketing: it gets no marketing, learnings or sources pages
  --parked        an idea only: its cover is created, nothing else is required of it yet
  --check         write nothing; say what it would do

Which pages a project has, and the template of each, come from config.json `project_pages`.
Exit code: 0 done, 1 refused (a clash or a mistake; nothing was written).
"""
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I leaves the script folder off sys.path

import brain_lib as lib  # noqa: E402
import connect  # noqa: E402


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 3 or not flags <= {"--no-marketing", "--parked", "--check"}:
        print(__doc__)
        return 1
    root, slug, name = Path(args[0]).resolve(), args[1], args[2]
    cfg_path = lib.config_path(root)
    cfg = lib.load_config(root)
    es = cfg.get("language") == "es"
    t = (lambda en, es_: es_ if es else en)
    projects = cfg["layout"]["projects"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        print(t("The folder name must be lower case letters, digits and hyphens.", "El nombre de la carpeta solo lleva minúsculas, números y guiones."))
        return 1
    if slug in cfg.get("projects", {}) or (root / projects / slug).exists():
        print(t(f"'{slug}' already exists (registered or as a folder). Nothing was written.", f"'{slug}' ya existe (registrado o como carpeta). No se escribió nada."))
        return 1

    marketing, parked = "--no-marketing" not in flags, "--parked" in flags
    spec = cfg["project_pages"]
    wanted = spec["always"] if parked else spec["always"] + (spec["if_marketing"] if marketing else [])
    tokens = cfg["new_project"]["tokens"]
    today = datetime.date.today().isoformat()
    sysdir = cfg_path.parent
    plan = []
    for entry in wanted:
        template = sysdir / spec.get("templates", "templates") / (entry["template"] + ".md")
        if not template.exists():
            print(t(f"Missing template: {template}", f"Falta la plantilla: {template}"))
            return 1
        text, _crlf = lib.read(template)
        for key, value in {"project": slug, "name": name, "date": today}.items():
            text = text.replace(tokens[key], value)
        plan.append((root / projects / slug / entry["file"].format(p=slug), text))

    # a project without marketing (or a parked idea) has no marketing pages: its cover must not link them
    made = {Path(page).stem for page, _ in plan}
    prefix = re.compile(r"\[\[" + re.escape(projects) + "/" + re.escape(slug) + r"/([^\]|#/\\]+)")
    plan = [(page, "\n".join(line for line in text.split("\n") if all(m in made for m in prefix.findall(line))))
            for page, text in plan]

    for page, _text in plan:
        print(t("would write ", "escribiría ") + page.relative_to(root).as_posix() if "--check" in flags else t("writing ", "escribo ") + page.relative_to(root).as_posix())
    if "--check" in flags:
        print(t("would register it in config.json, add its row to index.md and run connect.py. Nothing was written.",
                "lo registraría en config.json, agregaría su fila a index.md y correría connect.py. No se escribió nada."))
        return 0

    for page, text in plan:
        lib.write(page, text)
    for folder in ([] if parked else spec.get("folders", [])):
        keep = root / projects / slug / folder / ".gitkeep"  # git does not keep empty folders
        keep.parent.mkdir(parents=True, exist_ok=True)
        keep.touch()
    cfg.setdefault("projects", {})[slug] = {"name": name, "marketing": marketing, "parked": parked}
    lib.save_config(cfg, cfg_path)

    index = root / (cfg.get("checks", {}).get("index_page", "index") + ".md")
    if index.exists():
        text, crlf = lib.read(index)
        row = cfg["new_project"]["index_row"].replace("{p}", slug).replace("{name}", name)
        row = re.sub(r"\[\[[^\]]*\]\]", lambda m: m.group(0) if all(x in made for x in prefix.findall(m.group(0))) else "-", row)
        lines = text.split("\n")
        rows = [i for i, l in enumerate(lines) if l.startswith("| ") and not l.startswith("| ---")]
        if rows:
            lines.insert(rows[-1] + 1, row)
            lib.write(index, "\n".join(lines), crlf)
        else:
            print(t("index.md has no projects table: add the row by hand.", "index.md no tiene tabla de proyectos: agrega la fila a mano."))

    code = connect.main([str(root)])
    print(t(f"Done. Next: fill in {projects}/{slug}/{slug}.md (what it is), then run check.py. "
            "If the project has a repo, list it in its cover.",
            f"Listo. Siguiente: completa {projects}/{slug}/{slug}.md (qué es) y corre check.py. "
            "Si el proyecto tiene repo, anótalo en su portada."))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
