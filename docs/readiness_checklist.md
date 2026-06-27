# Readiness Checklist

This checklist separates repository-level readiness from machine-level runtime readiness.

## Repository Checks

Run these commands before considering a development checkpoint usable:

```bash
python bin/genefam/run_release_checks.py --outdir results/release_checks
python -m pytest tests -q
python bin/genefam/validate_config.py configs/example.config.yaml
python bin/genefam/run_mock_mvp.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/mock_mvp
```

After the release gate finishes, the first file to inspect is:

- `results/handoff/handoff_report.md`
- `results/handoff/handoff_summary.tsv`
- `results/local_acceptance/local_acceptance_summary.md`
- `results/publication_report_audit/publication_report_audit.md`
- `results/report_index_audit/standard_report_index_audit.md`
- `results/report_index_audit/wgd_report_index_audit.md`
- `results/delivery_bundle_smoke/figure_gallery_audit.md`
- `results/delivery_bundle_smoke/delivery_manifest_audit.md`
- `results/delivery_bundle/delivery_manifest.tsv`
- `results/delivery_bundle/delivery_bundle.md`

The handoff Markdown is the human-facing status summary. The local acceptance summary is the compact local acceptance pass/fail index for release, `publication_report_audit`, report-index closure, quickstart, and delivery-bundle refresh steps. The publication audit is the paper-style report closure check for valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, complete per-figure close-reading text, QC tables and warnings, software/R package versions, per-figure method/software version coverage, and reproducibility commands. The standard and WGD report-index audits verify that each report index exposes plot manifests, software versions, figure interpretations in TSV/Markdown, final reports, and `figure_traceability_matrix` anchors. The figure-gallery audit at `results/delivery_bundle_smoke/figure_gallery_audit.md` verifies plot_manifest coverage for the standard and WGD report manifests and verifies that every delivery-gallery plot, interpretation, software-version, final-report, and traceability target exists. The delivery-manifest audit at `results/delivery_bundle_smoke/delivery_manifest_audit.md` verifies that available and blocked handoff index paths resolve to real files or accepted runtime locators. The delivery bundle is the final index for standard reports, prepared WGD reports, alpha/beta/gamma/theta event evidence, Reference governance, runtime availability, runtime recovery, and documentation entrypoints. The TSV summaries carry stable machine-readable tables for automated checks; `results/handoff/handoff_summary.tsv` includes `container_default_smoke` as `Dockerfile -> results/container_default_smoke`. Together they summarize release readiness, objective completion, available and missing runtime commands, container-profile smoke status, runtime recovery artifacts, and the report/evidence files to open first.

Expected core mock outputs:

- `results/mock_mvp/tables/species_manifest.tsv`
- `results/mock_mvp/tables/run_plan.tsv`
- `results/mock_mvp/tables/family_candidates.tsv`
- `results/mock_mvp/tables/family_counts.tsv`
- `results/mock_mvp/tables/alignment_manifest.tsv`
- `results/mock_mvp/tables/phylogeny_manifest.tsv`
- `results/mock_mvp/sequences/family_members.faa`
- `results/mock_mvp/report/report_index.tsv`
- `results/mock_mvp/report/final_report.md`

## Runtime Command Audit

Run:

```bash
python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv
python bin/genefam/plan_runtime_bootstrap.py \
  --readiness results/readiness/command_readiness.tsv \
  --outdir results/readiness
```

The command writes a `requirement` column. It exits with status `0` when all required core analysis commands are available, even if optional container-stage commands such as `docker` or `apptainer` are missing. It exits with status `1` when at least one required command is missing and still writes the TSV report. Optional missing container commands stay visible in the TSV so the bootstrap planner and handoff reports can keep the final packaging gap explicit.

The bootstrap planner reads the TSV and writes:

- `results/readiness/runtime_bootstrap_plan.md`
- `results/readiness/runtime_bootstrap.sh`

After the Docker image is built, the generated shell runs `docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest` so the image default smoke writes `results/container_default_smoke`.

After a missing runtime is installed, rerun `scripts/run_local_acceptance.sh` to refresh `results/handoff/handoff_report.md`, `results/local_acceptance/local_acceptance_summary.md`, `results/publication_report_audit/publication_report_audit.md`, `results/report_index_audit/standard_report_index_audit.md`, `results/report_index_audit/wgd_report_index_audit.md`, `results/delivery_bundle/delivery_manifest.tsv`, and `results/delivery_bundle/delivery_bundle.md` from the same evidence set.

Default audited commands:

- `nextflow`
- `conda`
- `/usr/local/bin/R`
- `docker`
- `apptainer`
- `hmmsearch`
- `diamond`
- `mafft`
- `FastTree`
- `iqtree2`
- `meme`

## Interpretation

- Python helpers, config validation, mock MVP, and report assembly can be tested without external bioinformatics tools.
- Full local Nextflow execution requires `nextflow` and the `GeneFamilyFlow` environment tools.
- Docker profile execution requires Docker and the project image.
- Apptainer profile execution requires Apptainer and access to the Docker image.
- Alignment, phylogeny, and motif execution require MAFFT, IQ-TREE, and MEME-family tools through Conda or container profiles.

## Current Machine Note

On this development machine, recent audits found `/usr/local/bin/R` and `/Users/liuyue/miniforge3/bin/conda` on the host, and `nextflow`, `hmmsearch`, `diamond`, `mafft`, `FastTree`, `iqtree` as the IQ-TREE command, and `meme` inside the `GeneFamilyFlow` Conda environment. Docker and Apptainer are still missing, so local Conda Nextflow smoke can run, while container-profile verification still needs a container runtime configured.
