"""Copy the brain's global.md to the files Claude Code and Codex load in every session, in any folder.

Runs from the brain's git post-commit hook. Edit global.md, never the copies.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run with python -I, so add this folder by hand
from paths import GLOBAL_MARK, SYSTEM, msg  # noqa: E402

HOME = Path.home()
TARGETS = [HOME / ".claude" / "CLAUDE.md", HOME / ".codex" / "AGENTS.md"]


def global_copy():
    return f"{GLOBAL_MARK}\n<!-- {msg('global_header')} -->\n\n" + (SYSTEM / "global.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    text = global_copy()
    for target in TARGETS:
        if not target.parent.exists():
            continue  # that tool is not installed
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current.strip() and not current.startswith(GLOBAL_MARK):
            print(msg("not_mine", target=target))
            continue
        if current != text:
            target.write_text(text, encoding="utf-8")
            print(msg("updated", target=target))
