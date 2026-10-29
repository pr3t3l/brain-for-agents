"""Install each template (English and Spanish) into a fake HOME and check every change, without touching your real config.

Usage: python -I tests/test_installer.py
"""
import json
import locale
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
TEMPLATES = {"template": "_system", "plantilla": "_sistema"}
ENC = locale.getpreferredencoding(False)  # python -I ignores PYTHONIOENCODING, so children print in the locale encoding


def check_template(name, system):
    root = Path(tempfile.mkdtemp(prefix=f"install-test-{name}-"))
    home, brain, projects = root / "home", root / "Documents" / "brain", root / "Projects"
    (home / ".claude").mkdir(parents=True)
    (home / ".codex").mkdir()
    (home / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": ["Bash(ls *)"]}, "theme": "dark"}), encoding="utf-8")
    (home / ".claude" / "CLAUDE.md").write_text("my old rules\n", encoding="utf-8")
    (home / ".codex" / "config.toml").write_text('model = "x"\n\n[windows]\nsandbox = "elevated"\n', encoding="utf-8")
    projects.mkdir(parents=True)
    shutil.copytree(REPO / name, brain)
    cfg_path = brain / system / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["project_folders"] = [str(projects)]
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    env = dict(os.environ, USERPROFILE=str(home), HOME=str(home))
    env.pop("BRAIN_CONFIG", None)
    install = [sys.executable, "-I", str(brain / system / "scripts" / "install.py")]

    def run(args, **kw):
        return subprocess.run(args, env=env, capture_output=True, text=True, encoding=ENC, errors="replace", **kw)

    run(install + ["--dry-run"])
    checks = {"dry run changes nothing": (home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8") == "my old rules\n"}
    run(install)
    s = json.loads((home / ".claude" / "settings.json").read_text(encoding="utf-8"))
    codex = tomllib.loads((home / ".codex" / "config.toml").read_text(encoding="utf-8"))
    checks.update({
        "settings keep old content": s.get("theme") == "dark" and "Bash(ls *)" in s["permissions"]["allow"],
        "settings backed up": (home / ".claude" / "settings.json.before-brain").exists(),
        "brain is an additional directory": str(brain) in s["permissions"]["additionalDirectories"],
        "edit rule for the brain": any(r.startswith("Edit(") and r.endswith("/**)") for r in s["permissions"]["allow"]),
        "guardian hook": "guardian.py" in json.dumps(s["hooks"]["PreToolUse"]),
        "reminder hook": "reminder.py" in json.dumps(s["hooks"]["Stop"]),
        "old CLAUDE.md backed up": (home / ".claude" / "CLAUDE.md.before-brain").read_text(encoding="utf-8") == "my old rules\n",
        "global rules in CLAUDE.md": "brain:global-copy" in (home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8"),
        "global rules in Codex AGENTS.md": "brain:global-copy" in (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8"),
        "Codex writable root": str(brain) in codex["sandbox_workspace_write"]["writable_roots"],
        "Codex keeps old content": codex["windows"]["sandbox"] == "elevated",
        "git repo": (brain / ".git").exists(),
        "post-commit hook": (brain / ".git" / "hooks" / "post-commit").exists(),
    })
    run(install)
    s2 = json.loads((home / ".claude" / "settings.json").read_text(encoding="utf-8"))
    checks["original backup survives a second install"] = (home / ".claude" / "CLAUDE.md.before-brain").read_text(encoding="utf-8") == "my old rules\n"
    checks["no duplicate hooks"] = len(s2["hooks"]["PreToolUse"]) == 1 and len(s2["hooks"]["Stop"]) == 1
    checks["no duplicate Codex table"] = (home / ".codex" / "config.toml").read_text(encoding="utf-8").count("[sandbox_workspace_write]") == 1
    g = brain / system / "global.md"
    g.write_text(g.read_text(encoding="utf-8") + "\n- new test rule\n", encoding="utf-8")
    run(["git", "-C", str(brain), "add", "-A"])
    run(["git", "-C", str(brain), "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-q", "-m", "test"])
    checks["commit syncs the global rules"] = "new test rule" in (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
    hook_cmd = s2["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    projects_dir = cfg.get("layout", {}).get("projects", "projects")
    payload = json.dumps({"cwd": str(projects / "shop"), "tool_name": "Edit",
                          "tool_input": {"file_path": str(brain / projects_dir / "other" / "x.md")}})
    r = subprocess.run(hook_cmd, shell=True, input=payload.encode("utf-8"), env=env, capture_output=True)
    checks["installed guardian blocks another project"] = b'"deny"' in r.stdout
    guards = run([sys.executable, "-I", str(brain / system / "scripts" / "test_guards.py")])
    checks["guard tests pass"] = guards.returncode == 0
    shutil.rmtree(root, ignore_errors=True)
    return checks


ok = True
en_scripts = {p.name: p.read_bytes() for p in (REPO / "template" / "_system" / "scripts").glob("*.py")}
es_scripts = {p.name: p.read_bytes() for p in (REPO / "plantilla" / "_sistema" / "scripts").glob("*.py")}
same = en_scripts == es_scripts
ok &= same
print(("OK " if same else "BAD"), "both templates ship identical scripts")
for name, system in TEMPLATES.items():
    print(f"== {name} ==")
    for check, passed in check_template(name, system).items():
        ok &= passed
        print(("OK " if passed else "BAD"), check)
print("ALL GOOD" if ok else "SOMETHING FAILED")
sys.exit(0 if ok else 1)
