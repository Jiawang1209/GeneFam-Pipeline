# Quickstart

This is the shortest verified path for checking GeneFam-Pipeline on this machine.

## Runtime

- Use the `GeneFamilyFlow` Conda environment.
- Use `/usr/local/bin/R` for R plotting and report helpers.
- The default input model is a species bank: one folder per species, with protein, CDS, genome, and GFF3 files inside each species folder.
- `Reference/` is read-only source material for papers, plotting ideas, and example scripts. Do not stage or edit it during normal development.
- Example YAML files use `tests/fixtures/hmmer_profiles/PF00657.demo.hmm` only as a lightweight path fixture; replace `gene_family.hmm_profiles` with curated HMM profiles for biological runs.
- Non-mock configs such as `configs/advanced_modules.example.yaml` should keep HMM profiles and DIAMOND reference peptides under project data paths like `data/hmm_profiles/` and `data/reference/`, not under `tests/fixtures/`.
- Keep `HISTORY.md` updated after every development step and commit.

## 1. Run The Release Gate

For a local acceptance pass that runs the release gate and then still writes the quickstart handoff artifacts even when the current machine is runtime-blocked, use:

```bash
bash scripts/run_local_acceptance.sh
```

The wrapper also writes `results/local_acceptance/local_acceptance_summary.tsv` and `results/local_acceptance/local_acceptance_summary.md`, which record the release gate, `publication_report_audit`, report-index audit exit status, quickstart, delivery-bundle exit status, and `final_stage_blocker` in one place. On machines without Docker/Apptainer, `Overall status: blocked` means the analysis-flow evidence is release-ready but the final container packaging stage still needs the runtime unblock path. The publication audit points to `results/publication_report_audit/publication_report_audit.md` and verifies paper-style report closure: valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, complete per-figure close-reading text, QC tables and warnings, software/R package versions, per-figure method/software version coverage, and reproducibility commands.

Optional overrides:

```bash
PYTHON_BIN=/Users/liuyue/miniforge3/bin/python \
CONDA_ENV=GeneFamilyFlow \
bash scripts/run_local_acceptance.sh
```

```bash
python bin/genefam/run_release_checks.py --outdir results/release_checks
```

For a single config preflight with path existence checks:

```bash
python bin/genefam/validate_config.py configs/example.config.yaml --check-paths
```

Expected on the current Mac development machine:

- Python tests, config validation, mock MVP, standard smoke, WGD smoke, Nextflow mock MVP, Nextflow standard smoke, Nextflow standard single-tool smoke, Nextflow WGD smoke, and prepared WGD handoff example should pass through `GeneFamilyFlow`.
- The readiness audit may fail while `docker` and `apptainer` are unavailable.
- `results/release_checks/release_checks.md` separates `Required failed` from `Optional failed`, so optional container-profile smoke failures do not obscure the required readiness blocker.
- Inspect `results/release_checks/release_checks.md` and `results/readiness/command_readiness.tsv` for exact evidence.

When Docker and Apptainer are installed, use the generated unblock script:

```bash
bash results/readiness/runtime_bootstrap.sh
```

It builds `genefam-pipeline:latest`, builds `genefam-pipeline_latest.sif`, runs Docker and Apptainer profile smokes, and reruns the release gate.

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
- `results/quickstart/standard_smoke/tables/run_config_snapshot.tsv`
- `results/quickstart/example_prepared_wgd/report/final_report.md`
- `results/quickstart/example_prepared_wgd/tables/wgd_run_config_snapshot.tsv`

Both final reports include a `Run Configuration Snapshot` section so the selected species, runtime, identification rule, Ks bins, and WGD event mappings can be reviewed without opening the raw TSV first.

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
- `results/handoff/handoff_report.md`
- `results/local_acceptance/local_acceptance_summary.md`
- `results/publication_report_audit/publication_report_audit.md`
- `results/delivery_bundle/delivery_manifest.tsv`
- `results/delivery_bundle/delivery_bundle.md`
- `results/delivery_bundle/figure_gallery.tsv`
- `results/delivery_bundle/figure_gallery.md`
- `configs/manifest.example.yaml`
- `configs/example.config.yaml`
- `configs/wgd_events.brassicaceae.yaml`
- `tests/fixtures/species_manifest.tsv`
- `results/species_manifest_selection_smoke/tables/species_manifest.tsv`
- `results/nextflow_standard_manifest_smoke/nextflow_standard_smoke.tsv`

On the current development machine, Docker/Apptainer reproducibility is expected to remain `blocked` until a container runtime is available.

## 4. Primary YAML Entrypoints

- `configs/example.config.yaml`: primary species-bank YAML entrypoint for choosing target species, HMM profiles, DIAMOND references, optional expression matrix input, and enabled modules.
- `configs/wgd_events.brassicaceae.yaml`: primary WGD event YAML entrypoint for mapping anonymous Ks-supported WGD layers to named gamma, beta, alpha, theta, or custom events.
- `configs/manifest.example.yaml`: manifest-mode YAML entrypoint when species files are listed in a TSV instead of discovered from one folder per species.

## 5. Inspect The Delivery Bundle

The release gate writes the final delivery index after the objective audit. It collects species-bank and manifest-mode input entrypoints, the manifest-mode standard DSL2 smoke evidence, the standard final report, prepared WGD report, publication report audit, report-index closure, alpha/beta/gamma/theta event evidence, runtime status, documentation entrypoints, and a global paper-level figure gallery.

The delivery bundle now records both report-closure audits:

- `publication_report_audit`: standard report paper-style report closure at `results/publication_report_audit/publication_report_audit.md`, covering valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, complete per-figure close-reading text, QC tables and warnings, software/R package versions, per-figure method/software version coverage, and reproducibility commands
- `wgd_publication_report_audit`: WGD report closure at `results/publication_report_audit/wgd_publication_report_audit.md`, covering valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, complete Ka/Ks/WGD figure close-reading text, gamma beta alpha theta interpretation, QC tables and warnings, software/R package versions, per-figure method/software version coverage, and reproducibility commands
- `standard_report_index_audit`: standard report-index closure at `results/report_index_audit/standard_report_index_audit.md`, covering indexed plot manifests, software versions, `figure_interpretations.tsv`, `figure_interpretations.md`, `final_report.md`, and `figure_traceability_matrix`
- `wgd_report_index_audit`: WGD report-index closure at `results/report_index_audit/wgd_report_index_audit.md`, covering indexed plot manifests, software versions, `figure_interpretations.tsv`, `figure_interpretations.md`, `final_report.md`, and `figure_traceability_matrix`

The global paper-level figure gallery is the fastest way to inspect plots across the standard and WGD branches:

- `results/delivery_bundle/figure_gallery.tsv`: machine-readable plot index
- `results/delivery_bundle/figure_gallery.md`: human-readable plot index
- `results/delivery_bundle_smoke/figure_gallery_audit.tsv`: machine-readable figure-gallery link audit from `bin/genefam/audit_figure_gallery.py`
- `results/delivery_bundle_smoke/figure_gallery_audit.md`: human-readable figure-gallery link audit
- `results/delivery_bundle_smoke/delivery_manifest_audit.tsv`: machine-readable delivery-manifest path audit from `bin/genefam/audit_delivery_manifest.py`
- `results/delivery_bundle_smoke/delivery_manifest_audit.md`: human-readable delivery-manifest path audit

Each gallery row links a plot PDF to its `figure_interpretations.md`, `software_versions.tsv`, `final_report.md`, and `figure_traceability_matrix` anchor.
The delivery manifest audit verifies that available and blocked handoff index paths resolve to real files or accepted runtime locators.
The local acceptance summary records both `figure_gallery_audit` and `delivery_manifest_audit` as separate pass/fail rows so the final handoff index and global plot gallery can be checked without opening the full release table.

```bash
python bin/genefam/run_delivery_bundle.py \
  --release-checks results/release_checks/release_checks.tsv \
  --objective-audit results/objective_audit/objective_audit.tsv \
  --readiness results/readiness/command_readiness.tsv \
  --quickstart results/quickstart/quickstart_summary.tsv \
  --outdir results/delivery_bundle
```

## 6. Run The Standard Branch Smoke

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
- `results/standard_smoke/tables/wgd_handoff_manifest.tsv`
- `results/standard_smoke/tables/chromosome_locations.tsv`
- `results/standard_smoke/sequences/family_members.faa`
- `results/standard_smoke/report/final_report.md`

## 7. Run The Prepared WGD Handoff

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

## 8. Run The Nextflow Single-Tool Smoke

This checks real Nextflow routing for HMMER-only and DIAMOND-only standard identification paths through `GeneFamilyFlow`.

```bash
python bin/genefam/run_nextflow_single_tool_smoke.py \
  --conda-env GeneFamilyFlow \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/nextflow_single_tool_smoke
```

Key checks in `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv`:

- `nextflow_standard_hmmer_only`
- `nextflow_standard_diamond_only`

## 9. What To Read Next

- `docs/input_contract.md`: species bank, YAML, and prepared-table contracts.
- `docs/standard_to_wgd_handoff.md`: how standard branch outputs connect to WGD evidence.
- `docs/wgd_event_evidence.md`: anonymous WGD layers and named event interpretation.
- `docs/release_audit.md`: requirement-to-evidence map and known runtime gaps.
- `docs/runtime_environment.md`: Conda, Docker, Apptainer, and Nextflow profiles.
