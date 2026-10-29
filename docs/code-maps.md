# The brain and the code maps: two memories, nested

The brain answers **"what do we know and what did we decide?"**. A code map answers **"where in the code does this happen, and what breaks if I change it?"**. They are different memories, each living in its own place. The global rules tie them together, so every agent knows both exist.

```text
global rules (~/.claude/CLAUDE.md, ~/.codex/AGENTS.md)   ← loaded in every session, in any folder
 │   "the brain is here; if the repo has a code map, use it first and keep it fresh"
 │
 ├── brain/                                ← knowledge and decisions (Markdown, its own git repo)
 │     projects/shop/shop-sources.md         lists the project's repo and its maps
 │
 └── Projects/shop/                        ← the project's own git repo
       AGENTS.md                             how to query this repo's map and when to rebuild it
       graphify-out/                         the code graph: rebuilt, never edited by hand
```

## Why two, and not one big graph

- **Code changes every hour; decisions don't.** A code map has to be rebuilt from the code. The brain is written by hand (by the AI) at the moment something is decided or learned.
- **Code maps are cheap and exact.** [Graphify](https://github.com/safishamsi/graphify) reads code with tree-sitter (an AST, no model call), so rebuilding a code-only graph costs no tokens.
- **Don't run Graphify on the brain.** Graphify can also read documents, but it does that with Claude (tokens), and the brain's `[[links]]` already make the graph you see in Obsidian. Pointing Graphify at your notes duplicates the brain.
- **Each map stays with its code.** It is rebuilt in the project's repo, so every branch and worktree has the map of its own code.

## Set up a code map for one project (about 10 minutes)

1. Install Graphify (Python 3.10+):
   ```bash
   pip install graphifyy && graphify install
   ```
   On Windows, if application control blocks the generated `graphify.exe`, run it as `python -m graphify …`.
2. In the project's repo, build a **code-only** graph:
   ```bash
   python -m graphify extract . --code-only
   ```
   (Inside Claude Code you can also run `/graphify .`.) It creates `graphify-out/`: `graph.json`, `graph.html` (an interactive map you open in a browser) and `GRAPH_REPORT.md`.
3. Add `graphify-out/` to the repo's `.gitignore`. The graph is regenerated, not committed. Add a `.graphifyignore` for logs, QA dumps and anything large or private.
4. Keep it fresh. Either run `graphify update .` after big code changes (code-only, no tokens), or install its git hook (`graphify hook install`) so it rebuilds on every commit.
5. Tell the agents. Add three lines to the repo's `AGENTS.md`:
   ```markdown
   ## Code map
   For "where is this" and "what breaks if I change it", query the Graphify graph before searching by hand:
   `python -m graphify explain <ExactSymbol> --graph graphify-out/graph.json` or `affected <ExactSymbol> --depth 1`.
   Edges are leads, not proof: read the source and run the tests. Rebuild after big code changes.
   ```
6. Write the map in the project's page in the brain (`<project>-sources.md`), so an agent working from the brain knows it exists too.

The global rules in `template/_system/global.md` already include the general instruction ("if the repo has `MAPS.md` or `graphify-out/`, use it first and follow its update rules"), so steps 5 and 6 add the project-specific detail.

## Tips from real use

- **Ask with exact symbols first** (`explain prepareOrder`, `affected prepareOrder --depth 1`). Broad questions pull in hundreds of nodes.
- **Graph edges are leads, not proof** of runtime behaviour. Read the code and run the tests.
- **Pin the Graphify version** in a small wrapper script, so every agent gets the same graph.
- **Graphify's installer adds a line to `~/.claude/CLAUDE.md`.** That is fine: the brain's sync only replaces its own block in that file (between `brain:global-copy` markers) and keeps everything else.

## Going further: several maps that check themselves

In our largest product, the code map is one of four maps, all linked: **code** (Graphify), **data** (where each business field is stored and which step uses it), **AI-call contracts** (what each model call receives and must return) and **knowledge** (research principles, each with its source passage, hash-pinned). One command shows, for a given AI call, its principles, fields, code and what breaks. Two rules keep them true:

- **Each change updates its map in the same commit.** A commit that changes an AI call's prompt or fields updates its contract file, or says why the contract still holds.
- **A freshness check runs in CI and in a Claude Code hook.** It fails when a map no longer matches the code.

You don't need that to start. One brain plus one Graphify graph per repo gets you most of the way.
