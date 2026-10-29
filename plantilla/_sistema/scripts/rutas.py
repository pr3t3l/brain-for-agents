"""Shared helpers for the cerebro scripts: read the config, normalize paths, and decide where a session may write.

The cerebro is the folder two levels above this file. Project folders come from `_sistema/config.json`
(or from the file named in the CEREBRO_CONFIG environment variable, which the tests use).
"""
import json
import os
import re
from pathlib import Path, PureWindowsPath

ON_WINDOWS = os.name == "nt"


def norm(path):
    """Absolute-looking path with forward slashes, lower-case on Windows (case-insensitive there)."""
    p = str(path or "").replace("\\", "/")
    if ON_WINDOWS:
        p = re.sub(r"^/([a-zA-Z])/", r"\1:/", p)  # Git Bash style /c/Users -> c:/Users
        p = str(PureWindowsPath(p)).replace("\\", "/").lower()
    return p.rstrip("/")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _inside(path, folder):
    return path == folder or path.startswith(folder + "/")


def load_config():
    default = Path(__file__).resolve().parents[1] / "config.json"
    path = Path(os.environ.get("CEREBRO_CONFIG", default))
    cfg = json.loads(path.read_text(encoding="utf-8"))
    brain = cfg.get("cerebro") or str(Path(__file__).resolve().parents[2])
    return {
        "cerebro": norm(brain),
        "proyectos": [norm(p) for p in cfg.get("carpetas_de_proyectos", [])],
        "empresa": [norm(p) for p in cfg.get("carpetas_de_empresa", [])],
    }


CFG = load_config()
CEREBRO = CFG["cerebro"]


def in_brain(path):
    return _inside(norm(path), CEREBRO)


def session_scope(cwd):
    """Where a session belongs, from the folder it was opened in.

    ('proyecto', slug)  opened inside a project folder (a direct child of a projects folder) or cerebro/proyectos/<slug>
    ('empresa', None)   opened inside a company folder or cerebro/empresa
    (None, None)        anywhere else, including the root of the cerebro: no limit
    """
    c = norm(cwd)
    if _inside(c, CEREBRO):  # checked first, in case the cerebro lives inside a projects folder
        roots, companies = [f"{CEREBRO}/proyectos"], [f"{CEREBRO}/empresa"]
    else:
        roots, companies = CFG["proyectos"], CFG["empresa"]
    for root in roots:
        if c.startswith(root + "/"):
            return "proyecto", slug(c[len(root) + 1:].split("/", 1)[0])
    if any(_inside(c, f) for f in companies):
        return "empresa", None
    return None, None


def allowed_brain_prefix(cwd):
    """Folder inside the cerebro this session may write to, or None when it may write anywhere."""
    kind, project = session_scope(cwd)
    if kind == "proyecto":
        return f"{CEREBRO}/proyectos/{project}"
    if kind == "empresa":
        return f"{CEREBRO}/empresa"
    return None
