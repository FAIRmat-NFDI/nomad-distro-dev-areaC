# Managing simulation issues and pull requests

This is the shared contribution and triage guide for the simulation repositories:

| Working name | GitHub repository |
|---|---|
| nomad-simulations | [FAIRmat-NFDI/nomad-simulations](https://github.com/FAIRmat-NFDI/nomad-simulations) |
| simulation-parsers | [FAIRmat-NFDI/nomad-parser-plugins-simulation](https://github.com/FAIRmat-NFDI/nomad-parser-plugins-simulation) |
| nomad-results-normalizer | [FAIRmat-NFDI/nomad-results-normalizer](https://github.com/FAIRmat-NFDI/nomad-results-normalizer) |
| nomad-simulation-apps | [FAIRmat-NFDI/nomad-app-plugins-simulation](https://github.com/FAIRmat-NFDI/nomad-app-plugins-simulation) |

Maintain these shared rules here. Each repository's `CONTRIBUTING.md` should link
to the published guide and retain its own setup, tests, coding conventions, and
scientific validation instructions. Document repository-specific exceptions there.
These rules apply to the four repositories above; they do not impose a workflow
on other projects using this development distribution.

## Choosing and recording work

Open work in the repository that owns the change. Give an issue a bounded problem
or decision, the expected outcome, relevant examples, and links to related work.
For scientific changes, state the affected quantities, methods or workflows and
the evidence that would establish correctness. Search for existing work first.

Use code-level parser trackers to summarize first-version coverage and link the
bounded implementation issues and PRs. Keep their checklists current without
turning every useful future capability into a requirement for the first version.
For work spanning repositories, link the owning issues and make dependencies
explicit rather than duplicating the same task in several places.

Maintainers triage new work for scope, affected labels, native Priority, milestone
fit, and the next action. Unknown scope needs assessment; it does not automatically
mean Low priority. A contributor can propose a priority or milestone and explain
the reason when either is unclear.

## Priority: importance of execution

Use GitHub's **native issue Priority** as the source of truth:

| Priority | Meaning |
|---|---|
| Urgent | A verified immediate blocker requiring interruption of current work. |
| High | Required for the selected parser work, schema release readiness, or a prerequisite decision for either. |
| Medium | Valuable work that can follow those requirements. |
| Low | Longer-term or optional work with limited near-term impact. |

High priority identifies important work; it is not a request to start every High
issue at once. Select a small active queue according to dependencies and available
capacity. Size, assignee, milestone, and current workflow state are separate
decisions. Explain substantial reprioritization briefly in the issue discussion.

Native issue fields do not apply to PRs. Communicate a PR's importance through its
linked issues, dependencies, milestone, and review request. Some projects also
have an older project-local Priority field, such as P0/P1/P2. Do not treat that as
the native issue Priority or maintain competing priority values by hand.

## Labels: useful filters

Use the repository's existing labels for the affected area, parser, and work type.
Apply multiple parser labels when several parsers are affected. Labels such as
`fhiaims`, `vasp`, and `gaussian` describe scope; they do not establish urgency or
release readiness.

The parser `class 1`–`class 4` labels describe strategic code cohorts, based on data
volume, method coverage, and legacy parser maturity. For code-level trackers:

- Class 1/2 default to **Medium**.
- Class 3/4 default to **Low** and carry the `on hold` label for deliberate deferral.
- The selected FHI-aims, VASP, and Gaussian trackers are **High** exceptions.

These defaults apply to code-level trackers. Triage individual bugs, features,
shared improvements, and PRs on their own merits.

Use `small` for understood work of at most half a day, including validation and
review preparation. It is distinct from `good first issue`: a short task can still
require specialist knowledge. Use `testing` for tests, fixtures, or test
infrastructure where that label exists.

Keep a label when it supports a useful query or workflow. Discuss ambiguous,
redundant, or obsolete labels during triage before retiring them. Existing labels
have not all been audited or harmonized.

## Milestones: completion scope

| Milestone | Completion boundary |
|---|---|
| Schema `1.0.0` | A stable public schema, with settled public contracts and the documentation, terminology, examples, code cleanup, and release preparation needed to support it. |
| Parser `1.0.0` | First usable versions across the code-level parser trackers, including FHI-aims, VASP, and Gaussian. Supported routes and methods, validation, and deferred gaps must be explicit. |
| Parser `reprocessing` | Shared/general readiness for production reprocessing, initially aligned with FHI-aims and VASP and coordinated across packages. |
| Parser-specific core readiness | Bounded feature and validation work for the agreed FHI-aims, VASP, or Gaussian core scope. |

Keep milestone descriptions current with scope, completion criteria, dependencies,
and agreed deferrals. Membership identifies intended scope; it does not establish
that every part of a broad architectural issue blocks the first reprocessing
round. Agree a concrete completion boundary for shared or broad issues.

Schema `1.0.0` is independent of the parser milestones and does not require every
parser method to be covered. Before schema release, give each plausible breaking
design issue an explicit disposition: implement the change, retain a compatible
approach, or defer with a rationale consistent with the stability commitment.
Public-facing documentation and cleanup are part of release readiness.

Parser `1.0.0` does not impose one completion date on every code or require the
three selected parsers to be released together. Core-readiness criteria still need
agreement on supported features and explicit inclusion or deferral of uncertain
capabilities. A milestone assignment alone is not evidence of readiness.

Add dates when scope and responsibility are agreed. Distinguish a forecast from a
commitment and revisit dates when the underlying plan changes.

## Boards: actual workflow state

Repository projects track repository work. The
[Area C reprocessing project](https://github.com/orgs/FAIRmat-NFDI/projects/25)
coordinates cross-package dependencies and sequencing. Link detailed implementation
work from the owning repository; keep the coordination task's next action clear.

Use each board's available status names with these meanings:

| Status | When to use it |
|---|---|
| Backlog | Work has not started; it may be deferred or still need assessment. |
| Ready / Todo | Work is sufficiently scoped to be picked up. |
| In progress | Someone is actively working on it. |
| In review | Work is ready for and awaiting review. Keep unfinished PRs in Draft. |
| On hold | Previously started work has paused. Record the blocker and what would allow it to resume. |
| Done | The issue's agreed completion criteria have been met. |

**Use board On hold only for work that has already started.** Unstarted class 3/4
trackers stay in Backlog even when they have Low Priority and the `on hold` label.
The label can mark deliberate deferral; board status records actual progress.
Preserve an existing hold unless the underlying blocker has been resolved.

The two main repository boards have enabled Done-to-issue-closure workflows.
Moving an open issue to Done can close it. Confirm completion before making that
transition; do not use it as a tidying action. Check automation effects before
changing workflow configuration.

## Pull requests and review

Link the owning issue or issues and explain the concrete behavior change, its
purpose, and the validation performed. Keep the PR's scope understandable; state
dependencies and whether related changes must land first.

- Use Draft while implementation or required validation is unfinished.
- When requesting review, identify the reviewer or team, the review needed, and
  any unresolved scientific or design question.
- For blocked work, state the blocker and next action. Request changes to a
  milestone or dependency plan when the original scope no longer fits.
- For scientific changes, provide meaningful source-backed checks of quantities,
  units, shapes, provenance, and supported workflows as applicable. Use the owning
  repository's validation instructions and selected integration/fixture gates.
- Before merging, check validation on the current head, required reviews,
  unresolved discussions, and dependencies. A passing default branch, an old
  approval, or a non-draft PR alone does not establish merge readiness.
- Use a closing reference only when the PR resolves the issue's agreed scope;
  otherwise link it without promising automatic closure.

Update the issue or tracker when the outcome changes its coverage, remaining gaps,
or next action. Summarize material decisions where future contributors can find
them rather than leaving the only explanation in chat.

## Shared triage and maintenance

Contributors keep progress, blockers, and review requests current. Maintainers
resolve prioritization and milestone scope across related work. Assign a maintainer
to keep this shared guide current; that responsibility can rotate with triage.

- **Weekly:** review selected parser progress, shared schema/results blockers, and
  waiting PRs. Choose a small active queue and finish with named next actions. The
  current parser sequence is FHI-aims → VASP → Gaussian; shared prerequisites may
  need to come first.
- **Monthly:** reassess milestone scope, deferred work, broad code trackers, and
  label usefulness. Record compatible deferrals and consider explicit proposals
  to split, consolidate, or close work. Inactivity alone is not a completion
  criterion or a reason for automatic closure.
- **Before a release or reprocessing round:** verify the agreed supported-feature
  scope against scientific and end-to-end evidence, dependency revisions, public
  documentation, examples, and known gaps.

Change shared rules through a documentation PR here, involving maintainers of the
affected repositories. Keep repository-specific exceptions in those repositories.
Link to this guide instead of copying it or introducing automatic synchronization.
Priorities, active work, dates, and detailed milestone scope live in GitHub; this
guide explains how to maintain those records. Review it during monthly triage and
whenever workflow conventions change.
