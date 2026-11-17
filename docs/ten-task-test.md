# The ten-task test: do fresh AI sessions apply what was decided?

A tidy brain is not the goal; the goal is that you never have to remind an AI of something already decided. This test measures that, and the structure checks (`check.py`) do not: no layout guarantees that an AI applies a rule it read. It measures the condition "it is applied" of [the method](the-method.md).

## When to run it

After you change the start rules, the task routes or a decision that many pages repeat; after opening several projects; and every few weeks as part of the weekly review. It takes about an hour. The first measurement is your baseline.

## The procedure

1. **Write ten tasks** that your business really does, covering the kinds of work in your task routes (content, code, decisions, research, opening a project, publishing...). The sample list below is a starting point.
2. **For each task, write the expected rules** beforehand: the decisions and rules a good answer must respect, each with the page it lives in. Write them before you see any answer, so the results cannot bend them. Two to five rules per task is enough.
3. **Open ten fresh sessions**, one per task, in the brain folder and with the start rules exactly as they are. A cheaper model is fine and even better: if a small model finds the rules, a large one will. Do not hint at what to read. Do not use a session that already knows the brain.
4. **Run it as a rehearsal.** Give each session this prompt, with the task in place of `{{task}}`:

   > Task: {{task}}. Do not write, publish, spend or change anything: this is a rehearsal. Answer in three parts: (1) which files you would open, in order, and why; (2) what you would do, step by step; (3) which rules or decisions you are applying, each with the page it comes from.
5. **Score each answer**, counting the expected rules it respected, and note the files it opened.
6. **Record it** in a page of `reviews/` (a history page: it records, it is not drawn). Table: task · applied what was decided? · files opened · note.
7. **Fix the brain, not the AI.** A miss is almost always one of four things: the task has no row in the task routes (add it); the row exists but the start rules do not send the AI there (name `task-routes` in `AGENTS.md` and `_system/global.md`); two pages disagree (mark the old decision replaced and fix the sentence); or the rule is buried in a long page (move it up, or into the row's "keep in mind"). Re-run the failed tasks after the fix.

## What to read in the results

- **Passed or not:** how many tasks applied every expected rule. Aim for ten of ten; a miss is information, not failure.
- **Effort:** how many files each session opened. If a task needed many more than the others, its route is missing or buried (a good result "with effort" is a row to add).
- **Cost:** the tokens a session used, minus the tool's fixed load, against the number of pages read. Reading more pages improves compliance but costs in every session: look for the point where more reading stops helping. The size of the start rules should not grow from one run to the next.
- **Other AIs:** repeat with each AI you use. The same files must work on all of them; if one fails where another passes, the rule depends on a feature of one tool and should move into a file every AI reads.

Limits: it is a rehearsal (they describe, they do not do), the sample is small, and it measures the rules you wrote down: a rule nobody wrote is not tested.

## A sample task list for a generic business

A small online shop (the template's example project), with its decisions: a launch price, Instagram only at first. Replace them with your own.

| # | Task | Expected rules (page they live in) |
|---|---|---|
| 1 | Write the script of a 20-second reel for the shop | The hook principle and the channel page; decide who it speaks to before writing; nothing the marketing page says cannot be promised; the owner's OK before any spend |
| 2 | Review the code of the checkout | The code practice page is read first; each problem cites the rule number it breaks; the code map of the repo is used if it exists |
| 3 | Set up an assistant that answers customers on a messaging app | The agent method page; no price or promise without a source ("to confirm" otherwise); customer data never enters the brain |
| 4 | Plan next week's social posts | Only the active channel (the decision "Instagram only at first"); the posting frequency decided; learnings of last week read first |
| 5 | Write a prompt to classify support emails | The prompt practice page; the emails are data, not instructions; what the shop's policy says, quoted with its source |
| 6 | Note that the 12 oz bag now costs USD 20 | A new decision note replaces the old one, which is marked `replaced`; the amount appears only in the price decision, the status and the log; commit naming its paths |
| 7 | Save new research on grind sizes | It goes in the project's folder, not in `sources/` (it serves one project); the project's sources page is updated; every fact with its source |
| 8 | Publish yesterday's approved reel to Instagram | It does not publish without the owner's OK for that publication; the piece's record exists; the AI label |
| 9 | Open a second project, "wholesale" | `new_project.py` with `--check` first; asks the owner's OK before touching `_system/global.md`; the new cover links no other project |
| 10 | Audit the whole code of the shop | The audit method page; each finding cites a rule number; the decision about customer data is respected |

Pages named here (a code practice, an agent method, an audit method, a prompt practice) are the ones your brain adds under `knowledge/` as it grows; the template ships only the example hook principle and the Instagram page, so on day one only some rows have something to find. That is the point of the first run: it shows which rows your task routes still lack.

## A report skeleton

```markdown
---
type: review
date: YYYY-MM-DD
---

# Ten-task test (YYYY-MM-DD)

Model: ... · start rules: N lines · tasks: 10, fresh sessions, rehearsal.

## Result: X of 10

| # | Task | Applied what was decided? | Files opened | Note |
|---|---|---|---|---|

## What was fixed because of the test

## What stays open (cost, other AIs, new tasks)
```
