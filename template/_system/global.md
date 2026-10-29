# Global rules for any AI (Claude Code and Codex)

This file loads in every session, in any folder. Keep it short: the details live in the brain. Replace everything between `{{ }}`.

## Who I am and what I do
I am {{your name}}. My projects: {{project 1 (what it is)}}, {{project 2 (what it is)}}. Today's priority is {{your priority}}.

## Where everything we know lives
- **The brain:** `{{full path of the brain}}`. Start with `index.md` and, if you are working on a project, with `projects/<project>/<project>.md` and `<project>-status.md`.
- **Shared knowledge:** `knowledge/knowledge.md`.
- **Each project's code** lives in `{{projects folder}}`. The brain holds no code.
- **Code maps:** if the repo you work in has `MAPS.md` or a `graphify-out/` folder, query it before searching by hand ("which file does this, and what breaks if I change it?") and follow its `AGENTS.md` rules to keep it fresh. If the repo says nothing, run `graphify update .` after big code changes (code only, no tokens).

## How to work with me
- {{how you want to be talked to; for example: plainly, no jargon}}.
- If in this session I decide something, a task is finished or numbers come in, **note it right then** in the brain, in the folder of the project you are working on, following the brain's `AGENTS.md`. Do not wait for the end: my sessions never close.
- Write only in the folder of the project you are working on. If something affects another project or the company, leave a line in its `inbox.md`.
- Never invent facts, numbers or promises. With no source, write "to confirm".

## Forbidden
- Writing credentials, keys, account numbers or personal data in files.
- {{your own rules; for example: posting to my social accounts without my OK}}.
