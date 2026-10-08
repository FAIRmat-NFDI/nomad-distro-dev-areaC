#!/usr/bin/env bash
# Record the checked-out package commits as this branch's submodule pointers: list what moved, then commit it.
# Nothing is pushed. Packages with uncommitted changes are reported, since only their commits get recorded.
#
#   scripts/pin-packages.sh       list and commit
#   scripts/pin-packages.sh -n    only list
set -euo pipefail

dry=""
[ "${1:-}" = "-n" ] && dry=1
root=$(git rev-parse --show-toplevel)
cd "$root"
moved=()
summary=""
while read -r _key path; do
  # An empty folder (not initialised) would resolve to the distro repo itself, so compare toplevels.
  if [ "$(git -C "$path" rev-parse --show-toplevel 2>/dev/null)" != "$root/$path" ]; then continue; fi
  pinned=$(git rev-parse --short "HEAD:$path")
  head=$(git -C "$path" rev-parse --short HEAD)
  branch=$(git -C "$path" branch --show-current)
  dirty=""
  [ -n "$(git -C "$path" status --porcelain --untracked-files=no)" ] && dirty=" (uncommitted changes, not recorded)"
  if [ "$(git -C "$path" rev-parse HEAD)" = "$(git rev-parse "HEAD:$path")" ]; then
    echo "$path: ${branch:-detached} $head, unchanged$dirty"
  else
    line="$path: $pinned -> $head (${branch:-detached})"
    echo "$line$dirty"
    moved+=("$path")
    summary+="- $line"$'\n'
  fi
done < <(git config -f .gitmodules --get-regexp '^submodule\..*\.path$')

if [ ${#moved[@]} -eq 0 ]; then echo "Nothing to pin."; exit 0; fi
[ -n "$dry" ] && exit 0
git add -- "${moved[@]}"
git commit -q -m "Pin packages to their checked-out commits" -m "$summary" -- "${moved[@]}"
echo "Committed $(git rev-parse --short HEAD) on $(git branch --show-current); push when ready."
