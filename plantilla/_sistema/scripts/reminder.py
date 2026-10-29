"""Claude Code Stop hook: remind a project session to write to the brain when it changed files but noted nothing.

Fires only in sessions opened inside a project, only when this turn edited files outside the brain with Claude's
file tools and wrote nothing to the project's brain folder, and at most once every 30 minutes per session.
It reads the conversation file Claude Code keeps on disk; it does not call any model.
"""
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run with python -I, so add this folder by hand
from paths import BRAIN, allowed_brain_prefix, in_brain, msg, norm, session_scope  # noqa: E402

EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
QUIET_SECONDS = 30 * 60

data = json.loads(sys.stdin.buffer.read().decode("utf-8"))  # Windows consoles are not UTF-8 by default
if data.get("stop_hook_active"):
    sys.exit(0)
kind, project = session_scope(data.get("cwd"))
if kind != "project":
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

stamp = Path(tempfile.gettempdir()) / f"brain-reminder-{data.get('session_id', 'x')}"
if stamp.exists() and time.time() - stamp.stat().st_mtime < QUIET_SECONDS:
    sys.exit(0)
stamp.touch()

print(json.dumps({"decision": "block", "reason": msg("reminder", project=project, folder=prefix[len(BRAIN) + 1:])}))
