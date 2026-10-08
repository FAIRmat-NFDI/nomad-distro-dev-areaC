# Legacy vs. new parser parity report

Each runschema leaf filled by a legacy parser is translated with the runschema mapping table (`legacy/runschema_mapping.md`) and looked up in the archive of the new parser for the same file. Counts are distinct table rows over all compared files.

- **parity**: the new parser fills the mapped target.
- **parser gap**: the target exists, but the new parser leaves it empty.
- **schema gap**: the table marks the path as Unmapped.
- **unknown**: the path is missing from the table.
- **code-specific**: `x_` quantities and references, outside the table scope.

| Code | Files compared | Parity | Parser gap | Schema gap | Unknown | Code-specific |
| --- | --- | --- | --- | --- | --- | --- |
| abinit | 2/2 | 17 | 17 | 4 | 2 | 57 |
| ams | 1/1 | 11 | 11 | 11 | 8 | 46 |
| crystal | 1/1 | 13 | 11 | 1 | 1 | 48 |
| exciting | 12/12 | 22 | 38 | 9 | 9 | 93 |
| fhiaims | 1/1 | 28 | 20 | 8 | 11 | 46 |
| gpaw | 1/1 | 13 | 13 | 4 | 1 | 13 |
| gromacs | 8/8 | 26 | 36 | 7 | 6 | 17 |
| h5md | 0/1 | 0 | 0 | 0 | 0 | 0 |
| lammps | 10/11 | 13 | 34 | 7 | 3 | 52 |
| lobster | 7/7 | 28 | 24 | 13 | 4 | 65 |
| octopus | 1/1 | 8 | 25 | 5 | 0 | 25 |
| phonopy | 1/1 | 0 | 12 | 0 | 5 | 7 |
| quantumespresso | 12/12 | 16 | 34 | 11 | 1 | 245 |
| vasp | 1/2 | 24 | 18 | 10 | 4 | 4 |
| wannier90 | 1/1 | 19 | 15 | 7 | 0 | 2 |

## abinit

**Parser gap** (17)

- `calculation.dos_electronic.spin_channel → Outputs.electronic_dos.spin_channel`
- `calculation.energy.internal → InternalEnergy.value`
- `calculation.energy.kinetic_electronic.value → Outputs.kinetic_energies.value`
- `method.dft.xc_functional.name → XCFunctional.functional_key`
- `method.electronic.method → ModelMethod.name`
- `method.electronic.n_spin_channels → ModelMethodElectronic.is_spin_polarized`
- `method.electronic.smearing.kind → Smearing.name`
- `method.electrons_representation.basis_set.cutoff → PlaneWaveBasisSet.cutoff_energy`
- `method.electrons_representation.basis_set.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.k_mesh → KSpace.k_mesh`
- `method.scf.n_max_iteration → SelfConsistency.n_max_iterations`
- `method.scf.threshold_energy_change → SelfConsistency.threshold_change`
- `run.clean_end → Simulation.finished_without_errors`
- `run.program.compilation_host → Simulation.program.compilation_host`
- `system.atoms.n_atoms → ModelSystem.n_particles`

**Schema gap** (4)

- `calculation.energy.fermi`
- `calculation.stress.total.value`
- `method.electronic.smearing.width`
- `method.electrons_representation.basis_set.type`

**Unknown** (2)

- `calculation.calculation_converged`
- `calculation.energy.contributions.kind`

## ams

**Parser gap** (11)

- `method.atom_parameters.charge → AtomsState.charge`
- `method.atom_parameters.label → AtomsState.label`
- `method.atom_parameters.n_valence_electrons → Pseudopotential.n_valence_electrons`
- `method.electronic.n_spin_channels → ModelMethodElectronic.is_spin_polarized`
- `method.electronic.relativity_method → RelativityModel.level`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.k_mesh → KSpace.k_mesh`
- `run.time_run.date_start → Simulation.datetime`
- `system.atoms.lattice_vectors → ModelSystem.lattice_vectors`
- `system.atoms.periodic → ModelSystem.periodic_boundary_conditions`

**Schema gap** (11)

- `calculation.charges.analysis_method`
- `calculation.charges.orbital_projected.value`
- `calculation.charges.spin_projected.value`
- `calculation.charges.spins`
- `calculation.charges.total`
- `calculation.charges.value`
- `calculation.multipoles.dipole.total`
- `method.atom_parameters.charges`
- `method.atom_parameters.orbitals`
- `method.electronic.charge`
- `method.electrons_representation.basis_set.type`

**Unknown** (8)

- `calculation.charges.orbital_projected.atom_index`
- `calculation.charges.orbital_projected.atom_label`
- `calculation.charges.orbital_projected.orbital`
- `calculation.charges.orbital_projected.spin`
- `calculation.charges.spin_projected.atom_index`
- `calculation.charges.spin_projected.spin`
- `calculation.energy.electronic.kinetic`
- `calculation.forces`

## crystal

**Parser gap** (11)

- `method.dft.xc_functional.correlation.weight → XCFunctional.components.weight`
- `method.dft.xc_functional.exchange.weight → XCFunctional.components.weight`
- `method.dft.xc_functional.name → XCFunctional.functional_key`
- `method.electronic.method → ModelMethod.name`
- `method.electrons_representation.basis_set.atom_centered.atom_number → BasisSetComponent.species_scope`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.scf.n_max_iteration → SelfConsistency.n_max_iterations`
- `method.scf.threshold_energy_change → SelfConsistency.threshold_change`
- `run.time_run.date_end → Simulation.datetime_end`
- `run.time_run.date_start → Simulation.datetime`

**Schema gap** (1)

- `method.electrons_representation.basis_set.type`

**Unknown** (1)

- `calculation.calculation_converged`

## exciting

**Parser gap** (38)

- `calculation.band_structure_electronic.segment.endpoints_labels → KLinePath`
- `calculation.band_structure_electronic.segment.kpoints → Outputs.electronic_band_structures.k_path`
- `calculation.band_structure_electronic.segment.n_kpoints → KLinePath`
- `calculation.dos_electronic.atom_projected → Outputs.electronic_dos.projected_dos.value`
- `calculation.dos_electronic.spin_channel → Outputs.electronic_dos.spin_channel`
- `calculation.energy.correlation.value → Outputs.total_energies.contributions.value`
- `calculation.energy.coulomb.value → Outputs.total_energies.contributions.value`
- `calculation.energy.electrostatic.value → Outputs.total_energies.contributions.value`
- `calculation.energy.exchange.value → Outputs.total_energies.contributions.value`
- `calculation.energy.kinetic_electronic.value → Outputs.kinetic_energies.value`
- `calculation.energy.sum_eigenvalues.value → Outputs.total_energies.contributions.value`
- `calculation.energy.xc_potential.value → Outputs.total_energies.contributions.value`
- `calculation.scf_iteration.energy.total.value → Outputs.scf_steps.energies_total`
- `calculation.time_calculation → Outputs.wall_end`
- `calculation.time_physical → Outputs.wall_end`
- `method.atom_parameters.label → AtomsState.label`
- `method.atom_parameters.mass → ParticleState.mass`
- `method.dft.xc_functional.name → XCFunctional.functional_key`
- `method.electronic.method → ModelMethod.name`
- `method.electronic.n_spin_channels → ModelMethodElectronic.is_spin_polarized`
- `method.electronic.smearing.kind → Smearing.name`
- `method.electrons_representation.basis_set.atom_parameters → BasisSetComponent.species_scope`
- `method.electrons_representation.basis_set.cutoff_fractional → APWPlaneWaveBasisSet.cutoff_fractional`
- `method.electrons_representation.basis_set.orbital.energy_parameter → APWBaseOrbital.energy_parameter`
- `method.electrons_representation.basis_set.orbital.l_quantum_number → APWLChannel.name`
- `method.electrons_representation.basis_set.orbital.order → APWBaseOrbital.differential_order`
- `method.electrons_representation.basis_set.orbital.type → APWOrbital.type`
- `method.electrons_representation.basis_set.orbital.update → APWBaseOrbital.energy_status`
- `method.electrons_representation.basis_set.radius → MuffinTinRegion.radius`
- `method.electrons_representation.basis_set.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.k_mesh.dimensionality → KMesh.dimensionality`
- `method.k_mesh.grid → KMesh.grid`
- `method.k_mesh.n_points → KMesh.n_points`
- `method.k_mesh.offset → KMesh.offset`
- `method.scf.threshold_energy_change → SelfConsistency.threshold_change`
- `run.program.version_internal → Simulation.program.version_internal`

**Schema gap** (9)

- `calculation.charges.total`
- `calculation.charges.value`
- `calculation.energy.fermi`
- `calculation.scf_iteration.energy.fermi`
- `calculation.scf_iteration.time_physical`
- `method.electronic.smearing.width`
- `method.electrons_representation.basis_set.radius_lin_spacing`
- `method.electrons_representation.basis_set.type`
- `system.atoms.lattice_vectors_reciprocal`

**Unknown** (9)

- `calculation.scf_iteration.charges.total`
- `calculation.scf_iteration.charges.value`
- `calculation.scf_iteration.energy.correlation.value`
- `calculation.scf_iteration.energy.coulomb.value`
- `calculation.scf_iteration.energy.electrostatic.value`
- `calculation.scf_iteration.energy.exchange.value`
- `calculation.scf_iteration.energy.kinetic_electronic.value`
- `calculation.scf_iteration.energy.sum_eigenvalues.value`
- `calculation.scf_iteration.energy.xc_potential.value`

## fhiaims

**Parser gap** (20)

- `calculation.forces.free.value → Outputs.total_forces.contributions.value`
- `calculation.n_scf_iterations → Outputs.scf_steps.energies_total`
- `calculation.scf_iteration.energy.total.value → Outputs.scf_steps.energies_total`
- `calculation.time_calculation → Outputs.wall_end`
- `calculation.time_physical → Outputs.wall_end`
- `method.atom_parameters.charge → AtomsState.charge`
- `method.atom_parameters.label → AtomsState.label`
- `method.atom_parameters.mass → ParticleState.mass`
- `method.electronic.method → ModelMethod.name`
- `method.electronic.n_spin_channels → ModelMethodElectronic.is_spin_polarized`
- `method.electronic.smearing.kind → Smearing.name`
- `method.electrons_representation.basis_set.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.native_tier → BasisSetContainer.native_tier`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.k_mesh.dimensionality → KMesh.dimensionality`
- `method.k_mesh.n_points → KMesh.n_points`
- `run.program.compilation_host → Simulation.program.compilation_host`
- `run.time_run.cpu1_start → Simulation.cpu1_start`
- `run.time_run.wall_start → Simulation.wall_start`

**Schema gap** (8)

- `calculation.energy.fermi`
- `calculation.scf_iteration.energy.fermi`
- `calculation.scf_iteration.stress.total.value`
- `calculation.scf_iteration.thermodynamics`
- `calculation.scf_iteration.time_physical`
- `method.electronic.smearing.width`
- `method.electrons_representation.basis_set.type`
- `system.atoms.lattice_vectors_reciprocal`

**Unknown** (11)

- `calculation.calculation_converged`
- `calculation.scf_iteration.eigenvalues.energies`
- `calculation.scf_iteration.eigenvalues.kpoints`
- `calculation.scf_iteration.eigenvalues.occupations`
- `calculation.scf_iteration.energy.correction_entropy.value`
- `calculation.scf_iteration.energy.correction_hartree.value`
- `calculation.scf_iteration.energy.correction_xc.value`
- `calculation.scf_iteration.energy.free.value`
- `calculation.scf_iteration.energy.sum_eigenvalues.value`
- `calculation.scf_iteration.energy.total_t0.value`
- `calculation.scf_iteration.energy.xc_potential.value`

## gpaw

**Parser gap** (13)

- `method.electronic.method → ModelMethod.name`
- `method.electronic.relativity_method → RelativityModel.level`
- `method.electronic.smearing.kind → Smearing.name`
- `method.electrons_representation.basis_set.cutoff → PlaneWaveBasisSet.cutoff_energy`
- `method.electrons_representation.basis_set.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.k_mesh.grid → KMesh.grid`
- `method.k_mesh.n_points → KMesh.n_points`
- `method.k_mesh.points → KMesh.points`
- `method.k_mesh.sampling_method → KMesh.center`
- `method.scf.threshold_energy_change → SelfConsistency.threshold_change`
- `run.program.name → Simulation.program.name`

**Schema gap** (4)

- `calculation.energy.fermi`
- `method.electronic.charge`
- `method.electronic.smearing.width`
- `method.electrons_representation.basis_set.type`

**Unknown** (1)

- `calculation.calculation_converged`

## gromacs

**Parser gap** (36)

- `calculation.density → MassDensity.value`
- `calculation.energy.kinetic.value → Outputs.kinetic_energies.value`
- `calculation.energy.potential.value → Outputs.potential_energies.value`
- `calculation.energy.pressure_volume_work.value → Work.value`
- `calculation.enthalpy → Enthalpy.value`
- `calculation.forces.total.value → Outputs.total_forces.value`
- `calculation.pressure → Pressure.value`
- `calculation.virial_tensor → VirialTensor.value`
- `calculation.volume → Volume.value`
- `method.atom_parameters.charge → AtomsState.charge`
- `method.atom_parameters.label → AtomsState.label`
- `method.atom_parameters.mass → ParticleState.mass`
- `method.force_field.model → ForceField.contributions`
- `method.force_field.model.contributions.atom_indices → Potential.particle_indices`
- `method.force_field.model.contributions.atom_labels → Potential.particle_labels`
- `method.force_field.model.contributions.n_atoms → Potential.n_particles`
- `method.force_field.model.contributions.n_interactions → Potential.n_interactions`
- `method.force_field.model.contributions.parameters → Potential.parameters`
- `method.force_field.model.contributions.type → Potential.type`
- `run.program.version → Simulation.program.version`
- `run.time_run.date_end → Simulation.datetime_end`
- `run.time_run.date_start → Simulation.datetime`
- `system.atoms.bond_list → ModelSystem.bond_list`
- `system.atoms.labels → ModelSystem.particle_states.chemical_symbol`
- `system.atoms.lattice_vectors → ModelSystem.lattice_vectors`
- `system.atoms.n_atoms → ModelSystem.n_particles`
- `system.atoms.periodic → ModelSystem.periodic_boundary_conditions`
- `system.atoms.positions → ModelSystem.positions`
- `system.atoms.velocities → ModelSystem.velocities`
- `system.atoms_group.atom_indices → ModelSystem.sub_systems.particle_indices`
- `system.atoms_group.atoms_group → ModelSystem.sub_systems.sub_systems`
- `system.atoms_group.composition_formula → ModelSystem.sub_systems.composition_formula`
- `system.atoms_group.index → ModelSystem.sub_systems.branch_depth`
- `system.atoms_group.label → ModelSystem.sub_systems.branch_label`
- `system.atoms_group.n_atoms → ModelSystem.sub_systems.n_particles`
- `system.atoms_group.type → ModelSystem.sub_systems.type`

**Schema gap** (7)

- `calculation.pressure_tensor`
- `method.force_field.force_calculations.coulomb_cutoff`
- `method.force_field.force_calculations.coulomb_type`
- `method.force_field.force_calculations.neighbor_searching.neighbor_update_cutoff`
- `method.force_field.force_calculations.neighbor_searching.neighbor_update_frequency`
- `method.force_field.force_calculations.vdw_cutoff`
- `system.atoms_group.is_molecule`

**Unknown** (6)

- `calculation.energy.electrostatic.long_range`
- `calculation.energy.electrostatic.short_range`
- `calculation.energy.van_der_waals.correction`
- `calculation.energy.van_der_waals.long_range`
- `calculation.energy.van_der_waals.short_range`
- `calculation.forces.total`

## h5md

- skipped `h5md/test_traj_openmm_reduced-SOL_5frames_07-10-25.h5`: legacy: ValueError: Cannot set [[4. 4. 4.]
 [4. 4. 4.]
 [4. 4. 4.]
 ...
 [4. 4. 4.]
 [4. 4. 4.]
 [4. 4. 4.]] for the scalar quantity atomisticparsers.h5md.metainfo.h5md.CalcEntry.value:Quantity.

## lammps

- skipped `lammps/2_xyz_files/log.lammps`: new: TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'

**Parser gap** (34)

- `calculation.energy.contributions.value → Outputs.total_energies.contributions.value`
- `calculation.energy.current.value → Outputs.total_energies.value`
- `calculation.energy.total.value → Outputs.total_energies.value`
- `calculation.forces.total.value → Outputs.total_forces.value`
- `calculation.pressure → Pressure.value`
- `calculation.radius_of_gyration.radius_of_gyration_values.value → Outputs.radii_of_gyration.value`
- `calculation.step → WorkflowOutputs.step`
- `calculation.temperature → Outputs.temperatures.value`
- `calculation.time → TrajectoryOutputs.time`
- `calculation.time_calculation → Outputs.wall_end`
- `calculation.time_physical → Outputs.wall_end`
- `method.atom_parameters.charge → AtomsState.charge`
- `method.atom_parameters.mass → ParticleState.mass`
- `method.force_field.force_calculations.neighbor_searching → ForceCalculations`
- `method.force_field.model → ForceField.contributions`
- `method.force_field.model.contributions.atom_indices → Potential.particle_indices`
- `method.force_field.model.contributions.atom_labels → Potential.particle_labels`
- `method.force_field.model.contributions.n_atoms → Potential.n_particles`
- `method.force_field.model.contributions.n_interactions → Potential.n_interactions`
- `method.force_field.model.contributions.type → Potential.type`
- `run.program.version → Simulation.program.version`
- `system.atoms.bond_list → ModelSystem.bond_list`
- `system.atoms.labels → ModelSystem.particle_states.chemical_symbol`
- `system.atoms.lattice_vectors → ModelSystem.lattice_vectors`
- `system.atoms.n_atoms → ModelSystem.n_particles`
- `system.atoms.periodic → ModelSystem.periodic_boundary_conditions`
- `system.atoms.positions → ModelSystem.positions`
- `system.atoms_group.atom_indices → ModelSystem.sub_systems.particle_indices`
- `system.atoms_group.atoms_group → ModelSystem.sub_systems.sub_systems`
- `system.atoms_group.composition_formula → ModelSystem.sub_systems.composition_formula`
- `system.atoms_group.index → ModelSystem.sub_systems.branch_depth`
- `system.atoms_group.label → ModelSystem.sub_systems.branch_label`
- `system.atoms_group.n_atoms → ModelSystem.sub_systems.n_particles`
- `system.atoms_group.type → ModelSystem.sub_systems.type`

**Schema gap** (7)

- `calculation.radius_of_gyration.kind`
- `method.force_field.force_calculations.coulomb_cutoff`
- `method.force_field.force_calculations.coulomb_type`
- `method.force_field.force_calculations.neighbor_searching.neighbor_update_cutoff`
- `method.force_field.force_calculations.neighbor_searching.neighbor_update_frequency`
- `method.force_field.force_calculations.vdw_cutoff`
- `system.atoms_group.is_molecule`

**Unknown** (3)

- `calculation.energy.contributions.kind`
- `calculation.forces.total`
- `calculation.radius_of_gyration.radius_of_gyration_values.label`

## lobster

**Parser gap** (24)

- `calculation.dos_electronic.atom_projected → Outputs.electronic_dos.projected_dos.value`
- `calculation.dos_electronic.energies → Outputs.electronic_dos.energies.points`
- `calculation.dos_electronic.energy_fermi → Outputs.electronic_dos.energies_origin`
- `calculation.dos_electronic.n_energies → Outputs.electronic_dos.energies.n_points`
- `calculation.dos_electronic.spin_channel → Outputs.electronic_dos.spin_channel`
- `calculation.dos_electronic.total → Outputs.electronic_dos.value`
- `calculation.time_calculation → Outputs.wall_end`
- `calculation.time_physical → Outputs.wall_end`
- `method.atom_parameters.label → AtomsState.label`
- `method.electronic.method → ModelMethod.name`
- `method.electronic.n_spin_channels → ModelMethodElectronic.is_spin_polarized`
- `method.electrons_representation.basis_set.cutoff → PlaneWaveBasisSet.cutoff_energy`
- `method.electrons_representation.basis_set.frozen_core → FrozenCore`
- `method.electrons_representation.basis_set.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.native_tier → BasisSetContainer.native_tier`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.k_mesh.dimensionality → KMesh.dimensionality`
- `method.k_mesh.n_points → KMesh.n_points`
- `method.k_mesh.points → KMesh.points`
- `method.k_mesh.sampling_method → KMesh.center`
- `method.scf.threshold_energy_change → SelfConsistency.threshold_change`
- `run.clean_end → Simulation.finished_without_errors`
- `run.time_run.date_start → Simulation.datetime`

**Schema gap** (13)

- `calculation.charges.analysis_method`
- `calculation.charges.kind`
- `calculation.charges.value`
- `calculation.eigenvalues.kpoints_multiplicities`
- `calculation.eigenvalues.kpoints_weights`
- `calculation.energy.fermi`
- `calculation.energy.highest_occupied`
- `calculation.energy.lowest_unoccupied`
- `calculation.scf_iteration.time_physical`
- `calculation.stress.total.value`
- `method.electronic.n_electrons`
- `method.electrons_representation.basis_set.type`
- `run.program.compilation_datetime`

**Unknown** (4)

- `calculation.scf_iteration.energy.correction_hartree.value`
- `calculation.scf_iteration.energy.free.value`
- `calculation.scf_iteration.energy.total_t0.value`
- `calculation.scf_iteration.energy.xc.value`

## octopus

**Parser gap** (25)

- `calculation.eigenvalues.energies → Outputs.electronic_eigenvalues.value`
- `calculation.eigenvalues.kpoints → Outputs.electronic_eigenvalues`
- `calculation.eigenvalues.occupations → Outputs.electronic_eigenvalues.occupation`
- `calculation.energy.correction_entropy.value → Outputs.total_energies.contributions.value`
- `calculation.energy.correlation.value → Outputs.total_energies.contributions.value`
- `calculation.energy.electrostatic.value → Outputs.total_energies.contributions.value`
- `calculation.energy.exchange.value → Outputs.total_energies.contributions.value`
- `calculation.energy.free.value → Outputs.total_energies.contributions.value`
- `calculation.energy.kinetic_electronic.value → Outputs.kinetic_energies.value`
- `calculation.energy.nuclear_repulsion.value → Outputs.total_energies.contributions.value`
- `calculation.energy.sum_eigenvalues.value → Outputs.total_energies.contributions.value`
- `calculation.energy.van_der_waals.value → Outputs.total_energies.contributions.value`
- `calculation.scf_iteration.energy.total.value → Outputs.scf_steps.energies_total`
- `calculation.scf_iteration.time_calculation → Outputs.scf_steps.durations`
- `calculation.time_calculation → Outputs.wall_end`
- `calculation.time_physical → Outputs.wall_end`
- `method.dft.xc_functional.name → XCFunctional.functional_key`
- `method.electronic.method → ModelMethod.name`
- `method.electronic.smearing.kind → Smearing.name`
- `method.electrons_representation.basis_set.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.k_mesh.dimensionality → KMesh.dimensionality`
- `method.k_mesh.grid → KMesh.grid`
- `method.k_mesh.n_points → KMesh.n_points`

**Schema gap** (5)

- `calculation.energy.fermi`
- `calculation.scf_iteration.energy.fermi`
- `calculation.scf_iteration.time_physical`
- `method.electronic.smearing.width`
- `method.electrons_representation.basis_set.type`

## phonopy

**Parser gap** (12)

- `calculation.hessian_matrix → Hessian.value`
- `calculation.thermodynamics.heat_capacity_c_v → HeatCapacity.value`
- `calculation.thermodynamics.temperature → Outputs.temperatures.value`
- `calculation.thermodynamics.vibrational_free_energy_at_constant_volume → HelmholtzFreeEnergy.value`
- `method.electronic.method → ModelMethod.name`
- `run.program.name → Simulation.program.name`
- `run.program.version → Simulation.program.version`
- `system.atoms.labels → ModelSystem.particle_states.chemical_symbol`
- `system.atoms.lattice_vectors → ModelSystem.lattice_vectors`
- `system.atoms.periodic → ModelSystem.periodic_boundary_conditions`
- `system.atoms.positions → ModelSystem.positions`
- `system.atoms.supercell_matrix → ModelSystem.representations.supercell_matrix`

**Unknown** (5)

- `calculation.band_structure_phonon.segment.endpoints_labels`
- `calculation.band_structure_phonon.segment.energies`
- `calculation.band_structure_phonon.segment.kpoints`
- `calculation.dos_phonon.energies`
- `calculation.dos_phonon.total.value`

## quantumespresso

**Parser gap** (34)

- `calculation.scf_iteration.time_calculation → Outputs.scf_steps.durations`
- `calculation.spectra.excitation_energies → Outputs.absorption_spectra.energies.points`
- `calculation.spectra.intensities → Outputs.absorption_spectra.value`
- `calculation.spectra.n_energies → Outputs.absorption_spectra.energies.n_points`
- `calculation.spectra.type → Outputs.absorption_spectra`
- `calculation.thermodynamics.pressure → Pressure.value`
- `calculation.time_calculation → Outputs.wall_end`
- `calculation.time_physical → Outputs.wall_end`
- `method.atom_parameters.label → AtomsState.label`
- `method.atom_parameters.n_valence_electrons → Pseudopotential.n_valence_electrons`
- `method.core_hole.broadening → ExcitedStateMethodology.broadening`
- `method.core_hole.mode → CoreHoleSpectra.type`
- `method.electronic.method → ModelMethod.name`
- `method.electronic.n_spin_channels → ModelMethodElectronic.is_spin_polarized`
- `method.electronic.smearing → Smearing`
- `method.electronic.smearing.kind → Smearing.name`
- `method.electrons_representation.basis_set.cutoff → PlaneWaveBasisSet.cutoff_energy`
- `method.electrons_representation.basis_set.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.k_mesh.dimensionality → KMesh.dimensionality`
- `method.k_mesh.n_points → KMesh.n_points`
- `method.k_mesh.points → KMesh.points`
- `method.k_mesh.weights → KMesh.weights`
- `method.photon.multipole_type → Photon.multipole_type`
- `method.photon.polarization → Photon.polarization`
- `method.scf.threshold_energy_change → SelfConsistency.threshold_change`
- `run.clean_end → Simulation.finished_without_errors`
- `run.time_run.date_end → Simulation.datetime_end`
- `run.time_run.date_start → Simulation.datetime`
- `system.atoms.labels → ModelSystem.particle_states.chemical_symbol`
- `system.atoms.lattice_vectors → ModelSystem.lattice_vectors`
- `system.atoms.periodic → ModelSystem.periodic_boundary_conditions`
- `system.atoms.positions → ModelSystem.positions`

**Schema gap** (11)

- `calculation.energy.fermi`
- `calculation.energy.highest_occupied`
- `calculation.energy.lowest_unoccupied`
- `calculation.scf_iteration.time_physical`
- `calculation.spectra.intensities_units`
- `calculation.stress.total.value`
- `calculation.vibrational_frequencies.value`
- `method.core_hole.solver`
- `method.electronic.n_electrons`
- `method.electronic.smearing.width`
- `method.electrons_representation.basis_set.type`

**Unknown** (1)

- `calculation.thermodynamics`

## vasp

- skipped `vasp/with_chgcar/OUTCAR`: legacy: ValueError: Cannot normalize HDF5 value without context.

**Parser gap** (18)

- `calculation.dos_electronic.energy_fermi → Outputs.electronic_dos.energies_origin`
- `calculation.dos_electronic.orbital_projected → Outputs.electronic_dos.projected_dos.value`
- `calculation.time_calculation → Outputs.wall_end`
- `calculation.time_physical → Outputs.wall_end`
- `method.atom_parameters.label → AtomsState.label`
- `method.electronic.method → ModelMethod.name`
- `method.electrons_representation.basis_set.cutoff → PlaneWaveBasisSet.cutoff_energy`
- `method.electrons_representation.basis_set.frozen_core → FrozenCore`
- `method.electrons_representation.basis_set.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.native_tier → BasisSetContainer.native_tier`
- `method.electrons_representation.scope → BasisSetComponent.hamiltonian_scope`
- `method.electrons_representation.type → BasisSetContainer`
- `method.k_mesh.dimensionality → KMesh.dimensionality`
- `method.k_mesh.n_points → KMesh.n_points`
- `method.k_mesh.points → KMesh.points`
- `method.k_mesh.sampling_method → KMesh.center`
- `method.scf.threshold_energy_change → SelfConsistency.threshold_change`
- `run.time_run.date_start → Simulation.datetime`

**Schema gap** (10)

- `calculation.eigenvalues.kpoints_multiplicities`
- `calculation.eigenvalues.kpoints_weights`
- `calculation.energy.fermi`
- `calculation.energy.highest_occupied`
- `calculation.energy.lowest_unoccupied`
- `calculation.scf_iteration.time_physical`
- `calculation.stress.total.value`
- `method.electronic.n_electrons`
- `method.electrons_representation.basis_set.type`
- `run.program.compilation_datetime`

**Unknown** (4)

- `calculation.scf_iteration.energy.correction_hartree.value`
- `calculation.scf_iteration.energy.free.value`
- `calculation.scf_iteration.energy.total_t0.value`
- `calculation.scf_iteration.energy.xc.value`

## wannier90

**Parser gap** (15)

- `calculation.band_structure_electronic.reciprocal_cell → Outputs.electronic_band_structures.reciprocal_cell`
- `calculation.band_structure_electronic.segment.kpoints → Outputs.electronic_band_structures.k_path`
- `calculation.band_structure_electronic.segment.occupations → Outputs.electronic_band_structures.occupation`
- `calculation.dos_electronic.energy_fermi → Outputs.electronic_dos.energies_origin`
- `calculation.hopping_matrix.degeneracy_factors → Outputs.hopping_matrices.degeneracy_factors`
- `calculation.hopping_matrix.n_orbitals → Outputs.hopping_matrices.n_orbitals`
- `calculation.hopping_matrix.n_wigner_seitz_points → Outputs.hopping_matrices`
- `calculation.hopping_matrix.value → Outputs.hopping_matrices.value`
- `method.k_mesh.dimensionality → KMesh.dimensionality`
- `method.tb.wannier.n_bands → Wannier.n_bloch_bands`
- `method.tb.wannier.n_projected_orbitals → Wannier.n_orbitals_per_atom`
- `run.program.name → Simulation.program.name`
- `system.atoms.labels → ModelSystem.particle_states.chemical_symbol`
- `system.atoms_group.n_atoms → ModelSystem.sub_systems.n_particles`
- `system.atoms_group.type → ModelSystem.sub_systems.type`

**Schema gap** (7)

- `calculation.energy.fermi`
- `calculation.energy.highest_occupied`
- `method.atom_parameters.n_orbitals`
- `method.atom_parameters.orbitals`
- `method.tb.wannier.convergence_tolerance_max_localization`
- `system.atoms.lattice_vectors_reciprocal`
- `system.atoms_group.is_molecule`
