# The method: one core, project islands and fixed bridges

How to keep a brain ordered while it grows, on one page. The programs that enforce it are explained in [the programs](the-programs.md); how to measure that it works is in [the ten-task test](ten-task-test.md).

## The problem

A brain that grows turns into a blob. Every new page links to whatever is near it, programs that "connect" pages link everything to everything, and one day the graph is a smear where you cannot tell what belongs to whom or where to enter. It hurts a person looking at the graph and an AI looking for what to read.

Most of the damage comes from your own fixes. The usual ones: a list page that links every item "so nothing is plain text"; a link that every page has identically (it says nothing); labels turned into links to the generic page that explains the label; template links that tie every project to every topic. All of them add lines and remove meaning.

## The idea

- **One core** with what holds for every project: how each channel works, principles with their sources, how we do things.
- **One island per project**, with everything of that project inside.
- **Fixed bridges:** every island reaches the core through the same few doors, and also cites the specific page it really uses.

Eight principles hold it up:

1. **The folder says the layer.** Pages are not moved or tagged to tidy up.
2. **Projects cite the core; the core does not cite projects by hand.**
3. **Each project is an island with two doors:** its cover and its marketing page.
4. **You enter by task** ("you are going to do X, read Y"), with one table: `task-routes.md`.
5. **A link must say something.** What would come out the same on every page is text, not a link.
6. **History is recorded, not drawn.** Nobody navigates by logs.
7. **What can be deduced is written by a program,** and a rule that does not make a check fail is not a rule: a written instruction is not a control.
8. **Move up without moving out:** when something of one project serves all, write the general version as a new page of the core; the project's page stays and cites it.

The test of the core: if tomorrow a project folder is deleted, nothing in the core breaks; and the core can be copied to another business without erasing proper names.

## The layers

The layer of a page comes from its folder and its `type`. It is not written in the page.

| Layer | What lives there | Where |
|---|---|---|
| Door | Where you enter and what to read for each task | `AGENTS.md`, `index.md`, `task-routes.md` |
| Core | What holds for every project | `knowledge/` |
| Islands | Everything of one project | `projects/<project>/` |
| Company | Company decisions, what waits for the owner | `company/` |
| Sources | Raw documents; never rewritten | `sources/` |
| History | What happened, not what is true today: logs, inboxes, pending, reviews, proposals | Recognised by the page's `type`, not by its name |
| System and listings | Rules, templates, programs, generated indexes | `_system/` and the `*-index` pages |

## The link rule

You link toward what is more stable.

| From → to | Rule |
|---|---|
| Island → core | Allowed. Two forms: the fixed bridges of the cover, and a citation of the specific page it uses (a channel, a principle) |
| Island → sources, company | Allowed |
| Island → another island | No. Leave a line in the other one's inbox, or move what is shared up to the core |
| Core → sources | Allowed, to a document that exists in `sources/`. If the source lives elsewhere, name it as text |
| Core → company | Only to decisions |
| Core → island | Never by hand. A program writes it in a "Where it applies" block, only if a live page of that project cites that core page |
| Core → history | No. An approved proposal becomes a new page of the core |
| History → anything | Allowed: it is a record. It is not counted or drawn |
| Anything → history | Only your own project's or zone's (a project may link its log and inbox). One exception, a fixed bridge: the owner's "pending" page |

In five sentences: projects cite the core; the core does not cite projects by hand; an island does not link another island; history records and is not drawn; a link must say something. `check.py` fails on each of them.

## Generated blocks

A page is either written by hand or by a program. When a program needs to put something inside a hand-written page, it uses two markers:

```text
<!-- brain:links:start -->
...what the program writes...
<!-- brain:links:end -->
```

What is between the markers can be deleted and regenerated without loss; what is outside belongs to whoever wrote it. Nobody edits inside a block: the next run reverts it. **The program refuses to write when the end marker is missing**: guessing where a block ends would delete hand-written text (the check and the connector both detect it). Blocks have names, so a page can carry more than one without them stepping on each other.

## The parts of a project

A big island is drawn scattered if every folder hangs on its own. So each folder of a project is a **part** with one **center page** that gathers all its pages, and the project cover links every center, with how many pages it has. Any live page of the project is then at most two hops from its cover. The center is a page you wrote (named `<project>-<folder>`, `<folder>` or `README`, or the only `index` page of the folder) or, if there is none, one the connector generates. A new folder gets tied the next time the connector runs, and the check fails if a folder has no center or a live page is more than two hops away.

## Task routes

`task-routes.md` is the single "before doing X, read Y" table. One row per task: what to read, in order, and what to keep in mind. It is what lets an AI that never saw your brain find the decisions that apply without you reminding it. Two things keep it true: the check fails if a route points to a page that does not exist, and warns if the start rules (`AGENTS.md`, `_system/global.md`) stop naming it (`checks.required_reads` in `config.json`). A short version of the table lives in `_system/global.md`, which every session loads. Add a row every time a task takes an AI longer than it should to find its way.

## Opening a project, repeatably

1. The owner decides. While it is only an idea, the cover alone is enough, and the project is marked `parked`.
2. `python -I _system/scripts/new_project.py . <folder> "<Name>"` creates its pages from the templates, registers it in `config.json`, adds its row to `index.md` and runs the connector. Add `--check` to see what it would do.
3. The cover receives its fixed bridges: task routes, shared knowledge, what waits for the owner, its own inbox. It never links another project.
4. Run `check.py`.

## How to know it works

"The best version" cannot be confirmed; what can be measured is six conditions. The goal behind them: the owner never has to remind an AI of what is already decided.

| Condition | What it means | How it is measured |
|---|---|---|
| It is found | What matters is a few steps from where the AI starts | Hops from each cover to the key pages (`check.py`) |
| It is read unasked | The start rules and skills send the AI to those pages | `checks.required_reads` of `config.json` (`check.py` warns if one is missing) |
| It is applied | The AI uses what was decided in its work | The [ten-task test](ten-task-test.md): fresh sessions, no reminders, counting the rules respected |
| It says the right thing | No two pages contradict each other | Open contradictions, and pages that contradict a current decision (`check.py` warns when a decision "in force" is already replaced) |
| It holds up | Growth does not disorder it | Provoked breakages that the check detects; a new project comes out wired by itself (`test_brain.py`) |
| It is cheap and works on every AI | The start instructions do not grow, and the same files work in Claude, Codex, Kimi, Gemini... | Size of the start rules, which should not rise from one review to the next; rules and reads live in files every AI reads, not in one tool's features |

Two limits: no structure guarantees that an AI applies a rule it read, so you measure the result and not only the order; and sending the AI to read more pages improves compliance but costs more in every session, so look for the point where reading more stops helping.

## Mistakes we made, and what they teach

1. **A page with hundreds of links in the middle.** To make an app's features "not plain text" we created one list page linking each principle each feature reads. It made almost every pair of principles share a neighbour. *A list that links everything is not a map.* Wiring that belongs to one project goes in its island, and links to the topics, not to each principle.
2. **Many pages pointing at one sources index.** The source lived in another repo, so every principle linked an index "so it was not plain text". The index became the biggest page of the graph. *A link every page has says nothing; if the source is not in the brain, leave it as text.*
3. **The same template links in every project.** One block put the same topics and channels in each project's marketing page, and in each topic a link back to every project. All projects looked alike in the drawing, and since every link had its mirror, removing one direction did not remove a line. *A link between a project and a topic exists only if that project really uses it: generate it as the mirror of real citations, not from a list.*
4. **Labels that were not links.** Content cards carried their hook or type as plain text, and the fix pointed them at the generic page that explains the field. *A label becomes a link to its specific concept, by program; never to the generic page about the field.*
5. **Rules that only existed in prose.** Five breakages were provoked on a copy; the weekly review stayed green on all of them. *Principle 7: what matters is checked by a program that fails, not by a report someone reads on Mondays.*
6. **Entry pages that said the opposite of what was decided.** Several pages kept saying something a later decision had changed, and the two old decisions still showed as current. *When a decision replaces another, the same day you mark the old one replaced and fix the sentence in the pages people enter through.*

## What is not done

- Live pages are not moved or renamed to tidy up: skills and code repos cite them by path.
- Logs and generated indexes are not deleted (pages would lose their only entry): they are hidden in the graph views.
- The connector does not run inside the autosave nor before each commit: it writes pages, and that must be a deliberate act.
- The Obsidian graph config is not edited with Obsidian open: it rewrites it on every zoom.

## Importers are an optional pattern

In our own brain, a core section is regenerated from a source that lives elsewhere (a knowledge map exported by an app, a documented course). Those programs are not in this template because they depend on the source's format, but the pattern travels: **validate before writing** (an unknown topic or label stops everything without touching a file), **write everything at once, already with its connections**, call the connector at the end, and store a fingerprint of the hand-written part of each page it writes whole, to notice later that someone edited it by hand. If you have such a source, build the importer on `brain_lib.py` and register its page types in `config.json`.
