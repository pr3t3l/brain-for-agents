"""Connect this brain to Claude Code and Codex on this computer.

Usage: python -I install.py [--dry-run]

What it does (backing up every file before its first change, as <name>.before-brain):
1. Starts a git repo in the brain if there is none, with a post-commit hook that copies global.md
   to ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md, and pushes when there is a remote.
2. Writes those two global files now.
3. Claude Code (~/.claude/settings.json): the brain as an extra working folder, permission to edit it,
   the guardian (PreToolUse) and the reminder (Stop) hooks.
4. Codex (~/.codex/config.toml): the brain as a writable root.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run with python -I, so add this folder by hand
from paths import CFG, SYSTEM  # noqa: E402
from sync_global import global_block, merged  # noqa: E402

DRY = "--dry-run" in sys.argv
ES = CFG["language"] == "es"
HOME = Path.home()
SCRIPTS = Path(__file__).resolve().parent
BRAIN = SYSTEM.parent
PY = Path(sys.executable).as_posix()
SYS_DIR = SYSTEM.name  # _system or _sistema


def t(en, es):
    return es if ES else en


def say(text):
    print((t("[dry run] ", "[prueba] ") if DRY else "") + text)


def backup(path):
    """Keep the very first version: running the installer twice must not overwrite the original backup."""
    saved = path.with_name(path.name + ".before-brain")
    if path.exists() and not saved.exists() and not DRY:
        shutil.copy2(path, saved)


def write(path, text):
    say(t("writing ", "escribo ") + str(path))
    if not DRY:
        backup(path)
        path.write_text(text, encoding="utf-8")


def permission_path(p):
    """Claude Code permission rules write absolute paths as //c/Users/... (Windows) or //Users/... (macOS, Linux)."""
    posix = p.as_posix()
    if len(posix) > 1 and posix[1] == ":":
        return "//" + posix[0].lower() + posix[2:]
    return "/" + posix


if not CFG["projects"]:
    sys.exit(t(f"First edit {SYSTEM / 'config.json'}: put the folder (or folders) where your projects live in 'project_folders'.",
               f"Primero edita {SYSTEM / 'config.json'}: pon en 'project_folders' la carpeta (o carpetas) donde viven tus proyectos."))

# 1. git and the post-commit hook
if not (BRAIN / ".git").exists():
    say(f"git init {BRAIN}")
    if not DRY:
        subprocess.run(["git", "init", "-q", "-b", "main", str(BRAIN)], check=True)
hook = BRAIN / ".git" / "hooks" / "post-commit"
write(hook, "\n".join([
    "#!/bin/sh",
    "# Copy global.md to ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md",
    f'"{PY}" -I "$(git rev-parse --show-toplevel)/{SYS_DIR}/scripts/sync_global.py"',
    "# Backup: push every commit when there is a remote; a failed push never blocks the commit",
    "if git remote | grep -q .; then git push -q origin HEAD >/dev/null 2>&1 & fi",
    "",
]))
if not DRY:
    hook.chmod(0o755)

# 2. global rules for both tools: backup first, then our block goes on top and anything already there is kept
for target in [HOME / ".claude" / "CLAUDE.md", HOME / ".codex" / "AGENTS.md"]:
    if target.parent.exists():
        write(target, merged(target.read_text(encoding="utf-8") if target.exists() else "", global_block()))
    else:
        say(t(f"skipping {target}: that tool is not installed", f"salto {target}: esa herramienta no está instalada"))

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

    def ours(entry):
        return scripts in json.dumps(entry).replace("\\\\", "/")

    hooks["PreToolUse"] = [h for h in hooks.get("PreToolUse", []) if not ours(h)] + [{
        "matcher": "Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [{"type": "command", "command": f'"{PY}" -I "{scripts}/guardian.py"', "timeout": 10}]}]
    hooks["Stop"] = [h for h in hooks.get("Stop", []) if not ours(h)] + [{
        "hooks": [{"type": "command", "command": f'"{PY}" -I "{scripts}/reminder.py"', "timeout": 15}]}]
    write(settings_path, json.dumps(s, indent=2, ensure_ascii=False) + "\n")
else:
    say(t("skipping Claude Code: ~/.claude not found", "salto Claude Code: no encontré ~/.claude"))

# 4. Codex config
codex = HOME / ".codex" / "config.toml"
if codex.parent.exists():
    text = codex.read_text(encoding="utf-8") if codex.exists() else ""
    if str(BRAIN) in text:
        say(t("Codex already has the brain as a writable root", "Codex ya tiene el cerebro como carpeta con permiso de escritura"))
    elif "[sandbox_workspace_write]" in text:
        say(t(f"Codex already has [sandbox_workspace_write]: add '{BRAIN}' to its writable_roots list in {codex} by hand",
              f"Codex ya tiene [sandbox_workspace_write]: agrega a mano '{BRAIN}' a su lista writable_roots en {codex}"))
    else:
        write(codex, text.rstrip("\n") + "\n\n# Brain: any session may write there (the brain's rules say in which folder)\n"
                                         f"[sandbox_workspace_write]\nwritable_roots = ['{BRAIN}']\n")
else:
    say(t("skipping Codex: ~/.codex not found", "salto Codex: no encontré ~/.codex"))

say(t("Done. Open a new Claude Code or Codex session so it loads the global rules.",
      "Listo. Abre una sesión nueva de Claude o Codex para que cargue las reglas globales."))
