"""Health check for the cerebro: broken [[links]], repeated file names, decisions without tipo, and "por confirmar" per project.

Usage: python -I revisar_salud.py [cerebro folder]   (defaults to the cerebro this script lives in)
"""
import collections
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[2])
PLACEHOLDERS = {"...", "enlaces", "conocimiento/canales/..."}
pages = [p for p in root.rglob("*.md") if not p.relative_to(root).as_posix().startswith((".", "fuentes/"))]
files = {p.relative_to(root).with_suffix("").as_posix() for p in root.rglob("*.md")}
files |= {p.relative_to(root).as_posix() for p in root.rglob("*.base")}
names = {pathlib.PurePosixPath(f).name for f in files}

broken = {}
for p in pages:
    for m in re.findall(r"\[\[([^\]|#]+)", p.read_text(encoding="utf-8")):
        t = m.strip().rstrip("\\")
        if t not in files and t not in names and t not in PLACEHOLDERS:
            broken.setdefault(p.relative_to(root).as_posix(), set()).add(t)
print(f"Enlaces rotos: {sum(len(v) for v in broken.values())}")
for k, v in sorted(broken.items()):
    print(f"  {k} -> {sorted(v)}")

stems = collections.defaultdict(list)
for p in pages:
    rel = p.relative_to(root).as_posix()
    if "/decisiones/" not in rel:
        stems[p.stem.lower()].append(rel)
repeated = {k: v for k, v in stems.items() if len(v) > 1}
print(f"Nombres repetidos: {len(repeated)}")
for k, v in sorted(repeated.items()):
    print(f"  {k}: {v}")

decisions = list(root.glob("proyectos/*/decisiones/*.md"))
untyped = [d.relative_to(root).as_posix() for d in decisions if "tipo: decision" not in d.read_text(encoding="utf-8")]
print(f"Decisiones: {len(decisions)} (sin 'tipo: decision': {untyped or 'ninguna'})")

projects = root / "proyectos"
if projects.exists():
    print("'Por confirmar' por proyecto:")
    for project in sorted(p.name for p in projects.iterdir() if p.is_dir()):
        n = sum(f.read_text(encoding="utf-8").lower().count("por confirmar") for f in (projects / project).rglob("*.md"))
        print(f"  {project}: {n}")
