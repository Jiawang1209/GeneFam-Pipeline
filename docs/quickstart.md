# Quickstart

This is the shortest verified path for checking GeneFam-Pipeline on this machine.

## Runtime

- Use the `GeneFamilyFlow` Conda environment.
- Use `/usr/local/bin/R` for R plotting and report helpers.
- The default input model is a species bank: one folder per species, with protein, CDS, genome, and GFF3 files inside each species folder.
- `Reference/` is read-only source material for papers, plotting ideas, and example scripts. Do not stage or edit it during normal development.
- Keep `HISTORY.md` updated after every development step and commit.

## 1. Run The Release Gate

```bash
python bin/genefam/run_release_checks.py --outdir results/release_checks
```

Expected on the current Mac development machine:

- Python tests, config validation, mock MVP, standard smoke, WGD smoke, Nextflow mock MVP, Nextflow standard smoke, Nextflow WGD smoke, and prepared WGD handoff example should pass through `GeneFamilyFlow`.
- The readiness audit may fail while `docker` and `apptainer` are unavailable.
- Inspect `results/release_checks/release_checks.md` and `results/readiness/command_readiness.tsv` for exact evidence.

## 2. Run The Quickstart Handoff

This one command runs the standard branch smoke and prepared WGD handoff, then writes a compact summary.

```bash
python bin/genefam/run_quickstart.py \
  --conda-env GeneFamilyFlow \
  --outdir results/quickstart
```

Key outputs:

- `results/quickstart/quickstart_summary.tsv`
- `results/quickstart/quickstart_summary.md`
- `results/quickstart/standard_smoke/report/final_report.md`
- `results/quickstart/example_prepared_wgd/report/final_report.md`

## 3. Audit The Long Objective

The release gate writes this automatically after the readiness audit. You can also regenerate the machine-readable summary of the original long-form goal manually:

```bash
python bin/genefam/audit_objective_completion.py \
  --release-checks results/release_checks/release_checks.tsv \
  --readiness results/readiness/command_readiness.tsv \
  --outdir results/objective_audit
```

Key outputs:

- `results/objective_audit/objective_audit.tsv`
- `results/objective_audit/objective_audit.md`

On the current development machine, Docker/Apptainer reproducibility is expected to remain `blocked` until a container runtime is available.

## 4. Run The Standard Branch Smoke

This checks the species-bank driven family identification post-processing path without requiring external HMMER or DIAMOND execution.

```bash
python bin/genefam/run_standard_smoke.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/standard_smoke
```

Key outputs:

- `results/standard_smoke/tables/family_candidates.tsv`
- `results/standard_smoke/tables/chromosome_locations.tsv`
- `results/standard_smoke/sequences/family_members.faa`
- `results/standard_smoke/report/final_report.md`

## 5. Run The Prepared WGD Handoff

This checks the reusable handoff from family candidates plus prepared duplication and Ka/Ks tables into WGD layer and named-event evidence.

```bash
python bin/genefam/run_prepared_wgd_handoff_example.py \
  --conda-env GeneFamilyFlow \
  --example-dir examples/prepared_wgd_handoff \
  --outdir results/example_prepared_wgd
```

Key outputs:

- `results/example_prepared_wgd/tables/wgd_event_evidence.tsv`
- `results/example_prepared_wgd/tables/family_wgd_event_membership.tsv`
- `results/example_prepared_wgd/tables/family_event_retention_summary.tsv`
- `results/example_prepared_wgd/report/final_report.md`

The example verifies configured `alpha`, `beta`, `gamma`, and `theta` WGD event labels. These labels are interpreted from Ks-supported WGD layers and the configured event mapping; they are not raw MCScanX or Ka/Ks outputs.

## 6. What To Read Next

- `docs/input_contract.md`: species bank, YAML, and prepared-table contracts.
- `docs/standard_to_wgd_handoff.md`: how standard branch outputs connect to WGD evidence.
- `docs/wgd_event_evidence.md`: anonymous WGD layers and named event interpretation.
- `docs/release_audit.md`: requirement-to-evidence map and known runtime gaps.
- `docs/runtime_environment.md`: Conda, Docker, Apptainer, and Nextflow profiles.
