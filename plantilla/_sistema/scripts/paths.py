"""Shared helpers for the brain scripts: read the config, normalize paths, decide where a session may write, and speak
the brain's language (English or Spanish).

The brain is the folder two levels above this file. Settings come from `config.json` next to `scripts/`
(or from the file named in the BRAIN_CONFIG environment variable, which the tests use).
"""
import json
import os
import re
from pathlib import Path, PureWindowsPath

ON_WINDOWS = os.name == "nt"
SYSTEM = Path(__file__).resolve().parents[1]  # _system (English template) or _sistema (Spanish template)
DEFAULT_LAYOUT = {
    "projects": "projects",
    "company": "company",
    "inbox": "inbox.md",
    "decisions": "decisions",
    "decision_tag": "type: decision",
    "unconfirmed": "to confirm",
}
GLOBAL_MARK = "<!-- brain:global-copy -->"

MESSAGES = {
    "en": {
        "guard": ("Brain guardian: this session belongs to `brain/{where}` and can only write there. "
                  "If your work affects another project or the company, add a line to its `{inbox}` "
                  "(date, where you come from, what changed, what needs deciding)."),
        "reminder": ("Brain reminder: in this reply you changed files of {project} and noted nothing in "
                     "`brain/{folder}/`. If there was a decision by the owner, a finished task or new numbers, "
                     "note it now in `{project}-log.md` and in the page it belongs to, following the brain's `AGENTS.md`. "
                     "If there was none of that, finish without doing anything else and without mentioning it."),
        "global_header": "Automatic copy of the brain's global.md. Do not edit it here: edit that file and commit in the brain.",
        "not_mine": "left alone: {target} has your own content. Run install.py, which backs it up before replacing it.",
        "updated": "updated: {target}",
    },
    "es": {
        "guard": ("Guardián del cerebro: esta sesión es de `cerebro/{where}` y solo puede escribir ahí. "
                  "Si tu trabajo afecta a otro proyecto o a la empresa, agrega una línea en su `{inbox}` "
                  "(fecha, de dónde vienes, qué cambió, qué hay que decidir)."),
        "reminder": ("Recordatorio del cerebro: en esta respuesta cambiaste archivos de {project} y no anotaste nada en "
                     "`cerebro/{folder}/`. Si hubo una decisión del dueño, una tarea terminada o números nuevos, "
                     "anótalo ahora en `{project}-log.md` y en la página que corresponda, siguiendo `AGENTS.md` del cerebro. "
                     "Si no hubo nada de eso, termina sin hacer nada más y sin mencionarlo."),
        "global_header": "Copia automática del global.md del cerebro. No la edites aquí: edita ese archivo y haz commit en el cerebro.",
        "not_mine": "no lo toco: {target} tiene contenido tuyo. Corre install.py, que lo respalda antes de reemplazarlo.",
        "updated": "actualizado: {target}",
    },
}


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
    path = Path(os.environ.get("BRAIN_CONFIG", SYSTEM / "config.json"))
    cfg = json.loads(path.read_text(encoding="utf-8"))
    return {
        "brain": norm(cfg.get("brain") or SYSTEM.parent),
        "projects": [norm(p) for p in cfg.get("project_folders", [])],
        "company": [norm(p) for p in cfg.get("company_folders", [])],
        "layout": {**DEFAULT_LAYOUT, **cfg.get("layout", {})},
        "language": cfg.get("language", "en"),
    }


CFG = load_config()
BRAIN = CFG["brain"]
LAYOUT = CFG["layout"]


def msg(key, **values):
    return MESSAGES.get(CFG["language"], MESSAGES["en"])[key].format(**values)


def in_brain(path):
    return _inside(norm(path), BRAIN)


def session_scope(cwd):
    """Where a session belongs, from the folder it was opened in.

    ('project', slug)  opened inside a project folder (a direct child of a project folder) or brain/<projects>/<slug>
    ('company', None)  opened inside a company folder or brain/<company>
    (None, None)       anywhere else, including the root of the brain: no limit
    """
    c = norm(cwd)
    if _inside(c, BRAIN):  # checked first, in case the brain lives inside a project folder
        roots, companies = [f"{BRAIN}/{LAYOUT['projects']}"], [f"{BRAIN}/{LAYOUT['company']}"]
    else:
        roots, companies = CFG["projects"], CFG["company"]
    for root in roots:
        if c.startswith(root + "/"):
            return "project", slug(c[len(root) + 1:].split("/", 1)[0])
    if any(_inside(c, f) for f in companies):
        return "company", None
    return None, None


def allowed_brain_prefix(cwd):
    """Folder inside the brain this session may write to, or None when it may write anywhere."""
    kind, project = session_scope(cwd)
    if kind == "project":
        return f"{BRAIN}/{LAYOUT['projects']}/{project}"
    if kind == "company":
        return f"{BRAIN}/{LAYOUT['company']}"
    return None
