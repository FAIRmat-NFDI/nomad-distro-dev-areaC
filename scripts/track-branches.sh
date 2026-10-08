#!/usr/bin/env bash
# Put every submodule on the branch .gitmodules declares for it (`git submodule update` leaves them detached),
# fast-forwarded to origin's tip. Packages on another branch, with uncommitted changes, or not initialised are skipped.
#
#   scripts/track-branches.sh       switch and fast-forward
#   scripts/track-branches.sh -n    only show what it would do
set -euo pipefail

dry=""
[ "${1:-}" = "-n" ] && dry=1
root=$(git rev-parse --show-toplevel)
cd "$root"
status=0
while read -r key path; do
  name=${key#submodule.}; name=${name%.path}
  branch=$(git config -f .gitmodules "submodule.$name.branch" || true)
  if [ -z "$branch" ]; then echo "$path: no branch in .gitmodules, skipped"; continue; fi
  if ! git -C "$path" rev-parse --git-dir >/dev/null 2>&1; then
    echo "$path: not initialised (git submodule update --init), skipped"; continue
  fi
  current=$(git -C "$path" branch --show-current)
  if [ -n "$current" ] && [ "$current" != "$branch" ]; then
    echo "$path: on $current, not $branch; left alone"; continue
  fi
  if [ -n "$(git -C "$path" status --porcelain --untracked-files=no)" ]; then
    echo "$path: uncommitted changes; left alone"; continue
  fi
  if [ -n "$dry" ]; then echo "$path: would switch to $branch and fast-forward to origin/$branch"; continue; fi
  git -C "$path" fetch -q origin "$branch"
  if git -C "$path" show-ref -q --verify "refs/heads/$branch"; then
    git -C "$path" switch -q "$branch"
  else
    git -C "$path" switch -q -c "$branch" --track "origin/$branch"
  fi
  git -C "$path" merge -q --ff-only "origin/$branch" || { echo "$path: $branch has diverged from origin; not moved"; status=1; continue; }
  echo "$path: $branch at $(git -C "$path" rev-parse --short HEAD)"
done < <(git config -f .gitmodules --get-regexp '^submodule\..*\.path$')
exit "$status"
