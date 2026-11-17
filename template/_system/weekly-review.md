# Weekly review (instructions for a scheduled task)

Paste the text below as the instructions of a weekly scheduled task: in the Claude desktop app, "Scheduled" in the sidebar, or the `/schedule` command in Claude Code. Replace the paths between `{{ }}`.

---

You are the weekly reviewer of {{your name}}'s brain, at `{{full path of the brain}}`. Work from the root of that folder (not a subfolder: the guardian limits sessions opened inside a project), and read `AGENTS.md` and `index.md` first.

Goal: keep the brain true and sourced, so any AI can work on any project without being told everything again.

1. **Health.** Run `python -I _system/scripts/check.py` and fix every failure it reports (each one says the page, the rule and how to fix it); then `python -I _system/scripts/connect.py` so the generated links are up to date. Read its warnings too: a key page too far from a cover, a status that no longer fits one screen, a start rule that stopped naming a required read.
2. **What's new in each project since the last review** (the date is in the last `review` entry of `log.md`). Read, without changing anything outside the brain: {{list of sources per project: decision logs, status files, weekly reports}}. Then create new decision notes with the template, update `<project>-status.md` and `<project>-marketing.md` when a dated source contradicts them, and note each change in `<project>-log.md`. Every fact with its source; with no source, "to confirm".
3. **Gather what publishing taught us.** Read each project's `<project>-learnings.md`, and add what is new to the "What publishing taught us" section of `knowledge/channels/<channel>.md` (date, the project's name as plain text, piece, numbers, lesson). The shared knowledge never links a project by hand: the `Where it applies` block shows who uses each channel.
4. **Review.** Look for pages that contradict a current decision (when a decision replaces another, the old one is marked `replaced` and the sentence is fixed in the pages people enter through), contradictions between pages, status pages not updated in more than 14 days, current decisions that were already replaced, and the "to confirm" items that block the most.
5. **Report.** Write `reviews/review-YYYY-MM-DD.md` with what changed, what you fixed, contradictions, and at most 5 questions for the owner. Link it from `log.md` with `## [YYYY-MM-DD] review | Weekly review`, and put the questions in `company/inbox.md`.
6. **Save.** `git add -A` and `git commit` with a clear message. If there is a remote, check it was pushed.

Every few weeks, or after changing the rules, also run the ten-task test (`docs/the-method.md` of the public repo) and note the result in the report.

Forbidden: editing `sources/`, `_system/global.md` or any file outside the brain; writing credentials or personal data; deleting pages (if something is redundant, propose it in the report).

At the end, answer in 5 lines or fewer: what changed this week and the questions for the owner, with the link to the report.
