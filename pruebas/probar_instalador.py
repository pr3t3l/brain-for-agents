"""Install the template into a fake HOME and check every change, without touching your real config.

Usage: python -I pruebas/probar_instalador.py
"""
import json, locale, os, shutil, subprocess, sys, tempfile, tomllib
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(__file__).resolve().parents[1] / "plantilla"
root = Path(tempfile.mkdtemp(prefix="instalar-prueba-"))
home, brain, projects = root / "home", root / "Documentos" / "cerebro", root / "Proyectos"
(home / ".claude").mkdir(parents=True)
(home / ".codex").mkdir()
(home / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": ["Bash(ls *)"]}, "theme": "dark"}), encoding="utf-8")
(home / ".claude" / "CLAUDE.md").write_text("mis reglas viejas\n", encoding="utf-8")
(home / ".codex" / "config.toml").write_text('model = "x"\n\n[windows]\nsandbox = "elevated"\n', encoding="utf-8")
projects.mkdir(parents=True)
shutil.copytree(SRC, brain)
cfg = brain / "_sistema" / "config.json"
cfg.write_text(json.dumps({"carpetas_de_proyectos": [str(projects)], "carpetas_de_empresa": []}), encoding="utf-8")
env = dict(os.environ, USERPROFILE=str(home), HOME=str(home), PYTHONIOENCODING="utf-8")
env.pop("CEREBRO_CONFIG", None)


def run(*args, cwd=None):
    r = subprocess.run(list(args), cwd=cwd, env=env, capture_output=True, text=True, encoding=locale.getpreferredencoding(False), errors="replace")
    print(r.stdout.strip(), r.stderr.strip(), sep="\n" if r.stderr.strip() else "")
    return r


print("== dry run ==")
run(sys.executable, "-I", str(brain / "_sistema/scripts/instalar.py"), "--dry-run")
assert (home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8") == "mis reglas viejas\n", "dry run changed files"
print("== install ==")
run(sys.executable, "-I", str(brain / "_sistema/scripts/instalar.py"))
s = json.loads((home / ".claude" / "settings.json").read_text(encoding="utf-8"))
checks = {
    "settings keeps old content": s.get("theme") == "dark" and "Bash(ls *)" in s["permissions"]["allow"],
    "settings backed up": (home / ".claude" / "settings.json.antes-del-cerebro").exists(),
    "additionalDirectories": str(brain) in s["permissions"]["additionalDirectories"],
    "edit rule": any("cerebro/**" in r for r in s["permissions"]["allow"]),
    "guardian hook": "guardian.py" in json.dumps(s["hooks"]["PreToolUse"]),
    "aviso hook": "aviso.py" in json.dumps(s["hooks"]["Stop"]),
    "old CLAUDE.md backed up": (home / ".claude" / "CLAUDE.md.antes-del-cerebro").read_text(encoding="utf-8") == "mis reglas viejas\n",
    "global in CLAUDE.md": "Reglas globales" in (home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8"),
    "global in codex AGENTS.md": "Reglas globales" in (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8"),
    "codex writable root": str(brain) in tomllib.loads((home / ".codex" / "config.toml").read_text(encoding="utf-8"))["sandbox_workspace_write"]["writable_roots"],
    "codex keeps old content": tomllib.loads((home / ".codex" / "config.toml").read_text(encoding="utf-8"))["windows"]["sandbox"] == "elevated",
    "git repo": (brain / ".git").exists(),
    "post-commit hook": (brain / ".git" / "hooks" / "post-commit").exists(),
}
print("== second install is idempotent ==")
run(sys.executable, "-I", str(brain / "_sistema/scripts/instalar.py"))
s2 = json.loads((home / ".claude" / "settings.json").read_text(encoding="utf-8"))
checks["original backup survives a second install"] = (home / ".claude" / "CLAUDE.md.antes-del-cerebro").read_text(encoding="utf-8") == "mis reglas viejas" + chr(10)
checks["no duplicate hooks"] = len(s2["hooks"]["PreToolUse"]) == 1 and len(s2["hooks"]["Stop"]) == 1
checks["no duplicate codex table"] = (home / ".codex" / "config.toml").read_text(encoding="utf-8").count("[sandbox_workspace_write]") == 1
print("== commit triggers sync ==")
(brain / "_sistema" / "global.md").write_text((brain / "_sistema" / "global.md").read_text(encoding="utf-8") + "\n- regla nueva de prueba\n", encoding="utf-8")
run("git", "-C", str(brain), "add", "-A")
run("git", "-C", str(brain), "-c", "user.name=prueba", "-c", "user.email=prueba@example.com", "commit", "-q", "-m", "prueba")
checks["sync after commit"] = "regla nueva de prueba" in (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
print("== guardian with the installed hook command ==")
hook_cmd = s2["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
payload = json.dumps({"cwd": str(projects / "tienda"), "tool_name": "Edit", "tool_input": {"file_path": str(brain / "proyectos" / "otro" / "x.md")}})
r = subprocess.run(hook_cmd, shell=True, input=payload, env=env, capture_output=True, text=True, encoding=locale.getpreferredencoding(False), errors="replace")
checks["installed guardian blocks"] = '"deny"' in r.stdout
for k, v in checks.items():
    print(("OK " if v else "MAL"), k)
print("TODO BIEN" if all(checks.values()) else "HAY FALLAS")
shutil.rmtree(root, ignore_errors=True)
