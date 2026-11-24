# Maintaining simulation issues and pull requests

For triage and review coordination across the simulation repositories.
Contributor instructions are in the [issue and PR guide](issue-and-pr-management.md).

## Priority

Use native issue Priority as the source of truth. Prioritize PR reviews using
linked issues and dependencies.

| Priority | Meaning |
|---|---|
| Urgent | An immediate blocker requiring interruption of current work. |
| High | Needed for an agreed release or goal, or a prerequisite to that work. |
| Medium | Valuable work that can follow the High-priority requirements. |
| Low | Longer-term or optional work with limited near-term impact. |

Start only as many issues as the team can actively handle. Record the reason when
changing an issue's Priority. Unclear scope needs assessment, not an automatic Low.

## Labels

Use labels for work type, affected area, and components such as programs or formats.
Apply multiple component labels when a change affects several components.

- `small`: understood work of at most half a day, including validation and review preparation.
- `testing`: tests, fixtures, or test infrastructure.

Agree additions and retirements based on useful filtering and workflow needs.

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

The `on hold` label can mark deferred, unstarted work, which stays in Backlog.
Done may automatically close an issue; confirm completion first.

## Review and triage

Assign reviewers and identify next actions for blocked PRs. Before merging, check
required reviews, current-head checks, unresolved discussions, and dependencies.

Review new work and waiting PRs weekly; milestone scope and label usefulness
monthly. Inactivity prompts review, not automatic closure.

## Temporary: parser reprocessing

This section can be removed after the current reprocessing effort.

- Existing per-code trackers record initial coverage; update their checklists and implementation links.
- Class labels group codes by data volume, method coverage, and legacy maturity. Tracker defaults: class 1/2 Medium; class 3/4 Low with `on hold`. Triage individual bugs and features separately.
- FHI-aims → VASP → Gaussian trackers are High exceptions. Shared schema/results prerequisites may come first; unstarted trackers stay in Backlog.
