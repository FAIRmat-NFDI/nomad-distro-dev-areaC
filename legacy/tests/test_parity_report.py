import json
from pathlib import Path

import pytest
from nomad.datamodel import EntryArchive
from nomad_simulations.schema_packages.general import Program, Simulation
from nomad_simulations.schema_packages.model_system import ModelSystem
from parity_collect import walk_legacy, walk_new
from parity_report import (
    build_report,
    classify,
    is_code_specific,
    lookup,
    main,
    parse_mapping_table,
    render_report,
)

MAPPING_TABLE = """
| runschema path | Status | nomad-simulations target | Notes |
| --- | --- | --- | --- |
| `run.program.name` | Mapped | `Simulation.program.name` | |
| `system.atoms.labels` | Mapped | `ModelSystem.particle_states[].chemical_symbol` \
(`AtomsState.chemical_symbol`) | |
| `system.atoms.lattice_vectors` | Mapped | `ModelSystem.lattice_vectors` | |
| `calculation.stress.total.value` | Unmapped | — | no stress |
| `calculation.energy.total` | Partial | `Outputs.total_energies[]` | per-step list |
"""


@pytest.fixture
def rows():
    return parse_mapping_table(MAPPING_TABLE)


def test_parse_mapping_table(rows):
    n_rows = sum(line.startswith('| `') for line in MAPPING_TABLE.splitlines())
    assert len(rows) == n_rows
    assert rows['system.atoms.labels'] == (
        'Mapped',
        'ModelSystem.particle_states.chemical_symbol',
    )
    assert rows['calculation.stress.total.value'] == ('Unmapped', None)
    assert rows['calculation.energy.total'] == ('Partial', 'Outputs.total_energies')


@pytest.mark.parametrize(
    'path, expected',
    [
        ('system.atoms.labels', 'system.atoms.labels'),
        # `Run`-level rows carry the `run.` prefix, the collected paths do not
        ('program.name', 'run.program.name'),
        # unlisted leaves fall back to their closest listed ancestor
        ('calculation.energy.total.value', 'calculation.energy.total'),
        ('calculation.forces.total.value', None),
    ],
)
def test_lookup(rows, path, expected):
    match = lookup(path, rows)
    assert (match[0] if match else None) == expected


@pytest.mark.parametrize(
    'path, expected',
    [
        ('x_fhi_aims_number_of_tasks', True),
        ('method.x_abinit_section.value', True),
        ('calculation.system_ref', True),
        ('calculation.forces.free.value_raw', True),
        ('calculation.energy.total.value', False),
        ('system.atoms.x', False),
    ],
)
def test_is_code_specific(path, expected):
    assert is_code_specific(path) is expected


@pytest.mark.parametrize(
    'legacy_path, new_paths, category, item',
    [
        (
            'system.atoms.labels',
            ['ModelSystem.particle_states.chemical_symbol'],
            'parity',
            'system.atoms.labels',
        ),
        # a filled sub-path of the target also counts
        (
            'calculation.energy.total.value',
            ['Outputs.total_energies.value'],
            'parity',
            'calculation.energy.total',
        ),
        (
            'system.atoms.lattice_vectors',
            ['ModelSystem.positions'],
            'parser gap',
            'system.atoms.lattice_vectors → ModelSystem.lattice_vectors',
        ),
        (
            'calculation.stress.total.value',
            [],
            'schema gap',
            'calculation.stress.total.value',
        ),
        (
            'calculation.forces.total.value',
            [],
            'unknown',
            'calculation.forces.total.value',
        ),
        ('x_vasp_incar', [], 'code-specific', 'x_vasp_incar'),
    ],
)
def test_classify(rows, legacy_path, new_paths, category, item):
    categories = classify([legacy_path], new_paths, rows)
    assert dict(categories) == {category: {item}}


def test_classify_only_leaves(rows):
    """Sections are covered by their filled quantities, not counted themselves."""
    legacy = ['system', 'system.atoms', 'system.atoms.labels']
    categories = classify(legacy, ['ModelSystem.particle_states.chemical_symbol'], rows)
    assert dict(categories) == {'parity': {'system.atoms.labels'}}


def test_walk_new_class_qualified_paths():
    archive = EntryArchive(
        data=Simulation(
            program=Program(name='VASP'),
            model_system=[ModelSystem(is_representative=True)],
        )
    )
    paths: set[str] = set()
    walk_new(archive.data, [], paths)
    assert 'Simulation.program.name' in paths
    assert 'Program.name' in paths
    assert 'ModelSystem.is_representative' in paths
    assert 'Simulation.model_system.is_representative' in paths


def test_walk_legacy_relative_paths():
    """`walk_legacy` is schema-agnostic, so a `Simulation` stands in for `Run`."""
    simulation = Simulation(
        program=Program(name='VASP'), model_system=[ModelSystem(is_representative=True)]
    )
    paths: set[str] = set()
    walk_legacy(simulation, '', paths)
    assert {'program', 'program.name', 'model_system.is_representative'} <= paths
    assert not any(p.startswith('Simulation') for p in paths)


def test_build_report_skips_failed_and_unmatched_files(rows):
    legacy = [
        dict(code='a', file='a/1', paths=['system.atoms.labels'], error=None),
        dict(code='a', file='a/2', paths=[], error='ValueError: broken'),
        dict(code='b', file='b/1', paths=['x_b'], error=None),
    ]
    new = [
        dict(code='a', file='a/1', paths=[], error=None),
        dict(code='a', file='a/2', paths=[], error=None),
    ]
    per_code, files = build_report(legacy, new, rows)
    assert files == {
        'a': [('a/1', None), ('a/2', 'legacy: ValueError: broken')],
    }
    assert per_code['a']['parser gap'] == {
        'system.atoms.labels → ModelSystem.particle_states.chemical_symbol'
    }
    report = render_report(per_code, files)
    assert '| a | 1/2 | 0 | 1 | 0 | 0 | 0 |' in report
    assert '- skipped `a/2`: legacy: ValueError: broken' in report


def test_main(tmp_path: Path):
    mapping = tmp_path / 'mapping.md'
    mapping.write_text(MAPPING_TABLE, encoding='utf-8')
    entry = dict(code='a', file='a/1', error=None)
    legacy = tmp_path / 'legacy.json'
    legacy.write_text(json.dumps([{**entry, 'paths': ['program.name']}]))
    new = tmp_path / 'new.json'
    new.write_text(json.dumps([{**entry, 'paths': ['Simulation.program.name']}]))
    output = tmp_path / 'report.md'

    arguments = ['--mapping', str(mapping), '--legacy', str(legacy)]
    arguments += ['--new', str(new), '--output', str(output)]
    assert main(arguments) == 0
    assert '| a | 1/1 | 1 | 0 | 0 | 0 | 0 |' in output.read_text(encoding='utf-8')
