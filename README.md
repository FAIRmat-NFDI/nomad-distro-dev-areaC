# NOMAD Area C Development Distribution

This repository is the common starting base for FAIRmat Area C (computational materials science) to develop setups that coordinate changes across the NOMAD simulation stack. It is a fork of [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev): a `uv` workspace that installs `nomad-lab` and a curated set of plugins in editable mode from git submodules under `packages/`, so a single environment spans all repositories under active development.

For the general setup instructions (Docker services, `uv` installation, adding or removing plugins, day-to-day commands), refer to the upstream [`nomad-distro-dev` README](https://github.com/FAIRmat-NFDI/nomad-distro-dev#readme). This README only covers what is specific to the Area C distribution: which packages it tracks and the protocol for coordinated branches, pull requests, and CI across them.

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

Each submodule declares its tracked branch in `.gitmodules`, and the weekly `Update Submodules` workflow opens a pull request that advances all pointers to the current tips. Note that `nomad-simulation-parsers` pins `nomad-simulations` and `nomad-file-parser` to their `develop` branches in its own `pyproject.toml`; the workspace drops these pins through `override-dependencies` so that the local checkouts are used instead.

The test-fixtures submodule carries no Python package: it stores large test inputs for `nomad-simulation-parsers`, with paths mirroring `tests/data/` in the parser repository, and is excluded from the `uv` workspace. It tracks `main` because the repository has no `develop` branch. The parser tests marked `large_fixture` (and the pipeline tests that use them) read these inputs from the directory named by `NOMAD_SIM_PARSERS_LARGE_FIXTURE_ROOT`, so point it at the submodule's `tests/data` when running them locally:

```bash
cd packages/nomad-simulation-parsers
NOMAD_SIM_PARSERS_LARGE_FIXTURE_ROOT=$PWD/../nomad-simulation-parser-test-fixtures/tests/data \
  uv run pytest tests -m 'pipeline or large_fixture'
```

## Standard setup `std/legacy`

The `std/legacy` branch is a starting base for work that bridges the legacy simulation stack and the one above: comparing what the legacy parsers write to `archive.run` with what the new parsers write to `archive.data`, and maintaining the mapping between the two schemas. On top of `main`, it adds the legacy parsers and the schemas they write as editable workspace members, tracking `develop` (or `master` where no `develop` exists):

| Package | Repository | Form |
| --- | --- | --- |
| `nomad-parser-plugins-electronic` | [electronic-parsers](https://github.com/nomad-coe/electronic-parsers) | submodule, editable |
| `nomad-parser-plugins-atomistic` | [atomistic-parsers](https://github.com/nomad-coe/atomistic-parsers) | submodule, editable |
| `nomad-parser-plugins-workflow` | [workflow-parsers](https://github.com/nomad-coe/workflow-parsers) | submodule on `master`, editable |
| `nomad-schema-plugin-run` (`runschema`) | [nomad-schema-plugin-run](https://github.com/nomad-coe/nomad-schema-plugin-run) | submodule, editable |
| `nomad-schema-plugin-simulation-workflow` (`simulationworkflowschema`) | [nomad-schema-plugin-simulation-workflow](https://github.com/nomad-coe/nomad-schema-plugin-simulation-workflow) | submodule, editable |

Their entry points are added to the `nomad.yaml` include list, so both parser generations are loaded side by side. For files both can read, `match_parser` returns only one of them, and `match_parser(..., parser_name=...)` forces the named parser without testing the file; to pick a generation, test the candidates' `is_mainfile` instead, as `legacy/parity/parity_collect.py` does. Keep `std/legacy` current by merging `main` into it; changes meant for every setup go to `main` first.

### Tools

The `legacy/` directory holds the tooling that relates the two stacks; its [README](legacy/README.md) documents the conventions and the method in detail.

| Tool | Purpose |
| --- | --- |
| `legacy/runschema_mapping.md` | Attribute-level mapping from `runschema` to `nomad-simulations`, with Mapped, Partial and Unmapped status per row. |
| `legacy/parity/mapping_check.py` | Verifies that every row of the mapping resolves in the installed schemas. |
| `legacy/parity/parity_collect.py` | Runs the legacy or the new parsers on a directory of test files and records the archive paths they fill. |
| `legacy/parity/parity_report.py` | Compares both recordings through the mapping and writes `legacy/parity_report.md`. |

All of them run from the distribution root in the `std/legacy` environment; the tests are under `legacy/tests` (`uv run pytest legacy/tests`).

## Quickstart

```bash
git clone --recurse-submodules git@github.com:FAIRmat-NFDI/nomad-distro-dev-areaC.git
cd nomad-distro-dev-areaC
uv run poe setup   # starts docker services (nomad.yaml is committed)
uv run poe start   # API + new GUI at http://localhost:8000/nomad-oasis/gui/v2/
```

Run a package's tests from the workspace with `uv run --directory packages/<package> pytest`.

Unlike upstream, this distribution commits its `nomad.yaml`. Authentication uses the central NOMAD Keycloak with the `fairdi_nomad_test` realm (shared test users such as `test`/`password`), and the loaded plugins are restricted to the Area C stack through wildcard patterns in `plugins.entry_points.include` (for example `nomad_simulation_parsers.*`), plus the two built-in search apps the GUI uses. Wildcard support in the include/exclude lists landed on `nomad-FAIR`'s `develop` in September 2026, which this distribution tracks.

## Coordinated development protocol

The purpose of this distribution is to make changes that span several repositories reviewable and testable as one unit. The protocol has three parts: a branch convention, a coordinated set of pull requests, and CI verification.

**Branches.** For a coordinated change, pick one descriptive branch name and use it in every repository the change touches. Create the branch from the tracked branch (usually `develop`) in each affected package repository, and a branch with the same name from this repository's starting base. In the distro branch, commit the submodule pointers at the tips of the package branches (work inside `packages/<package>` as in any git checkout: branch, commit, push; then `git add packages/<package>` in the distro and commit the moved pointer). The submodule pointers make the distro branch an exact snapshot of the coordinated state, which `uv sync` materializes; the one floating element is `nomad-gui`, which resolves from its `develop` branch at lock time. The branch namespace in this repository follows two conventions:

- Starting bases are `main` and, in the future, additional standard setups published as `std/<branch name>`; coordinated work forks from and merges back into one of these.
- Feature branches carry their owner's initials as a prefix, e.g. `jfr/<branch name>`, and the same prefixed name is used in every repository the change touches.

**Pull requests.**

- Open a pull request in each affected package repository (base: its tracked branch, usually `develop`) and one in this repository (base: the starting branch, e.g. `main`).
- The distro pull request is the coordination point: its description lists and links every package pull request, and each package pull request links back to it.
- Merge in dependency order, leaves first: package pull requests are merged into their tracked branches, then the distro branch is updated to point the submodules at the resulting commits, and finally the distro pull request is merged.
- Never merge a distro pull request while its submodule pointers still reference branches that have been deleted or rewritten.

**CI verification.** Each package repository runs its own CI when its branch is pushed, so the per-repository checks come for free. To re-run those per-repository checks on demand, this repository provides the `Trigger sub-CI` workflow (`.github/workflows/trigger-sub-ci.yaml`). Run it from the Actions tab or with the CLI:

```bash
gh workflow run trigger-sub-ci.yaml -f ref=<branch> \
  -f repos=nomad-simulations,nomad-parser-plugins-simulation,nomad-file-parser,nomad-results-normalizer
```

The `ref` input defaults to `tracked`, which resolves to each repository's default branch (`develop` or `main` per the table above) — the right choice for a routine health check. For a coordinated change, pass the shared branch name explicitly; repositories without that branch are reported as warnings.

It dispatches the `actions.yml` CI of each listed GitHub repository on the given ref and links the resulting runs in the workflow summary. Two properties to be aware of: each repository tests its branch in isolation, with its own dependency resolution rather than the distro workspace, and the dispatch is fire-and-forget — results are checked through the summary links, not reflected in the trigger run. The GitLab-hosted repositories (`nomad-FAIR`, `nomad-gui`) are not covered. If a repository is reported as a warning instead of a dispatch, the `SUB_CI_TOKEN` secret or the target's `workflow_dispatch` trigger needs attention from a maintainer.

The combined state — all coordinated branches resolved together through the workspace overrides — is verified locally: `uv sync` to materialize it, then run the test suites of the affected packages with `uv run --directory packages/<package> pytest`.
