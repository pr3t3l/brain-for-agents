"""Claude Code Stop hook: remind a project session to write to the cerebro when it changed files but noted nothing.

Fires only in sessions opened inside a project, only when this turn edited files outside the cerebro with Claude's
file tools and wrote nothing to cerebro/proyectos/<project>, and at most once every 30 minutes per session.
It reads the conversation file Claude Code keeps on disk; it does not call any model.
"""
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run with python -I, so add this folder by hand
from rutas import allowed_brain_prefix, in_brain, norm, session_scope  # noqa: E402

EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
QUIET_SECONDS = 30 * 60

data = json.loads(sys.stdin.buffer.read().decode("utf-8"))  # Windows consoles are not UTF-8 by default
if data.get("stop_hook_active"):
    sys.exit(0)
kind, project = session_scope(data.get("cwd"))
if kind != "proyecto":
    sys.exit(0)


def is_real_user_message(entry):
    if entry.get("type") != "user":
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    return any(isinstance(b, dict) and b.get("type") == "text" for b in content or [])


entries = []
try:
    with open(data["transcript_path"], encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except ValueError:
                pass
except (OSError, KeyError):
    sys.exit(0)

start = max((i for i, e in enumerate(entries) if is_real_user_message(e)), default=-1)
touched = []
for e in entries[start + 1:]:
    if e.get("type") != "assistant":
        continue
    for block in (e.get("message") or {}).get("content") or []:
        if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") in EDIT_TOOLS:
            inp = block.get("input") or {}
            path = inp.get("file_path") or inp.get("notebook_path")
            if path:
                touched.append(norm(path))

prefix = allowed_brain_prefix(data.get("cwd"))
project_edits = [p for p in touched if not in_brain(p)]
brain_edits = [p for p in touched if p.startswith(prefix + "/")]
if not project_edits or brain_edits:
    sys.exit(0)

stamp = Path(tempfile.gettempdir()) / f"cerebro-aviso-{data.get('session_id', 'x')}"
if stamp.exists() and time.time() - stamp.stat().st_mtime < QUIET_SECONDS:
    sys.exit(0)
stamp.touch()

print(json.dumps({"decision": "block", "reason": (
    f"Recordatorio del cerebro: en esta respuesta cambiaste archivos de {project} y no anotaste nada en "
    f"`cerebro/proyectos/{project}/`. Si hubo una decisión, una tarea terminada o números nuevos, "
    f"anótalo ahora en `{project}-log.md` y en la página que corresponda, siguiendo `cerebro/AGENTS.md`. "
    "Si no hubo nada de eso, termina sin hacer nada más y sin mencionarlo."
)}))
