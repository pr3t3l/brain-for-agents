"""Copy the brain's global.md into the files Claude Code and Codex load in every session, in any folder.

The copy lives between two markers. Only that block is replaced: whatever you or other tools write outside it
(for example the line Graphify's installer adds to ~/.claude/CLAUDE.md) is kept.
Runs from the brain's git post-commit hook. Edit global.md, never the copies.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run with python -I, so add this folder by hand
from paths import GLOBAL_MARK, SYSTEM, msg  # noqa: E402

HOME = Path.home()
TARGETS = [HOME / ".claude" / "CLAUDE.md", HOME / ".codex" / "AGENTS.md"]
END_MARK = "<!-- brain:global-end -->"


def global_block():
    body = (SYSTEM / "global.md").read_text(encoding="utf-8").rstrip("\n")
    return f"{GLOBAL_MARK}\n<!-- {msg('global_header')} -->\n\n{body}\n\n{END_MARK}\n"


def merged(current, block):
    """Replace our block inside `current`, or put it on top of whatever is already there."""
    if GLOBAL_MARK in current and END_MARK in current:
        before, rest = current.split(GLOBAL_MARK, 1)
        after = rest.split(END_MARK, 1)[1].lstrip("\n")
        return before + block + ("\n" + after if after else "")
    if current.startswith(GLOBAL_MARK):  # older copy without an end marker: it was all ours
        return block
    return block + ("\n" + current if current.strip() else "")


if __name__ == "__main__":
    block = global_block()
    for target in TARGETS:
        if not target.parent.exists():
            continue  # that tool is not installed
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        text = merged(current, block)
        if text != current:
            target.write_text(text, encoding="utf-8")
            print(msg("updated", target=target))
