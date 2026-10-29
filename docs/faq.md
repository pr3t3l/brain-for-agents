# FAQ

These are the questions I asked myself while building it, with the answers we found by testing.

## About the idea

**What is Karpathy's "LLM Wiki" technique?**
Instead of the AI searching your documents every time, it writes and maintains a Markdown wiki that grows with every new source. It has three layers (raw sources, AI-maintained pages and rules), three routines (ingest, query, lint) and an index and a log. [The original](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

**What is Obsidian for here?**
Viewing. The brain is a folder of Markdown files; Obsidian shows it with links, a graph of connections and tables. The AI does not need Obsidian: it reads and writes the files directly.

**What is Graphify? Is it an app like Obsidian?**
No. It is a command-line program that turns a code folder into a knowledge graph (HTML files you open in a browser, plus a report). It is for **code** ("which file does this, and what breaks if I change it?"). The brain is for **what we know and decide**. They complement each other.

## About the structure

**One brain for the whole company, or one per project?**
One for everything, with a folder per project. Projects can link to each other, you see every decision in one table, and there is one repo to back up. If a project someday has partners, its folder can be split out without breaking anything.

**But with one global brain, don't I have to open every chat from there?**
No. The global rules load in every session, wherever you open it. You open the chat in your project and the AI still knows where the brain is.

**What if a chat writes into the wrong project?**
AIs follow rules well, but we don't leave it to trust: the guardian blocks any Claude write into another project's folder. If some work affects another project, the AI leaves a line in that project's inbox (`inbox.md`).

**Why not keep the knowledge inside each project's repo?**
Because it gets copied in every worktree and lives on branches: a decision written on a branch is invisible until it is merged. What changes with the code goes in the code; what we know goes in the brain.

**My Obsidian vault is full of loose dots. Why?**
You probably opened a code folder as a vault: worktrees, `node_modules`, generated files. Excluding them helps, but what remains shows the truth: the documents barely link to each other. A separate brain, with `[[...]]` links, looks like a connected map.

**I have many pages called `index`, `marketing` or `log`. Should I rename them?**
Yes. Obsidian shows the file name in tabs, search and the graph. The rule: every page starts with its project's name (`shop.md`, `shop-marketing.md`), and only the root `index.md` and `log.md` use those names.

**Each project has its own decisions. How do I see them all together?**
Each decision is a note in its project's folder, and `decisions.base` (Obsidian Bases) shows them all in one table grouped by project. It grows by itself.

## About Claude Code and Codex

**Does Claude Code read the `CLAUDE.md` files in parent folders? How far up?**
Yes, all the way to the root of the drive. From `C:\...\projects\shop\app` it would read the ones in `app`, `shop`, `projects`, and so on up to `C:\`. Even when each project is its own repo.

**And Codex?**
Codex stops at the repo root. That is why the global rules go in `~/.codex/AGENTS.md`, which always loads.

**When do I open the chat in the brain, and when in the project?**
Where the thing you will change lives. Code? In the project's folder. Marketing or decisions for one project? In `brain/projects/<project>`. Something across projects? At the root of the brain.

**Do sessions I already had open pick up the new rules?**
The guardian and the reminder do, because Claude Code settings apply live. The global rules don't: they are read when a session starts. Open a new one, or tell the old one to read the brain's `_system/global.md`.

## About keeping it up to date

**People say "update it when the session ends", but I never end sessions. I use them until they compact or fail.**
That is why the rule is **note it in the moment**: when you decide something, when a task is done or when numbers come in. And the reminder nudges the AI if it forgot.

**Where are the rules applied?**
The brain's `AGENTS.md` applies in sessions opened inside the brain. `_system/global.md` (copied to your personal files) applies in every session. The guardian and the reminder live in `~/.claude/settings.json`.

**How does the reminder know you edited files, or that you already noted it? Does it read the conversation?**
It reads the file where Claude Code saves the conversation, but with no AI: it looks for the "edited this file" entries since your last message. If any of them is in the project's folder in the brain, you already noted it.

**When does the reminder fire? Always?**
No. Only when four things are true at once: the chat belongs to a project, that reply edited the project's files, nothing was noted in the brain, and it has not reminded in the last 30 minutes.

**Do the scripts cost tokens?**
Running them doesn't: they are local Python. It costs a little when the guardian blocks or the reminder fires, plus the global rules at the start of each session, and above all the weekly review.

**Does it go stale?**
That is what the weekly review is for. It checks each project's sources, updates, gathers learnings and leaves you at most 5 questions.

## About servers and work

**Do I need my own server or MCP for memory?**
Not to start. I had a server with a database and semantic search, and it fell behind: the AI had to remember to call it, and projects were missing. Markdown in git loads by itself, ships in the same commit as the change and costs nothing. A server only adds semantic search or phone access, and for reading from your phone, GitHub is enough.

**Can I use the same thing at my day job?**
The method, yes. Don't mix the data: build a second brain from the same template, somewhere your employer allows. What you share are the techniques, not the information.
