"""Put the views of the brain into Obsidian: color groups by layer and by project, the default filter, and one bookmark
per view. Colors and views come from `_system/obsidian/views.json` and from the list of projects in config.json: a new
project gets its color and its view the next time this runs. History is recorded, not drawn: the views that hide the
logs and inboxes are what make the graph readable.

What it writes, and nothing else:
  - `.obsidian/graph.json`: `colorGroups` always; with --view also `search` (the default filter) and the switches; with
    --switches only the switches. Forces and zoom are never touched.
  - `.obsidian/bookmarks.json` (with --bookmarks): one group of graph bookmarks, one per view. Bookmarks you made by
    hand, outside that group, are kept.

Obsidian keeps these files in memory and rewrites them, so an edit made while the app is open is lost. The script
therefore refuses to run when an Obsidian process is found, or when it cannot tell. Before writing it leaves a backup
next to each file: `<name>.before-<date>-<time>`.

Usage: python -I apply_views.py [brain folder] [--dry-run] [--switches] [--view <id>] [--bookmarks] [--all]
  --dry-run    say what would change, write nothing
  --switches   also set the switches of the reference (tags off, attachments off, unresolved hidden, orphans off)
  --view <id>  make that view the default filter of the graph (for example clean-map)
  --bookmarks  write the bookmarks, so each view opens with one click
  --all        the same as --view all --bookmarks
"""
import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I leaves the script folder off sys.path

import brain_lib as lib  # noqa: E402

SWITCHES = ("showTags", "showAttachments", "hideUnresolved", "showOrphans")


def obsidian_is_open():
    """True if an Obsidian process is running, False if not, None if it could not be checked."""
    try:
        if sys.platform == "win32":
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Obsidian.exe", "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True, timeout=20)
            return "obsidian.exe" in out.stdout.lower() if out.returncode == 0 else None
        out = subprocess.run(["ps", "-A", "-o", "comm="], capture_output=True, text=True, timeout=20)
        if out.returncode != 0:
            return None
        return any(line.strip().lower().endswith("obsidian") for line in out.stdout.splitlines())
    except (OSError, subprocess.SubprocessError):
        return None


def expand(query, cfg):
    """{history} -> every history type of config.json as an Obsidian property search; {not_history} -> the same, negated."""
    key = cfg["layout"]["type_key"]
    hist = [f"[{key}:{t}]" for t in cfg.get("types", {}).get("history", [])]
    return query.replace("{history}", " OR ".join(hist)).replace("{not_history}", " ".join("-" + h for h in hist))


def load_reference(root, cfg):
    """(color groups in graph.json shape, switches, views, bookmark group title). Raises ValueError if malformed."""
    data = json.loads((lib.config_path(root).parent / "obsidian" / "views.json").read_text(encoding="utf-8"))
    projects_dir = cfg["layout"]["projects"]
    groups = []
    for i, g in enumerate(data.get("layer_colors", []), 1):
        if not isinstance(g.get("query"), str) or not g["query"].strip():
            raise ValueError(f"color group {i} has no query")
        if not isinstance(g.get("rgb"), int) or not 0 <= g["rgb"] <= 0xFFFFFF:
            raise ValueError(f"color group {i} has no valid color")
        groups.append({"query": expand(g["query"], cfg), "color": {"a": 1, "rgb": g["rgb"]}})
    spare, chosen, used = data.get("spare_colors", []), data.get("project_colors", {}), 0
    projects = cfg.get("projects", {})
    for slug in projects:
        rgb = chosen.get(slug)
        if rgb is None:
            if not spare:
                raise ValueError(f"project {slug} has no color: add one to project_colors or spare_colors")
            rgb, used = spare[used % len(spare)], used + 1
        groups.append({"query": f'path:"{projects_dir}/{slug}/"', "color": {"a": 1, "rgb": rgb}})
    switches = {k: v for k, v in data.get("switches", {}).items() if k in SWITCHES and isinstance(v, bool)}
    template, views = data.get("project_view", ""), []
    for v in data.get("views", []):
        if not v.get("id") or not v.get("title") or not isinstance(v.get("query"), str):
            raise ValueError("a view lacks id, title or query")
        if v["id"] == "project":  # one view per project goes here
            for slug, info in projects.items():
                if not info.get("parked") and template:
                    views.append({"id": f"project-{slug}", "title": f"{v['title']}: {info['name']}",
                                  "query": expand(template.replace("<project-folder>", slug), cfg)})
            continue
        views.append({"id": v["id"], "title": v["title"], "query": expand(v["query"], cfg)})
    return groups, switches, views, data.get("bookmark_group") or "Brain views"


def read_json(path):
    with open(path, encoding="utf-8", newline="") as f:
        raw = f.read()
    return raw, json.loads(raw)


def write_json(path, raw, data):
    """Write keeping the file's own line endings; leaves a backup that never overwrites an earlier one."""
    backup = None
    if path.exists():
        stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        backup, n = path.with_name(f"{path.name}.before-{stamp}"), 1
        while backup.exists():
            n += 1
            backup = path.with_name(f"{path.name}.before-{stamp}-{n}")
        shutil.copy2(path, backup)
    eol = "\r\n" if "\r\n" in raw else "\n"
    text = json.dumps(data, ensure_ascii=False, indent=2).replace("\n", eol)
    if not raw or raw.endswith(("\n", "\r\n")):
        text += eol
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return backup


def apply(root, dry=False, with_switches=False, view=None, bookmarks=False, check_process=obsidian_is_open):
    """Apply the reference. Returns the exit code (0 done or nothing to do, 1 refused)."""
    cfg = lib.load_config(root)
    graph, marks = root / ".obsidian" / "graph.json", root / ".obsidian" / "bookmarks.json"
    try:
        groups, switches, views, group_title = load_reference(root, cfg)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"views.json is missing or badly written ({e}). Nothing was changed.")
        return 1
    by_id = {v["id"]: v for v in views}
    if view and view not in by_id:
        print(f"There is no view '{view}'. The ones there are: {', '.join(by_id)}")
        return 1
    try:
        raw, before = read_json(graph) if graph.is_file() else ("", {})
    except json.JSONDecodeError as e:
        print(f"{graph} is not valid JSON ({e}). Nothing was changed.")
        return 1
    after = dict(before)
    after["colorGroups"] = groups
    if with_switches or view:
        after.update(switches)
    if view:
        after["search"] = by_id[view]["query"]
    changed = [k for k in after if before.get(k) != after[k]]

    new_marks, marks_raw = None, ""
    if bookmarks:
        try:
            marks_raw, marks_before = read_json(marks) if marks.is_file() else ("", {"items": []})
        except json.JSONDecodeError as e:
            print(f"{marks} is not valid JSON ({e}). Nothing was changed.")
            return 1
        now = int(datetime.datetime.now().timestamp() * 1000)
        old = next((i for i in marks_before.get("items", []) if i.get("type") == "group" and i.get("title") == group_title), {})
        old_times = {i.get("title"): i.get("ctime") for i in old.get("items", [])}
        items = []
        for v in views:
            options = {**after, **switches, "search": v["query"]}
            options.pop("close", None)
            items.append({"type": "graph", "ctime": old_times.get(v["title"]) or now, "title": v["title"], "options": options})
        group = {"type": "group", "ctime": old.get("ctime") or now, "title": group_title, "items": items}
        new_marks = dict(marks_before)
        rest = [i for i in marks_before.get("items", []) if not (i.get("type") == "group" and i.get("title") == group_title)]
        new_marks["items"] = [group, *rest]
        if new_marks == marks_before:
            new_marks = None

    if not changed and new_marks is None:
        print("Obsidian already has the colors and views of the reference. Nothing to change.")
        return 0
    if changed:
        print(f"Graph: would change {', '.join(changed)} ({len(before.get('colorGroups', []))} color groups today, {len(groups)} in the reference).")
    if new_marks is not None:
        print(f"Bookmarks: would put the group '{group_title}' with {len(views)} views: " + ", ".join(v["title"] for v in views))
    if dry:
        print("Dry run: nothing was written.")
        return 0

    state = check_process()
    if state is None:
        print("I could not check whether Obsidian is open, so I am not writing. Close it and run again.")
        return 1
    if state:
        print("Obsidian is open. Close it completely (also the tray icon) and run again: with the app open, Obsidian "
              "throws this change away at the next zoom.")
        return 1
    if changed:
        backup = write_json(graph, raw, after)
        _, written = read_json(graph)
        untouched = all(written.get(k) == v for k, v in before.items() if k not in changed)
        if written.get("colorGroups") != groups or not untouched or set(written) != set(after):
            if backup:
                shutil.copy2(backup, graph)
            print("What was written does not match what was expected: I left the graph as it was.")
            return 1
        print(f"Done: {len(groups)} color groups" + (f" and the view '{by_id[view]['title']}' as the filter" if view else "")
              + f" in {graph}." + (f" Backup: {backup.name}" if backup else ""))
    if new_marks is not None:
        backup = write_json(marks, marks_raw, new_marks)
        print(f"Done: {len(views)} bookmarks in {marks}." + (f" Backup: {backup.name}" if backup else ""))
    return 0


def main(argv):
    flags = ("--dry-run", "--switches", "--bookmarks", "--all", "--view")
    args, view, skip = [], None, False
    for i, a in enumerate(argv):
        if skip:
            skip = False
        elif a == "--view":
            if i + 1 >= len(argv):
                print("--view needs the name of a view, for example: --view clean-map")
                return 1
            view, skip = argv[i + 1], True
        elif a.startswith("--"):
            if a not in flags:
                print(f"I do not know {a}. Options: {', '.join(flags)}")
                return 1
        else:
            args.append(a)
    everything = "--all" in argv
    root = Path(args[0]) if args else lib.HERE.parents[1]
    return apply(root.resolve(), dry="--dry-run" in argv, with_switches="--switches" in argv,
                 view=view or ("all" if everything else None), bookmarks=everything or "--bookmarks" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
