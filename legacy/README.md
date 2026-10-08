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

Run the commands from the distribution root, so that its `nomad.yaml` applies: the parser repository's own `nomad.yaml` excludes the new VASP parser. The report is written to `parity_report.md`.

## Tests

```bash
uv run pytest legacy/tests
```

The tests cover the table parsing, the classification and the report on synthetic inputs, and run the mapping check on the committed table.
