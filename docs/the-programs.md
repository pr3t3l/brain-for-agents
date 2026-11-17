# The programs: how the connector, the check, the hooks and the autosave fit together

Everything lives in `_system/scripts/` (`_sistema/scripts/` in the Spanish template) and runs with `python -I`, which keeps stray files out of Python's import path. They are local Python: **they cost no tokens**. The method they enforce is in [the method](the-method.md).

## Who does what

| Program | What it does | Writes? |
|---|---|---|
| `config.json` | The single list of projects, page types, zones, bridges, limits and checks. No program names a project or a page: it all comes from here | (you edit it) |
| `brain_lib.py` | What the others share: reading and writing while keeping each file's line endings, the page header, link resolution, the layer of a page, the generated blocks | no |
| `connect.py` | **The only connector.** Writes every generated link: the bridges and parts of each project cover, the center page of a folder that has none, and "Where it applies" on the core pages a project cites. Running it twice changes nothing the second time; `--check` writes nothing | yes, only inside blocks |
| `check.py` | **The only checker.** Read only; exits with 1 if a rule is broken. Replaces the older `health_check.py` (its broken links, repeated names, decision tags and "to confirm" counts are all in here) | no |
| `new_project.py` | Opens a project: pages from templates, registers it in `config.json`, adds its row to `index.md`, runs the connector | yes |
| `apply_views.py` | Puts colors by layer and by project, the default filter and one bookmark per view into Obsidian's graph, from `_system/obsidian/views.json` and `config.json`. Only with Obsidian closed | `.obsidian/` |
| `autosave.py` | Keeps the folder and the remote equal: saves what was left unsaved, pulls, pushes. Runs the check first and never lets a failure stop the save | git |
| `_system/hooks/pre-commit` | Runs `check.py`; blocks a commit while it fails | no |
| `_system/hooks/post-commit` | Runs `sync_global.py` and pushes in the background | `~/.claude`, `~/.codex` |
| `sync_global.py`, `install.py`, `guardian.py`, `reminder.py`, `paths.py` | The global rules, the installer, the guardian and the reminder, as in [how it works inside](how-it-works.md) | see there |
| `test_brain.py`, `test_guards.py` | The tests, on temporary copies; your brain and your real HOME are never touched | no |

## How the pieces fit

```text
you or an AI edit a page
        │
        ▼
 connect.py   ← run after creating a page or a folder (never automatic: it writes pages)
        │
        ▼
 git commit ──► pre-commit hook ──► check.py ──fails──► the commit does not go in; whoever sees it fixes it,
        │                                                even if the failure came from another session
        ▼ passes
 post-commit hook ──► sync_global.py (global.md → ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md) ──► push

 every 10 minutes: autosave.py ──► saves what stayed unsaved (with BRAIN_AUTOSAVE=1 the hook lets it through),
                                   runs check.py and writes any failure in the commit message ──► pull ──► push
 every week: the review runs check.py and connect.py and reads the warnings
```

The one subtle point is the autosave. The hook blocks people and AIs because a broken page that gets in becomes everyone's problem; the autosave must not block because losing work is worse than saving a page that breaks a rule. So it passes the hook through with an environment variable, runs the check itself, and writes the failures in its commit message and in `.git/brain-autosave.log`. The next session sees the failures at its first commit and fixes them.

## The check, rule by rule

**Fails** (exit 1): a generated block without its end marker; a broken link (a link to a missing page from a history page only warns); a task route that does not exist; a fixed bridge to a missing page; a hand-written link island → island, core → island, core → history, core → company (decisions aside), or to the history of another zone; a link from the core to history inside a generated block; a hand-written page with more than `max_links_hand` links; more than `max_cite_decision` core pages linking one decision; a project folder not registered, a registered one without its minimum pages or folder; a folder of a project without a center page; a live page more than `hops` hops from its cover; a decision without its header tag; two pages with the same name (decisions, inboxes and raw sources aside).

**Warns** (exit 0): running the connector would change something; a key page more than `hops` hops from a cover; one link that is the same in most pages of a group; a status page over one screen; a log over its size limit; a page with a type `config.json` does not know; a decision "in force" already replaced by another; a start file that no longer names a required read; frozen links that no longer exist; working copies inside the brain.

Each message gives the page, the rule and how to fix it. The links that already broke a rule on the day you adopt it go in `checks.frozen` of `config.json`: the check fails only for a new one, and warns when a frozen one is no longer needed.

`test_brain.py` provokes the breakages (a damaged marker, an island-to-island link, a core-to-island link, a core-to-history link, a broken task route, an unregistered project, a decision without its tag, a page with too many links, a folder without a center) and verifies the check fails on each, that the connector refuses a damaged page without touching it, that a rebuild from nothing gives the same brain, and that a new project comes out wired and with 0 failures. A check that was never seen to fail is not a check.

## The configuration

| Key | What it is |
|---|---|
| `layout` | The words that depend on the language: folder names, the decision tag, the header keys (`type`/`tipo`...). The reason the same scripts work in both languages |
| `projects` | `{folder: {name, marketing, parked}}`. `parked` is an idea: only its cover is required |
| `project_pages` | The minimum pages of a project and the template of each |
| `types` | The valid page types; which are history; which no program writes into |
| `zones`, `root_pages` | Folder → layer (island, core, company, sources, history, system) |
| `raw` | Folders of raw documents: no program writes in them and the check asks nothing of them |
| `parts` | How the center page of each project folder is chosen or generated |
| `bridges` | The fixed bridges of every project cover |
| `cited` | What a cover shows it cites from the core, and the core pages that get "Where it applies" |
| `limits` | Caps: links per page, hops, sizes |
| `checks` | Task routes page, key pages, required reads, frozen links |

To add a project: `new_project.py`. To add a fixed bridge: one line in `bridges`. To support another AI tool: one line in `TARGETS` of `sync_global.py`.

## Hooks and the autosave, step by step

- **Activate the hooks** (the installer does it): `git config core.hooksPath _system/hooks`. They live in the brain, so they are versioned with it. If you already use `core.hooksPath` for something else, the installer does not touch it and tells you.
- **Hooks are shell scripts:** `.gitattributes` forces LF endings on them so a Windows checkout does not break them. They find Python as `python3` or `python`.
- **Schedule the autosave** every 10 minutes: on Windows, Task Scheduler with the action `python -I <brain>\_system\scripts\autosave.py`; on macOS or Linux, cron: `*/10 * * * * python3 -I <brain>/_system/scripts/autosave.py`. It needs a remote (`git remote add origin ...`) to push; without one it saves locally and says so. Try it first with `--dry-run`.
- It never saves files named like a key or a credential (`.env`, `*.pem`, `*.key`, `*secret*`, `*token*`...), does nothing while another git command runs, and if a pull collides it undoes the merge and writes the collision in its log instead of forcing anything.
- `.gitattributes` makes git merge logs and inboxes by union, so two sessions appending at the end at the same time keep both entries.

## The graph views

History is recorded, not drawn, so the views hide it. `views.json` has a color per layer, a color per project (new projects take one from `spare_colors`) and five views: the whole brain, a clean map, the shared core, one per project, and history only. `python -I _system/scripts/apply_views.py . --all` writes them into `.obsidian/graph.json` and bookmarks; `--dry-run` says what would change. It refuses to write if Obsidian is open or if it cannot tell.

## Why the scripts exist once per template, identical

The repo ships two complete templates, English (`template/`) and Spanish (`plantilla/`), because you copy one folder. Each has its own `_system/scripts`, and the two copies are **byte-identical**: everything that depends on the language is in `config.json` (`layout`) and in `views.json`; the messages are written in both languages inside the programs. `tests/test_installer.py` fails if the copies differ, so you edit the English ones and copy them over. Hooks follow the same rule: they find their own folder, so they do not name `_system` or `_sistema`.

## What was not ported, on purpose

The importers of our own brain (a program that regenerates a core section from an app's export, another from a documented course) and the lists of contradictions between sources are specific to those sources. They are described as an optional pattern at the end of [the method](the-method.md).

## Limits

- The guardian and the reminder are Claude Code features; the check, the hooks and the autosave work with any AI because they are git and files.
- The check reads Markdown links (`[[...]]` and `[text](page.md)`); it does not understand prose. A page that says the opposite of a decision without linking it is only caught by the ten-task test and the weekly review.
- Tested on Windows with Git Bash. Written for macOS and Linux too, untested there.
