# Brain for agents

**One place where Claude Code, Codex and you keep everything you know about your projects. It keeps itself up to date, and no AI can mess it up.**

[Versión en español](README.es.md)

If you work with several AIs across several projects, you know the problem. Every chat starts from zero, so you explain everything again. Decisions get buried in conversations nobody rereads. And every tool keeps its own "memory" somewhere else.

This repo is the template, and the guide, for how I solved it in my company: several products in parallel, with Claude Code and Codex agents working at the same time. It is meant to be copied in an afternoon.

## Where it comes from

Andrej Karpathy published [the "LLM Wiki" pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Instead of the AI searching your documents on every question, the AI **writes and maintains a Markdown wiki**.

- **Three layers:** raw sources nobody edits, pages the AI maintains, and a rules file.
- **Three routines:** ingest, query and lint.
- **Two files:** an index and a log.

Obsidian is the viewer. Read the original: it is short and very good.

## What this repo adds

Karpathy's pattern is designed for **one wiki, one person and one AI**. Using it with several projects and several agents at once surfaced problems the pattern does not solve. Here is what we added:

| Real problem | What this brain does |
|---|---|
| Every AI starts knowing nothing | **Global rules** that Claude Code and Codex load in **every** session, in any folder, copied automatically from the brain on every commit |
| A chat for one project writes into another project | **Guardian:** a Claude Code hook that blocks any write into another project's folder |
| "Update it when the session ends", but sessions never end | **Write in the moment**, plus a **reminder** that nudges the AI when it changed files and noted nothing |
| Each project's decisions are scattered | **One note per decision**, in its project's folder, plus **one live table** (Obsidian Bases) that shows them all |
| Many pages called `index` or `marketing` in Obsidian | **Unique names:** every page carries its project's name |
| Nobody checks the wiki is still true | **A scheduled weekly review** that checks against the sources, fixes what it can and leaves you at most 5 questions |
| If the computer dies, it is gone | **A GitHub backup** on every commit |
| What one project learns does not help another | **Learnings per project**, gathered by channel in the weekly review |

This is not "better than Karpathy". It is his idea, plus the operating layer you need when several projects and several agents work at once.

## What it looks like

```text
brain/                           ← an Obsidian vault and a (private) git repo
  AGENTS.md  CLAUDE.md           ← the brain's rules
  index.md   log.md              ← front page and log
  decisions.base                 ← live table of every decision
  _system/
    global.md                    ← rules EVERY AI loads, in any folder
    config.json                  ← where your projects live, and the brain's language
    templates/  scripts/  weekly-review.md
  knowledge/                     ← what serves every project: channels, sourced principles
  sources/                       ← raw documents, never edited
  projects/
    shop/                        ← one project: shop.md, shop-status.md, shop-marketing.md,
      decisions/                   shop-learnings.md, shop-sources.md, shop-log.md
  company/   inbox.md            ← what cuts across projects, and the notice inbox
  reviews/                       ← weekly reports
```

Code does **not** live here. Each project stays in its own folder and its own repo; the brain holds what we know, decide and learn.

There are two templates with the same scripts: `template/` in English and `plantilla/` in Spanish. The language and the folder names are set in `_system/config.json`.

## Install it (about 20 minutes)

You need Python 3.11 or newer, git, and Claude Code and/or Codex. Obsidian is optional, just for viewing.

1. **Copy the template** to wherever you want your brain, for example `Documents/brain`:
   ```bash
   git clone https://github.com/pr3t3l/brain-for-agents.git
   cp -r brain-for-agents/template ~/Documents/brain
   ```
2. **Edit `_system/config.json`:** in `project_folders`, put the folder where your projects live (each subfolder is one project). If you have a company folder, put it in `company_folders`.
3. **Edit `_system/global.md`:** who you are, your projects, the brain's path and your rules. Every AI will always read it, so keep it short.
4. **Test the guards:** `python -I _system/scripts/test_guards.py` must print `ALL GOOD`.
5. **Install:** first `python -I _system/scripts/install.py --dry-run` to see what will change, then again without `--dry-run`. It backs up every file before changing it (`*.before-brain`).
6. **Backup (recommended):** create a **private** GitHub repo and connect it (`git remote add origin ...`). From then on, every commit is pushed automatically.
7. **Weekly review (recommended):** create a scheduled task with the text in `_system/weekly-review.md`.
8. Open the folder as a vault in Obsidian, delete the example project `projects/shop` and create your own.

Open a **new** Claude Code or Codex session: global rules load when a session starts.

## How to use it day to day

**Open the chat where the thing you will change lives:**

| What you will do | Open the chat in |
|---|---|
| Write or fix a project's code | The project's code folder |
| Marketing or decisions for **one** project | `brain/projects/<project>` |
| Something across several projects | The root of the brain |

Work as usual. When you decide something or numbers come in, the AI notes it right then. If it forgets, the reminder nudges it. Every week, the review brings everything up to date and leaves you its questions.

## More

- [How it works inside](docs/how-it-works.md), including its honest limits.
- [FAQ](docs/faq.md): every question I asked myself while building it.
- In Spanish: [README](README.es.md), [cómo funciona](docs/es/como-funciona.md), [preguntas frecuentes](docs/es/preguntas.md).

## Credits and license

Base idea: [Andrej Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Built by Alfredo Pretel (Pretel Ventures) with Claude Code. MIT license: use it, copy it and improve it.
