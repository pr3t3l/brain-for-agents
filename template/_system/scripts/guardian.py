"""Claude Code PreToolUse hook: a session opened inside a project may only write to that project's folder in the brain.

Sessions opened at the root of the brain, or outside any project, are not limited. Any session may add to an inbox
file (inbox.md / entrada.md). Only covers Claude's file tools (Write, Edit, MultiEdit, NotebookEdit), not shell commands.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run with python -I, so add this folder by hand
from paths import BRAIN, LAYOUT, allowed_brain_prefix, in_brain, msg, norm  # noqa: E402

data = json.loads(sys.stdin.buffer.read().decode("utf-8"))  # Windows consoles are not UTF-8 by default
tool_input = data.get("tool_input") or {}
target = tool_input.get("file_path") or tool_input.get("notebook_path")
if not target or not in_brain(target):
    sys.exit(0)

prefix = allowed_brain_prefix(data.get("cwd"))
t = norm(target)
if prefix is None or t == prefix or t.startswith(prefix + "/") or t.endswith("/" + LAYOUT["inbox"].lower()):
    sys.exit(0)

print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": msg("guard", where=prefix[len(BRAIN) + 1:], inbox=LAYOUT["inbox"]),
}}))
