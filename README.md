# NOMAD Area C Development Distribution

This repository is the common starting base for FAIRmat Area C (computational materials science) work on the NOMAD simulation stack. It bundles the repositories of that stack as editable checkouts in one `uv` workspace, on `main` and on standard setups published as `std/<name>` branches that add further packages for a particular kind of work, and ships the tools around them: poe tasks that set the environment up and keep every package on its recorded branch, and workflows that advance the packages weekly, dispatch their CI, and merge a change spanning several repositories as one unit. The packages and the standard setups are listed in [What this distribution tracks](#what-this-distribution-tracks) at the end.

The workspace is a fork of [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev), which installs `nomad-lab` and the plugins in editable mode from git submodules under `packages/`. For the general setup instructions (Docker services, `uv` installation, adding or removing plugins, day-to-day commands), refer to the upstream [`nomad-distro-dev` README](https://github.com/FAIRmat-NFDI/nomad-distro-dev#readme). This README only covers what is specific to the Area C distribution: the protocol for coordinated issues, branches, pull requests, CI, and merging across repositories, the local setup with worktrees and package branches, and what it tracks.

## Coordinated development protocol

The purpose of this distribution is to make changes that span several repositories reviewable and testable as one unit. Two kinds of work are tracked here, and they follow different rules.

**Distribution issues** concern this repository itself: setup, tooling, workflows, documentation, the recorded branches. They carry the `distro` label. A pull request that addresses one is based on `main` (or on the `std/<name>` branch it is specific to), needs one approval, and is merged; `main` is then merged into every `std/<name>` branch so all setups pick it up. The starting bases (`main` and `std/<name>`) move **only** through such pull requests and the weekly `Update Submodules` pull requests: **no direct pushes**.

**Coordination issues** track a change that spans several packages. They carry labels for the packages in scope, link the package issues and pull requests they coordinate, and those link back. A pull request for one may exist here, but it is a working record, not a change to the distribution: it is **never merged** into a starting base, and it is **closed by hand**, together with its issue, once the package pull requests are in. The protocol for such a change has three parts: a branch convention, a coordinated set of pull requests, and CI verification.

**Branches.** Pick **one** descriptive branch name and use it in **every** repository the change touches. Create the branch from the tracked branch (usually `develop`) in each affected package repository, and a branch with the same name from this repository's starting base. In the distro branch, record the shared branch for the affected packages (`uv run poe record`) and commit the submodule pointers at the tips of the package branches (work inside `packages/<package>` as in any git checkout: branch, commit, push; then `uv run poe pin` in the distro commits the moved pointers; see [Local setup](#local-setup-worktrees-and-package-branches)). The submodule pointers make the distro branch an exact snapshot of the coordinated state, which `uv sync` materializes; the one floating element is `nomad-gui`, which resolves from its `develop` branch at lock time. The branch namespace in this repository follows two conventions:

- Starting bases are `main` and the standard setups `std/<name>` listed under [What this distribution tracks](#what-this-distribution-tracks); coordinated work forks from one of these and is **not merged back**.
- Feature branches carry their owner's initials as a prefix, e.g. `jfr/<branch name>`, and the same prefixed name is used in every repository the change touches.

**Pull requests.**

- Open a pull request in each affected package repository (base: its tracked branch, usually `develop`) and, as the coordination record, one in this repository (base: the starting branch, e.g. `main`). Assign your pull requests to yourself.
- The distro pull request is the coordination point: its description lists and links every package pull request, and each package pull request links back to it.
- Merge in dependency order, leaves first: package pull requests are merged into their tracked branches, then the distro branch is updated to point the submodules at the resulting commits. Both steps are automated by the `Merge coordinated PRs` workflow (see Merging below).
- The distro pull request is **not merged**: once the package pull requests are in and the pointers recorded, **close it by hand** together with its issue. The next weekly `Update Submodules` run brings the merged commits into `main` and the `std/<name>` branches.

**Merging.** The `Merge coordinated PRs` workflow (`.github/workflows/merge-coordinated-prs.yaml`) performs the merge step. Run it from the distro branch of the change (or pass the branch name as input): it finds the package pull requests whose head is that branch, checks that every open one can be merged (targets the default branch, not a draft, no conflicts, checks green, reviews done; a closed, unmerged one blocks too) and **refuses to merge anything otherwise**, since merges across repositories are not atomic. It then squash-merges them leaves first, each pinned to the head commit that passed the checks, points the submodules at the resulting commits, sets the recorded branches back to the base branches, and pushes that commit to the distro branch. Already merged pull requests count as done, so a run that stopped halfway can be repeated. The `dry_run` input (**default on**) only reports; the `body` input replaces the squash commit message body of every merged pull request. The distro pull request is then closed by hand. The same logic runs locally as `uv run poe merge-prs <branch> [-n]` from a clean checkout of that distro branch, with an authenticated `gh`. The workflow runs in the `package-repos` environment, which holds the `MERGE_TOKEN` secret (a fine-grained PAT that may merge in the package repositories) and requires a reviewer to approve each dispatch before the token is released, since the job executes the script of the dispatched branch. Branches of the GitLab-hosted packages are reported and **must be merged by hand**.

**CI verification.** Each package repository runs its own CI when its branch is pushed, so the per-repository checks come for free. To re-run those per-repository checks on demand, this repository provides the `Trigger sub-CI` workflow (`.github/workflows/trigger-sub-ci.yaml`). Run it from the Actions tab or with the CLI:

```bash
gh workflow run trigger-sub-ci.yaml -f ref=<branch> \
  -f repos=nomad-simulations,nomad-parser-plugins-simulation,nomad-file-parser,nomad-results-normalizer
```

The `ref` input defaults to `tracked`, which resolves to each repository's default branch (`develop` or `main` per the package table under [What this distribution tracks](#what-this-distribution-tracks)) — the right choice for a routine health check. For a coordinated change, pass the shared branch name explicitly; repositories without that branch are reported as warnings.

It dispatches the `actions.yml` CI of each listed GitHub repository on the given ref and links the resulting runs in the workflow summary. Two properties to be aware of: each repository tests its branch in isolation, with its own dependency resolution rather than the distro workspace, and the dispatch is fire-and-forget — results are checked through the summary links, not reflected in the trigger run. The GitLab-hosted repositories (`nomad-FAIR`, `nomad-gui`) are not covered. The workflow runs in the `package-repos` environment, which holds the `SUB_CI_TOKEN` secret and requires a reviewer to approve each dispatch. If a repository is reported as a warning instead of a dispatch, that secret or the target's `workflow_dispatch` trigger needs attention from a maintainer.

The combined state — all coordinated branches resolved together through the workspace overrides — is verified locally: `uv sync` to materialize it, then run the test suites of the affected packages with `uv run --directory packages/<package> pytest`.

## Quickstart

```bash
git clone --recurse-submodules git@github.com:FAIRmat-NFDI/nomad-distro-dev-areaC.git
cd nomad-distro-dev-areaC
uv run poe track   # moves the packages from the pinned commits onto their recorded branches
uv run poe setup   # starts docker services (nomad.yaml is committed)
uv run poe start   # serves the API and the new GUI at http://localhost:8000/nomad-oasis/gui/v2/
```

Run a package's tests from the workspace with `uv run --directory packages/<package> pytest`.

Unlike upstream, this distribution commits its `nomad.yaml`. Authentication uses the central NOMAD Keycloak with the `fairdi_nomad_test` realm (shared test users such as `test`/`password`), and the loaded plugins are restricted to the Area C stack through wildcard patterns in `plugins.entry_points.include` (for example `nomad_simulation_parsers.*`), plus the two built-in search apps the GUI uses. Wildcard support in the include/exclude lists landed on `nomad-FAIR`'s `develop` in September 2026, which this distribution tracks.

## Local setup: worktrees and package branches

**Recorded state.** Two things describe which code a distro branch uses:

1. **The branch each package follows**, recorded in `pyproject.toml` under `[tool.distro.packages]` and mirrored in `.gitmodules`. `uv` ignores this table: the workspace only knows the folders under `packages/`.
2. **The exact commits**, stored as the submodule pointers of the distro commit (`git ls-tree HEAD packages/`).

Three poe tasks move between the checkouts and this record; each takes `-n` for a dry run:

- `uv run poe track` switches every package to its recorded branch and fast-forwards it to `origin`. Packages on another branch, with uncommitted changes, or not initialised are left alone.
- `uv run poe record` writes the branches currently checked out into `[tool.distro.packages]` and `.gitmodules` (detached packages keep their entry). Review with `git diff` and commit.
- `uv run poe pin` commits the checked-out commits as submodule pointers, listing what moved in the commit message. It **does not push**.

For a coordinated change, check out the shared branch in each affected package, run `poe record` and commit, so that `poe track` follows those branches on this distro branch. Run `poe pin` whenever the distro branch should reference an exact state, **at the latest before the coordinated merge**; the merge workflow then sets the recorded branches back to the tracked ones (`develop` or `main`) itself.

**Worktrees.** One clone can hold several distro branches side by side with `git worktree`; each worktree gets its own package checkouts and its own `.venv`:

```bash
cd nomad-distro-dev-areaC                       # starts from the main clone
git worktree add -b <initials>/<name> ../<name> main
cd ../<name>
git submodule update --init                     # checks the packages out at the pinned commits, detached
uv run poe track                                # moves the packages onto their recorded branches
uv sync
```

Initialise the submodules with **plain `git` first**: `uv run` syncs the workspace before running a task, which fails while `packages/` is empty. Remove a worktree with `git worktree remove ../<name>` once its packages hold no uncommitted work.

**Docker in worktrees.** Docker Compose names its volumes after the directory, so `docker compose up -d` inside a worktree creates a separate, empty set of volumes (`<name>_nomad_mongo`, `<name>_nomad_elastic`, ...). That suits throwaway tests; for uploads and entries that should persist, start the infrastructure from the main clone and use its volumes. **Only one stack can run at a time**, because the compose file fixes the container names (`nomad_elastic`, `nomad_mongo`, `nomad_temporal`) and ports, so stop the running stack before switching. Remove a worktree's volumes with `docker compose down -v` from that worktree when its tests are done.

## What this distribution tracks

Each coordinated repository follows the branch listed below — `develop` wherever one exists, otherwise `main`:

| Package | Repository | How it is included |
| --- | --- | --- |
| `nomad-lab` | [nomad-FAIR](https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-FAIR) (GitLab) | submodule, editable |
| `nomad-simulations` | [nomad-simulations](https://github.com/FAIRmat-NFDI/nomad-simulations) | submodule, editable |
| `nomad-simulation-parsers` | [nomad-parser-plugins-simulation](https://github.com/FAIRmat-NFDI/nomad-parser-plugins-simulation) | submodule, editable |
| `nomad-file-parser` | [nomad-file-parser](https://github.com/FAIRmat-NFDI/nomad-file-parser) | submodule, editable |
| `nomad-results-normalizer` | [nomad-results-normalizer](https://github.com/FAIRmat-NFDI/nomad-results-normalizer) | submodule on `main`, editable |
| `nomad-gui` | [nomad-gui](https://gitlab.mpcdf.mpg.de/nomad-lab/nomad-gui) (GitLab) | `uv` git dependency resolved from `develop` at lock time (the Python package lives in the repository's `infra/` directory); no checkout under `packages/`, so not editable here |
| (no package) | [nomad-simulation-parser-test-fixtures](https://github.com/FAIRmat-NFDI/nomad-simulation-parser-test-fixtures) | submodule on `main`; large test inputs for `nomad-simulation-parsers`, not a Python package |

The branch each package follows is recorded in `pyproject.toml` under `[tool.distro.packages]` and mirrored in `.gitmodules` (see [Local setup](#local-setup-worktrees-and-package-branches)), and the weekly `Update Submodules` workflow opens a pull request that advances all pointers to the current tips. Note that `nomad-simulation-parsers` pins `nomad-simulations` and `nomad-file-parser` to their `develop` branches in its own `pyproject.toml`; the workspace drops these pins through `override-dependencies` so that the local checkouts are used instead.

The test-fixtures submodule carries no Python package: it stores large test inputs for `nomad-simulation-parsers`, with paths mirroring `tests/data/` in the parser repository, and is excluded from the `uv` workspace. It tracks `main` because the repository has no `develop` branch. The parser tests marked `large_fixture` (and the pipeline tests that use them) read these inputs from the directory named by `NOMAD_SIM_PARSERS_LARGE_FIXTURE_ROOT`, so point it at the submodule's `tests/data` when running them locally:

```bash
cd packages/nomad-simulation-parsers
NOMAD_SIM_PARSERS_LARGE_FIXTURE_ROOT=$PWD/../nomad-simulation-parser-test-fixtures/tests/data \
  uv run pytest tests -m 'pipeline or large_fixture'
```

**Standard setups.** `main` carries the stack above and is the base for everything else. A `std/<name>` branch is a standard setup built on top of it: the same tooling, with further packages added for a particular kind of work, and its README documents those additions. Each one is kept current by merging `main` into it, so **changes meant for every setup go to `main` first**, and the weekly `Update Submodules` workflow opens a pull request against each of these branches, not only `main`.

| Branch | Use it for |
| --- | --- |
| `main` | coordinated development of the packages listed above |
| `std/main` | the default setup under the `std/` namespace; identical to `main`, nothing added |
| `std/legacy` | work that bridges the legacy simulation stack and the one above: comparing what the legacy parsers write to `archive.run` with what the new parsers write to `archive.data`, and maintaining the mapping between the two schemas |

`std/legacy` adds the legacy parsers and the schemas they write as editable workspace members, tracking `develop` (or `master` where no `develop` exists), and includes their entry points in `nomad.yaml` so both parser generations load side by side:

| Package | Repository | How it is included |
| --- | --- | --- |
| `nomad-parser-plugins-electronic` (`electronicparsers`) | [electronic-parsers](https://github.com/nomad-coe/electronic-parsers) | submodule, editable |
| `nomad-parser-plugins-atomistic` (`atomisticparsers`) | [atomistic-parsers](https://github.com/nomad-coe/atomistic-parsers) | submodule, editable |
| `nomad-parser-plugins-workflow` (`workflowparsers`) | [workflow-parsers](https://github.com/nomad-coe/workflow-parsers) | submodule on `master`, editable |
| `nomad-schema-plugin-run` (`runschema`) | [nomad-schema-plugin-run](https://github.com/nomad-coe/nomad-schema-plugin-run) | submodule, editable |
| `nomad-schema-plugin-simulation-workflow` (`simulationworkflowschema`) | [nomad-schema-plugin-simulation-workflow](https://github.com/nomad-coe/nomad-schema-plugin-simulation-workflow) | submodule, editable |
