# Brain: rules for agents

This is the brain: what we know, decide and learn about each project. There is no code here. Code lives in the project folders listed in `_system/config.json`.

It follows Andrej Karpathy's "LLM Wiki" pattern: raw sources nobody edits, pages the AI maintains, and these rules.

## What is where

| Folder | What it holds | Edited? |
|---|---|---|
| `index.md` | The front page: a map of the whole brain | Yes, when pages are created or moved |
| `log.md` | The general log (append only) | Append only |
| `_system/` | `global.md` (rules every AI reads), `templates/`, `scripts/`, `config.json` | Only with the owner's OK |
| `knowledge/` | What serves every project (for example, how each social network works), with sources | From the root of the brain |
| `sources/` | Raw copies of documents | **No.** Read and cite them, never edit |
| `projects/<project>/` | Everything about a project: `<project>.md` (its front page), `<project>-status.md`, `<project>-marketing.md`, `<project>-learnings.md`, `<project>-sources.md`, `<project>-log.md` and `decisions/` | Yes, only from a session of that project |
| `company/` | What cuts across projects | Yes, from a company session; everyone else only appends to `inbox.md` |
| `reviews/` | The weekly review reports | The weekly review |

## How to work

1. **When you start:** read `index.md` and, for the project you are working on, its front page (`<project>.md`) and its status (`<project>-status.md`).
2. **Write in the moment, not at the end.** When the owner decides something, a task is finished or numbers come in, update the right page right then and add a line to `<project>-log.md`. Sessions never close: do not wait for the end.
3. **One decision = one note** in `projects/<project>/decisions/`, using `_system/templates/decision.md`. Never edit an old decision: if it changes, create a new one and mark the old one `replaced`.
4. **Every fact with its source** (a path, a link or "the owner said so on YYYY-MM-DD"). With no source, write "to confirm". Never invent facts, numbers or promises.
5. **Write only in your project's folder.** If your work affects another project or the company, add a line to that place's `inbox.md` (date, where you come from, what changed, what needs deciding) and touch nothing else.
6. **Link with `[[...]]`** using the full path (for example `[[projects/shop/shop-marketing|marketing]]`), so the Obsidian graph shows the connections.
7. **Unique names.** No file repeats another file's name (except decisions, which carry a date). A project's pages start with the project's name. Only the root `index.md` and `log.md` use those names.
8. **Log format:** `## [YYYY-MM-DD] type | title`, with type `decision`, `ingest`, `publication`, `learning`, `review` or `change`.

## Routines

- **Ingest a source:** save the original in `sources/` (or link it if it already lives in a repo), summarize what is useful in the pages it touches, and note it in the log.
- **Query:** answer citing pages. If the answer is worth keeping, save it as a new page.
- **What publishing taught us:** each project notes it in its `<project>-learnings.md` (date, channel, piece, numbers, lesson). The weekly review gathers it into `knowledge/channels/`.
- **Weekly review:** see `_system/weekly-review.md`.

## What takes care of itself

- **Global rules:** `_system/global.md` is copied to `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` after every commit (`_system/scripts/sync_global.py`). Edit only `global.md`.
- **Guardian (Claude Code):** a session opened inside a project (in its code folder or in `brain/projects/<project>`) can only write to `brain/projects/<project>/` and to any `inbox.md`. It does not cover shell commands or Codex: there, rule 5 applies.
- **Reminder (Claude Code):** if a reply changed a project's files and noted nothing, Claude gets a reminder (at most once every 30 minutes per session).
- **Tests:** `python -I _system/scripts/test_guards.py`. **Health:** `python -I _system/scripts/health_check.py`.

## Forbidden

Credentials, keys, passwords, account numbers or personal data. Add your own rules here.
