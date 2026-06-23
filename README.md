# GeneFam-Pipeline

Reusable Nextflow pipeline for large-scale multi-species gene family analysis.

The first implementation target is a YAML-driven workflow that scans a large species bank, selects a run-specific subset of species, identifies gene family members with HMMER and DIAMOND/BLAST, filters candidates, summarizes copy numbers, and writes report-ready tables and FASTA files.

## Planned Scope

- Genome-wide family identification with HMMER and DIAMOND/BLAST.
- Domain filtering and candidate evidence merging.
- Multi-species family member summaries.
- Alignment and phylogeny.
- Motif and gene structure analysis.
- Chromosome localization.
- Synteny, duplication classification, WGD-layer inference, and retention enrichment.
- Evidence-backed WGD event interpretation for gamma, beta, alpha, theta, and other configured events.
- Duplicate-type retention enrichment for WGD-retained family members.
- Ka/Ks and selection-pressure analysis.
- RNA-seq expression integration.
- Reproducible reports.

## Input Model

The default input is a species bank with one folder per species:

```text
data/species_bank/
  Arabidopsis_thaliana/
    Arabidopsis_thaliana.pep.fa
    Arabidopsis_thaliana.cds.fa
    Arabidopsis_thaliana.genome.fa
    Arabidopsis_thaliana.gff3
  Brassica_rapa/
    Brassica_rapa.pep.fa
    Brassica_rapa.cds.fa
    Brassica_rapa.genome.fa
    Brassica_rapa.gff3
```

The species ID defaults to the folder name. A run can analyze all species, a manual include list, or a named species group.

## Project Files

- `AGENT.md`: project-wide development rules.
- `CLAUDE.md`: Claude-specific guidance.
- `HISTORY.md`: single-file development diary.
- `configs/example.config.yaml`: example analysis configuration.
- `configs/advanced_modules.example.yaml`: advanced module configuration example.
- `docs/input_contract.md`: input format contract.
- `docs/advanced_module_examples.md`: safe examples for enabling advanced modules.
- `docs/release_audit.md`: requirement-to-evidence release audit and known runtime gaps.
- `docs/wgd_event_evidence.md`: WGD layer and named-event evidence contract.
- `docs/runtime_environment.md`: Conda, Docker, and Nextflow profile runtime notes.
- `docs/readiness_checklist.md`: repository and machine-level readiness checks.
- `docs/superpowers/plans/2026-06-23-genefam-pipeline.md`: implementation plan.

## Runtime Convention

- Shared environment name: `GeneFamilyFlow`
- R binary: `/usr/local/bin/R`

Nextflow defaults are recorded in `workflows/nextflow.config`. R scripts should be executed through `/usr/local/bin/R` rather than relying on the shell-default `R` or `Rscript`.

Runtime files:

- `envs/GeneFamilyFlow.conda.yaml`
- `Dockerfile`
- `workflows/nextflow.config` profiles: `local`, `docker`, `apptainer`

Readiness audit:

```bash
python bin/genefam/run_release_checks.py --outdir results/release_checks
python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv
python bin/genefam/plan_runtime_bootstrap.py \
  --readiness results/readiness/command_readiness.tsv \
  --outdir results/readiness
```

The release checks runner writes TSV and Markdown summaries. The readiness audit writes a TSV report and exits non-zero when required runtime commands are missing. The bootstrap planner converts the TSV into `results/readiness/runtime_bootstrap_plan.md` and `results/readiness/runtime_bootstrap.sh`.

## Reference Plotting Scripts

The `Reference/` directory contains paper-derived plotting scripts and result examples. New reusable plots should inspect these scripts first, reuse their scientific plotting logic where appropriate, and then implement parameterized versions under `scripts/`.

Reference files are source material: do not edit them unless explicitly requested.

## MVP Command

The first runnable checkpoint generates a species manifest:

```bash
nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml
```

The offline mock MVP runs without HMMER, DIAMOND, or Nextflow:

```bash
python bin/genefam/run_mock_mvp.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/mock_mvp
```

It writes:

- `results/mock_mvp/tables/species_manifest.tsv`
- `results/mock_mvp/tables/run_plan.tsv`
- `results/mock_mvp/tables/family_candidates.tsv`
- `results/mock_mvp/tables/family_counts.tsv`
- `results/mock_mvp/tables/alignment_manifest.tsv`
- `results/mock_mvp/tables/phylogeny_manifest.tsv`
- `results/mock_mvp/sequences/family_members.faa`
- `results/mock_mvp/report/summary.md`
- `results/mock_mvp/report/final_report.md`
- `results/mock_mvp/report/report_index.tsv`

When Nextflow is available, the same mock runner is exposed through:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --mock_mvp true \
  --mock_evidence_dir tests/fixtures/mock_evidence \
  --outdir results/mock_mvp
```

## Duplication And WGD Event Branch

The duplication-retention helper chain is available as a Nextflow branch for prepared intermediate tables:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --run_duplication_retention true \
  --duplicates path/to/duplicate_types.tsv \
  --family_members path/to/family_candidates.tsv \
  --kaks_pairs path/to/kaks_pairs.tsv \
  --events_config configs/wgd_events.brassicaceae.yaml \
  --ks_bins 0.3,0.8,1.5 \
  --wgd_event_args "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta"
```

This branch produces normalized duplicate classifications, family duplicate classifications, WGD layer assignments, named-event evidence, family WGD event membership, family event retention summaries, and duplicate-type retention enrichment.

## Current Status

- Project governance files are in place.
- YAML config and schema draft are in place.
- Species discovery helper is implemented and tested.
- Offline mock MVP runner is implemented and tested.
- Report index generation is implemented for stable downstream reporting.
- Duplication, WGD-event, and retention helper processes are wired as a prepared-table Nextflow branch.
- Alignment, phylogeny, motif parsing, chromosome location, and expression-subset processes are represented as Nextflow DSL2 modules.
- Full external-tool workflow wiring is still under development.
