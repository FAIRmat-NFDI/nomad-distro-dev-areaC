"""Collect the archive paths a parser generation fills on a set of test files.

`legacy` uses the parsers from `electronicparsers`, `atomisticparsers` and
`workflowparsers` and walks `archive.run`, emitting runschema paths relative to `Run`
(`system.atoms.labels`), as written in the source column of `runschema_mapping.md`.
`new` uses `nomad_simulation_parsers` and walks `archive.data`, emitting each filled
path relative to every enclosing section class and its bases
(`Outputs.total_energies.value`), as written in the target column.

Both generations are loaded side by side in `std/legacy`, so the parser is chosen
among those of the requested generation, in NOMAD's matching order.

    uv run python legacy/parity/parity_collect.py legacy <data> legacy.json --normalize
"""

import argparse
import json
import os
import signal
from pathlib import Path
from typing import Any

import magic
from nomad.client import normalize_all
from nomad.config import config
from nomad.datamodel import EntryArchive, EntryMetadata
from nomad.parsing.parsers import _compressions, parsers
from nomad.utils import get_logger

PACKAGES = {
    'legacy': ('electronicparsers', 'atomisticparsers', 'workflowparsers'),
    'new': ('nomad_simulation_parsers',),
}


class ParseTimeout(Exception):
    pass


def _raise_timeout(*_: Any) -> None:
    raise ParseTimeout()


def candidate_parsers(mode: str) -> list[Any]:
    """Registered parsers of one generation, in NOMAD's matching order.

    The order follows `match_parser`: permissive parsers (e.g. the legacy ABACUS
    parser) rely on a late `matching_order` and would otherwise claim unrelated files.
    Plugin parsers can come wrapped, so the origin is read from both the class module
    and the entry point id (`electronicparsers:abinit_parser_entry_point`).
    """
    ordered = (
        sorted(parsers, key=lambda parser: (parser.matching_order, parser.name))
        if any(parser.matching_order != 0 for parser in parsers)
        else parsers
    )
    return [
        parser
        for parser in ordered
        if any(
            package in f'{type(parser).__module__} {parser}'
            for package in PACKAGES[mode]
        )
    ]


def match(mainfile: str, candidates: list[Any]) -> Any:
    """The first candidate whose `is_mainfile` accepts the file.

    `match_parser(..., parser_name=...)` forces the named parser without testing it,
    so the check is done here on the same buffer `match_parser` reads.
    """
    with open(mainfile, 'rb') as f:
        compression, open_compressed = _compressions.get(f.read(3), (None, open))
    with open_compressed(mainfile, 'rb') as f:
        buffer = f.read(config.process.parser_matching_size)
    mime_type = magic.from_buffer(buffer, mime=True)
    try:
        decoded_buffer = buffer.decode('utf-8')
    except UnicodeDecodeError:
        decoded_buffer = None
    for candidate in candidates:
        try:
            if candidate.is_mainfile(
                mainfile, mime_type, buffer, decoded_buffer, compression
            ):
                return candidate
        except Exception:
            continue
    return None


def walk_legacy(section: Any, prefix: str, paths: set[str]) -> None:
    """Add the runschema paths of filled quantities and sub-sections below `section`."""
    for quantity in section.m_def.all_quantities.values():
        if section.m_is_set(quantity):
            paths.add(f'{prefix}.{quantity.name}' if prefix else quantity.name)
    for sub_section in section.m_def.all_sub_sections.values():
        children = section.m_get_sub_sections(sub_section)
        path = f'{prefix}.{sub_section.name}' if prefix else sub_section.name
        if children:
            paths.add(path)
        for child in children:
            walk_legacy(child, path, paths)


def walk_new(
    section: Any, ancestors: list[tuple[list[str], list[str]]], paths: set[str]
) -> None:
    """Add each filled path below `section`, relative to every enclosing class."""

    def emit(chain: list[tuple[list[str], list[str]]], leaf: str) -> None:
        for class_names, relative in chain:
            for class_name in class_names:
                paths.add('.'.join([class_name, *relative, leaf]))

    class_names = [base.name for base in section.m_def.all_base_sections]
    chain = [*ancestors, ([*class_names, section.m_def.name], [])]
    for quantity in section.m_def.all_quantities.values():
        if section.m_is_set(quantity):
            emit(chain, quantity.name)
    for sub_section in section.m_def.all_sub_sections.values():
        children = section.m_get_sub_sections(sub_section)
        if children:
            emit(chain, sub_section.name)
        nested = [(names, [*relative, sub_section.name]) for names, relative in chain]
        for child in children:
            walk_new(child, nested, paths)


def collect(
    mode: str,
    data_dir: str | Path,
    skip_codes: set[str],
    normalize: bool = False,
    timeout: int = 120,
) -> list[dict[str, Any]]:
    """Parse every file under `data_dir/<code>` matched by a parser of `mode`."""
    logger = get_logger(__name__)
    candidates = candidate_parsers(mode)
    signal.signal(signal.SIGALRM, _raise_timeout)
    results = []
    for code_dir in sorted(Path(data_dir).iterdir()):
        if not code_dir.is_dir() or code_dir.name in skip_codes:
            continue
        for root, dirs, files in os.walk(code_dir):
            # skip generated artefacts (`.nomad-visualizations/`, offset caches)
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for name in sorted(f for f in files if not f.startswith('.')):
                mainfile = os.path.join(root, name)
                parser = match(mainfile, candidates)
                if parser is None:
                    continue
                entry: dict[str, Any] = dict(
                    code=code_dir.name,
                    file=os.path.relpath(mainfile, data_dir),
                    parser=parser.name,
                    paths=[],
                    error=None,
                )
                # the legacy normalizers require entry metadata such as `upload_id`
                archive = EntryArchive(
                    metadata=EntryMetadata(
                        upload_id='parity', entry_id='parity', mainfile=entry['file']
                    )
                )
                signal.alarm(timeout)
                try:
                    parser.parse(mainfile, archive, logger)
                    if normalize:
                        normalize_all(archive, logger=logger)
                    paths: set[str] = set()
                    if mode == 'legacy':
                        for run in archive.run:
                            walk_legacy(run, '', paths)
                    elif archive.data is not None:
                        walk_new(archive.data, [], paths)
                    entry['paths'] = sorted(paths)
                except Exception as e:
                    entry['error'] = f'{type(e).__name__}: {e}'[:200]
                finally:
                    signal.alarm(0)
                results.append(entry)
    return results


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Collect the archive paths filled by the legacy or new parsers.'
    )
    parser.add_argument('mode', choices=sorted(PACKAGES))
    parser.add_argument('data_dir', help='Directory with one sub-directory per code.')
    parser.add_argument('output', help='Output JSON path.')
    parser.add_argument(
        '--normalize', action='store_true', help='Run the normalizers after parsing.'
    )
    parser.add_argument(
        '--skip',
        nargs='*',
        default=['orca'],
        help='Code directories to skip (default: %(default)s).',
    )
    args = parser.parse_args(arguments)
    results = collect(args.mode, args.data_dir, set(args.skip), args.normalize)
    Path(args.output).write_text(json.dumps(results, indent=1), encoding='utf-8')
    print(f'Collected {len(results)} files: {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
