"""Check that every row of `runschema_mapping.md` names paths that exist.

Source paths must resolve in `runschema`, starting at `Run` (`system.atoms.labels`,
`run.program.name`) or at a named section (`AtomParameters.core_hole.degeneracy`).
Targets of Mapped and Partial rows must resolve in `nomad_simulations`, starting at the
named section (`ModelSystem.particle_states.chemical_symbol`). A step may name a
quantity, a sub-section or a Python attribute such as a `@property`, may be found on a
subclass of the declared sub-section type (`particle_states` holds `AtomsState`), may
select that subclass explicitly (`contributions[HubbardInteractions]`) and may list
alternatives (`orbital_1/orbital_2`).

    uv run python legacy/parity/mapping_check.py
"""

import importlib
import pkgutil
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import nomad_simulations.schema_packages
import runschema
from nomad.config import config
from parity_report import MAPPING_TABLE, parse_mapping_table
from runschema.run import Run

STEP = re.compile(r'(\w+)(?:\[(\w+)\])?$')


def section_index(package: ModuleType) -> dict[str, Any]:
    """All section definitions in the modules of `package`, by name."""
    index: dict[str, Any] = {}
    for module_info in pkgutil.walk_packages(package.__path__, f'{package.__name__}.'):
        try:
            module = importlib.import_module(module_info.name)
        except Exception:
            continue
        for value in vars(module).values():
            definition = getattr(value, 'm_def', None)
            if type(definition).__name__ == 'Section':
                index.setdefault(definition.name, definition)
    return index


def _family(section: Any, index: dict[str, Any]) -> list[Any]:
    # compare by name: a sub-section declared by string resolves to an equal,
    # not identical, definition
    return [section] + [
        candidate
        for candidate in index.values()
        if section.name in {base.name for base in candidate.all_base_sections}
    ]


def resolve(section: Any, steps: list[str], index: dict[str, Any]) -> bool:
    """Whether `steps` lead from `section` to a quantity, sub-section or attribute."""
    if not steps:
        return True
    step, rest = steps[0], steps[1:]
    if '/' in step:
        return all(resolve(section, [alt, *rest], index) for alt in step.split('/'))
    match = STEP.match(step)
    if match is None:
        return False
    name, selector = match.groups()
    for candidate in _family(section, index):
        if name in candidate.all_sub_sections:
            target = (
                index.get(selector)
                if selector
                else candidate.all_sub_sections[name].sub_section
            )
            if target is not None and resolve(target, rest, index):
                return True
        elif name in candidate.all_quantities or hasattr(candidate.section_cls, name):
            if not rest:
                return True
    return False


def _normalize_target(target: str) -> str:
    target = re.sub(r'^[a-z_]+\.(?=[A-Z])', '', target)  # `atoms_state.CoreHole`
    # `settings[KSpace.k_mesh[KMesh]]` -> `settings[KSpace].k_mesh[KMesh]`
    return re.sub(r'\[(\w+)\.(\w+)\[(\w+)\]\]', r'[\1].\2[\3]', target)


def check_table(
    rows: dict[str, tuple[str, str | None]],
    run: Any,
    legacy_index: dict[str, Any],
    new_index: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Return the rows whose source, respectively target, does not resolve."""
    bad_sources, bad_targets = [], []
    for source, (status, target) in rows.items():
        steps = source.split('.')
        if steps[0] in legacy_index:
            found = resolve(legacy_index[steps[0]], steps[1:], legacy_index)
        else:
            found = resolve(
                run, steps[1:] if steps[0] == 'run' else steps, legacy_index
            )
        if not found:
            bad_sources.append(source)
        if target and status != 'Unmapped':
            steps = _normalize_target(target).split('.')
            root = new_index.get(steps[0])
            if root is None or not resolve(root, steps[1:], new_index):
                bad_targets.append(f'{source} -> {target}')
    return bad_sources, bad_targets


def check_installed(table: Path = MAPPING_TABLE) -> tuple[list[str], list[str]]:
    config.load_plugins()
    rows = parse_mapping_table(table.read_text(encoding='utf-8'))
    return check_table(
        rows,
        Run.m_def,
        section_index(runschema),
        section_index(nomad_simulations.schema_packages),
    )


if __name__ == '__main__':
    bad_sources, bad_targets = check_installed()
    for line in bad_sources:
        print(f'source not in runschema: {line}')
    for line in bad_targets:
        print(f'target not in nomad-simulations: {line}')
    sys.exit(1 if bad_sources or bad_targets else 0)
