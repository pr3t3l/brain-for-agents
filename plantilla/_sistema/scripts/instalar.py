"""Connect this cerebro to Claude Code and Codex on this computer.

Usage: python -I instalar.py [--dry-run]

What it does (and backs up every file before changing it, as <name>.antes-del-cerebro):
1. Starts a git repo in the cerebro if there is none, with a post-commit hook that copies _sistema/global.md
   to ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md, and pushes when there is a remote.
2. Writes those two global files now.
3. Claude Code (~/.claude/settings.json): the cerebro as an extra working folder, permission to edit it,
   the guardian (PreToolUse) and the reminder (Stop) hooks.
4. Codex (~/.codex/config.toml): the cerebro as a writable root.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

DRY = "--dry-run" in sys.argv
HOME = Path.home()
SCRIPTS = Path(__file__).resolve().parent
BRAIN = SCRIPTS.parents[1]
PY = Path(sys.executable).as_posix()
MARK = "cerebro/_sistema/scripts"


def say(msg):
    print(("[prueba] " if DRY else "") + msg)


def backup(path):
    """Keep the very first version: running the installer twice must not overwrite the original backup."""
    saved = path.with_name(path.name + ".antes-del-cerebro")
    if path.exists() and not saved.exists() and not DRY:
        shutil.copy2(path, saved)


def write(path, text):
    say(f"escribo {path}")
    if not DRY:
        backup(path)
        path.write_text(text, encoding="utf-8")


def permission_path(p):
    """Claude Code permission rules write absolute paths as //c/Users/... (Windows) or //Users/... (Mac, Linux)."""
    posix = p.as_posix()
    if len(posix) > 1 and posix[1] == ":":
        return "//" + posix[0].lower() + posix[2:]
    return "/" + posix


cfg_path = BRAIN / "_sistema" / "config.json"
cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
if not cfg.get("carpetas_de_proyectos"):
    sys.exit(f"Primero edita {cfg_path}: pon en 'carpetas_de_proyectos' la carpeta (o carpetas) donde viven tus proyectos.")

# 1. git and the post-commit hook
if not (BRAIN / ".git").exists():
    say(f"git init en {BRAIN}")
    if not DRY:
        subprocess.run(["git", "init", "-q", "-b", "main", str(BRAIN)], check=True)
hook = BRAIN / ".git" / "hooks" / "post-commit"
write(hook, "\n".join([
    "#!/bin/sh",
    "# Copia _sistema/global.md a ~/.claude/CLAUDE.md y ~/.codex/AGENTS.md",
    f'"{PY}" -I "$(git rev-parse --show-toplevel)/_sistema/scripts/sincronizar_global.py"',
    "# Respaldo: sube cada commit si hay un remoto; si falla, no bloquea el commit",
    'if git remote | grep -q .; then git push -q origin HEAD >/dev/null 2>&1 & fi',
    "",
]))
if not DRY:
    hook.chmod(0o755)

# 2. global rules for both tools (backup first, then the copy script owns them)
header = "<!-- Copia automática de cerebro/_sistema/global.md. No la edites aquí: edita esa y haz commit en el cerebro. -->\n\n"
global_text = header + (BRAIN / "_sistema" / "global.md").read_text(encoding="utf-8")
for target in [HOME / ".claude" / "CLAUDE.md", HOME / ".codex" / "AGENTS.md"]:
    if target.parent.exists():
        write(target, global_text)
    else:
        say(f"salto {target}: esa herramienta no está instalada")

# 3. Claude Code settings
settings_path = HOME / ".claude" / "settings.json"
if settings_path.parent.exists():
    s = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.exists() else {}
    perm = s.setdefault("permissions", {})
    dirs = perm.setdefault("additionalDirectories", [])
    if str(BRAIN) not in dirs:
        dirs.append(str(BRAIN))
    rule = f"Edit({permission_path(BRAIN)}/**)"
    if rule not in perm.setdefault("allow", []):
        perm["allow"].append(rule)
    hooks = s.setdefault("hooks", {})
    scripts = SCRIPTS.as_posix()
    hooks["PreToolUse"] = [h for h in hooks.get("PreToolUse", []) if MARK not in json.dumps(h)] + [{
        "matcher": "Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [{"type": "command", "command": f'"{PY}" -I "{scripts}/guardian.py"', "timeout": 10}]}]
    hooks["Stop"] = [h for h in hooks.get("Stop", []) if MARK not in json.dumps(h)] + [{
        "hooks": [{"type": "command", "command": f'"{PY}" -I "{scripts}/aviso.py"', "timeout": 15}]}]
    write(settings_path, json.dumps(s, indent=2, ensure_ascii=False) + "\n")
else:
    say("salto Claude Code: no encontré ~/.claude")

# 4. Codex config
codex = HOME / ".codex" / "config.toml"
if codex.parent.exists():
    text = codex.read_text(encoding="utf-8") if codex.exists() else ""
    if str(BRAIN) in text:
        say("Codex ya tiene el cerebro como carpeta con permiso de escritura")
    elif "[sandbox_workspace_write]" in text:
        say(f"Codex ya tiene [sandbox_workspace_write]: agrega a mano '{BRAIN}' a su lista writable_roots en {codex}")
    else:
        write(codex, text.rstrip("\n") + f"\n\n# Cerebro: cualquier sesión puede escribir allí (sus reglas dicen en qué carpeta)\n"
                                         f"[sandbox_workspace_write]\nwritable_roots = ['{BRAIN}']\n")
else:
    say("salto Codex: no encontré ~/.codex")

say("Listo. Abre una sesión nueva de Claude o Codex para que cargue las reglas globales.")
