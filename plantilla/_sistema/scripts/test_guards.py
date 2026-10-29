"""Tests for the guardian and the reminder, with made-up folders. Your real config is read only for its language and
layout; it is not used for paths and nothing is changed.

Usage: python -I test_guards.py
"""
import glob
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
real = json.loads((HERE.parent / "config.json").read_text(encoding="utf-8"))
L = {"projects": "projects", "company": "company", "inbox": "inbox.md", "decisions": "decisions", **real.get("layout", {})}
FAKE = Path(tempfile.gettempdir()) / "brain-test"
B, P, C = FAKE / "brain", FAKE / "projects", FAKE / "company"
config = FAKE / "config.json"
config.parent.mkdir(parents=True, exist_ok=True)
config.write_text(json.dumps({"brain": str(B), "project_folders": [str(P)], "company_folders": [str(C)],
                              "language": real.get("language", "en"), "layout": real.get("layout", {})}), encoding="utf-8")
env = dict(os.environ, BRAIN_CONFIG=str(config))


def run(script, payload):
    r = subprocess.run([sys.executable, "-I", str(HERE / script)], input=json.dumps(payload).encode("utf-8"),
                       capture_output=True, env=env)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    return r.stdout.decode("utf-8").strip()


def guard(cwd, target):
    out = run("guardian.py", {"cwd": str(cwd), "tool_name": "Edit", "tool_input": {"file_path": str(target)}})
    return "blocks" if out and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny" else "allows"


shop, app = P / "shop", P / "mobile-app"
bp, bc = B / L["projects"], B / L["company"]
cases = [
    ("project -> its brain folder", shop / "src", bp / "shop/shop-log.md", "allows"),
    ("project -> another project's folder", shop / "src", bp / "mobile-app/mobile-app-log.md", "blocks"),
    ("project -> company inbox", shop, bc / L["inbox"], "allows"),
    ("project -> its own code", shop / "src", shop / "src/index.ts", "allows"),
    ("project -> brain rules", shop, B / "AGENTS.md", "blocks"),
    ("project -> shared knowledge", shop, B / "knowledge/channels/instagram.md", "blocks"),
    ("brain root -> any folder", B, bp / "mobile-app/mobile-app-log.md", "allows"),
    ("brain project folder -> same project", bp / "shop", bp / "shop" / L["decisions"] / "x.md", "allows"),
    ("brain project folder -> another project", bp / "shop", bp / "mobile-app/mobile-app-log.md", "blocks"),
    ("company -> brain company folder", C / "accounting", bc / "company.md", "allows"),
    ("company -> global rules", C, B / "_system/global.md", "blocks"),
    ("outside everything -> any folder", FAKE / "elsewhere", bp / "shop/shop-log.md", "allows"),
]
ok = True
for name, cwd, target, want in cases:
    got = guard(cwd, target)
    ok &= got == want
    print(f"{'OK ' if got == want else 'BAD'} guardian: {name}: {got}")

transcript = FAKE / "conversation.jsonl"
user = {"type": "user", "message": {"content": "make the change"}}
tool_result = {"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}}


def edit(path):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Edit", "input": {"file_path": str(path)}}]}}


code, note = shop / "src/index.ts", bp / "shop/shop-log.md"


def reminder(session, entries, active=False):
    transcript.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")
    out = run("reminder.py", {"session_id": session, "cwd": str(shop), "transcript_path": str(transcript), "stop_hook_active": active})
    return "reminds" if out else "quiet"


rcases = [
    ("edited code without noting", "a", [user, edit(code), tool_result], False, "reminds"),
    ("same session within 30 minutes", "a", [user, edit(code), tool_result], False, "quiet"),
    ("edited code and noted", "b", [user, edit(code), tool_result, edit(note)], False, "quiet"),
    ("no edits", "c", [user], False, "quiet"),
    ("second try of the same stop", "d", [user, edit(code)], True, "quiet"),
    ("the edit was in an earlier reply", "e", [user, edit(code), tool_result, user], False, "quiet"),
]
for name, sid, entries, active, want in rcases:
    got = reminder("test-" + sid, entries, active)
    ok &= got == want
    print(f"{'OK ' if got == want else 'BAD'} reminder: {name}: {got}")
for p in glob.glob(os.path.join(tempfile.gettempdir(), "brain-reminder-test-*")):
    os.remove(p)
print("ALL GOOD" if ok else "SOMETHING FAILED")
sys.exit(0 if ok else 1)
