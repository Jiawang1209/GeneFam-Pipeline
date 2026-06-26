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
python bin/genefam/run_nextflow_standard_smoke.py \
  --conda-env GeneFamilyFlow \
  --run-feature-summary \
  --run-mcscanx-circlize \
  --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv \
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
```

The readiness audit may exit non-zero when runtime commands are missing; inspect the TSV for exact missing tools and use the bootstrap planner to generate next-step commands.

The release checks runner writes:

- `results/release_checks/release_checks.tsv`
- `results/release_checks/release_checks.md`
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
- `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv`
- `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.md`
- `results/container_profile_smoke/docker/container_profile_smoke.tsv`
- `results/container_profile_smoke/docker/container_profile_smoke.md`
- `results/container_profile_smoke/apptainer/container_profile_smoke.tsv`
- `results/container_profile_smoke/apptainer/container_profile_smoke.md`
- `results/handoff/handoff_report.md`
- `results/handoff/handoff_summary.tsv`
- `results/delivery_bundle/delivery_manifest.tsv`
- `results/delivery_bundle/delivery_bundle.md`

The Markdown summary reports `Required failed` and `Optional failed` separately. Container profile smoke checks are optional evidence; the required readiness audit remains the release-blocking signal while Docker/Apptainer are unavailable.

## Requirement Audit

| Requirement | Evidence | Verification |
|---|---|---|
| Nextflow DSL2 workflow | `workflows/main.nf`; modules under `workflows/modules/`; standard branch calls `RUN_ALIGNMENT`, `RUN_PHYLOGENY`, optional `EXTRACT_PROMOTERS`, optional `PLOT_FEATURE_SUMMARY`, and optional `PLOT_MCSCANX_CIRCLIZE`; `bin/genefam/run_nextflow_smoke.py`; `bin/genefam/run_nextflow_standard_smoke.py`; `bin/genefam/run_nextflow_single_tool_smoke.py`; `results/nextflow_smoke/nextflow_smoke.md`; `results/nextflow_standard_manifest_smoke/nextflow_standard_smoke.tsv`; `results/nextflow_standard_feature_smoke/nextflow_standard_smoke.tsv`; `results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv` | `python -m pytest tests/test_workflow_modules.py tests/test_run_nextflow_smoke.py tests/test_run_nextflow_standard_smoke.py tests/test_run_nextflow_single_tool_smoke.py -q` |
| YAML-driven parameters | `configs/example.config.yaml`; `configs/advanced_modules.example.yaml`; `configs/manifest.example.yaml`; `tests/fixtures/species_manifest.tsv`; `bin/genefam/build_run_plan.py`; `bin/genefam/run_species_selection_smoke.py`; `results/species_selection_smoke/tables/species_manifest.tsv`; `results/species_selection_smoke/tables/run_plan.tsv`; `results/species_manifest_selection_smoke/tables/species_manifest.tsv`; `results/species_manifest_selection_smoke/species_selection_smoke.md` | `python bin/genefam/run_species_selection_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --outdir results/species_selection_smoke`, `python bin/genefam/run_species_selection_smoke.py --config configs/manifest.example.yaml --groups configs/species_groups.yaml --outdir results/species_manifest_selection_smoke`, and `python bin/genefam/build_run_plan.py --config configs/example.config.yaml --out results/mock_mvp/tables/run_plan.tsv` |
| GeneFamilyFlow runtime | `envs/GeneFamilyFlow.conda.yaml`; `workflows/nextflow.config`; `Dockerfile` | `python -m pytest tests/test_runtime_environment_files.py -q` |
| `/usr/local/bin/R` plotting and reporting convention | `workflows/modules/plots.nf`; `workflows/modules/duplication_retention.nf`; `scripts/plot_family_counts.R`; `scripts/plot_kaks.R`; `scripts/plot_duplicate_type_kaks.R`; `scripts/plot_expression_heatmap.R`; `scripts/plot_feature_summary.R`; `scripts/plot_tree_features.R`; `scripts/plot_mcscanx_circlize.R` | `python -m pytest tests/test_workflow_modules.py tests/test_runtime_environment_files.py tests/test_run_feature_summary_smoke.py tests/test_run_tree_feature_smoke.py tests/test_run_promoter_smoke.py tests/test_run_mcscanx_circlize_smoke.py tests/test_run_duplicate_type_kaks_smoke.py tests/test_run_expression_heatmap_smoke.py -q` |
| Docker/Conda reproducible running | `Dockerfile`; `envs/GeneFamilyFlow.conda.yaml`; `envs/GeneFamilyFlow.linux-64.conda.yaml`; `bin/genefam/audit_container_materials.py`; `bin/genefam/plan_runtime_bootstrap.py`; `workflows/nextflow.config` profiles `local`, `docker`, `apptainer`; `results/container_materials/container_materials.tsv`; `results/container_materials/container_materials.md`; Dockerfile default standard smoke output `results/container_default_smoke` | `python bin/genefam/audit_container_materials.py --outdir results/container_materials`, `python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv`, and `python bin/genefam/plan_runtime_bootstrap.py --readiness results/readiness/command_readiness.tsv --outdir results/readiness` |
| container profile smoke verification | `bin/genefam/run_container_profile_smoke.py`; `workflows/nextflow.config` profiles `docker`, `apptainer`; `results/container_profile_smoke/docker/container_profile_smoke.md`; `results/container_profile_smoke/apptainer/container_profile_smoke.md` | `python bin/genefam/run_container_profile_smoke.py --profile docker --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/docker` and `python bin/genefam/run_container_profile_smoke.py --profile apptainer --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/apptainer` |
| long objective completion audit | `bin/genefam/audit_objective_completion.py`; `results/objective_audit/objective_audit.tsv`; `results/objective_audit/objective_audit.md` | `python bin/genefam/audit_objective_completion.py --release-checks results/release_checks/release_checks.tsv --readiness results/readiness/command_readiness.tsv --outdir results/objective_audit` |
| history and Reference governance | `HISTORY.md`; `Reference/`; `bin/genefam/audit_reference_governance.py`; `results/reference_governance/reference_governance.tsv`; `results/reference_governance/reference_governance.md` | `python bin/genefam/audit_reference_governance.py --outdir results/reference_governance` and `python -m pytest tests/test_audit_reference_governance.py -q` |
| quickstart handoff for users | `bin/genefam/run_quickstart.py`; `bin/genefam/run_delivery_bundle.py`; `docs/quickstart.md`; `README.md`; `results/quickstart/quickstart_summary.md`; `results/delivery_bundle/delivery_manifest.tsv`; `results/delivery_bundle/delivery_bundle.md`; `results/release_checks/release_checks.md`; `results/standard_smoke/report/final_report.md`; `results/example_prepared_wgd/report/final_report.md` | `python bin/genefam/run_quickstart.py --conda-env GeneFamilyFlow --outdir results/quickstart`, `python bin/genefam/run_delivery_bundle.py --release-checks results/release_checks/release_checks.tsv --objective-audit results/objective_audit/objective_audit.tsv --readiness results/readiness/command_readiness.tsv --quickstart results/quickstart/quickstart_summary.tsv --outdir results/delivery_bundle`, and `python -m pytest tests/test_quickstart_docs.py tests/test_release_audit_docs.py -q` |
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
| MCScanX circlize visualization | `bin/genefam/build_circlize_inputs.py`; `bin/genefam/run_mcscanx_circlize_smoke.py`; `scripts/plot_mcscanx_circlize.R`; `circlize` R package; `workflows/modules/plots.nf` `PLOT_MCSCANX_CIRCLIZE`; `results/mcscanx_circlize_smoke/tables/circlize_chromosomes.tsv`; `results/mcscanx_circlize_smoke/tables/circlize_links.tsv`; `results/mcscanx_circlize_smoke/tables/circlize_skipped_links.tsv`; `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.pdf`; `results/mcscanx_circlize_smoke/plots/mcscanx_circlize.png`; `results/nextflow_standard_feature_smoke/standard/plots/mcscanx_circlize.pdf`; `results/nextflow_standard_feature_smoke/standard/plots/mcscanx_circlize.png` | `python bin/genefam/run_mcscanx_circlize_smoke.py --r-bin /usr/local/bin/R --outdir results/mcscanx_circlize_smoke`, `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv --outdir results/nextflow_standard_feature_smoke`, and `python -m pytest tests/test_build_circlize_inputs.py tests/test_run_mcscanx_circlize_smoke.py tests/test_run_nextflow_standard_smoke.py -q` |
| standard-to-WGD prepared handoff | `bin/genefam/run_prepared_wgd_handoff_example.py`; `bin/genefam/build_mcscanx_kaks_handoff.py`; `docs/standard_to_wgd_handoff.md`; `examples/prepared_wgd_handoff/`; `examples/prepared_wgd_handoff/family_candidates.tsv`; `examples/prepared_wgd_handoff/duplicate_types.tsv`; `examples/prepared_wgd_handoff/kaks_pairs.tsv`; `results/example_prepared_wgd/report/final_report.md`; `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/duplicate_types.tsv`; `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/kaks_pairs.tsv` | `python -m pytest tests/test_prepared_wgd_handoff_example.py tests/test_build_mcscanx_kaks_handoff.py -q`, `python bin/genefam/run_prepared_wgd_handoff_example.py --conda-env GeneFamilyFlow --example-dir examples/prepared_wgd_handoff --outdir results/example_prepared_wgd`, `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --mode raw-mcscanx-kaks --outdir results/nextflow_wgd_raw_smoke`, and the `--run_duplication_retention true` Nextflow command above |
| duplication retention | `bin/genefam/normalize_duplicate_types.py`; `bin/genefam/join_family_duplicates.py`; `bin/genefam/retention_enrichment.py`; `bin/genefam/run_retention_enrichment_smoke.py`; `examples/prepared_wgd_handoff/family_candidates.tsv`; `examples/prepared_wgd_handoff/duplicate_types.tsv`; `results/retention_enrichment_smoke/tables/normalized_duplicate_types.tsv`; `results/retention_enrichment_smoke/tables/family_duplicate_classification.tsv`; `results/retention_enrichment_smoke/tables/retention_enrichment.tsv` | `python bin/genefam/run_retention_enrichment_smoke.py --family-members examples/prepared_wgd_handoff/family_candidates.tsv --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv --outdir results/retention_enrichment_smoke` and `python -m pytest tests/test_normalize_duplicate_types.py tests/test_join_family_duplicates.py tests/test_retention_enrichment.py tests/test_run_retention_enrichment_smoke.py -q` |
| WGD layer and named event model | `bin/genefam/classify_wgd_layers.py`; `bin/genefam/build_wgd_event_evidence.py`; `bin/genefam/build_wgd_run_config_snapshot.py`; `bin/genefam/run_wgd_smoke.py`; `scripts/plot_kaks.R`; `configs/wgd_events.brassicaceae.yaml`; `results/wgd_smoke/tables/wgd_run_config_snapshot.tsv`; `results/wgd_smoke/report/final_report.md`; `results/nextflow_wgd_smoke/wgd/plots/ks_distribution.pdf`; `results/nextflow_wgd_smoke/wgd/plots/ks_distribution.png`; `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.pdf`; `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.png` | `python -m pytest tests/test_classify_wgd_layers.py tests/test_build_wgd_event_evidence.py tests/test_build_wgd_run_config_snapshot.py tests/test_run_wgd_smoke.py tests/test_run_nextflow_wgd_smoke.py -q` |
| gamma beta alpha theta interpretation | `configs/wgd_events.brassicaceae.yaml`; `docs/wgd_event_evidence.md`; `docs/duplication_retention_design.md`; WGD event names must be unique in the event YAML; WGD event metadata requires name, scope, evidence, and expected_relative_age; Configured WGD event labels must have matching event metadata | `python -m pytest tests/test_build_wgd_event_evidence.py -q` |
| Ka/Ks selection pressure | `bin/genefam/prepare_kaks_pairs.py`; `bin/genefam/parse_kaks_results.py`; `bin/genefam/build_mcscanx_kaks_handoff.py`; `bin/genefam/build_duplicate_type_kaks.py`; `bin/genefam/run_kaks_smoke.py`; `bin/genefam/run_duplicate_type_kaks_smoke.py`; `scripts/plot_kaks.R`; `scripts/plot_duplicate_type_kaks.R`; `tests/fixtures/kaks/kaks_calculator.tsv`; `results/kaks_smoke/tables/normalized_kaks.tsv`; `results/duplicate_type_kaks_smoke/tables/duplicate_type_kaks.tsv`; `results/duplicate_type_kaks_smoke/tables/duplicate_type_kaks_summary.tsv`; `results/duplicate_type_kaks_smoke/plots/duplicate_type_kaks.pdf`; `results/duplicate_type_kaks_smoke/plots/duplicate_type_kaks.png`; `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/normalized_kaks.tsv`; `results/nextflow_wgd_raw_smoke/wgd/mcscanx_kaks_handoff/tables/kaks_pairs.tsv`; `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.pdf`; `results/nextflow_wgd_raw_smoke/wgd/plots/ks_distribution.png`; `workflows/modules/duplication_retention.nf` `PREPARE_MCSCANX_KAKS_HANDOFF`, `PLOT_KAKS`, and `PLOT_DUPLICATE_TYPE_KAKS` | `python bin/genefam/run_kaks_smoke.py --kaks tests/fixtures/kaks/kaks_calculator.tsv --outdir results/kaks_smoke`, `python bin/genefam/run_duplicate_type_kaks_smoke.py --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv --kaks-pairs examples/prepared_wgd_handoff/kaks_pairs.tsv --r-bin /usr/local/bin/R --outdir results/duplicate_type_kaks_smoke`, `python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --mode raw-mcscanx-kaks --outdir results/nextflow_wgd_raw_smoke`, and `python -m pytest tests/test_prepare_kaks_pairs.py tests/test_parse_kaks_results.py tests/test_build_mcscanx_kaks_handoff.py tests/test_build_duplicate_type_kaks.py tests/test_run_duplicate_type_kaks_smoke.py tests/test_run_nextflow_wgd_smoke.py -q` |
| chromosome location | `bin/genefam/extract_chromosome_locations.py`; `bin/genefam/run_chromosome_smoke.py`; `results/chromosome_smoke/tables/chromosome_locations.tsv`; `workflows/modules/annotation_integration.nf` | `python bin/genefam/run_chromosome_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --outdir results/chromosome_smoke` and `python -m pytest tests/test_extract_chromosome_locations.py tests/test_workflow_modules.py -q` |
| promoter analysis and visualization | `bin/genefam/extract_promoters.py`; `bin/genefam/run_promoter_smoke.py`; `bin/genefam/summarize_feature_tables.py`; `scripts/plot_feature_summary.R`; `workflows/modules/annotation_integration.nf` `EXTRACT_PROMOTERS`; `results/promoter_smoke/tables/promoters.bed`; `results/promoter_smoke/sequences/promoters.fa`; `results/promoter_smoke/tables/feature_summary.tsv`; `results/promoter_smoke/plots/feature_summary.pdf`; `results/promoter_smoke/plots/feature_summary.png` | `python bin/genefam/run_promoter_smoke.py --r-bin /usr/local/bin/R --outdir results/promoter_smoke` and `python -m pytest tests/test_extract_promoters.py tests/test_run_promoter_smoke.py tests/test_workflow_modules.py -q` |
| promoter cis-element visualization | `bin/genefam/build_promoter_cis_elements.py`; `bin/genefam/run_promoter_cis_smoke.py`; `scripts/plot_promoter_cis_elements.R`; `workflows/modules/plots.nf` `PLOT_PROMOTER_CIS_ELEMENTS`; PlantCARE-style table aliases; `results/promoter_cis_smoke/tables/promoter_cis_elements.tsv`; `results/promoter_cis_smoke/tables/promoter_cis_gene_matrix.tsv`; `results/promoter_cis_smoke/tables/promoter_cis_category_summary.tsv`; `results/promoter_cis_smoke/plots/promoter_cis_elements.pdf`; `results/promoter_cis_smoke/plots/promoter_cis_elements.png` | `python bin/genefam/run_promoter_cis_smoke.py --r-bin /usr/local/bin/R --outdir results/promoter_cis_smoke` and `python -m pytest tests/test_build_promoter_cis_elements.py tests/test_run_promoter_cis_smoke.py tests/test_workflow_modules.py -q` |
| feature statistics and visualization for large gene families | `bin/genefam/summarize_feature_tables.py`; `bin/genefam/run_feature_summary_smoke.py`; `bin/genefam/build_tree_feature_matrix.py`; `bin/genefam/run_tree_feature_smoke.py`; `scripts/plot_feature_summary.R`; `scripts/plot_tree_features.R`; `workflows/modules/plots.nf` `PLOT_FEATURE_SUMMARY` and `PLOT_TREE_FEATURES`; domain hit count and coverage summaries; MEME motif count and site summaries; gene-structure length and exon summaries; tree-ordered feature tracks; MCScanX syntenic pair and block summaries; promoter length and clipping summaries; `results/feature_summary_smoke/tables/feature_summary.tsv`; `results/feature_summary_smoke/plots/feature_summary.pdf`; `results/feature_summary_smoke/plots/feature_summary.png`; `results/tree_feature_smoke/tables/tree_feature_matrix.tsv`; `results/tree_feature_smoke/plots/tree_features.pdf`; `results/tree_feature_smoke/plots/tree_features.png`; `results/nextflow_standard_feature_smoke/standard/tables/feature_summary.tsv`; `results/nextflow_standard_feature_smoke/standard/plots/feature_summary.pdf`; `results/nextflow_standard_feature_smoke/standard/plots/feature_summary.png` | `python bin/genefam/run_feature_summary_smoke.py --domains results/domain_filter_smoke/tables/filtered_domains.tsv --motifs results/motif_smoke/tables/motif_summary.tsv --gene-structures results/gene_structure_smoke/tables/gene_structure_summary.tsv --synteny results/synteny_smoke/tables/syntenic_pairs.tsv --promoters results/promoter_smoke/tables/promoters.bed --r-bin /usr/local/bin/R --outdir results/feature_summary_smoke`, `python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke`, `python bin/genefam/run_nextflow_standard_smoke.py --conda-env GeneFamilyFlow --run-feature-summary --run-mcscanx-circlize --syntenic-pairs tests/fixtures/mcscanx/syntenic_pairs.tsv --outdir results/nextflow_standard_feature_smoke`, and `python -m pytest tests/test_summarize_feature_tables.py tests/test_build_tree_feature_matrix.py tests/test_run_feature_summary_smoke.py tests/test_run_tree_feature_smoke.py tests/test_run_nextflow_standard_smoke.py -q` |
| PPI ggNetView | `bin/genefam/build_ppi_tables.py`; `bin/genefam/run_ppi_ggnetview_smoke.py`; `bin/genefam/run_ppi_ggnetview_plot_smoke.py`; `scripts/plot_ppi_ggnetview.R`; `workflows/modules/plots.nf` `PLOT_PPI_GGNETVIEW`; `Reference/Long_Weixiong_20240323_1_GDSL/R/11.ppi.R`; `results/ppi_ggnetview_smoke/ppi_ggnetview_smoke.tsv`; `results/ppi_ggnetview_plot_smoke/tables/ppi_edges.tsv`; `results/ppi_ggnetview_plot_smoke/tables/ppi_nodes.tsv`; `results/ppi_ggnetview_plot_smoke/tables/ppi_hubs.tsv`; `results/ppi_ggnetview_plot_smoke/tables/ppi_ggnetview_status.tsv`; `results/ppi_ggnetview_plot_smoke/plots/ppi_ggnetview.pdf`; `results/ppi_ggnetview_plot_smoke/plots/ppi_ggnetview.png`; status may be `missing_dependency` until the `ggNetView` R package is installed | `python bin/genefam/run_ppi_ggnetview_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_smoke`, `python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke`, and `python -m pytest tests/test_build_ppi_tables.py tests/test_run_ppi_ggnetview_smoke.py tests/test_run_ppi_ggnetview_plot_smoke.py tests/test_run_release_checks.py -q` |
| expression integration | `bin/genefam/subset_expression_matrix.py`; `bin/genefam/build_expression_summary.py`; `bin/genefam/run_expression_heatmap_smoke.py`; `workflows/modules/annotation_integration.nf`; `workflows/modules/plots.nf` `PLOT_EXPRESSION_HEATMAP`; `scripts/plot_expression_heatmap.R`; `tests/fixtures/expression/family_expression.tsv`; `tests/fixtures/expression/sample_metadata.tsv`; `results/standard_expression_smoke/tables/family_expression.tsv`; `results/standard_expression_smoke/tables/expression_sample_metadata.tsv`; `results/standard_expression_smoke/tables/expression_group_matrix.tsv`; `results/standard_expression_smoke/tables/expression_gene_summary.tsv`; `results/standard_expression_smoke/plots/expression_heatmap.pdf`; `results/standard_expression_smoke/plots/expression_heatmap.png`; `results/expression_heatmap_smoke/plots/expression_heatmap.pdf`; `results/expression_heatmap_smoke/plots/expression_heatmap.png` | `python bin/genefam/run_standard_smoke.py --config configs/example.config.yaml --groups configs/species_groups.yaml --mock-evidence-dir tests/fixtures/mock_evidence --expression-matrix tests/fixtures/expression/family_expression.tsv --expression-metadata tests/fixtures/expression/sample_metadata.tsv --r-bin /usr/local/bin/R --outdir results/standard_expression_smoke`, `python bin/genefam/run_expression_heatmap_smoke.py --expression tests/fixtures/expression/family_expression.tsv --metadata tests/fixtures/expression/sample_metadata.tsv --r-bin /usr/local/bin/R --outdir results/expression_heatmap_smoke`, and `python -m pytest tests/test_subset_expression_matrix.py tests/test_build_expression_summary.py tests/test_run_expression_heatmap_smoke.py tests/test_workflow_modules.py -q` |
| final report | `bin/genefam/assemble_report.py`; `workflows/modules/report.nf`; `results/mock_mvp/report/final_report.md` | `python -m pytest tests/test_assemble_report.py tests/test_run_mock_mvp.py -q` |
| HISTORY.md development diary | `HISTORY.md` records dated development entries and commit hashes | `git log --oneline -6` and inspect `HISTORY.md` |
| Reference/ read-only source material | `.dockerignore`; `docs/input_contract.md`; `README.md`; untracked `Reference/` files are not staged | `git status --short --untracked-files=all` |

## Known Gap

The repository-level implementation and tests are in place, but this machine does not currently prove full end-to-end runtime execution.

Recent readiness audits found:

- available: `conda`, `/usr/local/bin/R`
- available inside `GeneFamilyFlow`: `nextflow`, `hmmsearch`, `diamond`, `mafft`, `FastTree` via `fasttree`, `iqtree2` via `iqtree`, `meme`
- missing: `docker`, `apptainer`

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
