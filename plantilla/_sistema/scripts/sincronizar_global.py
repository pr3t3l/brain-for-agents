"""Copy _sistema/global.md to the files Claude Code and Codex load in every session, in any folder.

Runs from the cerebro git post-commit hook. Edit global.md, never the copies.
"""
from pathlib import Path

HOME = Path.home()
SOURCE = Path(__file__).resolve().parents[1] / "global.md"
TARGETS = [HOME / ".claude" / "CLAUDE.md", HOME / ".codex" / "AGENTS.md"]
HEADER = "<!-- Copia automática de cerebro/_sistema/global.md. No la edites aquí: edita esa y haz commit en el cerebro. -->\n\n"

text = HEADER + SOURCE.read_text(encoding="utf-8")
for target in TARGETS:
    if not target.parent.exists():
        continue  # that tool is not installed
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    if current.strip() and not current.startswith(HEADER[:40]):
        print(f"no lo toco: {target} tiene contenido tuyo. Corre instalar.py, que lo respalda antes de reemplazarlo.")
        continue
    if current != text:
        target.write_text(text, encoding="utf-8")
        print(f"actualizado: {target}")
