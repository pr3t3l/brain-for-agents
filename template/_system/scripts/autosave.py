"""Autosave for the brain: keep this folder and its GitHub repo (branch main) equal without anyone remembering.

Every run does three things, in this order:
  1. Commit what was left unsaved. Only files nobody has touched for QUIET_MIN minutes, so it does not grab a page a
     session is still writing. The commit names its files, so whatever another session has staged stays staged.
  2. Bring what others pushed (git merge origin/main). Logs and inboxes merge by themselves (.gitattributes). If two edits
     really collide, the merge is undone and the collision is written to the log: nothing is forced.
  3. Push.

It does nothing while another git command is running, during a merge, or if the folder is not on main. Before saving it
runs the check (check.py). Failures NEVER stop the save: they go in the commit message and in the log, because losing work
is worse than saving a page that breaks a rule. Commits made by people or AIs do get stopped by the pre-commit hook in
`_system/hooks` (core.hooksPath); this program sets BRAIN_AUTOSAVE=1 so the hook lets it through.

It never saves files named like a key or a credential (.env, *.pem, *.key, *secret*, *token*...).

Schedule it every 10 minutes (it uses plain git, so it costs nothing):
  Windows: Task Scheduler, action `python -I <brain>\\_system\\scripts\\autosave.py`, repeat every 10 minutes.
  macOS / Linux: cron, `*/10 * * * * python3 -I <brain>/_system/scripts/autosave.py`.

Log: .git/brain-autosave.log (inside .git, so it is never committed).
By hand:  python -I _system/scripts/autosave.py [--dry-run]   (reports, changes nothing)
"""
import datetime
import fnmatch
import os
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I leaves the script folder off sys.path

import brain_lib as lib  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT_DIR = ROOT / ".git"
LOG, LOCK = GIT_DIR / "brain-autosave.log", GIT_DIR / "brain-autosave.lock"
BRANCH = "main"
QUIET_MIN = 5
NEVER = [".env*", "*.pem", "*.key", "*.pfx", "*credential*", "*secret*", "*token*"]
DRY = "--dry-run" in sys.argv
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
ENV = {**os.environ, "BRAIN_AUTOSAVE": "1"}
ES = lib.load_config(ROOT).get("language") == "es"


def t(en, es):
    return es if ES else en


def git(*args, raw=False):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", creationflags=NO_WINDOW, timeout=180, env=ENV)
    # raw: the status list starts with a meaningful space (" M file"), so it must not be trimmed
    return r.returncode, (r.stdout if raw else (r.stdout + r.stderr).strip())


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {'[dry run] ' if DRY else ''}{msg}"
    print(line)
    try:
        old = LOG.read_text(encoding="utf-8").splitlines()[-400:] if LOG.exists() else []
        LOG.write_text("\n".join(old + [line]) + "\n", encoding="utf-8")
    except OSError:
        pass


def control():
    """Run check.py; return the failure lines ('' when it passes). Never stops the save."""
    try:
        r = subprocess.run([sys.executable, "-I", str(HERE / "check.py"), str(ROOT)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", creationflags=NO_WINDOW, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        return t(f"could not run the check: {e}", f"no pude correr el control: {e}")
    if r.returncode == 0:
        return ""
    keep, inside = [], False
    for line in r.stdout.splitlines():
        if line.startswith(("FAIL", "WARN", "check:")):
            inside = line.startswith("FAIL")
        if inside:
            keep.append(line)
    return "\n".join(keep)[:1500] or t("the check failed without saying why", "el control falló sin decir por qué")


def busy():
    return [n for n in ("index.lock", "MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD") if (GIT_DIR / n).exists()]


def pending():
    """Paths with unsaved changes: (ready to save, still being written, never saved by a robot)."""
    _, out = git("status", "--porcelain=v1", "-z", "--untracked-files=all", raw=True)
    tokens, ready, fresh, never = out.split("\0"), [], [], []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        i += 1
        if len(tok) < 4:
            continue
        code, paths = tok[:2], [tok[3:]]
        if "R" in code or "C" in code:  # a rename carries the old name in the next token
            paths.append(tokens[i])
            i += 1
        for path in paths:
            name = PurePosixPath(path).name.lower()
            if any(fnmatch.fnmatch(name, pat) for pat in NEVER):
                never.append(path)
                continue
            f = ROOT / path
            still = f.exists() and time.time() - f.stat().st_mtime < QUIET_MIN * 60
            (fresh if still else ready).append(path)
    return ready, fresh, never


def main():
    if LOCK.exists() and time.time() - LOCK.stat().st_mtime < 9 * 60:
        return log(t("another run is still going; leaving", "otra corrida sigue en marcha; salgo"))
    held = busy()
    if held:
        return log(t(f"git is busy ({', '.join(held)}); next time", f"git ocupado ({', '.join(held)}); en la próxima"))
    _, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch != BRANCH:
        return log(t(f"the folder is on branch '{branch}', not {BRANCH}; touching nothing", f"la carpeta está en la rama '{branch}', no en {BRANCH}; no toco nada"))
    LOCK.write_text(str(os.getpid()), encoding="utf-8")
    try:
        ready, fresh, never = pending()
        if never:
            log(t(f"WARNING: not saving, by their name: {', '.join(never)}", f"AVISO: no guardo por su nombre: {', '.join(never)}"))
        if ready:
            shown = ", ".join(ready[:6]) + (t(f" and {len(ready) - 6} more", f" y {len(ready) - 6} más") if len(ready) > 6 else "")
            if DRY:
                log(t(f"would save {len(ready)} files: {shown}", f"guardaría {len(ready)} archivos: {shown}"))
            else:
                for k in range(0, len(ready), 80):
                    git("add", "-A", "--", *ready[k:k + 80])
                body = "\n".join(ready[:40]) + ("\n..." if len(ready) > 40 else "")
                failures = control()
                if failures:
                    log(t("CAUTION: the check found failures; saving anyway so nothing is lost:\n", "OJO: el control encontró fallas; guardo igual para no perder nada:\n") + failures)
                    body = t("CAUTION: the check found failures (saved anyway):\n", "OJO: el control encontró fallas (se guardó igual):\n") + failures + t("\n\nFiles:\n", "\n\nArchivos:\n") + body
                msg = (t("Autosave: ", "Guardado automático: ") + f"{len(ready)} " + t("files", "archivos")
                       + (t(" (with check failures)", " (con fallas del control)") if failures else "")
                       + "\n\n" + t(f"Changes left unsaved for more than {QUIET_MIN} minutes. It does not say which AI wrote them.\n\n",
                                     f"Cambios que quedaron sin guardar más de {QUIET_MIN} minutos. No dice qué IA los escribió.\n\n") + body)
                rc, out = git("commit", "-q", "-m", msg, "--", *ready[:2000])
                log(t(f"saved {len(ready)} files: {shown}", f"guardé {len(ready)} archivos: {shown}") if rc == 0 else t(f"could not save: {out[-300:]}", f"no pude guardar: {out[-300:]}"))
        if fresh:
            log(t(f"{len(fresh)} files touched a moment ago wait for the next run", f"{len(fresh)} archivos recién tocados esperan a la próxima corrida"))

        remotes = git("remote")[1].split()
        if not remotes:
            return log(t("no remote configured: saved locally only", "sin remoto configurado: solo se guardó en local"))
        rc, out = git("fetch", "-q", "origin")
        if rc != 0:
            return log(t(f"no connection to the remote: {out[-200:]}", f"sin conexión con el remoto: {out[-200:]}"))
        _, behind = git("rev-list", "--count", f"HEAD..origin/{BRANCH}")
        if behind.isdigit() and int(behind) > 0:
            if DRY:
                log(t(f"would pull {behind} commits", f"bajaría {behind} commits"))
            else:
                rc, out = git("merge", "--no-edit", "-q", f"origin/{BRANCH}")
                if rc == 0:
                    log(t(f"pulled {behind} commits", f"bajé {behind} commits"))
                elif (GIT_DIR / "MERGE_HEAD").exists():
                    _, files = git("diff", "--name-only", "--diff-filter=U")
                    git("merge", "--abort")
                    return log(t("COLLISION while pulling, undone without losing anything. An AI fixes it by hand: ", "CHOQUE al bajar, deshecho sin perder nada. Lo arregla una IA a mano: ") + files.replace(chr(10), ", "))
                else:
                    return log(t(f"did not pull yet (half-written files would change): {out[-300:]}", f"no bajé todavía (hay archivos a medio escribir que cambiarían): {out[-300:]}"))
        _, ahead = git("rev-list", "--count", f"origin/{BRANCH}..HEAD")
        if ahead.isdigit() and int(ahead) > 0:
            if DRY:
                log(t(f"would push {ahead} commits", f"subiría {ahead} commits"))
            else:
                rc, out = git("push", "-q", "origin", f"HEAD:{BRANCH}")
                log(t(f"pushed {ahead} commits", f"subí {ahead} commits") if rc == 0 else t(f"the remote refused the push, next time: {out[-300:]}", f"el remoto no aceptó la subida, en la próxima: {out[-300:]}"))
        if not ready and behind == "0" and ahead == "0":
            log(t("all equal: nothing to save, pull or push", "todo igual: nada que guardar, bajar ni subir"))
    finally:
        try:
            LOCK.unlink()
        except OSError:
            pass


if __name__ == "__main__":
    main()
