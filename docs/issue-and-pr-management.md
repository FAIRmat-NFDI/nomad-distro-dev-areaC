# Managing simulation issues and pull requests

Shared workflow for [nomad-simulations](https://github.com/FAIRmat-NFDI/nomad-simulations),
[simulation-parsers](https://github.com/FAIRmat-NFDI/nomad-parser-plugins-simulation),
[nomad-results-normalizer](https://github.com/FAIRmat-NFDI/nomad-results-normalizer), and
[nomad-simulation-apps](https://github.com/FAIRmat-NFDI/nomad-app-plugins-simulation).

## Issues

Create an issue in the repository where the code or documentation needs to change.
State the problem, expected result, and a useful example. Check for existing issues.
Link dependencies and related tasks across repositories.

Maintainers assign Priority, labels, and milestones; unclear issues need an assessment or decision as their next action.

## Priority

Use GitHub's native issue Priority as the source of truth.

| Priority | Meaning |
|---|---|
| Urgent | An immediate blocker requiring interruption of current work. |
| High | Needed for an agreed release or goal, or a prerequisite to that work. |
| Medium | Valuable work that can follow the High-priority requirements. |
| Low | Longer-term or optional work with limited near-term impact. |

Choose a small active queue and explain reprioritization. Unknown scope is not
automatically Low. Native Priority applies only to issues; prioritize PR reviews
using linked issues and dependencies.

## Labels

Label work type, affected area, and parser; use multiple parser labels for shared changes.

- `small`: understood work of at most half a day, including validation and review preparation.
- `testing`: tests, fixtures, or test infrastructure, where this label exists.

Agree label additions or retirements during triage.

## Milestones

Group work around a release or delivery goal. Describe completion criteria,
dependencies, and exclusions in the milestone.

- Include work needed for the goal; priority alone does not determine membership.
- Define completion separately for each repository and link dependencies.
- Record scope changes, deferrals, and date changes; distinguish forecasts from commitments.
- Close when criteria are met and remaining work is completed or explicitly deferred.

Keep release-specific plans in milestone descriptions and GitHub Discussions.

## Repository boards

Use each repository's persistent project board for workflow state.

| Status | Meaning |
|---|---|
| Backlog | Work has not started; it may be deferred or need assessment. |
| Ready / Todo | Scoped and ready to pick up. |
| In progress | Actively being worked on. |
| In review | Ready for and awaiting review. |
| On hold | Previously started work has paused; record the blocker and what will unblock it. |
| Done | The agreed completion criteria are met. |

**On hold is only for started work.** The `on hold` label can mark deferred,
unstarted work, which stays in Backlog. Done may automatically close an issue;
confirm completion first.

## Pull requests

- Link issues; explain the change, purpose, dependencies, and validation.
- Use Draft until ready; request review and identify open design questions.
- Follow repository test instructions; validate scientific values, units, shapes, and provenance where applicable.
- Before merging, check reviews, current-head checks, unresolved discussions, and dependencies.
- Use closing references only for fully resolved issues. Update linked issues with outcomes and remaining gaps.

## Regular triage

Contributors update status, blockers, and next actions. Maintainers review new work
and waiting PRs weekly; milestone scope and label usefulness monthly. Inactivity
prompts review, not automatic closure.

## Temporary: parser reprocessing

Remove this section when the current reprocessing effort is finished.

- Existing per-code trackers record initial coverage; update their checklists and implementation links.
- Class labels group codes by data volume, method coverage, and legacy maturity. Tracker defaults: class 1/2 Medium; class 3/4 Low with `on hold`. Triage individual bugs and features separately.
- FHI-aims → VASP → Gaussian trackers are High exceptions. Shared schema/results prerequisites may come first; unstarted trackers stay in Backlog.
