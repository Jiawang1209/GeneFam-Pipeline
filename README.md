# GeneFam-Pipeline

中文说明见 [README.zh-CN.md](README.zh-CN.md)。

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
- `configs/publication_modules.example.yaml`: YAML-only standard visualization smoke configuration for report-scale figures.
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
- `Apptainer.def`
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

The release checks runner writes TSV and Markdown summaries. It also runs `R runtime health` through `bin/genefam/check_r_runtime.py` before R plotting smokes and writes `results/r_runtime_health/r_runtime_health.md`, so a missing or killed `/usr/local/bin/R` is visible before downstream visualization failures. The long objective audit requires both the readiness row for `/usr/local/bin/R` and the `R runtime health` release-check row before marking `/usr/local/bin/R plotting` achieved. The Nextflow smoke writes `results/nextflow_smoke/nextflow_smoke.md`; it runs the mock MVP through Nextflow when Nextflow is installed and otherwise records a `missing_nextflow` blocker. The readiness audit writes a TSV report with `requirement=required|optional` and exits non-zero only when required core analysis commands are missing. Docker and Apptainer remain optional container-stage commands until the final packaging phase, but missing container commands are still recorded for the bootstrap planner. The bootstrap planner converts the TSV into `results/readiness/runtime_bootstrap_plan.md` and `results/readiness/runtime_bootstrap.sh`. The static container-materials audit writes `results/container_materials/container_materials.md` and checks the Dockerfile, `Apptainer.def`, Linux Conda environment, and Nextflow container profile contracts before Docker/Apptainer are installed. `Apptainer.def` is Reference-safe: it copies only the required source, config, workflow, schema, environment, and `tests/fixtures` paths instead of local `Reference/` paper material. After the release and objective evidence is written, `bin/genefam/run_delivery_bundle.py` writes `results/delivery_bundle/delivery_manifest.tsv`, `results/delivery_bundle/delivery_bundle.md`, `results/delivery_bundle/figure_gallery.tsv`, and `results/delivery_bundle/figure_gallery.md` as the final user-facing index, including species-bank and manifest-mode input entries, runtime recovery entries, `mock_mvp`, `nextflow_mock_mvp_smoke`, `nextflow_single_tool_smoke`, `delivery_bundle_figure_gallery_smoke`, a `r_runtime_health` row pointing to `results/r_runtime_health/r_runtime_health.md`, a global paper-level figure gallery, and a `final_stage_blocker` row that points to the remaining Docker/Apptainer packaging blocker when those runtimes are unavailable.

`bash scripts/run_local_acceptance.sh` is the shortest local acceptance entrypoint: it runs the release gate, then runs the quickstart handoff so `results/handoff/handoff_report.md`, `results/handoff/handoff_summary.tsv`, `results/publication_report_audit/publication_report_audit.md`, `results/delivery_bundle/delivery_manifest.tsv`, `results/delivery_bundle/delivery_bundle.md`, `results/delivery_bundle/figure_gallery.tsv`, `results/delivery_bundle/figure_gallery.md`, and `results/quickstart/quickstart_summary.md` are refreshed even when the release gate remains blocked by missing Docker/Apptainer commands. It also writes `results/local_acceptance/local_acceptance_summary.md` as the compact local acceptance summary and pass/fail index for release, quickstart, publication-report audit, report-index audit, `figure_gallery_audit`, release-gate `delivery_manifest_audit`, final `final_delivery_manifest_audit`, and delivery-bundle steps. The final manifest audit writes `results/delivery_bundle/final_delivery_manifest_audit.tsv` and `results/delivery_bundle/final_delivery_manifest_audit.md` after the user-facing bundle is refreshed. The publication-report audit is the paper-style report closure check: it verifies valid plot file signatures, `report_index_plot_variants` PDF/PNG plot variants from report indexes, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, embedded PNG previews in `final_report.md`, complete per-figure close-reading text, result-statement interpretation narratives, including QC warnings and reading status, rather than instructional prompts, `figure_interpretation_qc_specificity` checks for figure-specific QC warnings, QC tables and warnings, software/R package versions, parseable detected version values, a `final_report_methods_summary` Methods Summary, per-figure method/software version coverage, and reproducibility commands before a result package is treated as MVP-ready.

When Docker and Apptainer are available, run the generated bootstrap script to build the local Docker image, build the local Apptainer SIF, smoke-test both container profiles, and rerun the release gate:

```bash
bash results/readiness/runtime_bootstrap.sh
```

The generated script also runs the Docker image default smoke with `docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest`, which writes `results/container_default_smoke` after the image is built.

For an Apptainer-native build path that does not depend on `docker-daemon://`, use the checked-in definition file:

```bash
apptainer build --force genefam-pipeline_latest.sif Apptainer.def
```

Container image defaults are configurable from Nextflow:

```text
params.container_image = "genefam-pipeline:latest"
params.apptainer_image = "genefam-pipeline_latest.sif"
```

After `python bin/genefam/run_release_checks.py --outdir results/release_checks`, the first file to inspect is:

- `results/handoff/handoff_report.md`
- `results/handoff/handoff_summary.tsv`
- `results/local_acceptance/local_acceptance_summary.md`
- `results/publication_report_audit/publication_report_audit.md`
- `results/publication_report_audit/wgd_publication_report_audit.md`
- `results/report_index_audit/standard_report_index_audit.md`
- `results/report_index_audit/wgd_report_index_audit.md`
- `results/delivery_bundle/delivery_bundle.md`
- `results/delivery_bundle/delivery_manifest.tsv`
- `results/delivery_bundle/figure_gallery.tsv`
- `results/delivery_bundle/figure_gallery.md`
- `results/delivery_bundle/final_delivery_manifest_audit.md`

The handoff Markdown is the human-facing status summary. The local acceptance summary is the compact pass/fail index for release, quickstart, publication-report audit, report-index closure, and delivery-bundle steps. The standard publication report audit verifies that the paper-style standard report package closes every registered plot with valid plot file signatures, `report_index_plot_variants` PDF/PNG plot variants from report indexes, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, embedded PNG previews in `final_report.md`, complete per-figure close-reading text, result-statement interpretation narratives, including QC warnings and reading status, rather than instructional prompts, `figure_interpretation_qc_specificity` checks for figure-specific QC warnings, QC tables and warnings, method/software entries, software/R package versions, parseable detected version values, visible non-detected version rows, a `final_report_methods_summary` Methods Summary naming the core HMMER, DIAMOND, MCScanX, Ka/Ks, gamma, beta, alpha, and theta context, per-figure method/software version coverage, and reproducibility commands. The WGD publication report audit applies the same closure to Ka/Ks/WGD figures and gamma beta alpha theta interpretation. The standard and WGD report-index audits verify that report indexes expose plot manifests, software versions, figure interpretations in TSV/Markdown, `figure_interpretations.md`, `final_report.md`, and `figure_traceability_matrix` anchors so users can navigate the whole report package from the index; they also verify that all available indexed report paths exist and that `figure_traceability_matrix` points to `final_report.md#figure-traceability-matrix`. The global paper-level figure gallery is the shortest plot-navigation entry: `figure_gallery.tsv` is script-friendly and exposes `plot_path` plus `plot_png_path`, while `figure_gallery.md` is human-readable and uses clickable Markdown links for each standard/WGD figure's PDF and PNG plot targets, close-reading report with per-figure close-reading anchors, software version table, final report, and traceability matrix. The release gate also writes `results/delivery_bundle_smoke/figure_gallery_audit.tsv` and `results/delivery_bundle_smoke/figure_gallery_audit.md`; `figure_gallery_audit` is generated by `bin/genefam/audit_figure_gallery.py` and confirms plot_manifest coverage for the standard and WGD report manifests before checking that every gallery row points to real PDF and PNG plot targets, close-reading, version, report, and traceability targets with valid gallery plot file signatures, including per-figure close-reading anchors, clickable Markdown links, and `figure_gallery_traceability_targets` checks that each row's traceability anchor belongs to its final report. The release gate also writes `results/delivery_bundle_smoke/delivery_manifest_audit.tsv` and `results/delivery_bundle_smoke/delivery_manifest_audit.md`; `delivery_manifest_audit` is generated by `bin/genefam/audit_delivery_manifest.py` and verifies release-gate bundle handoff paths, including the `r_runtime_health` row. Local acceptance then audits the final user-facing bundle and writes `results/delivery_bundle/final_delivery_manifest_audit.tsv` plus `results/delivery_bundle/final_delivery_manifest_audit.md`; `final_delivery_manifest_audit` verifies that available and blocked paths in `results/delivery_bundle/delivery_manifest.tsv` resolve to real files or accepted runtime locators. The delivery bundle is the final user-facing index for species-bank and manifest-mode input, standard reports, WGD event evidence, Reference governance, runtime availability, R runtime health, runtime recovery, and documentation; inspect `final_stage_blocker` first when release-ready analysis evidence exists but Docker/Apptainer packaging still needs local runtime support. The TSV summaries carry stable machine-readable tables for scripts, dashboards, or quick release parsing; `results/handoff/handoff_summary.tsv` includes `container_default_smoke` as `Dockerfile -> results/container_default_smoke`.

## Reference Plotting Scripts

The `Reference/` directory contains paper-derived plotting scripts and result examples. New reusable plots should inspect these scripts first, reuse their scientific plotting logic where appropriate, and then implement parameterized versions under `scripts/`.

Reference files are source material: do not edit them unless explicitly requested.

## MVP Command

The first runnable checkpoint generates a species manifest:

```bash
nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml
```

The species-selection smoke validates the YAML-driven species-bank entrypoint before downstream analysis:

```bash
python bin/genefam/run_species_selection_smoke.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --outdir results/species_selection_smoke
```

It writes `results/species_selection_smoke/tables/species_manifest.tsv`, `results/species_selection_smoke/tables/run_plan.tsv`, and `results/species_selection_smoke/species_selection_smoke.md`, and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

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

This branch builds HMMER and DIAMOND input tables from the YAML config and species manifest, runs evidence detection per species, merges candidate evidence, concatenates family candidate tables, writes `run_config_snapshot.tsv` for the selected species and tool settings, summarizes copy numbers, extracts `family_members.faa`, prepares alignment and phylogeny manifests, runs MAFFT alignment, runs the configured tree builder, parses `motif_summary.tsv` from the MEME text file supplied by `--meme_txt`, summarizes `gene_structure_summary.tsv` from species-bank GFF3 annotations, extracts `chromosome_locations.tsv`, writes `wgd_handoff_manifest.tsv` for the standard-to-WGD branch handoff, optionally subsets a `family_expression` matrix when `--expression_matrix` is supplied, creates the family-count plot, writes a standard report index, and assembles `final_report.md`. The report index and final report include the real alignment file and tree file, not only the preparation manifests. The Nextflow default tree builder is FastTree for large multi-species family trees; pass `--tree_builder iqtree` when slower model-selection/bootstrap runs are needed.

Optional standard-branch visualization switches are available for report-scale figures: `--run_promoter true` extracts promoter BED/FASTA when genome FASTA is present, `--run_feature_summary true` builds aggregate feature statistics and PDF/PNG plots, and `--run_mcscanx_circlize true --syntenic_pairs path/to/syntenic_pairs.tsv` renders MCScanX syntenic links with `circlize`. The same publication-module inputs can be driven from YAML for the standard smoke runner: `modules.feature_summary`, `modules.synteny` plus `plotting.syntenic_pairs`, `modules.promoter_cis` plus `promoter.cis_elements`, `modules.ppi` plus `ppi.edges`/`ppi.nodes`, and `modules.expression` plus `expression.matrix`/`expression.metadata`.

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

The motif parser smoke validates MEME text parsing before standard report integration:

```bash
python bin/genefam/run_motif_smoke.py \
  --meme-txt tests/fixtures/mock_evidence/meme.txt \
  --family-name GDSL \
  --outdir results/motif_smoke
```

It writes `results/motif_smoke/tables/motif_summary.tsv` and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

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

The gene-structure smoke validates the species-bank GFF3 bridge for identified family candidates:

```bash
python bin/genefam/run_gene_structure_smoke.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/gene_structure_smoke
```

It writes `results/gene_structure_smoke/tables/gene_structure_summary.tsv` and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The alignment/phylogeny smoke validates report-ready manifests for the external aligner and tree-builder steps:

```bash
python bin/genefam/run_alignment_phylogeny_smoke.py \
  --family-name GDSL \
  --fasta tests/fixtures/alignment/family_members.faa \
  --aligner mafft \
  --tree-builder fasttree \
  --outdir results/alignment_phylogeny_smoke
```

It writes `results/alignment_phylogeny_smoke/tables/alignment_manifest.tsv` and `results/alignment_phylogeny_smoke/tables/phylogeny_manifest.tsv`, then records those paths in `results/alignment_phylogeny_smoke/alignment_phylogeny_smoke.md`. Use `--tree-builder fasttree` for large multi-species family trees when speed is the priority; use `--tree-builder iqtree` for slower model-selection/bootstrap runs. This check is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The chromosome-location smoke validates the species-bank GFF3 coordinate bridge for identified family candidates:

```bash
python bin/genefam/run_chromosome_smoke.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/chromosome_smoke
```

It writes `results/chromosome_smoke/tables/chromosome_locations.tsv` and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The promoter smoke validates upstream sequence extraction from a genome FASTA plus GFF3 gene coordinates, then summarizes promoter lengths and boundary clipping for large family reports:

```bash
python bin/genefam/run_promoter_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/promoter_smoke
```

It writes `results/promoter_smoke/tables/promoters.bed`, `results/promoter_smoke/sequences/promoters.fa`, `results/promoter_smoke/tables/feature_summary.tsv`, and `results/promoter_smoke/plots/feature_summary.pdf`. This check is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The feature-summary smoke aggregates large-result tables before plotting, so MEME motif counts/sites, gene-structure lengths/exon counts, HMMER domain hits/coverage, MCScanX syntenic pairs/blocks, and promoter lengths can be inspected as statistics instead of only per-gene graphics:

```bash
python bin/genefam/run_feature_summary_smoke.py \
  --domains results/domain_filter_smoke/tables/filtered_domains.tsv \
  --motifs results/motif_smoke/tables/motif_summary.tsv \
  --gene-structures results/gene_structure_smoke/tables/gene_structure_summary.tsv \
  --synteny results/synteny_smoke/tables/syntenic_pairs.tsv \
  --promoters results/promoter_smoke/tables/promoters.bed \
  --r-bin /usr/local/bin/R \
  --outdir results/feature_summary_smoke
```

It writes `results/feature_summary_smoke/tables/feature_summary.tsv`, `results/feature_summary_smoke/plots/feature_summary.pdf`, and `results/feature_summary_smoke/plots/feature_summary.png`. This check is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

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

If you already have real MCScanX `.collinearity` output and a KaKs_Calculator-style result table, the WGD branch can prepare the duplicate and Ka/Ks handoff tables for you:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --run_duplication_retention true \
  --family_members path/to/family_candidates.tsv \
  --mcscanx_collinearity path/to/sample.collinearity \
  --kaks_results path/to/kaks_calculator.tsv \
  --events_config configs/wgd_events.brassicaceae.yaml \
  --ks_bins 0.3,0.8,1.5 \
  --wgd_event_args "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta"
```

This raw handoff writes `mcscanx_kaks_handoff/tables/syntenic_pairs.tsv`, `duplicate_types.tsv`, `normalized_kaks.tsv`, `kaks_pairs.tsv`, and `mcscanx_kaks_handoff.md` before feeding the WGD event branch.

For the complete handoff from the standard identification branch to the WGD branch, including the prepared-table contracts for real MCScanX/KaKs-derived inputs, see `docs/standard_to_wgd_handoff.md`.

The synteny parser smoke validates the MCScanX `.collinearity` input bridge into a normalized syntenic-pair table:

```bash
python bin/genefam/run_synteny_smoke.py \
  --collinearity tests/fixtures/mcscanx/sample.collinearity \
  --outdir results/synteny_smoke
```

It writes `results/synteny_smoke/tables/syntenic_pairs.tsv` and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The MCScanX circlize smoke validates publication-style syntenic-link visualization from MCScanX pairs plus gene chromosome coordinates:

```bash
python bin/genefam/run_mcscanx_circlize_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/mcscanx_circlize_smoke
```

It writes `results/mcscanx_circlize_smoke/tables/circlize_chromosomes.tsv`, `results/mcscanx_circlize_smoke/tables/circlize_links.tsv`, `results/mcscanx_circlize_smoke/tables/circlize_skipped_links.tsv`, `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.pdf`, and `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.png`. This is the dedicated MCScanX + `circlize` visualization check and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The Ka/Ks parser smoke validates KaKs_Calculator-style result normalization and selection-pressure categories before WGD retention summaries:

```bash
python bin/genefam/run_kaks_smoke.py \
  --kaks tests/fixtures/kaks/kaks_calculator.tsv \
  --outdir results/kaks_smoke
```

It writes `results/kaks_smoke/tables/normalized_kaks.tsv` and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

The retention-enrichment smoke validates duplicate-type normalization, family duplicate classification, and enrichment statistics from the prepared WGD handoff example:

```bash
python bin/genefam/run_retention_enrichment_smoke.py \
  --family-members examples/prepared_wgd_handoff/family_candidates.tsv \
  --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv \
  --outdir results/retention_enrichment_smoke
```

It writes `results/retention_enrichment_smoke/tables/normalized_duplicate_types.tsv`, `results/retention_enrichment_smoke/tables/family_duplicate_classification.tsv`, and `results/retention_enrichment_smoke/tables/retention_enrichment.tsv`, and is included in `python bin/genefam/run_release_checks.py --outdir results/release_checks`.

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
- The standard identification branch is wired through Nextflow DSL2 for HMMER, DIAMOND, domain filtering, family summaries, family FASTA extraction, MAFFT alignment, FastTree-by-default phylogeny, chromosome locations, optional RNA-seq expression handoff, plotting, and final report assembly.
- `run_nextflow_single_tool_smoke.py` verifies HMMER-only and DIAMOND-only standard routing through Nextflow with `mock_external_tools: false`.
- The prepared-table WGD branch is wired through Nextflow DSL2 for duplicate classification, Ka/Ks-supported WGD layers, gamma/beta/alpha/theta named-event evidence, family event membership, retention summaries, retention enrichment, and final report assembly.
- The local `GeneFamilyFlow` runtime verifies Nextflow, HMMER, DIAMOND, MAFFT, IQ-TREE, MEME, and `/usr/local/bin/R`; Docker/Apptainer remain the current machine-level blocker.
- Docker/Apptainer unblock is documented through `bash results/readiness/runtime_bootstrap.sh`, using `params.container_image`, `params.apptainer_image`, Dockerfile, and the Reference-safe `Apptainer.def`; runtime recovery then finishes with `scripts/run_local_acceptance.sh`.
- The top-level delivery status is written to `results/handoff/handoff_report.md` for humans and `results/handoff/handoff_summary.tsv` for scripts after each release-gate run.
