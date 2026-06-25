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
- `results/delivery_bundle/delivery_manifest.tsv`
- `results/delivery_bundle/delivery_bundle.md`

The handoff Markdown is the human-facing status summary. The local acceptance summary is the compact local acceptance pass/fail index for release, quickstart, and delivery-bundle refresh steps. The delivery bundle is the final index for standard reports, prepared WGD reports, alpha/beta/gamma/theta event evidence, Reference governance, runtime availability, runtime recovery, and documentation entrypoints. The TSV summaries carry stable machine-readable tables for automated checks; `results/handoff/handoff_summary.tsv` includes `container_default_smoke` as `Dockerfile -> results/container_default_smoke`. Together they summarize release readiness, objective completion, available and missing runtime commands, container-profile smoke status, runtime recovery artifacts, and the report/evidence files to open first.

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

The command exits with status `0` only when all checked commands are available. It exits with status `1` when at least one command is missing and still writes the TSV report.

The bootstrap planner reads the TSV and writes:

- `results/readiness/runtime_bootstrap_plan.md`
- `results/readiness/runtime_bootstrap.sh`

After the Docker image is built, the generated shell runs `docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest` so the image default smoke writes `results/container_default_smoke`.

After a missing runtime is installed, rerun `scripts/run_local_acceptance.sh` to refresh `results/handoff/handoff_report.md`, `results/local_acceptance/local_acceptance_summary.md`, `results/delivery_bundle/delivery_manifest.tsv`, and `results/delivery_bundle/delivery_bundle.md` from the same evidence set.

Default audited commands:

- `nextflow`
- `conda`
- `/usr/local/bin/R`
- `docker`
- `apptainer`
- `hmmsearch`
- `diamond`
- `mafft`
- `iqtree2`
- `meme`

## Interpretation

- Python helpers, config validation, mock MVP, and report assembly can be tested without external bioinformatics tools.
- Full local Nextflow execution requires `nextflow` and the `GeneFamilyFlow` environment tools.
- Docker profile execution requires Docker and the project image.
- Apptainer profile execution requires Apptainer and access to the Docker image.
- Alignment, phylogeny, and motif execution require MAFFT, IQ-TREE, and MEME-family tools through Conda or container profiles.

## Current Machine Note

On this development machine, recent audits found `/usr/local/bin/R` and `/Users/liuyue/miniforge3/bin/conda` on the host, and `nextflow`, `hmmsearch`, `diamond`, `mafft`, `iqtree` as the IQ-TREE command, and `meme` inside the `GeneFamilyFlow` Conda environment. Docker and Apptainer are still missing, so local Conda Nextflow smoke can run, while container-profile verification still needs a container runtime configured.
