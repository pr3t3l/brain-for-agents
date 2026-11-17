---
type: routes
---

# Task routes: you are going to do this, read this

The only "before doing X, read Y" table of the brain. Find your task, open the pages in the order they appear and read no more until you need to. If your task is not here, enter through [[index|the front page]] and, once you find the way, add a row here.

It is taken for granted that you already read [[AGENTS|the rules]] and, for the project you work on, its cover and its status.

| You are going to… | Read, in this order | Keep in mind |
|---|---|---|
| Do marketing or content and you do not know where to start | [[knowledge/knowledge\|Shared knowledge]] (channels and principles) → the `<project>-marketing` page of your project | The project's page says what can be promised and what cannot. |
| Plan a post, a reel or a campaign, before writing it | [[knowledge/principles/example-hook-in-the-first-seconds\|The hook principle]] → [[knowledge/channels/instagram\|the channel's page]] | Decide who you talk to and from where before writing; then write. |
| Publish a piece | [[knowledge/channels/instagram\|The channel's page]] → the project's learnings page | Only approved pieces, with the owner's OK. Note the numbers at 48 hours in the learnings page. |
| Write or review code | The project's cover (it says where the repo is) → the repo's code map, if it has one | The code lives in the project's repo, not here. |
| Write a prompt or rules for another AI | The `_system/global.md` rules as a model of short and clear | Say what to do and what good looks like; whatever must never happen is checked by a program or a person afterwards. |
| Record or change a decision | [[_system/templates/decision\|The decision template]] → [[company/company\|company]] (if it concerns the whole company) → [[company/pending\|what waits for the owner]] | One decision = one note. An old decision is never edited: create the new one and mark the old one `replaced`. If it affects another project, leave a line in that project's inbox. |
| Research or look for a source | [[sources/sources\|Sources]] → [[knowledge/knowledge\|shared knowledge]] (each principle carries its source) | A fact with no source is written "to confirm". Raw originals in `sources/` are never rewritten. |
| Save new research or a report | The project's `<project>-sources` page | If it serves one project only, it goes in that project's folder; only what serves several goes in `sources/`. |
| Open a new project | [[AGENTS\|The rules]] → [[_system/templates/status\|the status template]] | The pages are created by a program from the templates: `python -I _system/scripts/new_project.py . <folder> "<Name>"` (without `--check` it writes). |
| Do the weekly review | [[_system/weekly-review\|The weekly review]] → [[company/pending\|what waits for the owner]] → [[company/inbox\|the company inbox]] | The report goes in `reviews/`. |
