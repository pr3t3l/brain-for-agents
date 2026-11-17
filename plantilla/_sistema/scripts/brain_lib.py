"""Shared helpers for the brain programs (connect.py, check.py, new_project.py, apply_views.py and the tests).

One copy of each thing: the configuration (config.json), reading and writing while keeping each file's line endings,
the page header, link resolution, the layer of a page (from its path and its `type`) and the generated blocks.
Nothing here knows a project, a topic or a page by name: all of that lives in config.json. Every word that depends on
the language (folder names, header keys) comes from `config.json` -> `layout`, so the same file ships in both templates.

Generated blocks sit between two marker lines:
    <!-- brain:NAME:start -->  ...  <!-- brain:NAME:end -->
A program only ever rewrites what is between its own markers. If a start marker has no end marker (or the markers are
otherwise unpaired), the block functions REFUSE to touch the page and raise BlockDamaged: guessing where the block ends
would delete hand-written text.

The programs run with `python -I`, which does not put the script folder on sys.path, so each one starts with:
    import sys; from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import brain_lib as lib
"""
import collections
import json
import os
import re
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
SYSTEM_NAMES = ("_system", "_sistema")
GEN_KEY, GEN_VALUE = "generated_by", "connect.py"  # header of the pages connect.py writes whole


# ---------------------------------------------------------------- configuration
def config_path(root=None):
    """config.json of the brain at `root` (its _system or _sistema folder); next to the scripts when `root` is None."""
    if root is not None:
        for name in SYSTEM_NAMES:
            candidate = Path(root) / name / "config.json"
            if candidate.exists():
                return candidate
    return HERE.parent / "config.json"


def load_config(root=None):
    return json.loads(config_path(root).read_text(encoding="utf-8"))


def dumps_config(obj, indent=0):
    """JSON a person can read: one key per line, short lists on a single line. The same data always gives the same
    text, so a program can rewrite config.json without reshuffling it."""
    pad = "  " * (indent + 1)
    flat = json.dumps(obj, ensure_ascii=False)
    if not isinstance(obj, (dict, list)) or not obj:
        return flat
    if isinstance(obj, list) and len(flat) <= 150 and not any(isinstance(x, dict) for x in obj):
        return flat
    if isinstance(obj, dict) and indent > 1 and len(flat) <= 110 and not any(isinstance(v, (dict, list)) for v in obj.values()):
        return flat
    if isinstance(obj, dict):
        items = [f"{pad}{json.dumps(k, ensure_ascii=False)}: {dumps_config(v, indent + 1)}" for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + "\n" + "  " * indent + "}"
    return "[\n" + ",\n".join(pad + dumps_config(x, indent + 1) for x in obj) + "\n" + "  " * indent + "]"


def save_config(cfg, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(dumps_config(cfg) + "\n")


# ---------------------------------------------------------------- reading and writing
def read(path):
    """(text with LF line ends, True when the file on disk uses CRLF)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    return raw.replace("\r\n", "\n"), "\r\n" in raw


def write(path, text, crlf=None):
    """Write `text` (LF inside) keeping the line endings the file already has; a new file gets LF.

    Returns True when the bytes on disk changed. Never uses the platform default (on Windows that is CRLF)."""
    path = Path(path)
    old, old_crlf = read(path) if path.exists() else (None, False)
    if crlf is None:
        crlf = old_crlf
    if old is not None and old == text and crlf == old_crlf:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n") if crlf else text)
    return True


# ---------------------------------------------------------------- page header
_FRONT = re.compile(r"\A---\n(.*?)\n---", re.S)


def front(text):
    """The simple `key: value` pairs of the header (values without their quotes)."""
    m = _FRONT.match(text)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        if ":" in line and not line.startswith((" ", "#", "-")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def title_of(text, default=""):
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else default


# ---------------------------------------------------------------- generated blocks
_MARK = re.compile(r"^<!-- brain:([a-z0-9][a-z0-9-]*):(start|end) -->$")


class BlockDamaged(ValueError):
    """A generated block whose markers are not a clean start/end pair. The page must not be rewritten."""


def markers(name):
    return f"<!-- brain:{name}:start -->", f"<!-- brain:{name}:end -->"


def find_blocks(text):
    """{name: (first line index, last line index)} of every generated block.

    Raises BlockDamaged when a start has no end, an end has no start, blocks are nested or a name repeats. A marker shown
    as an example inside a fenced code block is hand-written text, not a block."""
    found, open_name, open_at, fence = {}, None, None, None
    fence_at, mark_in_fence = None, None
    for i, line in enumerate(text.split("\n")):
        s = line.strip()
        if open_at is None and s.startswith(("```", "~~~")):
            if fence and s.startswith(fence):
                fence = None
            elif not fence:
                fence, fence_at, mark_in_fence = s[:3], i, None
            continue
        if fence:
            if mark_in_fence is None and _MARK.match(s):
                mark_in_fence = i
            continue
        m = _MARK.match(s)
        if not m:
            continue
        name, kind = m.group(1), m.group(2)
        if kind == "start":
            if open_at is not None:
                raise BlockDamaged(f"the block '{open_name}' that starts at line {open_at + 1} has no end marker")
            if name in found:
                raise BlockDamaged(f"the block '{name}' appears twice (line {i + 1})")
            open_name, open_at = name, i
        else:
            if open_at is None or open_name != name:
                raise BlockDamaged(f"there is an end marker for the block '{name}' without its start (line {i + 1})")
            found[name] = (open_at, i)
            open_name, open_at = None, None
    if fence and mark_in_fence is not None:
        # An unclosed fence would hide every marker after it: the block would look missing and a new one would be added.
        raise BlockDamaged(f"the code fence {fence} that opens at line {fence_at + 1} is never closed and hides the "
                           f"marker at line {mark_in_fence + 1}; close the fence")
    if open_at is not None:
        raise BlockDamaged(f"the block '{open_name}' that starts at line {open_at + 1} has no end marker")
    return found


def strip_blocks(text):
    """The hand-written text: the page without any generated block."""
    spans = sorted(find_blocks(text).values())
    if not spans:
        return text
    lines, out, at = text.split("\n"), [], 0
    for a, b in spans:
        out += lines[at:a]
        at = b + 1
    out += lines[at:]
    return "\n".join(out)


def set_block(text, lines, name, before=None):
    """Text with the block `name` replaced by `lines`; `lines` empty or None removes the block.

    before: a line prefix (for example "## Sources"). A new block goes in front of the first line outside any
    generated block that starts with it; without it (or when nothing matches) an existing block stays where it is and a
    new one goes at the end of the page. Raises BlockDamaged instead of guessing when the markers are damaged: the
    caller must then leave the page alone."""
    spans = find_blocks(text)
    start, end = markers(name)
    block = [start, *lines, end] if lines else None
    all_lines = text.split("\n")
    span = spans.get(name)

    if span is not None:
        rest = all_lines[:span[0]] + all_lines[span[1] + 1:]
        shift = span[1] - span[0] + 1
        others = [(a, b) if b < span[0] else (a - shift, b - shift) for n, (a, b) in spans.items() if n != name]
    else:
        rest, others = all_lines, list(spans.values())

    if block is None:
        if span is None:
            return text
        head, tail = "\n".join(rest[:span[0]]).rstrip("\n"), "\n".join(rest[span[0]:]).strip("\n")
        return (head + "\n\n" + tail + "\n") if head and tail else ((head or tail) + "\n")

    at = None
    if before:
        inside = set()
        for a, b in others:
            inside.update(range(a, b + 1))
        at = next((i for i, l in enumerate(rest) if i not in inside and l.startswith(before)), None)
    if at is None and span is not None:
        at = span[0]  # stays where it was
    if at is None:
        body = "\n".join(rest).rstrip("\n")
        return (body + "\n\n" if body.strip() else "") + "\n".join(block) + "\n"
    head = "\n".join(rest[:at]).rstrip("\n")
    tail = "\n".join(rest[at:]).strip("\n")
    out = (head + "\n\n" if head else "") + "\n".join(block) + "\n"
    if tail:
        out += "\n" + tail + "\n"
    return out


# ---------------------------------------------------------------- the brain in memory
_WIKI = re.compile(r"!?\[\[([^\]|#]+)")
_MDLINK = re.compile(r"\]\(([^)#\s:]+)\.md")


class Brain:
    """Every visible page of the brain, read once. Programs change the texts in memory and call save() at the end, so a
    run either leaves a page as it should be or does not touch it."""

    def __init__(self, root, config=None):
        self.root = Path(root)
        self.cfg = config if config is not None else load_config(self.root)
        self.layout = self.cfg["layout"]
        self.text, self.disk, self.crlf = {}, {}, {}
        for p in sorted(self.root.rglob("*.md")):
            rel = p.relative_to(self.root)
            if any(part.startswith(".") for part in rel.parts):
                continue  # .obsidian, .git, tool folders: not pages
            key = rel.with_suffix("").as_posix()
            self.text[key], self.crlf[key] = read(p)
            self.disk[key] = self.text[key]
        self.others = {p.relative_to(self.root).as_posix() for p in self.root.rglob("*.base")
                       if not any(part.startswith(".") for part in p.relative_to(self.root).parts)}
        types = self.cfg.get("types", {})
        self.history_types = set(types.get("history", []))
        self.no_block_types = set(types.get("no_blocks", []))
        self.listing_suffix = self.cfg.get("listing_suffix", "-index")
        self._index()

    def _index(self):
        self.byname = collections.defaultdict(list)
        for rel in self.text:
            self.byname[PurePosixPath(rel).name].append(rel)
        for name in self.byname:
            self.byname[name].sort(key=lambda r: (r.count("/"), r))

    # -- pages
    def path(self, rel):
        return self.root / (rel + ".md")

    def set(self, rel, text):
        new = rel not in self.text
        self.text[rel] = text
        if new:
            self.crlf[rel] = False
            self._index()

    def delete(self, rel):
        if rel in self.text:
            del self.text[rel]
            self._index()

    def front(self, rel):
        return front(self.text[rel])

    def type(self, rel):
        return self.front(rel).get(self.layout["type_key"], "")

    def title(self, rel):
        return title_of(self.text[rel], PurePosixPath(rel).name)

    def hand(self, rel):
        """The page without its generated blocks. A page with damaged markers is returned whole."""
        try:
            return strip_blocks(self.text[rel])
        except BlockDamaged:
            return self.text[rel]

    # -- links
    def resolve(self, target):
        """The page a [[link]] points to: the full path, or the page with that name (shallowest path first)."""
        t = target.strip().rstrip("\\")
        if t in self.text:
            return t
        if t.endswith(".md") and t[:-3] in self.text:
            return t[:-3]
        hits = self.byname.get(PurePosixPath(t).name)
        return hits[0] if hits else None

    def links(self, rel, text=None):
        """Pages that `text` (default: the whole page) links to, from [[wiki]] links and [text](other.md) links."""
        text = self.text[rel] if text is None else text
        here, out = PurePosixPath(rel).parent, set()
        for t in _WIKI.findall(text):
            d = self.resolve(t)
            if d and d != rel:
                out.add(d)
        for t in _MDLINK.findall(text):
            d = os.path.normpath((here / t.replace("%20", " ")).as_posix()).replace("\\", "/")
            if d in self.text and d != rel:
                out.add(d)
        return out

    # -- layers: door, core, island, company, sources, history, listing, system
    def project(self, rel):
        """The project folder a page belongs to, or None."""
        parts = rel.split("/")
        return parts[1] if parts[0] == self.layout["projects"] and len(parts) > 2 else None

    def zone(self, rel):
        if "/" not in rel:
            return self.cfg.get("root_pages", {}).get(rel, "root")
        for z in self.cfg.get("zones", []):
            if rel.startswith(z["path"]):
                return z["layer"]
        return "root"

    def is_history(self, rel):
        return self.type(rel) in self.history_types or self.zone(rel) == "history"

    def is_listing(self, rel):
        """A generated listing: a `*-index` page or any page a program writes whole (`generated_by` in its header)."""
        return rel.endswith(self.listing_suffix) or GEN_KEY in self.front(rel)

    def is_live(self, rel):
        """A page that says what is true today: not history and not a generated listing."""
        return not self.is_history(rel) and not self.is_listing(rel)

    def layer(self, rel):
        """The layer of a page, from its path and its type. Nothing is written in the pages: history is decided by the
        type of the page, not by its name."""
        if self.is_history(rel):
            return "history"
        if self.is_listing(rel):
            return "listing"
        return self.zone(rel)

    def is_raw(self, rel):
        """A raw document, saved as it came: config.json `raw`. Never rewritten."""
        return any(rel == x.rstrip("/") or rel.startswith(x) for x in self.cfg.get("raw", []))

    def allows_blocks(self, rel):
        """False for pages no program may write into: logs, inboxes, decisions and the raw sources."""
        return not self.is_raw(rel) and self.type(rel) not in self.no_block_types

    # -- parts of a project
    def parts(self, p):
        """The parts of project `p`: {folder: (center, generated)}.

        A part is each direct folder of projects/<p>/ that holds at least one page that is neither history nor a
        generated listing (subfolders included). Its center is the page that gathers all its pages, chosen by
        config.json `parts`, in this order:
          1. `centers`: an entry "<p>/<folder>" or "<folder>" naming the page; `{p}` is the project;
          2. a page at the root of the folder named like `names` (for example {p}-{folder} or README);
          3. the only page at the root of the folder whose type is `center_type`.
        A candidate must be able to hold a generated block (not raw, not history, not a decision). Without a center,
        the part gets a generated one, `generated_name`: inside the folder, or next to it (at the root of the project)
        when the folder is raw or listed in `outside_folder` (a decisions folder only holds decisions). generated is
        True for that page. It never ends in the listing suffix, so the graph views never hide it."""
        cfg = self.cfg.get("parts", {})
        suffix = cfg.get("suffix_if_clash", "-part")
        base = f"{self.layout['projects']}/{p}/"
        folders = sorted({r[len(base):].split("/")[0] for r in self.text
                          if r.startswith(base) and "/" in r[len(base):] and self.is_live(r)})
        centers, out = cfg.get("centers", {}), {}
        for f in folders:
            folder = base + f + "/"

            def valid(rel):
                return rel in self.text and self.is_live(rel) and self.allows_blocks(rel)

            fixed = centers.get(f"{p}/{f}") or centers.get(f)
            fixed = fixed.format(p=p, folder=f) if fixed else None
            if fixed and (valid(fixed) or (fixed in self.text and self.front(fixed).get(GEN_KEY) == GEN_VALUE)):
                out[f] = (fixed, False)
                continue
            beside = self.is_raw(folder) or f in cfg.get("outside_folder", [])
            casa = base if beside else folder
            gen = casa + cfg.get("generated_name", "{p}-{folder}").format(p=p, folder=f)
            cand = [folder + n.format(p=p, folder=f) for n in cfg.get("names", [])]
            center_type = cfg.get("center_type")
            if center_type:
                roots = [r for r in self.text if r.startswith(folder) and "/" not in r[len(folder):]
                         and self.type(r) == center_type and valid(r)]
                cand += roots if len(roots) == 1 else []
            center = next((x for x in cand if valid(x)), None)
            if center:
                out[f] = (center, False)
                continue
            if gen.endswith(self.listing_suffix):
                gen += suffix

            def free(rel):
                if rel in self.text and self.front(rel).get(GEN_KEY) != GEN_VALUE:
                    return False  # a page somebody wrote: never overwritten
                return all(x == rel or (x.startswith(folder) and self.front(x).get(GEN_KEY) == GEN_VALUE)
                           for x in self.byname.get(PurePosixPath(rel).name, []))

            while not free(gen):
                gen += suffix
            out[f] = (gen, True)
        return out

    # -- saving
    def changed(self):
        """(pages whose text differs from disk, pages that are new, pages to delete)."""
        mod = sorted(r for r, t in self.text.items() if r in self.disk and t != self.disk[r])
        new = sorted(r for r in self.text if r not in self.disk)
        gone = sorted(r for r in self.disk if r not in self.text)
        return mod, new, gone

    def save(self):
        """Write what changed (keeping each file's line endings; new files with LF) and delete what was removed.

        Several AIs write in the same folder. A page that someone else changed (or created) on disk after this run read
        it is NOT written: it is returned in the last list and the next run picks it up."""
        mod, new, gone = self.changed()
        skipped = []
        for rel in mod + gone:
            p = self.path(rel)
            if not p.exists() or read(p)[0] != self.disk[rel]:
                skipped.append(rel)
        skipped += [rel for rel in new if self.path(rel).exists()]
        for rel in mod + new:
            if rel in skipped:
                continue
            write(self.path(rel), self.text[rel], self.crlf.get(rel, False))
            self.disk[rel] = self.text[rel]
        for rel in gone:
            if rel in skipped:
                continue
            self.path(rel).unlink()
            del self.disk[rel]
        return mod, new, gone, skipped
