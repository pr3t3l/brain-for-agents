"""Tests for the guardian and the reminder, with made-up folders (your real config is not used or changed).

Usage: python -I probar_guardianes.py
"""
import glob
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAKE = Path(tempfile.gettempdir()) / "cerebro-prueba"
B = FAKE / "cerebro"            # the cerebro
P = FAKE / "proyectos"          # a projects folder
E = FAKE / "empresa"            # a company folder
config = FAKE / "config.json"
config.parent.mkdir(parents=True, exist_ok=True)
config.write_text(json.dumps({"cerebro": str(B), "carpetas_de_proyectos": [str(P)], "carpetas_de_empresa": [str(E)]}), encoding="utf-8")
env = dict(os.environ, CEREBRO_CONFIG=str(config))


def run(script, payload):
    r = subprocess.run([sys.executable, "-I", str(HERE / script)], input=json.dumps(payload).encode("utf-8"),
                       capture_output=True, env=env)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    return r.stdout.decode("utf-8").strip()


def guard(cwd, target):
    out = run("guardian.py", {"cwd": str(cwd), "tool_name": "Edit", "tool_input": {"file_path": str(target)}})
    return "bloquea" if out and json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny" else "permite"


tienda, app = P / "tienda", P / "app-movil"
cases = [
    ("proyecto -> su carpeta del cerebro", tienda / "src", B / "proyectos/tienda/tienda-log.md", "permite"),
    ("proyecto -> carpeta de otro proyecto", tienda / "src", B / "proyectos/app-movil/app-movil-log.md", "bloquea"),
    ("proyecto -> buzón de la empresa", tienda, B / "empresa/entrada.md", "permite"),
    ("proyecto -> su propio código", tienda / "src", tienda / "src/index.ts", "permite"),
    ("proyecto -> reglas del cerebro", tienda, B / "AGENTS.md", "bloquea"),
    ("proyecto -> conocimiento compartido", tienda, B / "conocimiento/canales/instagram.md", "bloquea"),
    ("raíz del cerebro -> cualquier carpeta", B, B / "proyectos/app-movil/app-movil-log.md", "permite"),
    ("cerebro/proyectos/tienda -> tienda", B / "proyectos/tienda", B / "proyectos/tienda/decisiones/x.md", "permite"),
    ("cerebro/proyectos/tienda -> app-movil", B / "proyectos/tienda", B / "proyectos/app-movil/app-movil-log.md", "bloquea"),
    ("empresa -> cerebro/empresa", E / "contabilidad", B / "empresa/empresa.md", "permite"),
    ("empresa -> reglas globales", E, B / "_sistema/global.md", "bloquea"),
    ("fuera de todo -> cualquier carpeta", FAKE / "otra-cosa", B / "proyectos/tienda/tienda-log.md", "permite"),
]
ok = True
for name, cwd, target, want in cases:
    got = guard(cwd, target)
    ok &= got == want
    print(f"{'OK ' if got == want else 'MAL'} guardián: {name}: {got}")

transcript = FAKE / "conversacion.jsonl"
user = {"type": "user", "message": {"content": "haz el cambio"}}
tool_result = {"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}}


def edit(path):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Edit", "input": {"file_path": str(path)}}]}}


code, note = tienda / "src/index.ts", B / "proyectos/tienda/tienda-log.md"


def aviso(session, entries, active=False):
    transcript.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")
    out = run("aviso.py", {"session_id": session, "cwd": str(tienda), "transcript_path": str(transcript), "stop_hook_active": active})
    return "avisa" if out else "calla"


acases = [
    ("editó código sin anotar", "a", [user, edit(code), tool_result], False, "avisa"),
    ("misma sesión antes de 30 minutos", "a", [user, edit(code), tool_result], False, "calla"),
    ("editó código y anotó", "b", [user, edit(code), tool_result, edit(note)], False, "calla"),
    ("sin ediciones", "c", [user], False, "calla"),
    ("segundo intento del mismo final", "d", [user, edit(code)], True, "calla"),
    ("la edición fue en una respuesta anterior", "e", [user, edit(code), tool_result, user], False, "calla"),
]
for name, sid, entries, active, want in acases:
    got = aviso("prueba-" + sid, entries, active)
    ok &= got == want
    print(f"{'OK ' if got == want else 'MAL'} aviso: {name}: {got}")
for p in glob.glob(os.path.join(tempfile.gettempdir(), "cerebro-aviso-prueba-*")):
    os.remove(p)
print("TODO BIEN" if ok else "HAY FALLAS")
sys.exit(0 if ok else 1)
