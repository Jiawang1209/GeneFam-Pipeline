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
- `docs/quickstart.md`: shortest verified local run path.
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
bash scripts/run_local_acceptance.sh
python bin/genefam/run_release_checks.py --outdir results/release_checks
python bin/genefam/run_nextflow_smoke.py --outdir results/nextflow_smoke
python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv
python bin/genefam/plan_runtime_bootstrap.py \
  --readiness results/readiness/command_readiness.tsv \
  --outdir results/readiness
```

The release checks runner writes TSV and Markdown summaries. The Nextflow smoke writes `results/nextflow_smoke/nextflow_smoke.md`; it runs the mock MVP through Nextflow when Nextflow is installed and otherwise records a `missing_nextflow` blocker. The readiness audit writes a TSV report and exits non-zero when required runtime commands are missing. The bootstrap planner converts the TSV into `results/readiness/runtime_bootstrap_plan.md` and `results/readiness/runtime_bootstrap.sh`. The static container-materials audit writes `results/container_materials/container_materials.md` and checks the Dockerfile, Linux Conda environment, and Nextflow container profile contracts before Docker/Apptainer are installed.

`bash scripts/run_local_acceptance.sh` is the shortest local acceptance entrypoint: it runs the release gate, then runs the quickstart handoff so `results/handoff/handoff_report.md`, `results/handoff/handoff_summary.tsv`, and `results/quickstart/quickstart_summary.md` are refreshed even when the release gate remains blocked by missing Docker/Apptainer commands.

When Docker and Apptainer are available, run the generated bootstrap script to build the local Docker image, build the local Apptainer SIF, smoke-test both container profiles, and rerun the release gate:

```bash
bash results/readiness/runtime_bootstrap.sh
```

Container image defaults are configurable from Nextflow:

```text
params.container_image = "genefam-pipeline:latest"
params.apptainer_image = "genefam-pipeline_latest.sif"
```

After `python bin/genefam/run_release_checks.py --outdir results/release_checks`, the first file to inspect is:

- `results/handoff/handoff_report.md`
- `results/handoff/handoff_summary.tsv`

The Markdown report is the human-facing handoff. The TSV summary carries the same top-level sections in a stable `section` / `summary` table for scripts, dashboards, or quick release parsing. Together they summarize release readiness, objective completion, available and missing runtime commands, container-profile smoke status, and links back to the detailed evidence files.

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

## Standard Identification Branch

When `GeneFamilyFlow` and external tools are available, run the HMMER/DIAMOND/domain-filter/family-summary branch explicitly:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --run_identification true \
  --final_rule intersection
```

This branch builds HMMER and DIAMOND input tables from the YAML config and species manifest, runs evidence detection per species, merges candidate evidence, concatenates family candidate tables, writes `run_config_snapshot.tsv` for the selected species and tool settings, summarizes copy numbers, extracts `family_members.faa`, prepares alignment and phylogeny manifests, parses `motif_summary.tsv` from the MEME text file supplied by `--meme_txt`, summarizes `gene_structure_summary.tsv` from species-bank GFF3 annotations, extracts `chromosome_locations.tsv`, optionally subsets a `family_expression` matrix when `--expression_matrix` is supplied, creates the family-count plot, writes a standard report index, and assembles `final_report.md`.

The domain filter smoke validates the normalized HMMER evidence thresholding step before standard candidate merging:

```bash
python bin/genefam/run_domain_filter_smoke.py \
  --input tests/fixtures/hmmer_domains/domains.tsv \
  --max-evalue 1e-10 \
  --min-bitscore 50 \
  --min-domain-coverage 0.5 \
  --outdir results/domain_filter_smoke
```

It writes `results/domain_filter_smoke/tables/filtered_domains.tsv` and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The offline standard-branch smoke check exercises the same post-identification reporting chain without requiring HMMER, DIAMOND, MAFFT, or IQ-TREE:

```bash
python bin/genefam/run_standard_smoke.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/standard_smoke
```

Add `--expression-matrix path/to/expression.tsv` to subset RNA-seq expression rows to the identified family members during the same smoke. The release gate also runs a dedicated expression smoke with `tests/fixtures/expression/family_expression.tsv`, calls `/usr/local/bin/R`, and writes `results/standard_expression_smoke/tables/family_expression.tsv` plus `results/standard_expression_smoke/plots/expression_heatmap.pdf`.

It writes `results/standard_smoke/tables/run_config_snapshot.tsv`, `results/standard_smoke/tables/gene_structure_summary.tsv`, `results/standard_smoke/tables/chromosome_locations.tsv`, `results/standard_smoke/tables/motif_summary.tsv`, records `family_expression` as missing when no expression matrix is supplied or available when `--expression-matrix` is provided, writes `results/standard_smoke/report/final_report.md`, and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The focused Nextflow single-tool smoke validates true HMMER-only and DIAMOND-only routing through `GeneFamilyFlow` without using mock evidence:

```bash
python bin/genefam/run_nextflow_single_tool_smoke.py \
  --conda-env GeneFamilyFlow \
  --outdir results/nextflow_single_tool_smoke
```

It records `nextflow_standard_hmmer_only` and `nextflow_standard_diamond_only` in `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv` and is part of the release gate.

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

This branch produces `wgd_run_config_snapshot.tsv`, normalized duplicate classifications, family duplicate classifications, WGD layer assignments, named-event evidence, family WGD event membership, family event retention summaries, and duplicate-type retention enrichment.

For the complete handoff from the standard identification branch to the WGD branch, including the prepared-table contracts for real MCScanX/KaKs-derived inputs, see `docs/standard_to_wgd_handoff.md`.

The synteny parser smoke validates the MCScanX `.collinearity` input bridge into a normalized syntenic-pair table:

```bash
python bin/genefam/run_synteny_smoke.py \
  --collinearity tests/fixtures/mcscanx/sample.collinearity \
  --outdir results/synteny_smoke
```

It writes `results/synteny_smoke/tables/syntenic_pairs.tsv` and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The Ka/Ks parser smoke validates KaKs_Calculator-style result normalization and selection-pressure categories before WGD retention summaries:

```bash
python bin/genefam/run_kaks_smoke.py \
  --kaks tests/fixtures/kaks/kaks_calculator.tsv \
  --outdir results/kaks_smoke
```

It writes `results/kaks_smoke/tables/normalized_kaks.tsv` and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The offline WGD smoke check validates the gamma, beta, alpha, and theta named-event evidence path without external MCScanX or Ka/Ks tools:

```bash
python bin/genefam/run_wgd_smoke.py \
  --events-config configs/wgd_events.brassicaceae.yaml \
  --outdir results/wgd_smoke
```

The Nextflow WGD smoke exercises the same prepared-table branch through `GeneFamilyFlow`:

```bash
python bin/genefam/run_nextflow_wgd_smoke.py \
  --conda-env GeneFamilyFlow \
  --outdir results/nextflow_wgd_smoke
```

It writes `results/wgd_smoke/tables/wgd_run_config_snapshot.tsv`, `results/wgd_smoke/report/final_report.md`, and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

## Current Status

- The repository is repository-ready but runtime-blocked on this machine until Docker/Apptainer reproducibility can be verified.
- YAML-driven species-bank discovery, manual species selection, named species groups, and run-plan generation are implemented and tested.
- The standard identification branch is wired through Nextflow DSL2 for HMMER, DIAMOND, domain filtering, family summaries, family FASTA extraction, alignment and phylogeny manifests, chromosome locations, optional RNA-seq expression handoff, plotting, and final report assembly.
- `run_nextflow_single_tool_smoke.py` verifies HMMER-only and DIAMOND-only standard routing through Nextflow with `mock_external_tools: false`.
- The prepared-table WGD branch is wired through Nextflow DSL2 for duplicate classification, Ka/Ks-supported WGD layers, gamma/beta/alpha/theta named-event evidence, family event membership, retention summaries, retention enrichment, and final report assembly.
- The local `GeneFamilyFlow` runtime verifies Nextflow, HMMER, DIAMOND, MAFFT, IQ-TREE, MEME, and `/usr/local/bin/R`; Docker/Apptainer remain the current machine-level blocker.
- Docker/Apptainer unblock is documented through `bash results/readiness/runtime_bootstrap.sh`, using `params.container_image` and `params.apptainer_image`.
- The top-level delivery status is written to `results/handoff/handoff_report.md` for humans and `results/handoff/handoff_summary.tsv` for scripts after each release-gate run.
