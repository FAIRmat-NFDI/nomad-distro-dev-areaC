# NOMAD Area C Development Distribution

This repository is the common starting base for FAIRmat Area C (computational materials science) to develop setups that coordinate changes across the NOMAD simulation stack. It is a fork of [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev): a `uv` workspace that installs `nomad-lab` and a curated set of plugins in editable mode from git submodules under `packages/`, so a single environment spans all repositories under active development.

For the general setup instructions (Docker services, `uv` installation, adding or removing plugins, day-to-day commands), refer to the upstream [`nomad-distro-dev` README](https://github.com/FAIRmat-NFDI/nomad-distro-dev#readme). This README only covers what is specific to the Area C distribution: which packages it tracks, the local setup with worktrees and package branches, and the protocol for coordinated branches, pull requests, and CI across them.

## What this distribution tracks

Each coordinated repository follows the branch listed below — `develop` wherever one exists, otherwise `main`:

| Package | Repository | Form |
| --- | --- | --- |
| `nomad-lab` | [nomad-FAIR](https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-FAIR) (GitLab) | submodule, editable |
| `nomad-simulations` | [nomad-simulations](https://github.com/FAIRmat-NFDI/nomad-simulations) | submodule, editable |
| `nomad-simulation-parsers` | [nomad-parser-plugins-simulation](https://github.com/FAIRmat-NFDI/nomad-parser-plugins-simulation) | submodule, editable |
| `nomad-file-parser` | [nomad-file-parser](https://github.com/FAIRmat-NFDI/nomad-file-parser) | submodule, editable |
| `nomad-results-normalizer` | [nomad-results-normalizer](https://github.com/FAIRmat-NFDI/nomad-results-normalizer) | submodule on `main`, editable |
| `nomad-gui` | [nomad-gui](https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-gui) (GitLab) | git pin on `develop` (`infra/` subdirectory), not editable |
| — | [nomad-simulation-parser-test-fixtures](https://github.com/FAIRmat-NFDI/nomad-simulation-parser-test-fixtures) | submodule on `main`, data only |

The branch each package follows is recorded in `pyproject.toml` under `[tool.distro.packages]` and mirrored in `.gitmodules` (see [Local setup](#local-setup-worktrees-and-package-branches)), and the weekly `Update Submodules` workflow opens a pull request that advances all pointers to the current tips. Note that `nomad-simulation-parsers` pins `nomad-simulations` and `nomad-file-parser` to their `develop` branches in its own `pyproject.toml`; the workspace drops these pins through `override-dependencies` so that the local checkouts are used instead.

The test-fixtures submodule carries no Python package: it stores large test inputs for `nomad-simulation-parsers`, with paths mirroring `tests/data/` in the parser repository, and is excluded from the `uv` workspace. It tracks `main` because the repository has no `develop` branch. The parser tests marked `large_fixture` (and the pipeline tests that use them) read these inputs from the directory named by `NOMAD_SIM_PARSERS_LARGE_FIXTURE_ROOT`, so point it at the submodule's `tests/data` when running them locally:

```bash
cd packages/nomad-simulation-parsers
NOMAD_SIM_PARSERS_LARGE_FIXTURE_ROOT=$PWD/../nomad-simulation-parser-test-fixtures/tests/data \
  uv run pytest tests -m 'pipeline or large_fixture'
```

## Quickstart

```bash
git clone --recurse-submodules git@github.com:FAIRmat-NFDI/nomad-distro-dev-areaC.git
cd nomad-distro-dev-areaC
uv run poe track   # packages from the pinned commits onto their recorded branches
uv run poe setup   # starts docker services (nomad.yaml is committed)
uv run poe start   # API + new GUI at http://localhost:8000/nomad-oasis/gui/v2/
```

Run a package's tests from the workspace with `uv run --directory packages/<package> pytest`.

Unlike upstream, this distribution commits its `nomad.yaml`. Authentication uses the central NOMAD Keycloak with the `fairdi_nomad_test` realm (shared test users such as `test`/`password`), and the loaded plugins are restricted to the Area C stack through wildcard patterns in `plugins.entry_points.include` (for example `nomad_simulation_parsers.*`), plus the two built-in search apps the GUI uses. Wildcard support in the include/exclude lists landed on `nomad-FAIR`'s `develop` in September 2026, which this distribution tracks.

## Local setup: worktrees and package branches

**Recorded state.** Two things describe which code a distro branch uses. The branch each package follows is recorded in `pyproject.toml` under `[tool.distro.packages]` (mirrored in `.gitmodules`); `uv` ignores this table, since the workspace only knows the folders under `packages/`. The exact commits are the submodule pointers stored in the distro commit (`git ls-tree HEAD packages/`). Three poe tasks move between the checkouts and this record; each takes `-n` for a dry run:

- `uv run poe track` switches every package to its recorded branch and fast-forwards it to `origin`. Packages on another branch, with uncommitted changes, or not initialised are left alone.
- `uv run poe record` writes the branches currently checked out into `[tool.distro.packages]` and `.gitmodules` (detached packages keep their entry). Review with `git diff` and commit.
- `uv run poe pin` commits the checked-out commits as submodule pointers, listing what moved in the commit message. It does not push.

For a coordinated change, check out the shared branch in each affected package, run `poe record` and commit, so that `poe track` follows those branches on this distro branch. Run `poe pin` whenever the distro branch should reference an exact state, at the latest before merging, and set the recorded branches back to the tracked ones (`develop` or `main`) before the distro pull request is merged.

**Worktrees.** One clone can hold several distro branches side by side with `git worktree`; each worktree gets its own package checkouts and its own `.venv`:

```bash
cd nomad-distro-dev-areaC                       # the main clone
git worktree add -b <initials>/<name> ../<name> main
cd ../<name>
git submodule update --init                     # packages at the pinned commits, detached
uv run poe track                                # packages onto their recorded branches
uv sync
```

Initialise the submodules with plain `git` first: `uv run` syncs the workspace before running a task, which fails while `packages/` is empty. Remove a worktree with `git worktree remove ../<name>` once its packages hold no uncommitted work.

**Docker in worktrees.** Docker Compose names its volumes after the directory, so `docker compose up -d` inside a worktree creates a separate, empty set of volumes (`<name>_nomad_mongo`, `<name>_nomad_elastic`, ...). That suits throwaway tests; for uploads and entries that should persist, start the infrastructure from the main clone and use its volumes. Only one stack can run at a time, because the compose file fixes the container names (`nomad_elastic`, `nomad_mongo`, `nomad_temporal`) and ports, so stop the running stack before switching. Remove a worktree's volumes with `docker compose down -v` from that worktree when its tests are done.

## Coordinated development protocol

The purpose of this distribution is to make changes that span several repositories reviewable and testable as one unit. The protocol has three parts: a branch convention, a coordinated set of pull requests, and CI verification.

**Branches.** For a coordinated change, pick one descriptive branch name and use it in every repository the change touches. Create the branch from the tracked branch (usually `develop`) in each affected package repository, and a branch with the same name from this repository's starting base. In the distro branch, record the shared branch for the affected packages (`uv run poe record`) and commit the submodule pointers at the tips of the package branches (work inside `packages/<package>` as in any git checkout: branch, commit, push; then `uv run poe pin` in the distro commits the moved pointers). The submodule pointers make the distro branch an exact snapshot of the coordinated state, which `uv sync` materializes; the one floating element is `nomad-gui`, which resolves from its `develop` branch at lock time. The branch namespace in this repository follows two conventions:

- Starting bases are `main` and, in the future, additional standard setups published as `std/<branch name>`; coordinated work forks from and merges back into one of these.
- Feature branches carry their owner's initials as a prefix, e.g. `jfr/<branch name>`, and the same prefixed name is used in every repository the change touches.

**Pull requests.**

- Open a pull request in each affected package repository (base: its tracked branch, usually `develop`) and one in this repository (base: the starting branch, e.g. `main`).
- The distro pull request is the coordination point: its description lists and links every package pull request, and each package pull request links back to it.
- Merge in dependency order, leaves first: package pull requests are merged into their tracked branches, then the distro branch is updated to point the submodules at the resulting commits, and finally the distro pull request is merged.
- Never merge a distro pull request while its submodule pointers still reference branches that have been deleted or rewritten.

**Merging.** The `Merge coordinated PRs` workflow (`.github/workflows/merge-coordinated-prs.yaml`) performs the merge step. Run it from the distro branch of the change (or pass the branch name as input): it finds the package pull requests whose head is that branch, checks that every open one can be merged (targets the default branch, not a draft, no conflicts, checks green, reviews done) and refuses to merge anything otherwise, since merges across repositories are not atomic. It then squash-merges them leaves first, points the submodules at the resulting commits, sets the recorded branches back to the base branches, and pushes that commit to the distro branch. Already merged pull requests count as done, so a run that stopped halfway can be repeated. The `dry_run` input (default on) only reports; the `body` input replaces the squash commit message body of every merged pull request. The distro pull request is then ready for a human to merge. The same logic runs locally as `uv run poe merge-prs <branch> [-n]` with an authenticated `gh`; the workflow needs the `MERGE_TOKEN` secret, a fine-grained PAT that may merge in the package repositories. Branches of the GitLab-hosted packages are reported and must be merged by hand.

**CI verification.** Each package repository runs its own CI when its branch is pushed, so the per-repository checks come for free. To re-run those per-repository checks on demand, this repository provides the `Trigger sub-CI` workflow (`.github/workflows/trigger-sub-ci.yaml`). Run it from the Actions tab or with the CLI:

```bash
gh workflow run trigger-sub-ci.yaml -f ref=<branch> \
  -f repos=nomad-simulations,nomad-parser-plugins-simulation,nomad-file-parser,nomad-results-normalizer
```

The `ref` input defaults to `tracked`, which resolves to each repository's default branch (`develop` or `main` per the table above) — the right choice for a routine health check. For a coordinated change, pass the shared branch name explicitly; repositories without that branch are reported as warnings.

It dispatches the `actions.yml` CI of each listed GitHub repository on the given ref and links the resulting runs in the workflow summary. Two properties to be aware of: each repository tests its branch in isolation, with its own dependency resolution rather than the distro workspace, and the dispatch is fire-and-forget — results are checked through the summary links, not reflected in the trigger run. The GitLab-hosted repositories (`nomad-FAIR`, `nomad-gui`) are not covered. If a repository is reported as a warning instead of a dispatch, the `SUB_CI_TOKEN` secret or the target's `workflow_dispatch` trigger needs attention from a maintainer.

The combined state — all coordinated branches resolved together through the workspace overrides — is verified locally: `uv sync` to materialize it, then run the test suites of the affected packages with `uv run --directory packages/<package> pytest`.
