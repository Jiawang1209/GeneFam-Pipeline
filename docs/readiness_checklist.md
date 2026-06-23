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
python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv
python bin/genefam/plan_runtime_bootstrap.py \
  --readiness results/readiness/command_readiness.tsv \
  --outdir results/readiness
```

The command exits with status `0` only when all checked commands are available. It exits with status `1` when at least one command is missing and still writes the TSV report.

The bootstrap planner reads the TSV and writes:

- `results/readiness/runtime_bootstrap_plan.md`
- `results/readiness/runtime_bootstrap.sh`

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

On this development machine, recent audits found `/usr/local/bin/R` and `/Users/liuyue/miniforge3/bin/conda`, while `nextflow`, `docker`, `apptainer`, `mafft`, `iqtree2`, and `meme` were not on `PATH`. That means repository-level checks can pass here, but full end-to-end Nextflow execution needs the missing tools installed or a container runtime configured.
