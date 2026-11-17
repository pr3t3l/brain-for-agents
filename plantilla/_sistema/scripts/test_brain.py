"""Tests of the brain programs: the library, the connector, the check, the new-project script, the hooks, the autosave and
the Obsidian views. Everything runs on temporary copies (and a temporary git repo with a temporary remote); your brain
is never touched and neither is your real HOME.

Usage: python -I test_brain.py        (prints one OK/BAD line per test, then ALL GOOD or SOMETHING FAILED)
Exit code: 0 all passed, 1 something failed.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")

import apply_views  # noqa: E402
import brain_lib as lib  # noqa: E402

BRAIN = HERE.parents[1]
CFG = lib.load_config(BRAIN)
LAY = CFG["layout"]
PD = LAY["projects"]
SLUG = next(iter(CFG["projects"]))
COVER = f"{PD}/{SLUG}/{SLUG}"
ROUTES = CFG["checks"]["routes"]
SYSDIR = lib.config_path(BRAIN).parent.name
ENC = "utf-8"
RESULTS = []


def ok(name, cond, detail=""):
    RESULTS.append(bool(cond))
    print(("OK  " if cond else "BAD ") + name + ("" if cond else f"  [{detail}]"))


def py(root, script, *args, env=None, check=False):
    r = subprocess.run([sys.executable, "-I", str(root / SYSDIR / "scripts" / script), *args], capture_output=True,
                       text=True, encoding=ENC, errors="replace", env=env)
    return r.returncode, r.stdout + r.stderr


def fresh_copy(tmp):
    dest = Path(tmp) / "brain"
    shutil.copytree(BRAIN, dest, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.before-*"))
    return dest


def rd(root, rel):
    return (root / (rel + ".md")).read_text(encoding=ENC)


def wr(root, rel, text):
    (root / (rel + ".md")).write_text(text, encoding=ENC, newline="")


def append(root, rel, text):
    wr(root, rel, rd(root, rel).rstrip("\n") + "\n" + text + "\n")


def tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts}


def library_tests():
    text = "# Page\n\nhand written\n"
    with_block = lib.set_block(text, ["line 1", "line 2"], "links")
    ok("lib: a block is added at the end", with_block.endswith("<!-- brain:links:end -->\n") and "hand written" in with_block)
    ok("lib: replacing a block twice gives the same text", lib.set_block(with_block, ["line 1", "line 2"], "links") == with_block)
    ok("lib: removing a block gives back the hand-written text", lib.set_block(with_block, None, "links").strip() == text.strip())
    ok("lib: strip_blocks keeps only hand-written text", "line 1" not in lib.strip_blocks(with_block) and "hand written" in lib.strip_blocks(with_block))
    two = lib.set_block(with_block, ["x"], "applied")
    ok("lib: two named blocks live in one page", set(lib.find_blocks(two)) == {"links", "applied"})
    damaged = with_block.replace("<!-- brain:links:end -->", "")
    try:
        lib.set_block(damaged, ["new"], "links")
        refused = False
    except lib.BlockDamaged:
        refused = True
    ok("lib: a start marker without its end is refused, nothing is guessed", refused)
    shown = "```\n<!-- brain:links:start -->\n```\n"
    ok("lib: a marker shown inside a code fence is text, not a block", lib.find_blocks(shown) == {})
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "a.md"
        f.write_bytes(b"one\r\ntwo\r\n")
        lib.write(f, "one\ntwo\nthree\n")
        ok("lib: writing keeps the CRLF line endings the file had", f.read_bytes() == b"one\r\ntwo\r\nthree\r\n")
        g = Path(tmp) / "b.md"
        lib.write(g, "x\ny\n")
        ok("lib: a new file gets LF, never the platform default", g.read_bytes() == b"x\ny\n")


def connector_and_check_tests(tmp):
    root = fresh_copy(tmp / "c")
    rc, out = py(root, "connect.py", str(root), "--check")
    ok("the shipped template is already connected (connect --check changes nothing)", rc == 0 and "0 page(s) would change" in out, out)
    rc, out = py(root, "check.py", str(root))
    ok("check: the shipped template has 0 failures", rc == 0 and "0 failures" in out.replace("0 fallas", "0 failures") and "FAIL" not in out, out)
    py(root, "connect.py", str(root))
    snap = tree(root)
    py(root, "connect.py", str(root))
    ok("connect: running it twice changes nothing", tree(root) == snap)

    # remove every generated block and generated page, rebuild: same result
    b = lib.Brain(root)
    for rel in list(b.text):
        if b.front(rel).get(lib.GEN_KEY) == lib.GEN_VALUE:
            (root / (rel + ".md")).unlink()
        else:
            stripped = b.text[rel]
            for name in list(lib.find_blocks(stripped)):
                stripped = lib.set_block(stripped, None, name)
            if stripped != b.text[rel]:
                wr(root, rel, stripped)
    py(root, "connect.py", str(root))
    ok("connect: removing every generated block and rebuilding gives the same brain", tree(root) == snap)

    # a damaged marker: refused, hand-written text kept, and the check fails
    marker_end = "<!-- brain:links:end -->"
    original = rd(root, COVER)
    wr(root, COVER, original.replace(marker_end, "") + "\nHand-written text after the block.\n")
    before = rd(root, COVER)
    rc, out = py(root, "connect.py", str(root))
    ok("connect: refuses a page whose end marker is missing and does not touch it", rc == 1 and rd(root, COVER) == before and "Hand-written text after the block." in rd(root, COVER), out)
    rc, out = py(root, "check.py", str(root))
    ok("check: detects a block without its end marker", rc == 1 and "FAIL" in out and COVER in out, out)
    wr(root, COVER, original)

    # five provoked breakages, each one must fail the check, naming the page
    knowledge = next(r for r in lib.Brain(root).text if lib.Brain(root).layer(r) == "core" and lib.Brain(root).type(r) not in ("index",))
    status = next(f"{PD}/{SLUG}/{e['file'].format(p=SLUG)[:-3]}" for e in CFG["project_pages"]["always"] if e.get("role") == "status")
    log_page = f"{PD}/{SLUG}/{SLUG}-log"
    py(root, "new_project.py", str(root), "other", "Other")
    broken = {
        "a link from a project to another project": (status, "\nSee [[%s/other/other]].\n" % PD, "island"),
        "a hand-written link from the core to a project": (knowledge, "\nSee [[%s]].\n" % COVER, "core->island"),
        "a link from the core to history": (knowledge, "\nSee [[%s]].\n" % log_page, "core->history"),
        "a broken link in the task routes": (ROUTES, "\n| Do x | [[no/such/page]] | y |\n", "routes"),
        "a broken link in a normal page": (status, "\nSee [[no/such/page]].\n", "broken"),
    }
    for name, (page, extra, _tag) in broken.items():
        keep = rd(root, page)
        append(root, page, extra)
        rc, out = py(root, "check.py", str(root))
        ok(f"check: fails on {name}", rc == 1 and "FAIL" in out and page in out, out[-400:])
        wr(root, page, keep)
    (root / PD / "ghost").mkdir()
    wr(root, f"{PD}/ghost/ghost", "---\n%s: project\n---\n\n# Ghost\n" % LAY["type_key"])
    rc, out = py(root, "check.py", str(root))
    ok("check: fails on a project folder that is not registered", rc == 1 and f"{PD}/ghost" in out, out[-400:])
    shutil.rmtree(root / PD / "ghost")
    first_decision = sorted((root / PD / SLUG / LAY["decisions"]).glob("*.md"))[0]
    saved = first_decision.read_text(encoding=ENC)
    first_decision.write_text(saved.replace(LAY["decision_tag"], "x: y"), encoding=ENC, newline="")
    rc, out = py(root, "check.py", str(root))
    ok("check: fails on a decision without its header tag", rc == 1 and first_decision.stem in out, out[-400:])
    first_decision.write_text(saved, encoding=ENC, newline="")
    many = "\n".join(f"[[{PD}/{SLUG}/{SLUG}-{i}]]" for i in range(70))
    keep = rd(root, status)
    append(root, status, many)
    rc, out = py(root, "check.py", str(root))
    ok("check: fails on a hand-written page with more than 60 links", rc == 1 and status in out, out[-300:])
    wr(root, status, keep)

    # a new folder in a project must get its center page, and the check says so until connect runs
    (root / PD / SLUG / "notes").mkdir()
    wr(root, f"{PD}/{SLUG}/notes/first-note", "---\n%s: guide\n---\n\n# First note\n" % LAY["type_key"])
    rc, out = py(root, "check.py", str(root))
    ok("check: fails on a folder of a project without a center page", rc == 1 and f"{PD}/{SLUG}/notes" in out, out[-400:])
    py(root, "connect.py", str(root))
    rc, out = py(root, "check.py", str(root))
    ok("connect: writes the center of the new folder and the check passes again", rc == 0 and (root / PD / SLUG / "notes" / f"{SLUG}-notes.md").exists(), out[-400:])
    shutil.rmtree(root / PD / SLUG / "notes")
    py(root, "connect.py", str(root))
    ok("connect: removes a generated center whose folder is gone", not (root / PD / SLUG / "notes" / f"{SLUG}-notes.md").exists())


def new_project_tests(tmp):
    root = fresh_copy(tmp / "n")
    before = tree(root)
    rc, out = py(root, "new_project.py", str(root), "cafe-two", "Cafe Two", "--check")
    ok("new_project: --check writes nothing", rc == 0 and tree(root) == before, out)
    rc, out = py(root, "new_project.py", str(root), "cafe-two", "Cafe Two")
    cfg = lib.load_config(root)
    ok("new_project: creates the pages, registers the project and wires it", rc == 0 and "cafe-two" in cfg["projects"]
       and (root / PD / "cafe-two" / "cafe-two.md").exists() and (root / PD / "cafe-two" / LAY["decisions"]).is_dir(), out)
    ok("new_project: adds its row to the front page", "cafe-two" in rd(root, CFG["checks"]["index_page"]))
    ok("new_project: the cover received the generated block of bridges", "<!-- brain:links:start -->" in rd(root, f"{PD}/cafe-two/cafe-two"))
    rc, out = py(root, "check.py", str(root))
    ok("new_project: the brain has 0 failures with the new project", rc == 0, out[-500:])
    snap = tree(root)
    py(root, "connect.py", str(root))
    ok("new_project: connecting again changes nothing", tree(root) == snap)
    rc, out = py(root, "new_project.py", str(root), "cafe-two", "Cafe Two")
    ok("new_project: refuses a project that already exists", rc == 1 and tree(root) == snap)
    rc, out = py(root, "new_project.py", str(root), "Bad Name", "Bad")
    ok("new_project: refuses a folder name with spaces or capitals", rc == 1)
    rc, out = py(root, "new_project.py", str(root), "idea-one", "Idea One", "--parked", "--no-marketing")
    rc2, out2 = py(root, "check.py", str(root))
    ok("new_project: a parked idea needs only its cover and the check passes", rc == 0 and rc2 == 0 and not (root / PD / "idea-one" / "idea-one-marketing.md").exists(), out2[-400:])


def views_tests(tmp):
    root = fresh_copy(tmp / "v")
    py(root, "new_project.py", str(root), "cafe-two", "Cafe Two")
    graph = root / ".obsidian" / "graph.json"
    graph.write_text(json.dumps({"showOrphans": True, "colorGroups": [], "centerStrength": 0.5}), encoding=ENC)
    rc = apply_views.apply(root, dry=True)
    ok("views: --dry-run writes nothing", rc == 0 and json.loads(graph.read_text(encoding=ENC))["colorGroups"] == [])
    rc = apply_views.apply(root, check_process=lambda: True)
    ok("views: refuses to write while Obsidian is open", rc == 1 and json.loads(graph.read_text(encoding=ENC))["colorGroups"] == [])
    rc = apply_views.apply(root, check_process=lambda: None)
    ok("views: refuses to write when it cannot tell whether Obsidian is open", rc == 1)
    rc = apply_views.apply(root, view="all", bookmarks=True, check_process=lambda: False)
    data = json.loads(graph.read_text(encoding=ENC))
    queries = " ".join(g["query"] for g in data["colorGroups"])
    ok("views: writes the layer colors and one color per project (the new one too)", rc == 0 and f'"{PD}/cafe-two/"' in queries and f'"{PD}/{SLUG}/"' in queries, queries[-200:])
    ok("views: forces and zoom of Obsidian are never touched", data.get("centerStrength") == 0.5)
    marks = json.loads((root / ".obsidian" / "bookmarks.json").read_text(encoding=ENC))
    titles = [i["title"] for i in marks["items"][0]["items"]]
    ok("views: one bookmark per view, and one view per project", any("Cafe Two" in t for t in titles) and len(titles) >= 5, titles)
    ok("views: the history filter is built from the history types of config.json", "[%s:%s]" % (LAY["type_key"], CFG["types"]["history"][0]) in " ".join(g["query"] for g in data["colorGroups"]))
    rc = apply_views.apply(root, view="all", bookmarks=True, check_process=lambda: False)
    ok("views: running it again has nothing to change", rc == 0)


def git(root, *args, env=None, check=True):
    r = subprocess.run(["git", "-C", str(root), "-c", "user.name=test", "-c", "user.email=test@example.com", *args],
                       capture_output=True, text=True, encoding=ENC, errors="replace", env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


def git_tests(tmp):
    root = fresh_copy(tmp / "g")
    fake_home = tmp / "home"
    fake_home.mkdir()
    env = dict(os.environ, HOME=str(fake_home), USERPROFILE=str(fake_home), GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="test@example.com",
               GIT_COMMITTER_NAME="test", GIT_COMMITTER_EMAIL="test@example.com")
    env.pop("BRAIN_AUTOSAVE", None)
    remote = tmp / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "remote", "add", "origin", str(remote))
    git(root, "config", "core.hooksPath", f"{SYSDIR}/hooks")
    for hook in (root / SYSDIR / "hooks").glob("*"):
        hook.chmod(0o755)
    git(root, "add", "-A")
    rc, out = git(root, "commit", "-q", "-m", "start", env=env)
    ok("hooks: a commit of a healthy brain goes in (pre-commit runs the check and passes)", rc == 0, out)
    status = next(f"{PD}/{SLUG}/{e['file'].format(p=SLUG)[:-3]}" for e in CFG["project_pages"]["always"] if e.get("role") == "status")
    append(root, status, "\nSee [[no/such/page]].")
    git(root, "add", "-A")
    rc, out = git(root, "commit", "-q", "-m", "break a link", env=env)
    _, count = git(root, "rev-list", "--count", "HEAD")
    ok("hooks: pre-commit blocks a commit while the check fails", rc != 0 and count == "1" and "no/such/page" in out, out)
    rc, out = git(root, "commit", "-q", "-m", "autosave", env={**env, "BRAIN_AUTOSAVE": "1"})
    ok("hooks: the autosave variable lets the commit through, so no work is lost", rc == 0, out)
    git(root, "reset", "-q", "--hard", "HEAD~1")
    # autosave: an old unsaved change with a broken link is saved anyway, with the failure in the message, and pushed
    append(root, status, "\nSee [[no/such/page]].")
    old = time.time() - 3600
    os.utime(root / (status + ".md"), (old, old))
    rc, out = py(root, "autosave.py", env=env)
    _, message = git(root, "log", "-1", "--format=%B")
    _, remote_log = git(remote, "log", "-1", "--format=%s")
    ok("autosave: saves an unsaved change even when the check fails, and says so in the message", rc == 0 and message.splitlines()[0].startswith(("Autosave", "Guardado")) and "no/such/page" in message, message)
    ok("autosave: pushes to the remote", remote_log.startswith(("Autosave", "Guardado")), remote_log)
    wr(root, f"{PD}/{SLUG}/.env", "")
    (root / PD / SLUG / "api.key").write_text("secret", encoding=ENC)
    os.utime(root / PD / SLUG / "api.key", (old, old))
    py(root, "autosave.py", env=env)
    _, tracked = git(root, "ls-files")
    ok("autosave: never saves a file named like a key or a credential", "api.key" not in tracked)
    append(root, status, "\nA fresh line.")
    rc, out = py(root, "autosave.py", "--dry-run", env=env)
    _, status_out = git(root, "status", "--porcelain")
    ok("autosave: leaves a page touched a moment ago for the next run, and --dry-run changes nothing", "A fresh line." in rd(root, status) and status.split("/")[-1] in status_out, out)


def main():
    with tempfile.TemporaryDirectory(prefix="brain-test-") as t:
        tmp = Path(t)
        for sub in ("c", "n", "v", "g"):
            (tmp / sub).mkdir()
        library_tests()
        connector_and_check_tests(tmp)
        new_project_tests(tmp)
        views_tests(tmp)
        git_tests(tmp)
        # on Windows a temp git repo can hold files open for a moment
    good = all(RESULTS)
    print(f"{sum(RESULTS)}/{len(RESULTS)} " + ("ALL GOOD" if good else "SOMETHING FAILED"))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
