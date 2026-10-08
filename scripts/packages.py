"""Keep the package checkouts under packages/ and their recorded state in sync.

The branch each package follows is recorded in pyproject.toml under [tool.distro.packages] (uv ignores this table;
the workspace itself only knows the folders). The exact commits are the submodule pointers of the distro commit.

    python scripts/packages.py track [-n]   switch packages to their recorded branch, fast-forward to origin
    python scripts/packages.py record [-n]  write the checked-out branches into pyproject.toml and .gitmodules
    python scripts/packages.py pin [-n]     commit the checked-out commits as submodule pointers (no push)

-n only shows what would happen. Run through poe: `uv run poe track|record|pin [-n]`.
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

TABLE = "tool.distro.packages"


def git(*args: str, cwd: Path, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    if check and result.returncode != 0:
        raise SystemExit(
            f"git {' '.join(args)} failed in {cwd}:\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def submodules(root: Path) -> list[tuple[str, str, str]]:
    """(name, path, branch from .gitmodules) for every submodule."""
    out = git(
        "config",
        "-f",
        ".gitmodules",
        "--get-regexp",
        r"^submodule\..*\.path$",
        cwd=root,
    )
    entries = []
    for line in out.splitlines():
        key, path = line.split(maxsplit=1)
        name = key.removeprefix("submodule.").removesuffix(".path")
        branch = git(
            "config",
            "-f",
            ".gitmodules",
            f"submodule.{name}.branch",
            cwd=root,
            check=False,
        )
        entries.append((name, path, branch))
    return entries


def recorded_branches(root: Path) -> dict[str, str]:
    data = tomllib.loads((root / "pyproject.toml").read_text())
    return data.get("tool", {}).get("distro", {}).get("packages", {})


def initialised(root: Path, path: str) -> bool:
    # An empty folder (not initialised) resolves to the distro repo itself, so compare toplevels.
    top = git("rev-parse", "--show-toplevel", cwd=root / path, check=False)
    return top == str(root / path)


def dirty(pkg: Path) -> bool:
    return bool(git("status", "--porcelain", "--untracked-files=no", cwd=pkg))


def track(root: Path, dry: bool) -> int:
    status = 0
    recorded = recorded_branches(root)
    for _name, path, gm_branch in submodules(root):
        key = Path(path).name
        branch = recorded.get(key) or gm_branch
        pkg = root / path
        if not branch:
            print(f"{path}: no branch recorded, skipped")
            continue
        if not initialised(root, path):
            print(f"{path}: not initialised (git submodule update --init), skipped")
            continue
        current = git("branch", "--show-current", cwd=pkg)
        if current and current != branch:
            print(f"{path}: on {current}, not {branch}; left alone")
            continue
        if dirty(pkg):
            print(f"{path}: uncommitted changes; left alone")
            continue
        if dry:
            print(
                f"{path}: would switch to {branch} and fast-forward to origin/{branch}"
            )
            continue
        git("fetch", "-q", "origin", branch, cwd=pkg)
        local = subprocess.run(
            ["git", "show-ref", "-q", "--verify", f"refs/heads/{branch}"],
            cwd=pkg,
            check=False,
        )
        if local.returncode == 0:
            git("switch", "-q", branch, cwd=pkg)
        else:
            git("switch", "-q", "-c", branch, "--track", f"origin/{branch}", cwd=pkg)
        if subprocess.run(
            ["git", "merge", "-q", "--ff-only", f"origin/{branch}"],
            cwd=pkg,
            check=False,
        ).returncode:
            print(f"{path}: {branch} has diverged from origin; not moved")
            status = 1
            continue
        print(f"{path}: {branch} at {git('rev-parse', '--short', 'HEAD', cwd=pkg)}")
    return status


def write_table(pyproject: Path, branches: dict[str, str]) -> None:
    """Replace (or append) the [tool.distro.packages] table, leaving the rest of the file untouched."""
    text = pyproject.read_text()
    body = "".join(f'"{key}" = "{value}"\n' for key, value in branches.items())
    block = (
        f"[{TABLE}]\n"
        "# Branch each package under packages/ follows (uv ignores this table). Read by `poe track`,\n"
        "# written by `poe record`; the exact commits are the submodule pointers (`poe pin`).\n"
        + body
    )
    pattern = re.compile(
        rf"^\[{re.escape(TABLE)}\]\n.*?(?=^\[|\Z)", re.DOTALL | re.MULTILINE
    )
    if pattern.search(text):
        text = pattern.sub(lambda _m: block + "\n", text, count=1).rstrip("\n") + "\n"
    else:
        text = text.rstrip("\n") + "\n\n" + block
    pyproject.write_text(text)


def record(root: Path, dry: bool) -> int:
    recorded = recorded_branches(root)
    branches = {}
    changed = False
    for name, path, gm_branch in submodules(root):
        key = Path(path).name
        old = recorded.get(key) or gm_branch
        new = old
        if initialised(root, path):
            current = git("branch", "--show-current", cwd=root / path)
            if current:
                new = current
            else:
                print(f"{path}: detached, keeps {old}")
        if new != old:
            print(f"{path}: {old} -> {new}")
        if new != recorded.get(key) or new != gm_branch:
            changed = True
            if not dry:
                git("submodule", "set-branch", "-b", new, "--", path, cwd=root)
        branches[key] = new
    if not changed:
        print("Recorded branches already match.")
        return 0
    if dry:
        return 0
    write_table(root / "pyproject.toml", branches)
    print("Updated pyproject.toml and .gitmodules; review with git diff and commit.")
    return 0


def pin(root: Path, dry: bool) -> int:
    moved = []
    for _name, path, _branch in submodules(root):
        if not initialised(root, path):
            continue
        pkg = root / path
        pinned = git("rev-parse", f"HEAD:{path}", cwd=root)
        head = git("rev-parse", "HEAD", cwd=pkg)
        branch = git("branch", "--show-current", cwd=pkg) or "detached"
        note = " (uncommitted changes, not recorded)" if dirty(pkg) else ""
        if head == pinned:
            print(f"{path}: {branch} {head[:7]}, unchanged{note}")
        else:
            line = f"{path}: {pinned[:7]} -> {head[:7]} ({branch})"
            print(line + note)
            moved.append((path, line))
    if not moved:
        print("Nothing to pin.")
        return 0
    if dry:
        return 0
    paths = [path for path, _ in moved]
    summary = "\n".join(f"- {line}" for _, line in moved)
    git("add", "--", *paths, cwd=root)
    git(
        "commit",
        "-q",
        "-m",
        "Pin packages to their checked-out commits",
        "-m",
        summary,
        "--",
        *paths,
        cwd=root,
    )
    print(
        f"Committed {git('rev-parse', '--short', 'HEAD', cwd=root)} on {git('branch', '--show-current', cwd=root)}; "
        "push when ready."
    )
    return 0


def main() -> int:
    commands = {"track": track, "record": record, "pin": pin}
    args = sys.argv[1:]
    if not args or args[0] not in commands:
        print(__doc__)
        return 2
    root = Path(git("rev-parse", "--show-toplevel", cwd=Path.cwd()))
    return commands[args[0]](root, dry="-n" in args[1:])


if __name__ == "__main__":
    sys.exit(main())
