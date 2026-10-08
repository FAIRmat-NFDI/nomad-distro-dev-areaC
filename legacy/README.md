# Legacy ↔ nomad-simulations bridge

This directory relates the legacy simulation stack (parsers writing `runschema` under `archive.run`) to the current one (parsers writing `nomad-simulations` under `archive.data`). It holds the schema mapping between the two and a report that uses it to compare what both parser generations extract from the same files. Everything here runs in the `std/legacy` workspace, where both generations and both schemas are installed side by side.

## Mapping table

`runschema_mapping.md` maps every attribute of `runschema` (`Run`, `System`, `Method`, `Calculation`) onto `nomad-simulations` (`Simulation` with `Program`, `ModelSystem`, `ModelMethod`, `Outputs`). Each section is a table of `runschema path | Status | nomad-simulations target | Notes`, where the status is Mapped (direct equivalent), Partial (renamed, restructured or lossy, explained in Notes) or Unmapped (no equivalent yet). The Unmapped rows double as a coverage-gap audit of `nomad-simulations`.

Source paths start at `Run` (`system.atoms.labels`, or `run.program.name` for quantities of `Run` itself) or, where a section is reachable from several places, at the section class (`HubbardKanamoriModel.u`). Targets start at a `nomad-simulations` section class and may select a subclass (`contributions[HubbardInteractions]`) or list alternatives (`orbital_1/orbital_2`).

Keep the table in step with both schemas. A new `nomad-simulations` attribute that fills a missing concept turns an Unmapped or Partial row into Mapped, and a renamed or restructured section changes a target. When editing, recompute the `**Summary:**` line of the section and the overall counts in the introduction, and refresh the date in the `generated-by` comment. Do not invent equivalents to raise coverage: an Unmapped row with a reason is the useful outcome.

`parity/mapping_check.py` verifies that every source path exists in the installed `runschema` and every Mapped or Partial target in the installed `nomad-simulations`; the tests run it on the committed table:

```bash
uv run python legacy/parity/mapping_check.py
```

## Parity report

The report classifies, per code, every `runschema` leaf a legacy parser fills on the test files of `nomad-parser-plugins-simulation`: parity (the new parser fills the mapped target), parser gap (the target exists but stays empty), schema gap (Unmapped), unknown (missing from the table) and code-specific (`x_` quantities and references). Collect the filled paths of both generations on the same files, then compare them:

```bash
DATA=packages/nomad-simulation-parsers/tests/data
uv run python legacy/parity/parity_collect.py legacy $DATA legacy.json --normalize
uv run python legacy/parity/parity_collect.py new $DATA new.json --normalize
uv run python legacy/parity/parity_report.py --legacy legacy.json --new new.json
```

Run the commands from the distribution root, so that its `nomad.yaml` applies: the parser repository's own `nomad.yaml` excludes the new VASP parser. The report is written to `parity_report.md`. Collection takes a few minutes per generation with `--normalize`; `--skip` lists code directories to leave out (ORCA by default).

### How the comparison works

`parity_collect.py` walks the code directories of the data directory and, for each file, picks the first parser of the requested generation whose `is_mainfile` accepts it, in NOMAD's `matching_order`. Both generations are loaded in this workspace, and `match_parser` alone would hand each file to whichever parser matches first, regardless of generation. Hidden files and directories (visualisation caches, trajectory offsets) are skipped. Each archive gets minimal entry metadata, which the legacy normalizers require, and with `--normalize` it runs through the full normalizer chain, so that quantities the new schema derives in `normalize` count as filled.

The two generations record their paths differently, to match the two columns of the mapping table. For the legacy parsers, every filled quantity and sub-section under `archive.run` is written relative to `Run` (`calculation.energy.total.value`). For the new parsers, every filled quantity and sub-section under `archive.data` is written relative to each enclosing section class and its base classes (`Outputs.total_energies.value`, `Simulation.outputs.total_energies.value`, ...), so that a target such as `Outputs.total_energies` is found wherever the section sits.

`parity_report.py` then takes the leaves of each legacy archive (paths without filled children) and classifies them, per code, over all files both generations parsed without error. A path with an `x_` component or ending in `_ref` or `_raw` is code-specific. Any other path is looked up in the table, first as written, then with the `run.` prefix, falling back to its closest listed ancestor. A missing row makes the path unknown, an Unmapped row a schema gap. Otherwise, the row is parity if the new archive fills the target or anything below it, and a parser gap if not. Counts are distinct table rows, so a quantity filled in many files counts once.

### Reading the report

A parser gap is the actionable outcome for the parser side: the schema has a place for the quantity, and the legacy parser extracts it from the same file. A schema gap points at `nomad-simulations` instead, and an unknown path at the table. Keep three limits in mind. The comparison only sees what the test files contain, so a code with one file is compared on one calculation. Partial rows count as parity once the target is filled, even where the Notes describe a loss. The ancestor fallback credits an unlisted leaf to its parent's row, which can hide a missing table entry behind a parity count. Files that fail to parse or normalize on either side are listed per code and left out of the counts.

## Tests

```bash
uv run pytest legacy/tests
```

The tests cover the table parsing, the classification and the report on synthetic inputs, and run the mapping check on the committed table.
