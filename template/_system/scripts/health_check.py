"""Health check for the brain: broken [[links]], repeated file names, decisions without their tag, and unconfirmed facts per project.

Usage: python -I health_check.py [brain folder]   (defaults to the brain this script lives in)
"""
import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))  # run with python -I, so add this folder by hand
from paths import CFG, LAYOUT, SYSTEM  # noqa: E402

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else SYSTEM.parent)
ES = CFG["language"] == "es"
skip = (".", "fuentes/", "sources/")
pages = [p for p in root.rglob("*.md") if not p.relative_to(root).as_posix().startswith(skip)]
files = {p.relative_to(root).with_suffix("").as_posix() for p in root.rglob("*.md")}
files |= {p.relative_to(root).as_posix() for p in root.rglob("*.base")}
names = {pathlib.PurePosixPath(f).name for f in files}

broken = {}
for p in pages:
    for m in re.findall(r"\[\[([^\]|#]+)", p.read_text(encoding="utf-8")):
        t = m.strip().rstrip("\\")
        if t not in files and t not in names and "..." not in t:  # [[...]] is a placeholder in rules and templates
            broken.setdefault(p.relative_to(root).as_posix(), set()).add(t)
print(f"{'Enlaces rotos' if ES else 'Broken links'}: {sum(len(v) for v in broken.values())}")
for k, v in sorted(broken.items()):
    print(f"  {k} -> {sorted(v)}")

stems = collections.defaultdict(list)
for p in pages:
    rel = p.relative_to(root).as_posix()
    if f"/{LAYOUT['decisions']}/" not in rel:
        stems[p.stem.lower()].append(rel)
repeated = {k: v for k, v in stems.items() if len(v) > 1}
print(f"{'Nombres repetidos' if ES else 'Repeated names'}: {len(repeated)}")
for k, v in sorted(repeated.items()):
    print(f"  {k}: {v}")

decisions = list(root.glob(f"{LAYOUT['projects']}/*/{LAYOUT['decisions']}/*.md"))
untagged = [d.relative_to(root).as_posix() for d in decisions if LAYOUT["decision_tag"] not in d.read_text(encoding="utf-8")]
print(f"{'Decisiones' if ES else 'Decisions'}: {len(decisions)} ({'sin' if ES else 'missing'} '{LAYOUT['decision_tag']}': {untagged or ('ninguna' if ES else 'none')})")

projects = root / LAYOUT["projects"]
if projects.exists():
    print(f"'{LAYOUT['unconfirmed']}' {'por proyecto' if ES else 'per project'}:")
    for project in sorted(p.name for p in projects.iterdir() if p.is_dir()):
        n = sum(f.read_text(encoding="utf-8").lower().count(LAYOUT["unconfirmed"]) for f in (projects / project).rglob("*.md"))
        print(f"  {project}: {n}")
