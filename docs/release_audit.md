# Release Audit

This document maps the original GeneFam-Pipeline goal to current repository evidence, verification commands, and known gaps.

## Verification Commands

Repository-level checks:

```bash
python bin/genefam/run_release_checks.py --outdir results/release_checks
python -m pytest tests -q
python bin/genefam/validate_config.py configs/example.config.yaml --check-paths
python bin/genefam/validate_config.py configs/advanced_modules.example.yaml
python bin/genefam/validate_config.py configs/manifest.example.yaml --check-paths
python bin/genefam/run_species_selection_smoke.py \
  --config configs/manifest.example.yaml \
  --groups configs/species_groups.yaml \
  --outdir results/species_manifest_selection_smoke
python bin/genefam/run_mock_mvp.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/mock_mvp
python bin/genefam/run_standard_smoke.py \
  --config configs/example.config.yaml \
  --groups configs/species_groups.yaml \
  --mock-evidence-dir tests/fixtures/mock_evidence \
  --outdir results/standard_smoke
python bin/genefam/run_promoter_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/promoter_smoke
python bin/genefam/run_gene_family_info_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/gene_family_info_smoke
python bin/genefam/run_promoter_cis_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/promoter_cis_smoke
python bin/genefam/run_feature_summary_smoke.py \
  --domains results/domain_filter_smoke/tables/filtered_domains.tsv \
  --motifs results/motif_smoke/tables/motif_summary.tsv \
  --gene-structures results/gene_structure_smoke/tables/gene_structure_summary.tsv \
  --synteny results/synteny_smoke/tables/syntenic_pairs.tsv \
  --promoters results/promoter_smoke/tables/promoters.bed \
  --r-bin /usr/local/bin/R \
  --outdir results/feature_summary_smoke
python bin/genefam/run_tree_feature_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/tree_feature_smoke
python bin/genefam/run_mcscanx_circlize_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/mcscanx_circlize_smoke
python bin/genefam/run_ppi_ggnetview_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/ppi_ggnetview_smoke
python bin/genefam/run_ppi_ggnetview_plot_smoke.py \
  --r-bin /usr/local/bin/R \
  --outdir results/ppi_ggnetview_plot_smoke
python bin/genefam/run_wgd_smoke.py \
  --events-config configs/wgd_events.brassicaceae.yaml \
  --outdir results/wgd_smoke
python bin/genefam/run_nextflow_smoke.py --outdir results/nextflow_smoke
python bin/genefam/run_nextflow_single_tool_smoke.py \
  --conda-env GeneFamilyFlow \
  --outdir results/nextflow_single_tool_smoke
python bin/genefam/run_nextflow_standard_smoke.py \
  --conda-env GeneFamilyFlow \
  --config configs/manifest.example.yaml \
  --outdir results/nextflow_standard_manifest_smoke
python bin/genefam/validate_config.py \
  configs/publication_modules.example.yaml \
  --check-paths
python bin/genefam/run_nextflow_standard_smoke.py \
  --conda-env GeneFamilyFlow \
  --config configs/publication_modules.example.yaml \
  --outdir results/nextflow_standard_feature_smoke
python bin/genefam/run_nextflow_wgd_smoke.py --outdir results/nextflow_wgd_smoke
python bin/genefam/run_nextflow_wgd_smoke.py \
  --conda-env GeneFamilyFlow \
  --mode raw-mcscanx-kaks \
  --outdir results/nextflow_wgd_raw_smoke
python bin/genefam/run_prepared_wgd_handoff_example.py \
  --conda-env GeneFamilyFlow \
  --example-dir examples/prepared_wgd_handoff \
  --outdir results/example_prepared_wgd
python bin/genefam/run_quickstart.py \
  --conda-env GeneFamilyFlow \
  --outdir results/quickstart
python bin/genefam/run_container_profile_smoke.py --profile docker \
  --conda-env GeneFamilyFlow \
  --outdir results/container_profile_smoke/docker
python bin/genefam/run_container_profile_smoke.py --profile apptainer \
  --conda-env GeneFamilyFlow \
  --outdir results/container_profile_smoke/apptainer
PATH="/Users/liuyue/miniforge3/envs/GeneFamilyFlow/bin:$PATH" nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile activated \
  --config configs/example.config.yaml \
  --run_duplication_retention true \
  --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv \
  --family_members examples/prepared_wgd_handoff/family_candidates.tsv \
  --kaks_pairs examples/prepared_wgd_handoff/kaks_pairs.tsv \
  --events_config configs/wgd_events.brassicaceae.yaml \
  --ks_bins 0.3,0.8,1.5 \
  --wgd_event_args "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta" \
  --outdir results/example_prepared_wgd
python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv
python bin/genefam/plan_runtime_bootstrap.py \
  --readiness results/readiness/command_readiness.tsv \
  --outdir results/readiness
python bin/genefam/audit_container_materials.py \
  --outdir results/container_materials
python bin/genefam/audit_objective_completion.py \
  --release-checks results/release_checks/release_checks.tsv \
  --readiness results/readiness/command_readiness.tsv \
  --outdir results/objective_audit
python bin/genefam/audit_reference_governance.py \
  --outdir results/reference_governance
python bin/genefam/audit_publication_report.py \
  --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv \
  --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv \
  --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv \
  --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md \
  --report-index results/nextflow_wgd_smoke/wgd/report/report_index.tsv \
  --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv \
  --out-md results/publication_report_audit/wgd_publication_report_audit.md
```

The standard report-scale visualization smoke is YAML-driven by `configs/publication_modules.example.yaml`; it enables `modules.feature_summary`, `modules.synteny` with `plotting.syntenic_pairs`, `modules.promoter_cis`, `modules.ppi`, and `modules.expression` without repeating those inputs as manual CLI switches.

The readiness audit writes `requirement=required|optional` for each command. It may exit non-zero when required core analysis commands are missing; optional container-stage commands such as Docker and Apptainer stay visible as missing rows without blocking analysis-flow MVP validation. Inspect the TSV for exact missing tools and use the bootstrap planner to generate next-step commands.

The release checks runner writes:

- `results/release_checks/release_checks.tsv`
- `results/release_checks/release_checks.md`
- `results/r_runtime_health/r_runtime_health.tsv`
- `results/r_runtime_health/r_runtime_health.md`
- `results/readiness/runtime_bootstrap_plan.md`
- `results/readiness/runtime_bootstrap.sh`
- `results/container_materials/container_materials.tsv`
- `results/container_materials/container_materials.md`
- `results/objective_audit/objective_audit.tsv`
- `results/objective_audit/objective_audit.md`
- `results/reference_governance/reference_governance.tsv`
- `results/reference_governance/reference_governance.md`
- `results/promoter_smoke/tables/promoters.bed`
- `results/promoter_smoke/sequences/promoters.fa`
- `results/promoter_smoke/plots/feature_summary.pdf`
- `results/gene_family_info_smoke/tables/gene_family_copy_number.tsv`
- `results/gene_family_info_smoke/tables/gene_family_copy_number_summary.tsv`
- `results/gene_family_info_smoke/tables/gene_family_pangenome_summary.tsv`
- `results/gene_family_info_smoke/tables/gene_family_protein_properties.tsv`
- `results/gene_family_info_smoke/plots/gene_family_info_summary.pdf`
- `results/gene_family_info_smoke/plots/gene_family_info_summary.png`
- `results/promoter_cis_smoke/tables/promoter_cis_elements.tsv`
- `results/promoter_cis_smoke/tables/promoter_cis_gene_matrix.tsv`
- `results/promoter_cis_smoke/tables/promoter_cis_category_summary.tsv`
- `results/promoter_cis_smoke/plots/promoter_cis_elements.pdf`
- `results/promoter_cis_smoke/plots/promoter_cis_elements.png`
- `results/feature_summary_smoke/tables/feature_summary.tsv`
- `results/feature_summary_smoke/plots/feature_summary.pdf`
- `results/feature_summary_smoke/plots/feature_summary.png`
- `results/tree_feature_smoke/tables/tree_feature_matrix.tsv`
- `results/tree_feature_smoke/plots/tree_features.pdf`
- `results/tree_feature_smoke/plots/tree_features.png`
- `results/mcscanx_circlize_smoke/tables/circlize_chromosomes.tsv`
- `results/mcscanx_circlize_smoke/tables/circlize_links.tsv`
- `results/mcscanx_circlize_smoke/tables/circlize_skipped_links.tsv`
- `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.pdf`
- `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.png`
- `results/ppi_ggnetview_smoke/ppi_ggnetview_smoke.tsv`
- `results/ppi_ggnetview_smoke/ppi_ggnetview_smoke.md`
- `results/ppi_ggnetview_plot_smoke/tables/ppi_edges.tsv`
- `results/ppi_ggnetview_plot_smoke/tables/ppi_nodes.tsv`
- `results/ppi_ggnetview_plot_smoke/tables/ppi_hubs.tsv`
- `results/ppi_ggnetview_plot_smoke/tables/ppi_ggnetview_status.tsv`
- `results/ppi_ggnetview_plot_smoke/plots/ppi_ggnetview.pdf`
- `results/ppi_ggnetview_plot_smoke/plots/ppi_ggnetview.png`
- `results/nextflow_standard_feature_smoke/standard/tables/feature_summary.tsv`
- `results/nextflow_standard_feature_smoke/standard/plots/feature_summary.pdf`
- `results/nextflow_standard_feature_smoke/standard/plots/feature_summary.png`
- `results/nextflow_standard_feature_smoke/standard/tables/circlize_chromosomes.tsv`
- `results/nextflow_standard_feature_smoke/standard/tables/circlize_links.tsv`
- `results/nextflow_standard_feature_smoke/standard/tables/circlize_skipped_links.tsv`
- `results/nextflow_standard_feature_smoke/standard/plots/mcscanx_circlize.pdf`
- `results/nextflow_standard_feature_smoke/standard/plots/mcscanx_circlize.png`
- `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/syntenic_pairs.tsv`
- `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/duplicate_types.tsv`
- `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/normalized_kaks.tsv`
- `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/kaks_pairs.tsv`
- `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/mcscanx_kaks_handoff.md`
- `results/nextflow_wgd_smoke/wgd/plots/ks_distribution.pdf`
- `results/nextflow_wgd_smoke/wgd/plots/ks_distribution.png`
- `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.pdf`
- `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.png`
- `results/duplicate_type_kaks_smoke/tables/duplicate_type_kaks.tsv`
- `results/duplicate_type_kaks_smoke/tables/duplicate_type_kaks_summary.tsv`
- `results/duplicate_type_kaks_smoke/plots/duplicate_type_kaks.pdf`
- `results/duplicate_type_kaks_smoke/plots/duplicate_type_kaks.png`
- `results/pangenome_kaks_smoke/tables/pangenome_kaks.tsv`
- `results/pangenome_kaks_smoke/tables/pangenome_kaks_summary.tsv`
- `results/pangenome_kaks_smoke/plots/pangenome_kaks.pdf`
- `results/pangenome_kaks_smoke/plots/pangenome_kaks.png`
- `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv`
- `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.md`
- `results/container_profile_smoke/docker/container_profile_smoke.tsv`
- `results/container_profile_smoke/docker/container_profile_smoke.md`
- `results/container_profile_smoke/apptainer/container_profile_smoke.tsv`
- `results/container_profile_smoke/apptainer/container_profile_smoke.md`
- `results/handoff/handoff_report.md`
- `results/handoff/handoff_summary.tsv`
- `results/publication_report_audit/publication_report_audit.tsv`
- `results/publication_report_audit/publication_report_audit.md`
- `results/publication_report_audit/wgd_publication_report_audit.tsv`
- `results/publication_report_audit/wgd_publication_report_audit.md`
- `results/delivery_bundle/delivery_manifest.tsv`
- `results/delivery_bundle/delivery_bundle.md`
- `results/delivery_bundle/figure_gallery.tsv`
- `results/delivery_bundle/figure_gallery.md`

The delivery manifest includes a `final_stage_blocker` row. For the current analysis-flow MVP, that row is `blocked` only when objective-audit evidence shows a remaining external packaging/runtime blocker such as missing Docker/Apptainer commands; it is the first machine-readable place to check after the release gate reports zero required failures. The delivery manifest also exposes baseline smoke handoff rows for `mock_mvp`, `nextflow_mock_mvp_smoke`, `nextflow_single_tool_smoke`, and `delivery_bundle_figure_gallery_smoke`, so the final user-facing index links back to the Python baseline, Nextflow baseline, single-tool routing, and delivery-gallery bundle smoke evidence. The delivery manifest exposes `r_runtime_health` as a required handoff row pointing to `results/r_runtime_health/r_runtime_health.md`, so `/usr/local/bin/R` startup health stays visible in the final user-facing bundle. The delivery manifest audit verifies both filesystem paths and required handoff items, including `r_runtime_health`, `standard_report_index_audit`, and `wgd_report_index_audit`, which makes accidental removal of runtime, baseline, or report-index closure rows release-visible. The delivery bundle also writes a global paper-level figure gallery so users can navigate every standard and WGD figure to PDF and PNG plot targets through `plot_path` and `plot_png_path`, close-reading interpretation through per-figure close-reading anchors, software/R package version table, final report context, and `figure_traceability_matrix` anchor. The release gate runs `bin/genefam/audit_figure_gallery.py` after the gallery smoke and writes `results/delivery_bundle_smoke/figure_gallery_audit.tsv` plus `results/delivery_bundle_smoke/figure_gallery_audit.md` to prove plot_manifest coverage for the standard and WGD report manifests, to prove every gallery row links to real PDF and PNG plot targets, close-reading, version, report, and traceability targets, to enforce valid gallery plot file signatures for PDF/PNG/SVG targets, to enforce per-figure close-reading anchors for `figure_interpretations.md#plot_key`, and to run `figure_gallery_traceability_targets`, which requires each gallery `traceability_matrix` value to point to that row's `final_report.md#figure-traceability-matrix`.

The WGD publication report audit now expects complete per-figure close-reading text for the WGD plot family instead of one generic Ka/Ks paragraph. The `ks_distribution` interpretation must call out Ks bin boundaries, event labels, pair counts, and synteny/phylogeny support before naming gamma/beta/alpha/theta layers. The `duplicate_type_kaks` interpretation must call out duplicate class assignments, skipped pairs, and per-class sample sizes. The `pangenome_kaks` interpretation must call out pangenome class thresholds, skipped pairs, and class sample sizes. The final report audit also requires valid plot file signatures, `report_index_plot_variants` PDF/PNG plot variants, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, result-statement interpretation narratives, including QC warnings and reading status, rather than instructional prompts, a `final_report_methods_summary` check that the `Methods Summary` names HMMER, DIAMOND, MCScanX, Ka/Ks, gamma, beta, alpha, theta, and points to software versions, a `Figure Traceability Matrix` linking each plot to interpretation status, QC tables and warnings, software/R package versions, parseable detected version values, `software_version_detection_warnings_visible` evidence for non-detected version rows such as `version_not_detected`, per-figure method/software version coverage, and reproducibility commands.

The standard publication report audit also expects complete per-figure close-reading text for the family information plot family. The `family_counts` interpretation must focus on selected species and member totals before expansion/contraction interpretation. The `gene_family_info_summary` interpretation must focus on copy-number balance, species order, pangenome calls, and protein-property summaries so it is not collapsed into the simpler count overview.

For the standard report, all standard registered figures must now carry `figure-specific close reading` in `results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv`; no `template-guided close reading` status remains for the standard plot manifest.

The standard report index audit and WGD report index audit are run by `bin/genefam/audit_report_index.py`. These checks make sure report indexes expose plot manifests, software versions, figure interpretations in TSV/Markdown, final reports, and figure_traceability_matrix anchors, including `figure_interpretations.md`, `final_report.md`, and `final_report.md#figure-traceability-matrix`, so users can navigate the whole report package from `report_index.tsv`. The `report_index_traceability_anchor` check specifically requires `figure_traceability_matrix` to point to the same file as `final_report` with the `#figure-traceability-matrix` anchor, not to a detached Markdown page. They also verify that all available indexed report paths exist, not only the core report artifacts.

The Markdown summary reports `Required failed` and `Optional failed` separately. `R runtime health` is a required early diagnostic generated by `bin/genefam/check_r_runtime.py`; it runs `/usr/local/bin/R` before the R plotting smokes and writes `results/r_runtime_health/r_runtime_health.tsv` plus `results/r_runtime_health/r_runtime_health.md`, so a killed or missing R runtime is visible before downstream visualization failures. The long objective audit uses that release-check row together with the command-readiness row, so `/usr/local/bin/R plotting` is blocked unless the path exists and R startup health passes. Container profile smoke checks are optional evidence; the required readiness audit remains the release-blocking signal while Docker/Apptainer are unavailable.

## Requirement Audit

| Requirement | Evidence | Verification |
|---|---|---|
| Nextflow DSL2 workflow | `workflows/main.nf`; modules under `workflows/modules/`; standard branch calls `RUN_ALIGNMENT`, `RUN_PHYLOGENY`, optional `EXTRACT_PROMOTERS`, optional `PLOT_FEATURE_SUMMARY`, and optional `PLOT_MCSCANX_CIRCLIZE`; `bin/genefam/run_nextflow_smoke.py`; `bin/genefam/run_nextflow_standard_smoke.py`; `bin/genefam/run_nextflow_single_tool_smoke.py`; `results/nextflow_smoke/nextflow_smoke.md`; `results/nextflow_standard_manifest_smoke/nextflow_standard_smoke.tsv`; `results/nextflow_standard_feature_smoke/nextflow_standard_smoke.tsv`; `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv` | `python -m pytest tests/test_workflow_modules.py tests/test_run_nextflow_smoke.py tests/test_run_nextflow_standard_smoke.py tests/test_run_nextflow_single_tool_smoke.py -q` |
| YAML-driven parameters | `configs/example.config.yaml`; `configs/advanced_modules.example.yaml`; `configs/manifest.example.yaml`; `tests/fixtures/species_manifest.tsv`; `bin/genefam/build_run_plan.py`; `bin/genefam/run_species_selection_smoke.py`; `results/species_selection_smoke/tables/species_manifest.tsv`; `results/species_selection_smoke/tables/run_plan.tsv`; `results/species_manifest_selection_smoke/tables/species_manifest.tsv`; `results/species_manifest_selection_smoke/species_selection_smoke.md` | `python bin/genefam/run_species_selection_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --outdir results/species_selection_smoke`, `python bin/genefam/run_species_selection_smoke.py --config configs/manifest.example.yaml --groups configs/species_groups.yaml --outdir results/species_manifest_selection_smoke`, and `python bin/genefam/build_run_plan.py --config configs/example.config.yaml --out results/mock_mvp/tables/run_plan.tsv` |
| GeneFamilyFlow runtime | `envs/GeneFamilyFlow.conda.yaml`; `workflows/nextflow.config`; `Dockerfile` | `python -m pytest tests/test_runtime_environment_files.py -q` |
| `/usr/local/bin/R` plotting and reporting convention | `bin/genefam/check_r_runtime.py`; `results/r_runtime_health/r_runtime_health.tsv`; `results/r_runtime_health/r_runtime_health.md`; `workflows/modules/plots.nf`; `workflows/modules/duplication_retention.nf`; `scripts/plot_family_counts.R`; `scripts/plot_kaks.R`; `scripts/plot_duplicate_type_kaks.R`; `scripts/plot_expression_heatmap.R`; `scripts/plot_feature_summary.R`; `scripts/plot_tree_features.R`; `scripts/plot_mcscanx_circlize.R`; R runtime health release gate before plotting smokes; objective audit requires command readiness plus `R runtime health` before marking `/usr/local/bin/R plotting` achieved | `python bin/genefam/check_r_runtime.py --r-bin /usr/local/bin/R --outdir results/r_runtime_health`, `python -m pytest tests/test_check_r_runtime.py tests/test_workflow_modules.py tests/test_runtime_environment_files.py tests/test_run_feature_summary_smoke.py tests/test_run_tree_feature_smoke.py tests/test_run_promoter_smoke.py tests/test_run_mcscanx_circlize_smoke.py tests/test_run_duplicate_type_kaks_smoke.py tests/test_run_expression_heatmap_smoke.py -q` |
| Docker/Conda reproducible running | `Dockerfile`; `envs/GeneFamilyFlow.conda.yaml`; `envs/GeneFamilyFlow.linux-64.conda.yaml`; `bin/genefam/audit_container_materials.py`; `bin/genefam/plan_runtime_bootstrap.py`; `workflows/nextflow.config` profiles `local`, `docker`, `apptainer`; `results/container_materials/container_materials.tsv`; `results/container_materials/container_materials.md`; Dockerfile default standard smoke output `results/container_default_smoke` | `python bin/genefam/audit_container_materials.py --outdir results/container_materials`, `python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv`, and `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` |
| container profile smoke verification | `bin/genefam/run_container_profile_smoke.py`; `workflows/nextflow.config` profiles `docker`, `apptainer`; `results/container_profile_smoke/docker/container_profile_smoke.md`; `results/container_profile_smoke/apptainer/container_profile_smoke.md` | `python bin/genefam/run_container_profile_smoke.py --profile docker --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/docker` and `python bin/genefam/run_container_profile_smoke.py --profile apptainer --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/apptainer` |
| long objective completion audit | `bin/genefam/audit_objective_completion.py`; `results/objective_audit/objective_audit.tsv`; `results/objective_audit/objective_audit.md` | `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` |
| history and Reference governance | `HISTORY.md`; `.gitignore`; `Reference/`; `bin/genefam/audit_reference_governance.py`; `results/reference_governance/reference_governance.tsv`; `results/reference_governance/reference_governance.md`; `Reference/` is ignored by `.gitignore`; tracked `Reference/` changes are release-blocking; audit Markdown reports `Reference/ ignored` and explains that Reference/ must also be ignored so paper PDFs, source data, and plotting templates are not accidentally staged | `python bin/genefam/audit_reference_governance.py --outdir results/reference_governance` and `python -m pytest tests/test_audit_reference_governance.py -q` |
| quickstart handoff for users | `bin/genefam/run_quickstart.py`; `bin/genefam/run_delivery_bundle.py`; `bin/genefam/audit_publication_report.py`; `bin/genefam/audit_report_index.py`; `bin/genefam/audit_figure_gallery.py`; `bin/genefam/audit_delivery_manifest.py`; `docs/quickstart.md`; `README.md`; `results/quickstart/quickstart_summary.md`; `results/r_runtime_health/r_runtime_health.md`; `results/publication_report_audit/publication_report_audit.tsv`; `results/publication_report_audit/publication_report_audit.md`; `results/publication_report_audit/wgd_publication_report_audit.tsv`; `results/publication_report_audit/wgd_publication_report_audit.md`; `results/report_index_audit/standard_report_index_audit.tsv`; `results/report_index_audit/standard_report_index_audit.md`; `results/report_index_audit/wgd_report_index_audit.tsv`; `results/report_index_audit/wgd_report_index_audit.md`; `results/delivery_bundle/delivery_manifest.tsv`; `results/delivery_bundle/delivery_bundle.md`; `results/delivery_bundle/figure_gallery.tsv`; `results/delivery_bundle/figure_gallery.md`; `results/delivery_bundle_smoke/figure_gallery_audit.tsv`; `results/delivery_bundle_smoke/figure_gallery_audit.md`; `results/delivery_bundle_smoke/delivery_manifest_audit.tsv`; `results/delivery_bundle_smoke/delivery_manifest_audit.md`; `results/delivery_bundle/final_delivery_manifest_audit.tsv`; `results/delivery_bundle/final_delivery_manifest_audit.md`; `results/release_checks/release_checks.md`; `results/mock_mvp/report/final_report.md`; `results/nextflow_smoke/nextflow_smoke.md`; `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv`; `results/delivery_bundle_smoke/delivery_bundle_smoke.md`; `results/standard_smoke/report/final_report.md`; `results/example_prepared_wgd/report/final_report.md`; `mock_mvp`; `nextflow_mock_mvp_smoke`; `nextflow_single_tool_smoke`; `delivery_bundle_figure_gallery_smoke`; `r_runtime_health` delivery-manifest row; `reference_gitignore` delivery-manifest row; standard and WGD publication report audits for valid plot file signatures, `report_index_plot_variants` PDF/PNG plot variants, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, complete per-figure close-reading text, result-statement interpretation narratives, including QC warnings and reading status, rather than instructional prompts, QC tables and warnings, software/R package versions, parseable detected version values, `software_version_detection_warnings_visible` evidence for version-not-detected rows, `final_report_methods_summary` Methods Summary coverage, per-figure method/software version coverage, and reproducibility commands; standard report index audit and WGD report index audit for report indexes expose plot manifests, software versions, figure interpretations in TSV/Markdown, final reports, and figure_traceability_matrix anchors, and verify that all available indexed report paths exist; global paper-level figure gallery in TSV/Markdown links each standard/WGD figure to plot files, close reading through per-figure close-reading anchors, software/R package versions, final report context, and traceability matrix; figure gallery audit verifies every gallery target exists, enforces valid gallery plot file signatures, enforces per-figure close-reading anchors, and runs `figure_gallery_traceability_targets` to require final-report traceability anchors; delivery manifest audit verifies release-gate smoke paths including R runtime health; `final_delivery_manifest_audit` verifies available and blocked paths in the final `results/delivery_bundle/delivery_manifest.tsv`; Reference/ ignored so paper PDFs, source data, and plotting templates are not accidentally staged | `python bin/genefam/run_quickstart.py --conda-env GeneFamilyFlow --outdir results/quickstart`, `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle`, `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv --figure-interpretations results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv --software-versions results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv --final-report results/nextflow_standard_feature_smoke/standard/report/final_report.md --report-index results/nextflow_standard_feature_smoke/standard/report/report_index.tsv --out-tsv results/publication_report_audit/publication_report_audit.tsv --out-md results/publication_report_audit/publication_report_audit.md`, `python bin/genefam/audit_publication_report.py --plot-manifest results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv --figure-interpretations results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv --software-versions results/nextflow_wgd_smoke/wgd/report/software_versions.tsv --final-report results/nextflow_wgd_smoke/wgd/report/final_report.md --report-index results/nextflow_wgd_smoke/wgd/report/report_index.tsv --out-tsv results/publication_report_audit/wgd_publication_report_audit.tsv --out-md results/publication_report_audit/wgd_publication_report_audit.md`, `python bin/genefam/audit_report_index.py --report-index results/nextflow_standard_feature_smoke/standard/report/report_index.tsv --profile standard --out-tsv results/report_index_audit/standard_report_index_audit.tsv --out-md results/report_index_audit/standard_report_index_audit.md`, `python bin/genefam/audit_report_index.py --report-index results/nextflow_wgd_smoke/wgd/report/report_index.tsv --profile wgd --out-tsv results/report_index_audit/wgd_report_index_audit.tsv --out-md results/report_index_audit/wgd_report_index_audit.md`, `python bin/genefam/audit_figure_gallery.py --figure-gallery results/delivery_bundle/figure_gallery.tsv --out-tsv results/delivery_bundle_smoke/figure_gallery_audit.tsv --out-md results/delivery_bundle_smoke/figure_gallery_audit.md`, `python bin/genefam/audit_delivery_manifest.py --delivery-manifest results/delivery_bundle/delivery_manifest.tsv --out-tsv results/delivery_bundle_smoke/delivery_manifest_audit.tsv --out-md results/delivery_bundle_smoke/delivery_manifest_audit.md`, and `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` |
| species bank input model | `docs/input_contract.md`; `bin/genefam/discover_species.py`; `bin/genefam/run_species_selection_smoke.py`; `tests/fixtures/species_bank`; `tests/fixtures/species_manifest.tsv`; `configs/manifest.example.yaml`; `results/species_selection_smoke/tables/species_manifest.tsv`; `results/species_manifest_selection_smoke/tables/species_manifest.tsv` | `python bin/genefam/run_species_selection_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --outdir results/species_selection_smoke`, `python bin/genefam/run_species_selection_smoke.py --config configs/manifest.example.yaml --groups configs/species_groups.yaml --outdir results/species_manifest_selection_smoke`, and `python -m pytest tests/test_discover_species.py -q` |
| target species selection | `configs/species_groups.yaml`; `species.include`; `species.exclude`; `run.species_group`; `results/species_selection_smoke/tables/run_plan.tsv` | `python bin/genefam/run_species_selection_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --outdir results/species_selection_smoke` and `python -m pytest tests/test_discover_species.py tests/test_build_run_plan.py tests/test_run_species_selection_smoke.py -q` |
| standard identification branch | `workflows/main.nf`; `workflows/modules/identification_inputs.nf`; `workflows/modules/standard_postprocess.nf`; `workflows/modules/annotation_integration.nf`; `workflows/modules/alignment_phylogeny.nf`; `workflows/nextflow.config` `params.meme_txt`, `params.tree_builder = "fasttree"`, and `params.expression_metadata`; `tests/fixtures/mock_evidence/meme.txt`; `tests/fixtures/expression/family_expression.tsv`; `tests/fixtures/expression/sample_metadata.tsv`; `bin/genefam/build_identification_inputs.py`; `bin/genefam/build_run_config_snapshot.py`; `bin/genefam/build_wgd_handoff_manifest.py`; `bin/genefam/extract_family_sequences.py`; `bin/genefam/extract_gene_structure.py`; `bin/genefam/run_gene_structure_smoke.py`; `bin/genefam/extract_chromosome_locations.py`; `bin/genefam/subset_expression_matrix.py`; `bin/genefam/build_expression_summary.py`; `bin/genefam/parse_meme_motifs.py`; `bin/genefam/build_standard_report_index.py`; `bin/genefam/assemble_report.py`; `bin/genefam/run_standard_smoke.py`; `bin/genefam/run_nextflow_single_tool_smoke.py`; `bin/genefam/concat_tsv.py`; full standard Nextflow smoke expects `alignment/GDSL.mafft.aln.faa` and `phylogeny/GDSL.fasttree.treefile`; report index keys include `alignment_file`, `phylogeny_tree`, `expression_sample_metadata`, `expression_group_matrix`, and `expression_gene_summary`; `results/standard_smoke/tables/run_config_snapshot.tsv`; `results/standard_smoke/tables/wgd_handoff_manifest.tsv`; `results/standard_smoke/tables/gene_structure_summary.tsv`; `results/gene_structure_smoke/tables/gene_structure_summary.tsv`; `results/standard_smoke/tables/chromosome_locations.tsv`; `results/standard_smoke/tables/motif_summary.tsv`; `results/standard_expression_smoke/tables/family_expression.tsv`; `results/standard_expression_smoke/tables/expression_sample_metadata.tsv`; `results/standard_expression_smoke/tables/expression_group_matrix.tsv`; `results/standard_expression_smoke/tables/expression_gene_summary.tsv`; `results/standard_expression_smoke/plots/expression_heatmap.pdf`; `results/standard_expression_smoke/plots/expression_heatmap.png`; `results/standard_smoke/report/final_report.md`; `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv` | `python -m pytest tests/test_build_identification_inputs.py tests/test_build_run_config_snapshot.py tests/test_build_wgd_handoff_manifest.py tests/test_concat_tsv.py tests/test_extract_family_sequences.py tests/test_extract_gene_structure.py tests/test_run_gene_structure_smoke.py tests/test_extract_chromosome_locations.py tests/test_subset_expression_matrix.py tests/test_build_expression_summary.py tests/test_parse_meme_motifs.py tests/test_standard_branch_report_index.py tests/test_assemble_report.py tests/test_run_standard_smoke.py tests/test_run_expression_heatmap_smoke.py tests/test_run_nextflow_single_tool_smoke.py tests/test_workflow_modules.py tests/test_runtime_environment_files.py -q` |
| HMMER family identification | `workflows/modules/hmmer_search.nf`; `bin/genefam/parse_hmmer_domtbl.py`; `bin/genefam/filter_hmmer_domains.py` | `python -m pytest tests/test_parse_hmmer_domtbl.py tests/test_filter_hmmer_domains.py -q` |
| DIAMOND confirmation | `workflows/modules/diamond_search.nf`; `bin/genefam/parse_diamond_outfmt6.py` | `python -m pytest tests/test_parse_diamond_outfmt6.py -q` |
| domain filtering | `bin/genefam/filter_hmmer_domains.py`; `bin/genefam/run_domain_filter_smoke.py`; `workflows/modules/domain_filter.nf`; `tests/fixtures/hmmer_domains/domains.tsv`; `results/domain_filter_smoke/tables/filtered_domains.tsv` | `python bin/genefam/run_domain_filter_smoke.py --input tests/fixtures/hmmer_domains/domains.tsv --max-evalue 1e-10 --min-bitscore 50 --min-domain-coverage 0.5 --outdir results/domain_filter_smoke` and `python -m pytest tests/test_filter_hmmer_domains.py tests/test_merge_identification_evidence.py -q` |
| family member summary | `bin/genefam/summarize_family.py`; `workflows/modules/family_summary.nf` | `python -m pytest tests/test_summarize_family.py -q` |
| gene family information and copy-number visualization | `bin/genefam/build_gene_family_info.py`; `bin/genefam/run_gene_family_info_smoke.py`; `scripts/plot_gene_family_info.R`; `workflows/modules/plots.nf` `PLOT_GENE_FAMILY_INFO`; per-species copy-number classes; pan/core/dispensable presence summary; protein length, molecular weight, pI, and GRAVY summaries; `results/gene_family_info_smoke/tables/gene_family_copy_number.tsv`; `results/gene_family_info_smoke/tables/gene_family_copy_number_summary.tsv`; `results/gene_family_info_smoke/tables/gene_family_pangenome_summary.tsv`; `results/gene_family_info_smoke/tables/gene_family_protein_properties.tsv`; `results/gene_family_info_smoke/plots/gene_family_info_summary.pdf`; `results/gene_family_info_smoke/plots/gene_family_info_summary.png` | `python bin/genefam/run_gene_family_info_smoke.py --r-bin /usr/local/bin/R --outdir results/gene_family_info_smoke` and `python -m pytest tests/test_build_gene_family_info.py tests/test_run_gene_family_info_smoke.py tests/test_workflow_modules.py -q` |
| gene structure | `bin/genefam/extract_gene_structure.py`; `bin/genefam/run_gene_structure_smoke.py`; `results/gene_structure_smoke/tables/gene_structure_summary.tsv`; `workflows/modules/annotation_integration.nf` | `python bin/genefam/run_gene_structure_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/gene_structure_smoke` and `python -m pytest tests/test_extract_gene_structure.py tests/test_run_gene_structure_smoke.py tests/test_workflow_modules.py -q` |
| alignment | `bin/genefam/prepare_alignment_inputs.py`; `bin/genefam/run_alignment_phylogeny_smoke.py`; `tests/fixtures/alignment/family_members.faa`; `results/alignment_phylogeny_smoke/tables/alignment_manifest.tsv`; `workflows/modules/alignment_phylogeny.nf` | `python bin/genefam/run_alignment_phylogeny_smoke.py --family-name GDSL --fasta tests/fixtures/alignment/family_members.faa --aligner mafft --tree-builder fasttree --outdir results/alignment_phylogeny_smoke` and `python -m pytest tests/test_prepare_alignment_inputs.py tests/test_run_alignment_phylogeny_smoke.py tests/test_workflow_modules.py -q` |
| phylogeny | `bin/genefam/prepare_phylogeny_inputs.py`; `bin/genefam/run_alignment_phylogeny_smoke.py`; `results/alignment_phylogeny_smoke/tables/phylogeny_manifest.tsv`; `workflows/modules/alignment_phylogeny.nf`; FastTree branch for large multi-species family trees; IQ-TREE branch retained for model-selection/bootstrap runs | `python bin/genefam/run_alignment_phylogeny_smoke.py --family-name GDSL --fasta tests/fixtures/alignment/family_members.faa --aligner mafft --tree-builder fasttree --outdir results/alignment_phylogeny_smoke` and `python -m pytest tests/test_prepare_phylogeny_inputs.py tests/test_run_alignment_phylogeny_smoke.py tests/test_workflow_modules.py -q` |
| motif | `bin/genefam/parse_meme_motifs.py`; `bin/genefam/run_motif_smoke.py`; `tests/fixtures/mock_evidence/meme.txt`; `results/motif_smoke/tables/motif_summary.tsv`; `workflows/modules/alignment_phylogeny.nf` | `python bin/genefam/run_motif_smoke.py --meme-txt tests/fixtures/mock_evidence/meme.txt --family-name GDSL --outdir results/motif_smoke` and `python -m pytest tests/test_parse_meme_motifs.py tests/test_workflow_modules.py -q` |
| tree motif gene-structure domain composite visualization | `bin/genefam/build_tree_feature_matrix.py`; per-gene `motif_architecture` and `domain_architecture` columns; `bin/genefam/run_tree_feature_smoke.py`; `scripts/plot_tree_features.R`; `workflows/modules/plots.nf` `PLOT_TREE_FEATURES`; `results/tree_feature_smoke/tables/tree_feature_matrix.tsv`; `results/tree_feature_smoke/plots/tree_features.pdf`; `results/tree_feature_smoke/plots/tree_features.png`; `results/nextflow_standard_smoke/standard/tables/tree_feature_matrix.tsv`; `results/nextflow_standard_smoke/standard/plots/tree_features.pdf`; `results/nextflow_standard_smoke/standard/plots/tree_features.png` | `python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke` and `python -m pytest tests/test_build_tree_feature_matrix.py tests/test_run_tree_feature_smoke.py tests/test_workflow_modules.py -q` |
| synteny | `bin/genefam/parse_mcscanx_collinearity.py`; `bin/genefam/build_mcscanx_kaks_handoff.py`; `bin/genefam/run_synteny_smoke.py`; `tests/fixtures/mcscanx/sample.collinearity`; `results/synteny_smoke/tables/syntenic_pairs.tsv`; `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/syntenic_pairs.tsv`; `workflows/modules/duplication_retention.nf` `PREPARE_MCSCANX_KAKS_HANDOFF` and prepared-table branch | `python bin/genefam/run_synteny_smoke.py --collinearity tests/fixtures/mcscanx/sample.collinearity --outdir results/synteny_smoke`, `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --mode raw-mcscanx-kaks --outdir results/nextflow_wgd_raw_smoke`, and `python -m pytest tests/test_parse_mcscanx_collinearity.py tests/test_build_mcscanx_kaks_handoff.py tests/test_workflow_modules.py -q` |
| MCScanX circlize visualization | `bin/genefam/build_circlize_inputs.py`; `bin/genefam/run_mcscanx_circlize_smoke.py`; `scripts/plot_mcscanx_circlize.R`; `circlize` R package; `workflows/modules/plots.nf` `PLOT_MCSCANX_CIRCLIZE`; `results/mcscanx_circlize_smoke/tables/circlize_chromosomes.tsv`; `results/mcscanx_circlize_smoke/tables/circlize_links.tsv`; `results/mcscanx_circlize_smoke/tables/circlize_skipped_links.tsv`; `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.pdf`; `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.png`; `results/nextflow_standard_feature_smoke/standard/plots/mcscanx_circlize.pdf`; `results/nextflow_standard_feature_smoke/standard/plots/mcscanx_circlize.png` | `python bin/genefam/run_mcscanx_circlize_smoke.py --r-bin /usr/local/bin/R --outdir results/mcscanx_circlize_smoke`, `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --config configs/publication_modules.example.yaml --outdir results/nextflow_standard_feature_smoke`, and `python -m pytest tests/test_build_circlize_inputs.py tests/test_run_mcscanx_circlize_smoke.py tests/test_run_nextflow_standard_smoke.py -q` |
| standard-to-WGD prepared handoff | `bin/genefam/run_prepared_wgd_handoff_example.py`; `bin/genefam/build_mcscanx_kaks_handoff.py`; `docs/standard_to_wgd_handoff.md`; `examples/prepared_wgd_handoff/`; `examples/prepared_wgd_handoff/family_candidates.tsv`; `examples/prepared_wgd_handoff/duplicate_types.tsv`; `examples/prepared_wgd_handoff/kaks_pairs.tsv`; `results/example_prepared_wgd/report/final_report.md`; `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/duplicate_types.tsv`; `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/kaks_pairs.tsv` | `python -m pytest tests/test_prepared_wgd_handoff_example.py tests/test_build_mcscanx_kaks_handoff.py -q`, `python bin/genefam/run_prepared_wgd_handoff_example.py --conda-env GeneFamilyFlow --example-dir examples/prepared_wgd_handoff --outdir results/example_prepared_wgd`, `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --mode raw-mcscanx-kaks --outdir results/nextflow_wgd_raw_smoke`, and the `--run_duplication_retention true` Nextflow command above |
| duplication retention | `bin/genefam/normalize_duplicate_types.py`; `bin/genefam/join_family_duplicates.py`; `bin/genefam/retention_enrichment.py`; `bin/genefam/run_retention_enrichment_smoke.py`; `examples/prepared_wgd_handoff/family_candidates.tsv`; `examples/prepared_wgd_handoff/duplicate_types.tsv`; `results/retention_enrichment_smoke/tables/normalized_duplicate_types.tsv`; `results/retention_enrichment_smoke/tables/family_duplicate_classification.tsv`; `results/retention_enrichment_smoke/tables/retention_enrichment.tsv` | `python bin/genefam/run_retention_enrichment_smoke.py --family-members examples/prepared_wgd_handoff/family_candidates.tsv --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv --outdir results/retention_enrichment_smoke` and `python -m pytest tests/test_normalize_duplicate_types.py tests/test_join_family_duplicates.py tests/test_retention_enrichment.py tests/test_run_retention_enrichment_smoke.py -q` |
| WGD layer and named event model | `bin/genefam/classify_wgd_layers.py`; `bin/genefam/build_wgd_event_evidence.py`; `bin/genefam/build_wgd_run_config_snapshot.py`; `bin/genefam/run_wgd_smoke.py`; `scripts/plot_kaks.R`; `configs/wgd_events.brassicaceae.yaml`; `results/wgd_smoke/tables/wgd_run_config_snapshot.tsv`; `results/wgd_smoke/report/final_report.md`; `results/nextflow_wgd_smoke/wgd/plots/ks_distribution.pdf`; `results/nextflow_wgd_smoke/wgd/plots/ks_distribution.png`; `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.pdf`; `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.png` | `python -m pytest tests/test_classify_wgd_layers.py tests/test_build_wgd_event_evidence.py tests/test_build_wgd_run_config_snapshot.py tests/test_run_wgd_smoke.py tests/test_run_nextflow_wgd_smoke.py -q` |
| gamma beta alpha theta interpretation | `configs/wgd_events.brassicaceae.yaml`; `docs/wgd_event_evidence.md`; `docs/duplication_retention_design.md`; WGD event names must be unique in the event YAML; WGD event metadata requires name, scope, evidence, and expected_relative_age; Configured WGD event labels must have matching event metadata | `python -m pytest tests/test_build_wgd_event_evidence.py -q` |
| Ka/Ks selection pressure | `bin/genefam/prepare_kaks_pairs.py`; `bin/genefam/parse_kaks_results.py`; `bin/genefam/build_mcscanx_kaks_handoff.py`; `bin/genefam/build_duplicate_type_kaks.py`; `bin/genefam/build_pangenome_kaks.py`; `bin/genefam/run_kaks_smoke.py`; `bin/genefam/run_duplicate_type_kaks_smoke.py`; `bin/genefam/run_pangenome_kaks_smoke.py`; `scripts/plot_kaks.R`; `scripts/plot_duplicate_type_kaks.R`; `scripts/plot_pangenome_kaks.R`; `tests/fixtures/kaks/kaks_calculator.tsv`; `results/kaks_smoke/tables/normalized_kaks.tsv`; `results/duplicate_type_kaks_smoke/tables/duplicate_type_kaks.tsv`; `results/duplicate_type_kaks_smoke/tables/duplicate_type_kaks_summary.tsv`; `results/duplicate_type_kaks_smoke/plots/duplicate_type_kaks.pdf`; `results/duplicate_type_kaks_smoke/plots/duplicate_type_kaks.png`; `results/pangenome_kaks_smoke/tables/pangenome_kaks.tsv`; `results/pangenome_kaks_smoke/tables/pangenome_kaks_summary.tsv`; `results/pangenome_kaks_smoke/plots/pangenome_kaks.pdf`; `results/pangenome_kaks_smoke/plots/pangenome_kaks.png`; `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/normalized_kaks.tsv`; `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/kaks_pairs.tsv`; `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.pdf`; `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.png`; `workflows/modules/duplication_retention.nf` `PREPARE_MCSCANX_KAKS_HANDOFF`, `PLOT_KAKS`, `PLOT_DUPLICATE_TYPE_KAKS`, and `PLOT_PANGENOME_KAKS` | `python bin/genefam/run_kaks_smoke.py --kaks tests/fixtures/kaks/kaks_calculator.tsv --outdir results/kaks_smoke`, `python bin/genefam/run_duplicate_type_kaks_smoke.py --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv --kaks-pairs examples/prepared_wgd_handoff/kaks_pairs.tsv --r-bin /usr/local/bin/R --outdir results/duplicate_type_kaks_smoke`, `python bin/genefam/run_pangenome_kaks_smoke.py --r-bin /usr/local/bin/R --outdir results/pangenome_kaks_smoke`, `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --mode raw-mcscanx-kaks --outdir results/nextflow_wgd_raw_smoke`, and `python -m pytest tests/test_prepare_kaks_pairs.py tests/test_parse_kaks_results.py tests/test_build_mcscanx_kaks_handoff.py tests/test_build_duplicate_type_kaks.py tests/test_build_pangenome_kaks.py tests/test_run_duplicate_type_kaks_smoke.py tests/test_run_pangenome_kaks_smoke.py tests/test_run_nextflow_wgd_smoke.py -q` |
| chromosome location | `bin/genefam/extract_chromosome_locations.py`; `bin/genefam/run_chromosome_smoke.py`; `results/chromosome_smoke/tables/chromosome_locations.tsv`; `workflows/modules/annotation_integration.nf` | `python bin/genefam/run_chromosome_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/chromosome_smoke` and `python -m pytest tests/test_extract_chromosome_locations.py tests/test_workflow_modules.py -q` |
| promoter analysis and visualization | `bin/genefam/extract_promoters.py`; `bin/genefam/run_promoter_smoke.py`; `bin/genefam/summarize_feature_tables.py`; `scripts/plot_feature_summary.R`; `workflows/modules/annotation_integration.nf` `EXTRACT_PROMOTERS`; `results/promoter_smoke/tables/promoters.bed`; `results/promoter_smoke/sequences/promoters.fa`; `results/promoter_smoke/tables/feature_summary.tsv`; `results/promoter_smoke/plots/feature_summary.pdf`; `results/promoter_smoke/plots/feature_summary.png` | `python bin/genefam/run_promoter_smoke.py --r-bin /usr/local/bin/R --outdir results/promoter_smoke` and `python -m pytest tests/test_extract_promoters.py tests/test_run_promoter_smoke.py tests/test_workflow_modules.py -q` |
| promoter cis-element visualization | `bin/genefam/build_promoter_cis_elements.py`; `bin/genefam/run_promoter_cis_smoke.py`; `scripts/plot_promoter_cis_elements.R`; `workflows/modules/plots.nf` `PLOT_PROMOTER_CIS_ELEMENTS`; PlantCARE-style table aliases; `results/promoter_cis_smoke/tables/promoter_cis_elements.tsv`; `results/promoter_cis_smoke/tables/promoter_cis_gene_matrix.tsv`; `results/promoter_cis_smoke/tables/promoter_cis_category_summary.tsv`; `results/promoter_cis_smoke/plots/promoter_cis_elements.pdf`; `results/promoter_cis_smoke/plots/promoter_cis_elements.png` | `python bin/genefam/run_promoter_cis_smoke.py --r-bin /usr/local/bin/R --outdir results/promoter_cis_smoke` and `python -m pytest tests/test_build_promoter_cis_elements.py tests/test_run_promoter_cis_smoke.py tests/test_workflow_modules.py -q` |
| feature statistics and visualization for large gene families | `bin/genefam/summarize_feature_tables.py`; `bin/genefam/run_feature_summary_smoke.py`; `bin/genefam/build_tree_feature_matrix.py`; `bin/genefam/run_tree_feature_smoke.py`; `scripts/plot_feature_summary.R`; `scripts/plot_tree_features.R`; `workflows/modules/plots.nf` `PLOT_FEATURE_SUMMARY` and `PLOT_TREE_FEATURES`; domain hit count and coverage summaries; MEME motif count and site summaries; gene-structure length and exon summaries; tree-ordered feature tracks; MCScanX syntenic pair and block summaries; promoter length and clipping summaries; `results/feature_summary_smoke/tables/feature_summary.tsv`; `results/feature_summary_smoke/plots/feature_summary.pdf`; `results/feature_summary_smoke/plots/feature_summary.png`; `results/tree_feature_smoke/tables/tree_feature_matrix.tsv`; `results/tree_feature_smoke/plots/tree_features.pdf`; `results/tree_feature_smoke/plots/tree_features.png`; `results/nextflow_standard_feature_smoke/standard/tables/feature_summary.tsv`; `results/nextflow_standard_feature_smoke/standard/plots/feature_summary.pdf`; `results/nextflow_standard_feature_smoke/standard/plots/feature_summary.png` | `python bin/genefam/run_feature_summary_smoke.py --domains results/domain_filter_smoke/tables/filtered_domains.tsv --motifs results/motif_smoke/tables/motif_summary.tsv --gene-structures results/gene_structure_smoke/tables/gene_structure_summary.tsv --synteny results/synteny_smoke/tables/syntenic_pairs.tsv --promoters results/promoter_smoke/tables/promoters.bed --r-bin /usr/local/bin/R --outdir results/feature_summary_smoke`, `python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke`, `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --config configs/publication_modules.example.yaml --outdir results/nextflow_standard_feature_smoke`, and `python -m pytest tests/test_summarize_feature_tables.py tests/test_build_tree_feature_matrix.py tests/test_run_feature_summary_smoke.py tests/test_run_tree_feature_smoke.py tests/test_run_nextflow_standard_smoke.py -q` |
| PPI ggNetView | `bin/genefam/build_ppi_tables.py`; `bin/genefam/run_ppi_ggnetview_smoke.py`; `bin/genefam/run_ppi_ggnetview_plot_smoke.py`; `scripts/plot_ppi_ggnetview.R`; `workflows/modules/plots.nf` `PLOT_PPI_GGNETVIEW`; `Reference/Long_Weixiong_20240323_1_GDSL/R/11.ppi.R`; `results/ppi_ggnetview_smoke/ppi_ggnetview_smoke.tsv`; `results/ppi_ggnetview_plot_smoke/tables/ppi_edges.tsv`; `results/ppi_ggnetview_plot_smoke/tables/ppi_nodes.tsv`; `results/ppi_ggnetview_plot_smoke/tables/ppi_hubs.tsv`; `results/ppi_ggnetview_plot_smoke/tables/ppi_ggnetview_status.tsv`; `results/ppi_ggnetview_plot_smoke/plots/ppi_ggnetview.pdf`; `results/ppi_ggnetview_plot_smoke/plots/ppi_ggnetview.png`; status may be `missing_dependency` until the `ggNetView` R package is installed | `python bin/genefam/run_ppi_ggnetview_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_smoke`, `python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke`, and `python -m pytest tests/test_build_ppi_tables.py tests/test_run_ppi_ggnetview_smoke.py tests/test_run_ppi_ggnetview_plot_smoke.py tests/test_run_release_checks.py -q` |
| expression integration | `bin/genefam/subset_expression_matrix.py`; `bin/genefam/build_expression_summary.py`; `bin/genefam/run_expression_heatmap_smoke.py`; `workflows/modules/annotation_integration.nf`; `workflows/modules/plots.nf` `PLOT_EXPRESSION_HEATMAP`; `scripts/plot_expression_heatmap.R`; `tests/fixtures/expression/family_expression.tsv`; `tests/fixtures/expression/sample_metadata.tsv`; `results/standard_expression_smoke/tables/family_expression.tsv`; `results/standard_expression_smoke/tables/expression_sample_metadata.tsv`; `results/standard_expression_smoke/tables/expression_group_matrix.tsv`; `results/standard_expression_smoke/tables/expression_gene_summary.tsv`; `results/standard_expression_smoke/plots/expression_heatmap.pdf`; `results/standard_expression_smoke/plots/expression_heatmap.png`; `results/expression_heatmap_smoke/plots/expression_heatmap.pdf`; `results/expression_heatmap_smoke/plots/expression_heatmap.png` | `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --expression-matrix tests/fixtures/expression/family_expression.tsv --expression-metadata tests/fixtures/expression/sample_metadata.tsv --r-bin /usr/local/bin/R --outdir results/standard_expression_smoke`, `python bin/genefam/run_expression_heatmap_smoke.py --expression tests/fixtures/expression/family_expression.tsv --metadata tests/fixtures/expression/sample_metadata.tsv --r-bin /usr/local/bin/R --outdir results/expression_heatmap_smoke`, and `python -m pytest tests/test_subset_expression_matrix.py tests/test_build_expression_summary.py tests/test_run_expression_heatmap_smoke.py tests/test_workflow_modules.py -q` |
| final report | `bin/genefam/assemble_report.py`; `bin/genefam/build_figure_interpretations.py`; `bin/genefam/audit_publication_report.py`; `bin/genefam/audit_report_index.py`; `workflows/modules/report.nf`; `workflows/modules/standard_postprocess.nf`; `workflows/modules/duplication_retention.nf`; `results/mock_mvp/report/final_report.md`; `results/nextflow_standard_feature_smoke/standard/report/final_report.md`; `results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv`; `results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md`; `results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv`; `results/report_index_audit/standard_report_index_audit.md`; `results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv`; `results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv`; `results/nextflow_wgd_smoke/wgd/report/figure_interpretations.md`; `results/nextflow_wgd_smoke/wgd/report/software_versions.tsv`; `results/report_index_audit/wgd_report_index_audit.md`; `results/publication_report_audit/publication_report_audit.md`; `results/publication_report_audit/wgd_publication_report_audit.md`; WGD publication report audit for complete Ka/Ks/WGD figure close-reading text and gamma beta alpha theta closure; report index audits for `figure_interpretations.md` and `final_report.md` navigation | `python -m pytest tests/test_assemble_report.py tests/test_build_figure_interpretations.py tests/test_audit_publication_report.py tests/test_audit_report_index.py tests/test_run_mock_mvp.py tests/test_run_nextflow_wgd_smoke.py -q` |
| HISTORY.md development diary | `HISTORY.md` records dated development entries and commit hashes | `git log --oneline -6` and inspect `HISTORY.md` |
| Reference/ read-only source material | `.dockerignore`; `docs/input_contract.md`; `README.md`; untracked `Reference/` files are not staged | `git status --short --untracked-files=all` |

## Known Gap

The repository-level implementation and tests are in place, but this machine does not currently prove full end-to-end runtime execution.

Recent readiness audits found:

- required available: `conda`, `/usr/local/bin/R`
- required available inside `GeneFamilyFlow`: `nextflow`, `hmmsearch`, `diamond`, `mafft`, `FastTree`, `iqtree2` via `iqtree`, `meme`
- optional container-stage missing: `docker`, `apptainer`

This means:

- Mock MVP and Python/R/report helpers can be validated locally.
- Full Nextflow mock-MVP execution now works through `GeneFamilyFlow` with the `activated` profile.
- The Nextflow entrypoint runs `validate_config.py --check-paths --base-dir` before species discovery, mock MVP, or standard identification branches.
- Docker profile execution needs Docker plus the `genefam-pipeline:latest` image.
- Apptainer profile execution needs Apptainer and access to the Docker image.
- External HMMER, DIAMOND, MAFFT, IQ-TREE, MEME, and related bioinformatics commands are available through the local `GeneFamilyFlow` Conda environment; Linux/container-only helpers such as `jcvi` and `kaks_calculator` are kept in `envs/GeneFamilyFlow.linux-64.conda.yaml`.
- `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` writes a Markdown plan and shell script for the current machine gap.
- The generated bootstrap shell runs `docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest` after the Docker build so `results/container_default_smoke` is created by the image default command.
- `python bin/genefam/audit_container_materials.py --outdir results/container_materials` verifies the static Dockerfile, Linux Conda environment, and Nextflow container-profile contracts before Docker/Apptainer are available.
- The container materials audit also checks that example `gene_family.hmm_profiles` paths do not depend on `Reference/`, because `Reference/` is intentionally excluded from Docker build context. The bundled `tests/fixtures/hmmer_profiles/PF00657.demo.hmm` is a fixture path, not a curated biological profile.
- `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` writes a compact goal-completion table and keeps Docker/Apptainer as an explicit blocker when unavailable.

## Release Decision

Current status is repository-ready but runtime-blocked on this machine.

Do not mark the full objective complete until at least one real runtime route is verified:

```bash
nextflow run workflows/main.nf -c workflows/nextflow.config --config configs/example.config.yaml --mock_mvp true
```

and the explicit standard identification branch is verified:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --run_identification true
```

or:

```bash
docker build -t genefam-pipeline:latest .
nextflow run workflows/main.nf -c workflows/nextflow.config -profile docker --config configs/example.config.yaml --mock_mvp true
```

or an equivalent Apptainer run after the missing runtime commands are available.
