# How it works inside

## 1. Three layers, as in Karpathy's pattern

- **Sources** (`sources/`): raw documents (articles, courses, research). The AI reads and cites them, and never edits them.
- **Pages** (`projects/`, `knowledge/`, `company/`): what the AI writes and maintains. Every fact carries its source or says "to confirm".
- **Rules** (the brain's `AGENTS.md` and `_system/global.md`): how work gets done.

## 2. Why the brain lives apart from the code

My first try was to put the knowledge inside each project's repo. That has two problems:

- **It gets copied many times.** If you work with worktrees (one copy of the repo per agent or branch), every document shows up as many times as you have worktrees. In my case, an Obsidian vault opened on the code folder had about 39,000 notes, almost all of them copies or libraries.
- **It lives on branches.** A decision written on one branch is invisible until that branch is merged.

The rule that came out of it: **what changes together with the code goes in the code** (code maps, contracts, specs your CI checks). **What we know or decide goes in the brain.**

## 3. How Claude Code and Codex load rules

We checked this with tests, not only by reading the docs:

- **Claude Code** reads the `CLAUDE.md` files in the folder where you open the session **and in every folder above it, up to the root of the drive**, even across separate repos. It also always reads `~/.claude/CLAUDE.md`, wherever you open it.
- **Codex** reads `~/.codex/AGENTS.md` and then the `AGENTS.md` files from the **repo root** down to your folder. **It does not look above the repo root.** We tested it with two folders: a "company" folder with one secret word, and a "project" repo inside it with another. Codex only saw the project's word.

That is why the global rules go in the two personal files (`~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`), which always load. To avoid keeping two copies by hand, the source of truth is the brain's `_system/global.md`, and a git `post-commit` hook copies it to both places every time you save the brain. It only replaces the brain's own block in those files (between `brain:global-copy` markers), so lines other tools add, like Graphify's, stay.

Inside the brain, `CLAUDE.md` contains only `@AGENTS.md`, so Claude and Codex read the same rules file.

## 4. The guardian

It is a Claude Code `PreToolUse` hook (`_system/scripts/guardian.py`). Before each of Claude's writes, it looks at two things: **the folder the session was opened in** and **the file Claude wants to write**.

- If the file is not in the brain: allow. It only watches the brain.
- If the session was opened in a project (its code folder or `brain/projects/<project>`): it only allows writing to `brain/projects/<project>/` and to any `inbox.md`.
- If it was opened in a company folder or `brain/company`: only `brain/company/`.
- If it was opened at the root of the brain, or anywhere else: no limit.

When it blocks, Claude gets the reason and the alternative: "add a line to that place's `inbox.md`".

## 5. The reminder

It is a Claude Code `Stop` hook (`_system/scripts/reminder.py`) that runs at the end of each reply. Claude Code saves every conversation as a file on your disk and passes its location to the hook. The script, **without calling any model**:

1. finds your last message;
2. lists the files Claude edited since then;
3. if Claude edited project files and nothing in `brain/projects/<project>/`, it sends Claude a reminder;
4. if there was no decision, finished task or new numbers, Claude finishes without doing anything else.

It fires at most once every 30 minutes per session, only in project sessions, and never twice on the same stop.

## 6. Decisions as notes, plus a live table

Each decision is a file with properties at the top (`type: decision`, `project`, `date`, `status`, `source`). `decisions.base` is an Obsidian Bases view that shows every note with `type: decision`, grouped by project. It grows by itself: each new decision appears in the table.

A decision is never edited. If it changes, a new one is created and the old one is marked `replaced`.

## 7. The weekly review

It is a scheduled Claude task (instructions in `_system/weekly-review.md`) that runs from the root of the brain:

- checks health (broken links, repeated names);
- reads each project's sources and updates statuses and decisions;
- gathers each project's learnings into the channel pages;
- leaves a report with at most 5 questions for you;
- saves and pushes everything.

## 8. Language and layout

`_system/config.json` sets `language` (`en` or `es`) and the folder names (`layout`). The scripts are identical in both templates; only the config changes. That means you can rename folders without touching code.

## 9. How many tokens does it cost?

- **The scripts cost no tokens:** they are local Python.
- **The guardian**, when it blocks, sends Claude a message of about 50 words.
- **The reminder**, when it fires, causes one extra round from Claude.
- **The global rules** (about 500 tokens) load at the start of each session.
- **The weekly review costs the most:** it is a full session once a week. And of course, an AI reading the brain to do its work, which is the whole point.

## 10. Honest limits

- **The guardian and the reminder are Claude Code features.** I could not confirm an equivalent in Codex: there, the protection is the written rule, plus `writable_roots` so it can write to the brain.
- **The guardian only watches Claude's file tools**, not shell commands.
- **Sessions that were already open** do not load the global rules until you start a new one. The guardian and the reminder do apply live.
- **Tested in real use on Windows** (with Git Bash). The scripts are written for macOS and Linux too, but are untested there.
- **If you work for an employer**, do not mix their information into your personal brain. Build a second brain from the same template, somewhere your employer allows.
