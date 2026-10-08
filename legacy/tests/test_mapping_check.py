import nomad_simulations.schema_packages
import pytest
from mapping_check import check_installed, resolve, section_index


@pytest.fixture(scope='module')
def index():
    return section_index(nomad_simulations.schema_packages)


@pytest.mark.parametrize(
    'path, expected',
    [
        ('ModelSystem.lattice_vectors', True),
        # quantity on a subclass of the declared sub-section type (`ParticleState`)
        ('ModelSystem.particle_states.chemical_symbol', True),
        # sub-section declared by string (`'LocalSymmetry'`), quantity on a subclass
        ('ModelSystem.local_symmetry.wyckoff_letters', True),
        ('ModelMethod.contributions[HubbardInteractions].u_interaction', True),
        ('ModelMethod.contributions[NoSuchSection].u_interaction', False),
        ('SlaterKoster.bonds[SlaterKosterBond].orbital_1/orbital_2', True),
        ('SlaterKoster.bonds[SlaterKosterBond].orbital_1/no_such_orbital', False),
        ('Potential.contributions', False),
        ('ModelSystem.no_such_quantity', False),
    ],
)
def test_resolve(index, path, expected):
    root, *steps = path.split('.')
    assert resolve(index[root], steps, index) is expected


def test_committed_table_resolves():
    bad_sources, bad_targets = check_installed()
    assert bad_sources == []
    assert bad_targets == []
