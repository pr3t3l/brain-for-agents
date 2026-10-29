# Brain for agents

**One place where Claude Code, Codex and you keep everything you know about your projects. It keeps itself up to date, and no AI can mess it up.**

[Versión en español](README.md)

The template and its scripts are in Spanish (the author's working language), and the structure is language-agnostic. This page is a summary.

## Where it comes from

Andrej Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): instead of searching your documents on every question, the AI **writes and maintains a Markdown wiki**. It has three layers (raw sources, AI-maintained pages and a rules file), three routines (ingest, query, lint) and an index and a log. Obsidian is the viewer.

## What this adds

That pattern assumes one wiki, one person and one AI. With several projects and several agents working at once, we added:

- **Global rules** that Claude Code and Codex load in **every** session, in any folder. One source file (`_sistema/global.md`) is copied by a git `post-commit` hook to `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`.
- **A guardian:** a Claude Code `PreToolUse` hook. A session opened inside one project can only write to that project's folder in the brain, plus any `entrada.md` inbox.
- **Write-in-the-moment rule plus a reminder:** a Claude Code `Stop` hook. It reads the local transcript (no model call), and if the turn edited project files without noting anything in the brain, it asks Claude to note it. At most once every 30 minutes.
- **One note per decision** and a live **Obsidian Bases table** of all decisions, grouped by project.
- **Unique file names** (`shop.md`, `shop-marketing.md`…) so Obsidian tabs, search and graph stay readable.
- **A weekly scheduled review** that checks the brain against each project's sources, fixes what it can, merges learnings per channel and leaves at most 5 questions for you.
- **A GitHub backup** on every commit.

Findings we verified by testing: Claude Code loads every `CLAUDE.md` from the working folder up to the filesystem root, even across separate repos. Codex stops at the repo root, which is why the global rules go in the user-level files.

## Install

```bash
git clone https://github.com/pr3t3l/cerebro-para-agentes.git
cp -r cerebro-para-agentes/plantilla ~/Documents/cerebro
```

1. Edit `_sistema/config.json` (your projects folder or folders).
2. Edit `_sistema/global.md` (who you are, your projects, your rules).
3. Run `python -I _sistema/scripts/probar_guardianes.py`. It should print `TODO BIEN`.
4. Run `python -I _sistema/scripts/instalar.py --dry-run`, then run it again without `--dry-run`. It backs up every file it changes.
5. Optional, and recommended: add a private GitHub remote, and schedule the weekly review using `_sistema/revision-semanal.md`.

## Honest limits

- The guardian and the reminder are Claude Code hooks. With Codex, the written rules are the only protection.
- The guardian only watches Claude's file tools, not shell commands.
- Tested in real use on Windows. The scripts are written for macOS and Linux too, but are untested there.

MIT license. Base idea by Andrej Karpathy. Built by Alfredo Pretel (Pretel Ventures) with Claude Code.
