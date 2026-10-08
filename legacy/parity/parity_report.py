"""Compare legacy and new parser coverage through the runschema mapping table.

Both inputs come from `parity_collect.py` run on the same test files: the legacy
parsers fill runschema paths, the new parsers fill nomad-simulations paths.
`legacy/runschema_mapping.md` translates each runschema leaf filled by the legacy
parser into its nomad-simulations target, which is then looked up in the paths filled
by the new parser.

    uv run python legacy/parity/parity_report.py --legacy legacy.json --new new.json
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

CATEGORIES = ('parity', 'parser gap', 'schema gap', 'unknown', 'code-specific')
DETAILED_CATEGORIES = ('parser gap', 'schema gap', 'unknown')


def _strip(path: str) -> str:
    return path.replace('[]', '').strip()


def parse_mapping_table(text: str) -> dict[str, tuple[str, str | None]]:
    """Return `{runschema path: (status, target)}` from the mapping table Markdown.

    The target is the first code span of the target cell, so qualifiers such as
    `` `ModelSystem.lattice_vectors` (`Representation.lattice_vectors`) `` reduce to
    the first path.
    """
    rows: dict[str, tuple[str, str | None]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith('| `'):
            continue
        cells = [cell.strip() for cell in line.strip('|').split(' | ')]
        targets = re.findall(r'`([^`]+)`', cells[2])
        rows[_strip(cells[0].strip('`'))] = (
            cells[1],
            _strip(targets[0]) if targets else None,
        )
    return rows


def lookup(
    path: str, rows: dict[str, tuple[str, str | None]]
) -> tuple[str, tuple[str, str | None]] | None:
    """Find the row of `path`, falling back to its closest listed ancestor.

    The table lists `Run`-level paths as `run.…` and all other sections without the
    prefix (`system.…`), so both spellings are tried.
    """
    for candidate in (path, f'run.{path}'):
        parts = candidate.split('.')
        for n in range(len(parts), 0, -1):
            key = '.'.join(parts[:n])
            if key in rows:
                return key, rows[key]
    return None


def is_code_specific(path: str) -> bool:
    """Code-specific `x_` quantities and archive references are outside the table."""
    return any(part.startswith('x_') for part in path.split('.')) or path.endswith(
        ('_ref', '_raw')
    )


def classify(
    legacy_paths: list[str],
    new_paths: list[str],
    rows: dict[str, tuple[str, str | None]],
) -> dict[str, set[str]]:
    """Sort the runschema leaves filled by the legacy parser into `CATEGORIES`."""
    categories: dict[str, set[str]] = defaultdict(set)
    filled = set(new_paths)
    legacy = set(legacy_paths)
    leaves = {p for p in legacy if not any(q.startswith(f'{p}.') for q in legacy)}
    for path in leaves:
        if is_code_specific(path):
            categories['code-specific'].add(path)
            continue
        match = lookup(path, rows)
        if match is None:
            categories['unknown'].add(path)
            continue
        key, (status, target) = match
        if status == 'Unmapped' or not target:
            categories['schema gap'].add(key)
        elif target in filled or any(p.startswith(f'{target}.') for p in filled):
            categories['parity'].add(key)
        else:
            categories['parser gap'].add(f'{key} → {target}')
    return categories


def build_report(
    legacy: list[dict[str, Any]],
    new: list[dict[str, Any]],
    rows: dict[str, tuple[str, str | None]],
) -> tuple[dict[str, dict[str, set[str]]], dict[str, list[tuple[str, str | None]]]]:
    """Classify per code, over the files both parser generations matched.

    Returns the categories per code and, per code, each file with the reason it was
    skipped (`None` when it was compared).
    """
    by_file = {(e['code'], e['file']): e for e in new}
    per_code: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    files: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
    for entry in legacy:
        counterpart = by_file.get((entry['code'], entry['file']))
        if counterpart is None:
            continue
        error = entry['error'] or counterpart['error']
        if error:
            side = 'legacy' if entry['error'] else 'new'
            files[entry['code']].append((entry['file'], f'{side}: {error}'))
            continue
        files[entry['code']].append((entry['file'], None))
        for category, items in classify(
            entry['paths'], counterpart['paths'], rows
        ).items():
            per_code[entry['code']][category] |= items
    return per_code, files


def render_report(
    per_code: dict[str, dict[str, set[str]]],
    files: dict[str, list[tuple[str, str | None]]],
) -> str:
    lines = [
        '# Legacy vs. new parser parity report',
        '',
        'Each runschema leaf filled by a legacy parser is translated with the '
        'runschema mapping table (`legacy/runschema_mapping.md`) and looked up in the '
        'archive of the new parser for the same file. Counts are distinct table rows '
        'over all compared files.',
        '',
        '- **parity**: the new parser fills the mapped target.',
        '- **parser gap**: the target exists, but the new parser leaves it empty.',
        '- **schema gap**: the table marks the path as Unmapped.',
        '- **unknown**: the path is missing from the table.',
        '- **code-specific**: `x_` quantities and references, outside the table scope.',
        '',
        '| Code | Files compared | '
        + ' | '.join(c.capitalize() for c in CATEGORIES)
        + ' |',
        '| --- ' * (len(CATEGORIES) + 2) + '|',
    ]
    for code in sorted(files):
        compared = sum(error is None for _, error in files[code])
        counts = ' | '.join(str(len(per_code[code][c])) for c in CATEGORIES)
        lines.append(f'| {code} | {compared}/{len(files[code])} | {counts} |')
    for code in sorted(files):
        lines += ['', f'## {code}']
        skipped = [(f, error) for f, error in files[code] if error]
        if skipped:
            lines.append('')
            lines += [f'- skipped `{f}`: {error}' for f, error in skipped]
        for category in DETAILED_CATEGORIES:
            items = sorted(per_code[code][category])
            if items:
                lines += ['', f'**{category.capitalize()}** ({len(items)})', '']
                lines += [f'- `{item}`' for item in items]
    return '\n'.join(lines) + '\n'


MAPPING_TABLE = Path(__file__).parents[1] / 'runschema_mapping.md'
REPORT = Path(__file__).parents[1] / 'parity_report.md'


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Compare legacy and new parser coverage via the runschema mapping.',
    )
    parser.add_argument(
        '--mapping',
        default=str(MAPPING_TABLE),
        help='Mapping table (default: %(default)s).',
    )
    parser.add_argument(
        '--legacy',
        required=True,
        help='parity_collect.py output of the legacy parsers.',
    )
    parser.add_argument(
        '--new', required=True, help='parity_collect.py output of the new parsers.'
    )
    parser.add_argument(
        '--output', default=str(REPORT), help='Output Markdown (default: %(default)s).'
    )
    args = parser.parse_args(arguments)
    rows = parse_mapping_table(Path(args.mapping).read_text(encoding='utf-8'))
    legacy = json.loads(Path(args.legacy).read_text(encoding='utf-8'))
    new = json.loads(Path(args.new).read_text(encoding='utf-8'))
    per_code, files = build_report(legacy, new, rows)
    Path(args.output).write_text(render_report(per_code, files), encoding='utf-8')
    print(f'Updated: {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
