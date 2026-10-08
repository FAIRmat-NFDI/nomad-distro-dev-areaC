"""Merge the package pull requests of a coordinated change and update the distro branch.

A coordinated change uses one branch name across the package repositories and this distro (see "Coordinated
development protocol" in the README). This script performs the merge step of that protocol:

1. Find, for every GitHub-hosted package, the pull request whose head is the shared branch.
2. Check that every open one can be merged: targets the repository's default branch, not a draft, no
   conflicts, checks green, no review pending or changes requested.
   If any fails, nothing is merged: the merges across repositories are not atomic, so they only start when
   all of them can go through.
3. Squash-merge them in dependency order, leaves first. Already merged pull requests count as done, so a run
   that stopped halfway can simply be repeated.
4. In the distro checkout, point each package's submodule at the resulting commit on its base branch and
   record that base branch in [tool.distro.packages] and .gitmodules, then commit. Nothing is pushed.

    python scripts/merge_prs.py <branch> [-n] [--body TEXT | --body-file FILE]

-n only reports what would happen. The body replaces the squash commit message body of every merged pull
request (default: the pull request description); the subject is always "<title> (#<number>)". Needs the `gh`
CLI authenticated as a user who may merge in the package repositories (GH_TOKEN in CI).
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from packages import git, recorded_branches, write_table

OWNER = "FAIRmat-NFDI"
# Dependency order, leaves first: a repository is merged only after the ones it depends on.
ORDER = [
    "nomad-simulations",
    "nomad-file-parser",
    "nomad-simulation-parser-test-fixtures",
    "nomad-parser-plugins-simulation",
    "nomad-results-normalizer",
]
PR_FIELDS = (
    "number,state,title,body,url,baseRefName,isDraft,mergeable,mergeStateStatus,"
    "reviewDecision,mergeCommit,statusCheckRollup"
)


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"gh {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def packages_by_repo(root: Path) -> tuple[dict[str, str], list[str]]:
    """GitHub-hosted submodules as repo name -> path, plus the clone URLs of the others."""
    github, other = {}, []
    out = git(
        "config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.url$", cwd=root
    )
    for line in out.splitlines():
        key, url = line.split(maxsplit=1)
        path = git(
            "config", "-f", ".gitmodules", key.removesuffix(".url") + ".path", cwd=root
        )
        match = re.fullmatch(rf"https://github\.com/{OWNER}/([^/]+?)(?:\.git)?/?", url)
        if match:
            github[match.group(1)] = path
        else:
            other.append(url)
    return github, other


def find_pr(repo: str, branch: str) -> dict | None:
    """The open pull request from `branch`, else the merged one, else None."""
    for attempt in range(5):
        prs = json.loads(
            gh(
                "pr", "list", "--repo", f"{OWNER}/{repo}", "--head", branch,
                "--state", "all", "--limit", "20", "--json", PR_FIELDS,
            )
        )  # fmt: skip
        pr = next(
            (pr for state in ("OPEN", "MERGED") for pr in prs if pr["state"] == state),
            None,
        )
        # GitHub computes mergeability lazily; the first query after a push may return UNKNOWN.
        if pr is None or pr["state"] != "OPEN" or pr["mergeable"] != "UNKNOWN":
            return pr
        time.sleep(2 * (attempt + 1))
    return pr


def default_branch(repo: str) -> str:
    return gh(
        "repo", "view", f"{OWNER}/{repo}", "--json", "defaultBranchRef",
        "--jq", ".defaultBranchRef.name",
    )  # fmt: skip


def blockers(pr: dict, tracked: str) -> list[str]:
    problems = []
    if pr["baseRefName"] != tracked:
        problems.append(f"base={pr['baseRefName']}, not {tracked}")
    if pr["isDraft"]:
        problems.append("draft")
    if pr["mergeable"] != "MERGEABLE":
        problems.append(f"mergeable={pr['mergeable']}")
    if pr["mergeStateStatus"] not in ("CLEAN", "HAS_HOOKS", "UNSTABLE", "BEHIND"):
        problems.append(f"mergeStateStatus={pr['mergeStateStatus']}")
    if pr["reviewDecision"] in ("CHANGES_REQUESTED", "REVIEW_REQUIRED"):
        problems.append(pr["reviewDecision"].lower())
    for check in pr["statusCheckRollup"] or []:
        # Check runs carry status/conclusion, commit statuses only state.
        outcome = check.get("conclusion") or check.get("state") or ""
        if check.get("status") not in (None, "COMPLETED") or outcome not in (
            "SUCCESS",
            "NEUTRAL",
            "SKIPPED",
        ):
            problems.append(
                f"check {check.get('name') or check.get('context')}: {outcome or check.get('status')}"
            )
    return problems


def merge(repo: str, pr: dict, body: str | None) -> str:
    """Squash-merge and return the merge commit."""
    args = [
        "pr",
        "merge",
        str(pr["number"]),
        "--repo",
        f"{OWNER}/{repo}",
        "--squash",
        "--subject",
        f"{pr['title']} (#{pr['number']})",
        "--body",
        body if body is not None else (pr["body"] or ""),
    ]
    gh(*args)
    for _ in range(30):
        merged = json.loads(
            gh(
                "pr",
                "view",
                str(pr["number"]),
                "--repo",
                f"{OWNER}/{repo}",
                "--json",
                "state,mergeCommit",
            )
        )
        if merged["state"] == "MERGED" and merged["mergeCommit"]:
            return merged["mergeCommit"]["oid"]
        time.sleep(2)
    raise SystemExit(f"{repo}#{pr['number']}: merge did not complete")


def warn_other_hosts(urls: list[str], branch: str) -> None:
    for url in urls:
        if git("ls-remote", "--heads", url, branch, cwd=Path.cwd(), check=False):
            print(
                f"warning: {url} has a branch {branch}; it is not on GitHub and must be merged by hand"
            )


def update_distro(
    root: Path, merged: dict[str, tuple[str, int, str, str]], dry: bool
) -> None:
    """merged: path -> (repo, pull request number, base branch, merge commit)."""
    recorded = recorded_branches(root)
    changed = False
    for path, (_repo, _number, base, commit) in merged.items():
        key = Path(path).name
        pinned = git("rev-parse", f"HEAD:{path}", cwd=root)
        if pinned == commit and recorded.get(key) == base:
            print(f"{path}: already at {commit[:7]} on {base}")
            continue
        changed = True
        branch_note = (
            ""
            if recorded.get(key) == base
            else f", recorded branch {recorded.get(key)} -> {base}"
        )
        print(f"{path}: {pinned[:7]} -> {commit[:7]}{branch_note}")
        if dry:
            continue
        git("update-index", "--cacheinfo", f"160000,{commit},{path}", cwd=root)
        git("submodule", "set-branch", "-b", base, "--", path, cwd=root)
        recorded[key] = base
    if not changed:
        print("Distro already up to date.")
        return
    if dry:
        return
    write_table(root / "pyproject.toml", recorded)
    summary = "\n".join(
        f"- {path}: {OWNER}/{repo}#{number} -> {base} {commit[:7]}"
        for path, (repo, number, base, commit) in merged.items()
    )
    git("add", "--", "pyproject.toml", ".gitmodules", *merged, cwd=root)
    git(
        "commit",
        "-q",
        "-m",
        "Point packages at the merged coordinated change",
        "-m",
        summary,
        cwd=root,
    )
    print(
        f"Committed {git('rev-parse', '--short', 'HEAD', cwd=root)} on {git('branch', '--show-current', cwd=root)}; push when ready."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("branch", help="shared branch name of the coordinated change")
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="only report what would happen"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--body", help="squash commit message body for every merged pull request"
    )
    group.add_argument("--body-file", type=Path, help="read the body from this file")
    args = parser.parse_args()
    body = args.body_file.read_text() if args.body_file else args.body

    root = Path(git("rev-parse", "--show-toplevel", cwd=Path.cwd()))
    github, other = packages_by_repo(root)
    unknown = sorted(set(github) - set(ORDER))
    if unknown:
        raise SystemExit(
            f"no merge order defined for: {', '.join(unknown)} (extend ORDER in {__file__})"
        )
    warn_other_hosts(other, args.branch)

    found: list[tuple[str, dict]] = []
    blocked = 0
    for repo in ORDER:
        if repo not in github:
            continue
        pr = find_pr(repo, args.branch)
        if pr is None:
            print(f"{repo}: no pull request from {args.branch}")
            continue
        found.append((repo, pr))
        if pr["state"] == "MERGED":
            print(
                f"{repo}#{pr['number']}: already merged into {pr['baseRefName']} as {pr['mergeCommit']['oid'][:7]}"
            )
            continue
        problems = blockers(pr, default_branch(repo))
        state = "blocked: " + ", ".join(problems) if problems else "ready"
        print(f"{repo}#{pr['number']} -> {pr['baseRefName']}: {state}  {pr['url']}")
        blocked += bool(problems)
    if not found:
        print("Nothing to merge.")
        return 0
    if blocked:
        print(f"Not merging: {blocked} pull request(s) blocked.")
        return 1

    merged: dict[str, tuple[str, int, str, str]] = {}
    for repo, pr in found:
        if pr["state"] == "MERGED":
            commit = pr["mergeCommit"]["oid"]
        elif args.dry_run:
            print(f"{repo}#{pr['number']}: would squash-merge into {pr['baseRefName']}")
            continue
        else:
            commit = merge(repo, pr, body)
            print(
                f"{repo}#{pr['number']}: merged into {pr['baseRefName']} as {commit[:7]}"
            )
        merged[github[repo]] = (repo, pr["number"], pr["baseRefName"], commit)
    update_distro(root, merged, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
