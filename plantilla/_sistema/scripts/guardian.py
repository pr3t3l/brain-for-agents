"""Claude Code PreToolUse hook: a session opened inside a project may only write to that project's folder in the cerebro.

Sessions opened at the root of the cerebro, or outside any project, are not limited. Any session may add to an
entrada.md (inbox). Only covers Claude's file tools (Write, Edit, MultiEdit, NotebookEdit), not shell commands.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run with python -I, so add this folder by hand
from rutas import CEREBRO, allowed_brain_prefix, in_brain, norm  # noqa: E402

data = json.loads(sys.stdin.buffer.read().decode("utf-8"))  # Windows consoles are not UTF-8 by default
tool_input = data.get("tool_input") or {}
target = tool_input.get("file_path") or tool_input.get("notebook_path")
if not target or not in_brain(target):
    sys.exit(0)

prefix = allowed_brain_prefix(data.get("cwd"))
t = norm(target)
if prefix is None or t == prefix or t.startswith(prefix + "/") or t.endswith("/entrada.md"):
    sys.exit(0)

where = prefix[len(CEREBRO) + 1:]
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": (
        f"Guardián del cerebro: esta sesión es de `cerebro/{where}` y solo puede escribir ahí. "
        "Si tu trabajo afecta a otro proyecto o a la empresa, agrega una línea en su `entrada.md` "
        "(fecha, de dónde vienes, qué cambió, qué hay que decidir)."
    ),
}}))
