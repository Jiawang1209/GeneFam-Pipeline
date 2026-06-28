from pathlib import Path


def test_hmmer_module_writes_normalized_tsv():
    module = Path("workflows/modules/hmmer_search.nf").read_text(encoding="utf-8")

    assert "process BUILD_REBUILT_HMMER_INPUTS" in module
    assert "build_rebuilt_hmmer_inputs.py" in module
    assert "mafft --auto two_pass_hmmer/first_pass_hits.faa" in module
    assert "hmmbuild two_pass_hmmer/${family_name}.rebuilt.hmm" in module
    assert 'path "two_pass_hmmer/rebuilt_hmmer_inputs.tsv", emit: inputs' in module
    assert 'path "two_pass_hmmer", emit: package_dir' in module
    assert "parse_hmmer_domtbl.py" in module
    assert "filter_hmmer_domains.py" in module
    assert "--species-id ${species_id}" in module
    assert "--min-domain-coverage ${params.hmmer_min_domain_coverage}" in module
    assert 'path("${species_id}.${hmm_id}.hmmer.tsv")' in module


def test_diamond_module_writes_normalized_tsv():
    module = Path("workflows/modules/diamond_search.nf").read_text(encoding="utf-8")

    assert "parse_diamond_outfmt6.py" in module
    assert "--species-id ${species_id}" in module
    assert "--out ${species_id}.diamond.tsv" in module


def test_identification_inputs_module_builds_hmmer_and_diamond_tables():
    module = Path("workflows/modules/identification_inputs.nf").read_text(encoding="utf-8")

    assert "process BUILD_IDENTIFICATION_INPUTS" in module
    assert "build_identification_inputs.py" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--reference-peptides ${reference_peptides}" in module
    assert 'path "identification_inputs/hmmer_inputs.tsv"' in module
    assert 'path "identification_inputs/diamond_inputs.tsv"' in module


def test_preprocess_module_cleans_species_bank_and_builds_reference():
    module = Path("workflows/modules/preprocess.nf").read_text(encoding="utf-8")

    assert "process PREPROCESS_SPECIES" in module
    assert "preprocess_species.py" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--outdir ." in module
    assert 'path "species_manifest.raw.tsv"' in module
    assert 'path "species_manifest.clean.tsv"' in module
    assert 'path "species_bank_clean"' in module
    assert 'path "all_transcript_gene_map.tsv"' in module
    assert 'path "all_representative_transcripts.tsv"' in module
    assert 'path "all_preprocess_warnings.tsv"' in module
    assert "process BUILD_REFERENCE_FROM_TAIR_DOMAINS" in module
    assert "build_reference_from_config.py" in module
    assert "--species-manifest ${clean_species_manifest}" in module
    assert "--outdir reference" in module
    assert 'path "reference/*.reference.pep.fa"' in module
    assert 'path "reference/reference_generation.tsv"' in module


def test_config_validation_module_runs_strict_path_preflight():
    module = Path("workflows/modules/config_validation.nf").read_text(encoding="utf-8")

    assert "process VALIDATE_CONFIG" in module
    assert "validate_config.py" in module
    assert "--check-paths" in module
    assert "--base-dir ${projectDir}/.." in module
    assert "validated_config.yaml" in module


def test_domain_filter_module_can_concatenate_species_candidate_tables():
    module = Path("workflows/modules/domain_filter.nf").read_text(encoding="utf-8")

    assert "process MOCK_IDENTIFICATION_EVIDENCE" in module
    assert "process EMPTY_HMMER_EVIDENCE" in module
    assert "process EMPTY_DIAMOND_EVIDENCE" in module
    assert "${mock_evidence_dir}/hmmer.tsv" in module
    assert "${mock_evidence_dir}/diamond.tsv" in module
    assert 'tuple val("mock"), path("hmmer.tsv"), path("diamond.tsv")' in module
    assert "species_id\\tgene_id\\thmm_id\\tevalue\\thmm_from\\thmm_to\\thmm_length\\tbitscore" in module
    assert "species_id\\tgene_id\\treference_hit\\tevalue" in module

    assert "process CONCAT_FAMILY_CANDIDATES" in module
    assert 'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true' in module
    assert "concat_tsv.py" in module
    assert "--inputs ${candidate_tables}" in module
    assert "--out family_candidates.tsv" in module


def test_standard_postprocess_module_extracts_family_sequences_and_report_index():
    module = Path("workflows/modules/standard_postprocess.nf").read_text(encoding="utf-8")

    assert "process EXTRACT_FAMILY_SEQUENCES" in module
    assert 'publishDir "${params.outdir}/sequences", mode: "copy", overwrite: true' in module
    assert "extract_family_sequences.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--out family_members.faa" in module

    assert "process BUILD_RUN_CONFIG_SNAPSHOT" in module
    assert "build_run_config_snapshot.py" in module
    assert "--config ${config}" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--out run_config_snapshot.tsv" in module

    assert "process PUBLISH_PREPROCESS_AUDIT" in module
    assert 'path clean_species_bank, stageAs: "clean_species_bank_input"' in module
    assert 'path "tables/species_manifest.tsv"' in module
    assert 'path "tables/all_transcript_gene_map.tsv"' in module
    assert 'path "tables/all_representative_transcripts.tsv"' in module
    assert 'path "tables/all_preprocess_warnings.tsv"' in module
    assert 'path "species_bank_clean"' in module
    assert "cp -RL clean_species_bank_input/. species_bank_clean/" in module

    assert "process BUILD_WGD_HANDOFF_MANIFEST" in module
    assert 'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true' in module
    assert "build_wgd_handoff_manifest.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--events-config ${params.events_config}" in module
    assert "--ks-bins ${params.ks_bins}" in module
    assert '--wgd-event-args "${params.wgd_event_args}"' in module
    assert "--out wgd_handoff_manifest.tsv" in module
    assert "process EMPTY_REFERENCE_MANIFEST" in module
    assert 'path "reference_generation.tsv"' in module
    assert "Reference generation skipped because mock evidence was supplied" in module

    assert "process PREPARE_REFERENCE_KAKS_INPUTS" in module
    assert 'publishDir "${params.outdir}/kaks_inputs", mode: "copy", overwrite: true' in module
    assert "prepare_reference_kaks_inputs.py" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--jcvi-dir ${jcvi_collinearity}" in module
    assert "--pair-source mcscanx=${mcscanx_self_circos}/mcscanx_gene_pairs.tsv" in module
    assert 'path "KaKs_Gene_Pair.tsv"' in module
    assert 'path "kaks_input_manifest.tsv"' in module
    assert 'path "kaks_input_status.tsv"' in module
    assert "process RUN_REFERENCE_KAKS_CALCULATOR" in module
    assert "path kaks_pair_fastas" in module
    assert "run_reference_kaks_calculator.py" in module
    assert "--manifest ${kaks_input_manifest}" in module
    assert 'path "kaks_calculator_status.tsv"' in module
    assert 'path "kaks_calculator_commands.tsv"' in module
    assert 'path "kaks_calculator_qc.tsv"' in module
    assert 'path "kaks_failure_summary.tsv"' in module
    assert "process NORMALIZE_REFERENCE_KAKS_RESULTS" in module
    assert "path kaks_results" in module
    assert "normalize_reference_kaks_results.py" in module
    assert "--calculator-results ${kaks_calculator_results}" in module
    assert 'path "kaks_pairs.tsv"' in module
    assert 'path "kaks_pairs_skipped.tsv"' in module
    assert 'path "kaks_pairs_summary.tsv"' in module
    assert "process CLASSIFY_STANDARD_WGD_LAYERS" in module
    assert "classify_wgd_layers.py" in module
    assert "--pairs ${kaks_pairs}" in module
    assert "--bins ${ks_bins}" in module
    assert "--out wgd_layers.tsv" in module
    assert "process BUILD_STANDARD_KAKS_WGD_ANNOTATIONS" in module
    assert "build_kaks_plot_annotations.py" in module
    assert 'path "kaks_wgd_annotations.tsv"' in module
    assert "process BUILD_STANDARD_WGD_EVENT_EVIDENCE" in module
    assert "build_wgd_event_evidence.py" in module
    assert "--events-config ${events_config}" in module
    assert 'path "wgd_event_evidence.tsv"' in module
    assert "process PLOT_STANDARD_KAKS_WGD" in module
    assert "plot_kaks.R" in module
    assert 'path "plots/ks_distribution.pdf"' in module
    assert 'path "plots/ks_distribution.png"' in module
    assert "process BUILD_STANDARD_MCSCANX_DUPLICATE_TYPES" in module
    assert "build_mcscanx_duplicate_types.py" in module
    assert "--mcscanx-pairs ${mcscanx_self_circos}/mcscanx_gene_pairs.tsv" in module
    assert 'path "tables/mcscanx_duplicate_types.tsv"' in module
    assert "process PLOT_STANDARD_DUPLICATE_TYPE_KAKS" in module
    assert "build_duplicate_type_kaks.py" in module
    assert "plot_duplicate_type_kaks.R" in module
    assert 'path "plots/duplicate_type_kaks.pdf"' in module
    assert 'path "plots/duplicate_type_kaks.png"' in module

    assert "process RUN_PFAM_CONFIRMATION" in module
    assert 'publishDir "${params.outdir}/tables/pfam_confirmation", mode: "copy", overwrite: true' in module
    assert "run_pfam_confirmation.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--family-members ${family_members_faa}" in module
    assert "--hmm-id ${hmm_id}" in module
    assert 'path "pfam_confirmation_status.tsv"' in module
    assert 'path "identify.ID.fa"' in module

    alignment_module = Path("workflows/modules/alignment_phylogeny.nf").read_text(encoding="utf-8")
    assert "process RUN_MEME_MOTIFS" in alignment_module
    assert 'publishDir "${params.outdir}", mode: "copy", overwrite: true' in alignment_module
    assert "meme ${family_members_faa}" in alignment_module
    assert "-protein" in alignment_module
    assert 'path "meme"' in alignment_module
    assert "--meme-txt ${meme_output}/meme.txt" in alignment_module

    assert "process BUILD_STANDARD_REPORT_INDEX" in module
    assert 'publishDir "${params.outdir}/report", mode: "copy", overwrite: true' in module
    assert "build_standard_report_index.py" in module
    assert "--run-config-snapshot ${run_config_snapshot}" in module
    assert "--family-members-faa ${family_members_faa}" in module
    assert "--gene-family-species-order ${gene_family_species_order}" in module
    assert "--gene-family-copy-number-expansion ${gene_family_copy_number_expansion}" in module
    assert "--gene-family-pangenome-summary ${gene_family_pangenome_summary}" in module
    assert "--phylogeny-manifest ${phylogeny_manifest}" in module
    assert "--alignment-file ${alignment_file}" in module
    assert "--phylogeny-tree ${phylogeny_tree}" in module
    assert "--tree-feature-matrix ${tree_feature_matrix}" in module
    assert "--tree-features-pdf ${tree_features_pdf}" in module
    assert "--tree-features-png ${tree_features_png}" in module
    assert '--promoters-bed "${promoters_bed}"' in module
    assert '--promoters-fasta "${promoters_fasta}"' in module
    assert '--promoter-cis-status "${promoter_cis_status}"' in module
    assert '--feature-summary "${feature_summary}"' in module
    assert '--feature-summary-pdf "${feature_summary_pdf}"' in module
    assert '--feature-summary-png "${feature_summary_png}"' in module
    assert '--mcscanx-circlize-pdf "${mcscanx_circlize_pdf}"' in module
    assert '--mcscanx-circlize-png "${mcscanx_circlize_png}"' in module
    assert '--circlize-link-density "${circlize_link_density}"' in module
    assert '--circlize-duplicate-type-tracks "${circlize_duplicate_type_tracks}"' in module
    assert '--ppi-edges "${ppi_edges}"' in module
    assert '--ppi-nodes "${ppi_nodes}"' in module
    assert '--ppi-hubs "${ppi_hubs}"' in module
    assert '--ppi-input-evidence "${ppi_input_evidence}"' in module
    assert '--ppi-network-qc "${ppi_network_qc}"' in module
    assert '--ppi-node-annotation "${ppi_node_annotation}"' in module
    assert '--ppi-species-annotation "${ppi_species_annotation}"' in module
    assert '--ppi-overview-status "${ppi_overview_status}"' in module
    assert '--ppi-ggnetview-status "${ppi_ggnetview_status}"' in module
    assert '--ppi-pdf "${ppi_pdf}"' in module
    assert '--ppi-png "${ppi_png}"' in module
    assert '--ppi-ggnetview-pdf "${ppi_ggnetview_pdf}"' in module
    assert '--ppi-ggnetview-png "${ppi_ggnetview_png}"' in module
    assert '--expression-status "${expression_status}"' in module
    assert "--wgd-handoff-manifest ${wgd_handoff_manifest}" in module
    assert '--wgd-layers "${wgd_layers}"' in module
    assert '--kaks-wgd-annotations "${kaks_wgd_annotations}"' in module
    assert '--wgd-event-evidence "${wgd_event_evidence}"' in module
    assert '--ks-distribution-pdf "${ks_distribution_pdf}"' in module
    assert '--ks-distribution-png "${ks_distribution_png}"' in module
    assert '--mcscanx-duplicate-types "${mcscanx_duplicate_types}"' in module
    assert '--duplicate-type-kaks "${duplicate_type_kaks}"' in module
    assert '--duplicate-type-kaks-summary "${duplicate_type_kaks_summary}"' in module
    assert '--duplicate-type-kaks-pdf "${duplicate_type_kaks_pdf}"' in module
    assert '--duplicate-type-kaks-png "${duplicate_type_kaks_png}"' in module
    assert "--software-versions ${software_versions}" in module
    assert "--figure-interpretations ${figure_interpretations}" in module
    assert "--published-outdir ${params.outdir}" in module
    assert "--out report_index.tsv" in module

    assert "process ASSEMBLE_STANDARD_REPORT" in module
    assert "val wgd_event_evidence" in module
    assert 'def wgdEvidenceArg = wgd_event_evidence ? "--wgd-event-evidence ${wgd_event_evidence}" : ""' in module
    assert 'publishDir "${params.outdir}/report", mode: "copy", overwrite: true' in module
    assert "assemble_report.py" in module
    assert "process COLLECT_SOFTWARE_VERSIONS" in module
    assert "collect_software_versions.py" in module
    assert "--r-bin ${params.r_bin}" in module
    assert "software_versions.tsv" in module
    assert "process BUILD_FIGURE_INTERPRETATIONS" in module
    assert "build_figure_interpretations.py" in module
    assert "--plot-manifest ${plot_manifest}" in module
    assert "figure_interpretations.tsv" in module
    assert "figure_interpretations.md" in module
    assert "--project-name ${project_name}" in module
    assert "--gene-family ${gene_family}" in module
    assert "--report-index ${report_index}" in module
    assert "--run-config-snapshot ${run_config_snapshot}" in module
    assert "${wgdEvidenceArg}" in module
    assert "--plot-manifest ${plot_manifest}" in module
    assert "--software-versions ${software_versions}" in module
    assert "--figure-interpretations ${figure_interpretations}" in module
    assert "--out final_report.md" in module
    assert "process ORGANIZE_MODULE_RESULTS" in module
    assert "path package_inputs" in module
    assert "mkdir -p organize_source" in module
    assert "cp -RL ${sourceDir}/. organize_source/" in module
    assert 'for item in ${package_inputs}; do' in module
    assert 'if [ -d "\\$item" ] && [ "\\$(basename "\\$item")" = "mcscanx_self_circos" ]; then' in module
    assert "organize_module_results.py" in module
    assert 'path "analysis_modules"' in module
    assert 'def sourceDir = params.outdir.toString().startsWith("/") ? params.outdir : "${projectDir}/../${params.outdir}"' in module
    assert "--source organize_source" in module
    assert "--final-report ${final_report}" in module
    assert "process AUDIT_REAL_REFERENCE_PACKAGE" in module
    assert 'publishDir "${params.outdir}", mode: "copy", overwrite: true' in module
    assert 'path "analysis_modules", emit: package_dir' in module
    assert 'path "report/reference_mvp_package_audit.tsv", emit: tsv' in module
    assert 'path "report/reference_mvp_package_audit.md", emit: md' in module
    assert "cp -RL ${analysis_modules} audited_analysis_modules" in module
    assert "mkdir -p audited_analysis_modules/report report" in module
    assert "--out-tsv audited_analysis_modules/report/reference_mvp_package_audit.tsv" in module
    assert "--out-md audited_analysis_modules/report/reference_mvp_package_audit.md" in module
    assert "cp audited_analysis_modules/report/reference_mvp_package_audit.tsv audited_analysis_modules/report/reference_mvp_package_audit.md report/" in module
    assert "mv audited_analysis_modules analysis_modules" in module
    assert "audit_real_reference_package.py" in module
    assert "--analysis-modules audited_analysis_modules" in module
    assert "--allow-incomplete" in module
    assert "process BUILD_REPRODUCIBILITY_CODE" in module
    assert "build_reproducibility_code.py" in module
    assert "--clean-species-manifest ${clean_species_manifest}" in module
    assert "--reference-manifest ${reference_manifest}" in module
    assert "--family-candidates ${family_candidates}" in module


def test_main_workflow_wires_standard_identification_branch():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "def asBooleanParam(value)" in workflow
    assert "include { VALIDATE_CONFIG } from './modules/config_validation.nf'" in workflow
    assert "VALIDATE_CONFIG(config_ch)" in workflow
    assert "validated_config_ch = VALIDATE_CONFIG.out" in workflow
    assert "if (asBooleanParam(params.mock_external_tools))" in workflow
    assert "include { BUILD_IDENTIFICATION_INPUTS } from './modules/identification_inputs.nf'" in workflow
    assert "include { PREPROCESS_SPECIES; BUILD_REFERENCE_FROM_TAIR_DOMAINS } from './modules/preprocess.nf'" in workflow
    assert "BUILD_RUN_CONFIG_SNAPSHOT;" in workflow
    assert "PUBLISH_PREPROCESS_AUDIT;" in workflow
    assert "BUILD_REPRODUCIBILITY_CODE" in workflow
    assert "EXTRACT_FAMILY_SEQUENCES;" in workflow
    assert "BUILD_WGD_HANDOFF_MANIFEST;" in workflow
    assert "EMPTY_REFERENCE_MANIFEST;" in workflow
    assert "RUN_PFAM_CONFIRMATION;" in workflow
    assert "BUILD_STANDARD_REPORT_INDEX;" in workflow
    assert "ASSEMBLE_STANDARD_REPORT" in workflow
    assert "ORGANIZE_MODULE_RESULTS" in workflow
    assert "EXTRACT_PROMOTERS;" in workflow
    assert "PLOT_FEATURE_SUMMARY;" in workflow
    assert "PLOT_TREE_FEATURES;" in workflow
    assert "PLOT_MCSCANX_CIRCLIZE;" in workflow
    assert "EMPTY_PROMOTER_CIS_ELEMENTS;" in workflow
    assert "BUILD_ARANET_PPI_FROM_RECIPROCAL_BLAST;" in workflow
    assert "PLOT_PPI_GGNETVIEW;" in workflow
    assert "COLLECT_SOFTWARE_VERSIONS" in workflow
    assert "BUILD_FIGURE_INTERPRETATIONS" in workflow
    assert "include { BUILD_REBUILT_HMMER_INPUTS; HMMER_SEARCH; HMMER_SEARCH as HMMER_SEARCH_REBUILT } from './modules/hmmer_search.nf'" in workflow
    assert "include { DIAMOND_SEARCH } from './modules/diamond_search.nf'" in workflow
    assert "DOMAIN_FILTER;" in workflow
    assert "CONCAT_FAMILY_CANDIDATES;" in workflow
    assert "MOCK_IDENTIFICATION_EVIDENCE;" in workflow
    assert "EMPTY_HMMER_EVIDENCE;" in workflow
    assert "EMPTY_DIAMOND_EVIDENCE" in workflow
    assert "} from './modules/domain_filter.nf'" in workflow
    assert "include { FAMILY_SUMMARY } from './modules/family_summary.nf'" in workflow
    assert "include { PREPARE_JCVI_COLLINEARITY; RUN_JCVI_COLLINEARITY } from './modules/jcvi_collinearity.nf'" in workflow
    assert "include { PREPARE_MCSCANX_SELF_CIRCOS; PLOT_MCSCANX_SELF_CIRCOS } from './modules/mcscanx_self_circos.nf'" in workflow
    assert "} else if (params.run_identification) {" in workflow
    assert "PREPROCESS_SPECIES(PREPARE_SPECIES.out)" in workflow
    assert "BUILD_REFERENCE_FROM_TAIR_DOMAINS(validated_config_ch, PREPROCESS_SPECIES.out[1])" in workflow
    assert "BUILD_IDENTIFICATION_INPUTS(validated_config_ch, PREPROCESS_SPECIES.out[1], BUILD_REFERENCE_FROM_TAIR_DOMAINS.out[0])" in workflow
    assert "species_ids_ch = PREPROCESS_SPECIES.out[1]" in workflow
    assert "if (asBooleanParam(params.use_hmmer))" in workflow
    assert "if (asBooleanParam(params.use_diamond))" in workflow
    assert "HMMER_SEARCH(hmmer_inputs_ch)" in workflow
    assert "if (run_two_pass_hmmer_value) {" in workflow
    assert "BUILD_REBUILT_HMMER_INPUTS(HMMER_SEARCH.out.map { species_id, hmmer_tsv -> hmmer_tsv }.collect(), PREPROCESS_SPECIES.out[1], family_name_ch)" in workflow
    assert "two_pass_hmmer_ch = BUILD_REBUILT_HMMER_INPUTS.out.package_dir" in workflow
    assert "HMMER_SEARCH_REBUILT(rebuilt_hmmer_inputs_ch)" in workflow
    assert "hmmer_evidence_ch = HMMER_SEARCH_REBUILT.out" in workflow
    assert "EMPTY_HMMER_EVIDENCE(species_ids_ch)" in workflow
    assert "DIAMOND_SEARCH(diamond_inputs_ch)" in workflow
    assert "EMPTY_DIAMOND_EVIDENCE(species_ids_ch)" in workflow
    assert "joined_evidence_ch = hmmer_evidence_ch" in workflow
    assert ".join(diamond_evidence_ch, by: 0)" in workflow
    assert "if (asBooleanParam(params.mock_external_tools))" in workflow
    assert "EMPTY_REFERENCE_MANIFEST()" in workflow
    assert "reference_manifest_ch = EMPTY_REFERENCE_MANIFEST.out" in workflow
    assert "MOCK_IDENTIFICATION_EVIDENCE(mock_evidence_ch)" in workflow
    assert "joined_evidence_ch = MOCK_IDENTIFICATION_EVIDENCE.out" in workflow
    assert "DOMAIN_FILTER(joined_evidence_ch, final_rule_ch)" in workflow
    assert "CONCAT_FAMILY_CANDIDATES(candidate_tables_ch.collect())" in workflow
    assert "BUILD_REPRODUCIBILITY_CODE(" in workflow
    assert "validated_config_ch," in workflow
    assert "PREPROCESS_SPECIES.out[1]," in workflow
    assert "reference_manifest_ch," in workflow
    assert "CONCAT_FAMILY_CANDIDATES.out" in workflow
    assert "if (!asBooleanParam(params.standard_stop_after_family_candidates))" in workflow
    assert "PUBLISH_PREPROCESS_AUDIT(" in workflow
    assert "PREPROCESS_SPECIES.out[3]," in workflow
    assert "PREPROCESS_SPECIES.out[4]," in workflow
    assert "PREPROCESS_SPECIES.out[5]," in workflow
    assert "BUILD_RUN_CONFIG_SNAPSHOT(validated_config_ch, PREPROCESS_SPECIES.out[1])" in workflow
    assert "BUILD_WGD_HANDOFF_MANIFEST(CONCAT_FAMILY_CANDIDATES.out)" in workflow
    assert 'project_name_value = params.project_name != "GDSL_demo" ? params.project_name : (yaml_project.name ?: params.project_name)' in workflow
    assert 'gene_family_value = params.gene_family != "GDSL" ? params.gene_family : (yaml_gene_family.name ?: params.gene_family)' in workflow
    assert "project_name_ch = Channel.value(project_name_value)" in workflow
    assert "family_name_ch = Channel.value(gene_family_value)" in workflow
    assert "pfam_confirm_hmm_id_value = params.pfam_confirm_hmm_id ?: (yaml_gene_family.hmm_profiles ? yaml_gene_family.hmm_profiles[0].id : gene_family_value)" in workflow
    assert "RUN_PFAM_CONFIRMATION(CONCAT_FAMILY_CANDIDATES.out, EXTRACT_FAMILY_SEQUENCES.out, pfam_confirm_hmm_id_value, pfam_db_value, hmmscan_domtbl_value)" in workflow
    assert "reference_kaks_inputs_ch = Channel.value(\"\")" in workflow
    assert "reference_kaks_failure_summary_ch = Channel.value(\"\")" in workflow
    assert "reference_manifest_ch = Channel.empty()" in workflow
    assert "reference_manifest_ch = BUILD_REFERENCE_FROM_TAIR_DOMAINS.out[1]" in workflow
    assert "two_pass_hmmer_ch = Channel.empty()" in workflow
    assert "standard_wgd_layers_ch = Channel.value(\"\")" in workflow
    assert "standard_kaks_wgd_annotations_ch = Channel.value(\"\")" in workflow
    assert "standard_wgd_event_evidence_ch = Channel.value(\"\")" in workflow
    assert "standard_ks_distribution_pdf_ch = Channel.value(\"\")" in workflow
    assert "standard_ks_distribution_png_ch = Channel.value(\"\")" in workflow
    assert "standard_mcscanx_duplicate_types_ch = Channel.value(\"\")" in workflow
    assert "standard_duplicate_type_kaks_ch = Channel.value(\"\")" in workflow
    assert "standard_duplicate_type_kaks_summary_ch = Channel.value(\"\")" in workflow
    assert "standard_duplicate_type_kaks_pdf_ch = Channel.value(\"\")" in workflow
    assert "standard_duplicate_type_kaks_png_ch = Channel.value(\"\")" in workflow
    assert "PREPARE_REFERENCE_KAKS_INPUTS(PREPROCESS_SPECIES.out[1], RUN_JCVI_COLLINEARITY.out, PLOT_MCSCANX_SELF_CIRCOS.out.package_dir)" in workflow
    assert "RUN_REFERENCE_KAKS_CALCULATOR(PREPARE_REFERENCE_KAKS_INPUTS.out[1], PREPARE_REFERENCE_KAKS_INPUTS.out[4])" in workflow
    assert "NORMALIZE_REFERENCE_KAKS_RESULTS(RUN_REFERENCE_KAKS_CALCULATOR.out[2], RUN_REFERENCE_KAKS_CALCULATOR.out[4])" in workflow
    assert "reference_kaks_failure_summary_ch = RUN_REFERENCE_KAKS_CALCULATOR.out[5]" in workflow
    assert "if (run_standard_wgd_value) {" in workflow
    assert "CLASSIFY_STANDARD_WGD_LAYERS(NORMALIZE_REFERENCE_KAKS_RESULTS.out[0], Channel.value(params.ks_bins), Channel.value(params.wgd_event_args ?: \"\"))" in workflow
    assert "BUILD_STANDARD_KAKS_WGD_ANNOTATIONS(CLASSIFY_STANDARD_WGD_LAYERS.out)" in workflow
    assert "BUILD_STANDARD_WGD_EVENT_EVIDENCE(CLASSIFY_STANDARD_WGD_LAYERS.out, Channel.value(file(params.events_config)))" in workflow
    assert "PLOT_STANDARD_KAKS_WGD(NORMALIZE_REFERENCE_KAKS_RESULTS.out[0], BUILD_STANDARD_KAKS_WGD_ANNOTATIONS.out)" in workflow
    assert "BUILD_STANDARD_MCSCANX_DUPLICATE_TYPES(PLOT_MCSCANX_SELF_CIRCOS.out.package_dir)" in workflow
    assert "PLOT_STANDARD_DUPLICATE_TYPE_KAKS(BUILD_STANDARD_MCSCANX_DUPLICATE_TYPES.out, NORMALIZE_REFERENCE_KAKS_RESULTS.out[0])" in workflow
    assert "standard_kaks_wgd_annotations_ch = BUILD_STANDARD_KAKS_WGD_ANNOTATIONS.out" in workflow
    assert "standard_ks_distribution_png_ch = PLOT_STANDARD_KAKS_WGD.out[1]" in workflow
    assert "standard_mcscanx_duplicate_types_ch = BUILD_STANDARD_MCSCANX_DUPLICATE_TYPES.out" in workflow
    assert "standard_duplicate_type_kaks_ch = PLOT_STANDARD_DUPLICATE_TYPE_KAKS.out[0]" in workflow
    assert "standard_duplicate_type_kaks_summary_ch = PLOT_STANDARD_DUPLICATE_TYPE_KAKS.out[1]" in workflow
    assert "standard_duplicate_type_kaks_png_ch = PLOT_STANDARD_DUPLICATE_TYPE_KAKS.out[4]" in workflow
    assert "FAMILY_SUMMARY(CONCAT_FAMILY_CANDIDATES.out)" in workflow
    assert "EXTRACT_FAMILY_SEQUENCES(CONCAT_FAMILY_CANDIDATES.out, PREPROCESS_SPECIES.out[1])" in workflow
    assert "yaml_modules = yaml_config.modules ?: [:]" in workflow
    assert "run_promoter_value = asBooleanParam(params.run_promoter) || yaml_modules.promoter == true" in workflow
    assert "if (run_promoter_value)" in workflow
    assert "EXTRACT_PROMOTERS(" in workflow
    assert "CONCAT_FAMILY_CANDIDATES.out," in workflow
    assert "PREPROCESS_SPECIES.out[1]," in workflow
    assert "run_feature_summary_value = asBooleanParam(params.run_feature_summary) || yaml_modules.feature_summary == true" in workflow
    assert "if (run_feature_summary_value)" in workflow
    assert "PLOT_TREE_FEATURES(" in workflow
    assert "PLOT_FEATURE_SUMMARY(" in workflow
    assert "run_mcscanx_circlize_value = asBooleanParam(params.run_mcscanx_circlize) || yaml_modules.synteny == true" in workflow
    assert "if (run_mcscanx_circlize_value) {" in workflow
    assert "PREPARE_JCVI_COLLINEARITY(CONCAT_FAMILY_CANDIDATES.out, PREPROCESS_SPECIES.out[1])" in workflow
    assert "RUN_JCVI_COLLINEARITY(PREPARE_JCVI_COLLINEARITY.out)" in workflow
    assert 'mcscanx_self_search_tool_value = params.mcscanx_self_search_tool ?: (yaml_mcscanx.search_tool ?: "diamond")' in workflow
    assert "PREPARE_MCSCANX_SELF_CIRCOS(CONCAT_FAMILY_CANDIDATES.out, PREPROCESS_SPECIES.out[1], mcscanx_self_dir_value, mcscanx_self_search_tool_value)" in workflow
    assert "PLOT_MCSCANX_SELF_CIRCOS(EXTRACT_CHROMOSOME_LOCATIONS.out, PREPARE_MCSCANX_SELF_CIRCOS.out)" in workflow
    assert "mcscanx_self_circos_ch = PLOT_MCSCANX_SELF_CIRCOS.out.package_dir" in workflow
    assert "circlize_link_density_ch = PLOT_MCSCANX_SELF_CIRCOS.out.link_density" in workflow
    assert "circlize_duplicate_type_tracks_ch = PLOT_MCSCANX_SELF_CIRCOS.out.duplicate_type_tracks" in workflow
    assert "mcscanx_circlize_pdf_ch = PLOT_MCSCANX_SELF_CIRCOS.out.pdf" in workflow
    assert "mcscanx_circlize_png_ch = PLOT_MCSCANX_SELF_CIRCOS.out.png" in workflow
    assert "if (run_mcscanx_circlize_value && syntenic_pairs_value)" not in workflow
    assert "PLOT_MCSCANX_CIRCLIZE(EXTRACT_CHROMOSOME_LOCATIONS.out" not in workflow
    assert "circlize_link_density_ch = PLOT_MCSCANX_CIRCLIZE.out[2]" not in workflow
    assert "circlize_duplicate_type_tracks_ch = PLOT_MCSCANX_CIRCLIZE.out[3]" not in workflow
    assert "mcscanx_circlize_pdf_ch = PLOT_MCSCANX_CIRCLIZE.out[5]" not in workflow
    assert "mcscanx_circlize_png_ch = PLOT_MCSCANX_CIRCLIZE.out[6]" not in workflow
    assert "run_ppi_value = asBooleanParam(params.run_ppi) || yaml_modules.ppi == true" in workflow
    assert "ppi_edges_value = params.ppi_edges ?: (yaml_ppi.edges ?: \"\")" in workflow
    assert "ppi_reference_species_value = params.ppi_reference_species ?: (yaml_ppi.reference_species ?: (yaml_reference_generation.reference_species ?: \"Arabidopsis_thaliana\"))" in workflow
    assert "mcscanx_self_dir_value = params.mcscanx_self_dir ?: (yaml_mcscanx.self_dir ?: \"\")" in workflow
    assert "params.mcscanx_execute_self = params.mcscanx_execute_self ?: (yaml_mcscanx.execute_self ?: false)" in workflow
    assert "if (run_ppi_value && ppi_edges_value)" in workflow
    assert "BUILD_ARANET_PPI_FROM_RECIPROCAL_BLAST(" in workflow
    assert "PREPROCESS_SPECIES.out[1]," in workflow
    assert "ppi_reference_species_value" in workflow
    assert "PLOT_PPI_GGNETVIEW(BUILD_ARANET_PPI_FROM_RECIPROCAL_BLAST.out[0], ppi_nodes_input_ch)" in workflow
    assert "ppi_input_evidence_ch = PLOT_PPI_GGNETVIEW.out[3]" in workflow
    assert "ppi_network_qc_ch = PLOT_PPI_GGNETVIEW.out[4]" in workflow
    assert "ppi_overview_status_ch = PLOT_PPI_GGNETVIEW.out[5]" in workflow
    assert "ppi_ggnetview_status_ch = PLOT_PPI_GGNETVIEW.out[6]" in workflow
    assert "ppi_pdf_ch = PLOT_PPI_GGNETVIEW.out[7]" in workflow
    assert "ppi_png_ch = PLOT_PPI_GGNETVIEW.out[8]" in workflow
    assert "ppi_ggnetview_pdf_ch = PLOT_PPI_GGNETVIEW.out[9]" in workflow
    assert "ppi_ggnetview_png_ch = PLOT_PPI_GGNETVIEW.out[10]" in workflow
    assert "ppi_node_annotation_ch = PLOT_PPI_GGNETVIEW.out[11]" in workflow
    assert "ppi_species_annotation_ch = PLOT_PPI_GGNETVIEW.out[12]" in workflow
    assert "PREPARE_ALIGNMENT_INPUTS(family_name_ch, EXTRACT_FAMILY_SEQUENCES.out, aligner_ch, alignment_outdir_ch)" in workflow
    assert "PREPARE_PHYLOGENY_INPUTS(PREPARE_ALIGNMENT_INPUTS.out, tree_builder_ch, phylogeny_outdir_ch)" in workflow
    assert "RUN_MEME_MOTIFS(EXTRACT_FAMILY_SEQUENCES.out)" in workflow
    assert "PARSE_MEME_MOTIFS(RUN_MEME_MOTIFS.out, family_name_ch)" in workflow
    assert "PLOT_FAMILY_COUNTS(FAMILY_SUMMARY.out)" in workflow
    assert "PLOT_FAMILY_COUNTS.out[0]" in workflow
    assert "PLOT_FAMILY_COUNTS.out[1]" in workflow
    assert "BUILD_PLOT_MANIFEST(" in workflow
    assert "run_feature_summary_value," in workflow
    assert "run_standard_wgd_value," in workflow
    assert "run_ppi_value && ppi_edges_value," in workflow
    assert "COLLECT_SOFTWARE_VERSIONS()" in workflow
    assert "BUILD_FIGURE_INTERPRETATIONS(BUILD_PLOT_MANIFEST.out)" in workflow
    assert "BUILD_STANDARD_REPORT_INDEX(" in workflow
    assert "BUILD_RUN_CONFIG_SNAPSHOT.out" in workflow
    assert "PLOT_TREE_FEATURES.out[0]" in workflow
    assert "PLOT_TREE_FEATURES.out[1]" in workflow
    assert "PLOT_TREE_FEATURES.out[2]" in workflow
    assert "ppi_ggnetview_pdf_ch" in workflow
    assert "promoter_cis_status_ch = EMPTY_PROMOTER_CIS_ELEMENTS.out[5]" in workflow
    assert "expression_status_ch = EMPTY_EXPRESSION_STATUS.out[0]" in workflow
    assert "promoter_cis_status_ch," in workflow
    assert "expression_status_ch," in workflow
    assert "BUILD_WGD_HANDOFF_MANIFEST.out" in workflow
    assert "reference_kaks_failure_summary_ch," in workflow
    assert "standard_kaks_wgd_annotations_ch," in workflow
    assert "standard_ks_distribution_png_ch," in workflow
    assert "standard_mcscanx_duplicate_types_ch," in workflow
    assert "standard_duplicate_type_kaks_ch," in workflow
    assert "standard_duplicate_type_kaks_summary_ch," in workflow
    assert "standard_duplicate_type_kaks_png_ch," in workflow
    assert "ASSEMBLE_STANDARD_REPORT(project_name_ch, family_name_ch, BUILD_STANDARD_REPORT_INDEX.out, BUILD_RUN_CONFIG_SNAPSHOT.out, standard_wgd_event_evidence_ch, reference_kaks_failure_summary_ch, BUILD_PLOT_MANIFEST.out, COLLECT_SOFTWARE_VERSIONS.out, BUILD_FIGURE_INTERPRETATIONS.out[0])" in workflow
    assert "ORGANIZE_MODULE_RESULTS(ASSEMBLE_STANDARD_REPORT.out, two_pass_hmmer_ch.concat(jcvi_collinearity_ch).concat(mcscanx_self_circos_ch).concat(reference_kaks_inputs_ch).concat(reference_kaks_results_ch).concat(reference_kaks_pairs_ch).concat(reference_kaks_failure_summary_ch).concat(standard_wgd_layers_ch).concat(standard_wgd_event_evidence_ch).concat(standard_ks_distribution_pdf_ch).concat(standard_ks_distribution_png_ch).concat(standard_mcscanx_duplicate_types_ch).concat(standard_duplicate_type_kaks_ch).concat(standard_duplicate_type_kaks_summary_ch).concat(standard_duplicate_type_kaks_pdf_ch).concat(standard_duplicate_type_kaks_png_ch).concat(RUN_PFAM_CONFIRMATION.out[0]).filter { it }.collect())" in workflow
    assert "AUDIT_REAL_REFERENCE_PACKAGE(ORGANIZE_MODULE_RESULTS.out)" in workflow
    assert 'AUDIT_REAL_REFERENCE_PACKAGE.out.tsv.view { audit -> "Reference MVP package audit: ${audit}" }' in workflow
    assert "Module result package:" in workflow


def test_duplication_retention_module_exposes_wgd_helper_processes():
    module = Path("workflows/modules/duplication_retention.nf").read_text(encoding="utf-8")

    assert "process PREPARE_MCSCANX_KAKS_HANDOFF" in module
    assert 'publishDir "${params.outdir}/mcscanx_kaks_handoff", mode: "copy", overwrite: true' in module
    assert "build_mcscanx_kaks_handoff.py" in module
    assert "--collinearity ${collinearity}" in module
    assert "--kaks ${kaks}" in module
    assert "--outdir ." in module
    assert 'path "tables/syntenic_pairs.tsv"' in module
    assert 'path "tables/duplicate_types.tsv"' in module
    assert 'path "tables/kaks_pairs.tsv"' in module

    assert "process BUILD_WGD_RUN_CONFIG_SNAPSHOT" in module
    assert "build_wgd_run_config_snapshot.py" in module
    assert "--events-config ${events_config}" in module
    assert "--ks-bins ${ks_bins}" in module
    assert '--event-args "${event_args}"' in module
    assert "--out wgd_run_config_snapshot.tsv" in module

    assert "process NORMALIZE_DUPLICATE_TYPES" in module
    assert 'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true' in module
    assert "normalize_duplicate_types.py" in module
    assert "--duplicates ${duplicates}" in module
    assert "--out normalized_duplicate_types.tsv" in module

    assert "process JOIN_FAMILY_DUPLICATES" in module
    assert "join_family_duplicates.py" in module
    assert "--family-members ${family_members}" in module
    assert "--duplicates ${normalized_duplicates}" in module
    assert "--out family_duplicate_classification.tsv" in module

    assert "process CLASSIFY_WGD_LAYERS" in module
    assert "classify_wgd_layers.py" in module
    assert "--bins ${ks_bins}" in module
    assert "--out wgd_layers.tsv" in module

    assert "process BUILD_KAKS_WGD_ANNOTATIONS" in module
    assert "build_kaks_plot_annotations.py" in module
    assert "--classified-pairs ${classified_pairs}" in module
    assert "--out kaks_wgd_annotations.tsv" in module
    assert 'path "kaks_wgd_annotations.tsv"' in module

    assert "process BUILD_WGD_EVENT_EVIDENCE" in module
    assert "build_wgd_event_evidence.py" in module
    assert "--events-config ${events_config}" in module
    assert "--out wgd_event_evidence.tsv" in module

    assert "process ANNOTATE_FAMILY_WGD_EVENTS" in module
    assert "annotate_family_wgd_events.py" in module
    assert "--family-duplicates ${family_duplicates}" in module
    assert "--classified-pairs ${classified_pairs}" in module
    assert "--out family_wgd_event_membership.tsv" in module

    assert "process SUMMARIZE_FAMILY_EVENT_RETENTION" in module
    assert "summarize_family_event_retention.py" in module
    assert "--family-wgd-events ${family_wgd_events}" in module
    assert "--out family_event_retention_summary.tsv" in module

    assert "process RETENTION_ENRICHMENT" in module
    assert "retention_enrichment.py" in module
    assert "--family-duplicates ${family_duplicates}" in module
    assert "--background-duplicates ${background_duplicates}" in module
    assert "--out retention_enrichment.tsv" in module

    assert "process PLOT_DUPLICATE_TYPE_KAKS" in module
    assert "build_duplicate_type_kaks.py" in module
    assert "plot_duplicate_type_kaks.R" in module
    assert "--duplicates ${normalized_duplicates}" in module
    assert "--kaks-pairs ${kaks_pairs}" in module
    assert 'path "tables/duplicate_type_kaks.tsv"' in module
    assert 'path "tables/duplicate_type_kaks_summary.tsv"' in module
    assert 'path "plots/duplicate_type_kaks.pdf"' in module
    assert 'path "plots/duplicate_type_kaks.png"' in module

    assert "process PLOT_PANGENOME_KAKS" in module
    assert "build_pangenome_kaks.py" in module
    assert "plot_pangenome_kaks.R" in module
    assert "--pangenome-classes ${pangenome_classes}" in module
    assert "--kaks-pairs ${kaks_pairs}" in module
    assert 'path "tables/pangenome_kaks.tsv"' in module
    assert 'path "tables/pangenome_kaks_summary.tsv"' in module
    assert 'path "tables/pangenome_kaks_skipped.tsv"' in module
    assert 'path "plots/pangenome_kaks.pdf"' in module
    assert 'path "plots/pangenome_kaks.png"' in module

    assert "process BUILD_WGD_PLOT_MANIFEST" in module
    assert "build_plot_manifest.py" in module
    assert '--plot "ks_distribution=plots/ks_distribution.pdf=Ks distribution for duplicated pairs and WGD layer interpretation"' in module
    assert '--plot "duplicate_type_kaks=plots/duplicate_type_kaks.pdf=Duplicate-type grouped Ks and Ka/Ks selection overview"' in module
    assert '--plot "pangenome_kaks=plots/pangenome_kaks.pdf=Pangenome-class grouped Ks and Ka/Ks selection overview"' in module
    assert "--out plot_manifest.tsv" in module
    assert "process COLLECT_WGD_SOFTWARE_VERSIONS" in module
    assert "collect_software_versions.py" in module
    assert "--r-bin ${params.r_bin}" in module
    assert "process BUILD_WGD_FIGURE_INTERPRETATIONS" in module
    assert "build_figure_interpretations.py" in module
    assert "--plot-manifest ${plot_manifest}" in module

    assert "process BUILD_WGD_REPORT_INDEX" in module
    assert "build_wgd_report_index.py" in module
    assert "--published-outdir ${published_outdir}" in module
    assert "--out report_index.tsv" in module

    assert "process ASSEMBLE_WGD_REPORT" in module
    assert "assemble_report.py" in module
    assert "--wgd-event-evidence ${wgd_event_evidence}" in module
    assert "--run-config-snapshot ${wgd_run_config_snapshot}" in module
    assert "--family-event-retention ${family_event_retention}" in module
    assert "--retention-enrichment ${retention_enrichment}" in module
    assert "--plot-manifest ${plot_manifest}" in module
    assert "--software-versions ${software_versions}" in module
    assert "--figure-interpretations ${figure_interpretations}" in module
    assert "--out final_report.md" in module


def test_mcscanx_self_circos_module_prepares_and_plots_self_outputs():
    module = Path("workflows/modules/mcscanx_self_circos.nf").read_text(encoding="utf-8")

    assert "process PREPARE_MCSCANX_SELF_CIRCOS" in module
    assert "process PLOT_MCSCANX_SELF_CIRCOS" in module
    assert "build_circlize_inputs.py" in module
    assert "plot_mcscanx_circlize.R" in module
    assert "--syntenic-pairs mcscanx_self_circos/mcscanx_gene_pairs.tsv" in module
    assert "mcscanx_circlize_status.tsv" in module
    assert 'path "mcscanx_self_circos", emit: package_dir' in module
    assert 'path "tables/circlize_link_density.tsv", emit: link_density' in module
    assert 'path "tables/circlize_duplicate_type_tracks.tsv", emit: duplicate_type_tracks' in module
    assert 'path "plots/mcscanx_circlize.pdf", optional: true, emit: pdf' in module
    assert 'path "plots/mcscanx_circlize.png", optional: true, emit: png' in module
    assert 'path "plots/species", optional: true, emit: species_plots' in module
    assert "cp mcscanx_self_circos/tables/circlize_link_density.tsv tables/circlize_link_density.tsv" in module
    assert "cp -R mcscanx_self_circos/plots/species plots/species" in module


def test_jcvi_collinearity_module_prepares_and_runs_when_available():
    module = Path("workflows/modules/jcvi_collinearity.nf").read_text(encoding="utf-8")

    assert "process PREPARE_JCVI_COLLINEARITY" in module
    assert "process RUN_JCVI_COLLINEARITY" in module
    assert "run_jcvi_collinearity.py" in module
    assert "--jcvi-dir jcvi_collinearity" in module
    assert "--python-bin ${params.python_bin}" in module
    assert "jcvi_run_status.tsv" in module


def test_main_workflow_includes_duplication_retention_processes():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "PREPARE_MCSCANX_KAKS_HANDOFF;" in workflow
    assert "if (params.mcscanx_collinearity && params.kaks_results)" in workflow
    assert "PREPARE_MCSCANX_KAKS_HANDOFF(" in workflow
    assert "duplicates_ch = PREPARE_MCSCANX_KAKS_HANDOFF.out[1]" in workflow
    assert "kaks_pairs_ch = PREPARE_MCSCANX_KAKS_HANDOFF.out[3]" in workflow
    assert "Missing WGD inputs: provide either --duplicates/--kaks_pairs or --mcscanx_collinearity/--kaks_results" in workflow
    assert "BUILD_WGD_RUN_CONFIG_SNAPSHOT" in workflow
    assert "BUILD_WGD_RUN_CONFIG_SNAPSHOT(duplicates_ch, family_members_ch, kaks_pairs_ch, events_config_ch, ks_bins_ch, event_args_ch)" in workflow
    assert "NORMALIZE_DUPLICATE_TYPES" in workflow
    assert "JOIN_FAMILY_DUPLICATES" in workflow
    assert "CLASSIFY_WGD_LAYERS" in workflow
    assert "BUILD_KAKS_WGD_ANNOTATIONS" in workflow
    assert "BUILD_KAKS_WGD_ANNOTATIONS(CLASSIFY_WGD_LAYERS.out)" in workflow
    assert "PLOT_KAKS(kaks_pairs_ch, BUILD_KAKS_WGD_ANNOTATIONS.out)" in workflow
    assert "BUILD_WGD_EVENT_EVIDENCE" in workflow
    assert "ANNOTATE_FAMILY_WGD_EVENTS" in workflow
    assert "SUMMARIZE_FAMILY_EVENT_RETENTION" in workflow
    assert "RETENTION_ENRICHMENT" in workflow
    assert "PLOT_DUPLICATE_TYPE_KAKS" in workflow
    assert "PLOT_DUPLICATE_TYPE_KAKS(NORMALIZE_DUPLICATE_TYPES.out, kaks_pairs_ch)" in workflow
    assert "pangenome_classes_ch = Channel.value(params.pangenome_classes ? file(params.pangenome_classes) : \"\")" in workflow
    assert "if (params.pangenome_classes)" in workflow
    assert "PLOT_PANGENOME_KAKS(pangenome_classes_ch, kaks_pairs_ch)" in workflow
    assert "BUILD_WGD_PLOT_MANIFEST()" in workflow
    assert "COLLECT_WGD_SOFTWARE_VERSIONS()" in workflow
    assert "BUILD_WGD_FIGURE_INTERPRETATIONS(BUILD_WGD_PLOT_MANIFEST.out)" in workflow
    assert "BUILD_WGD_REPORT_INDEX(outdir_ch)" in workflow
    assert "BUILD_WGD_RUN_CONFIG_SNAPSHOT.out," in workflow
    assert "ASSEMBLE_WGD_REPORT(" in workflow
    assert "BUILD_WGD_PLOT_MANIFEST.out," in workflow
    assert "COLLECT_WGD_SOFTWARE_VERSIONS.out," in workflow
    assert "BUILD_WGD_FIGURE_INTERPRETATIONS.out[0]" in workflow


def test_report_module_assembles_final_markdown():
    module = Path("workflows/modules/report.nf").read_text(encoding="utf-8")

    assert "process ASSEMBLE_REPORT" in module
    assert "assemble_report.py" in module
    assert "--project-name ${project_name}" in module
    assert "--gene-family ${gene_family}" in module
    assert "--report-index ${report_index}" in module
    assert "--out final_report.md" in module


def test_main_workflow_includes_report_process():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "include { ASSEMBLE_REPORT } from './modules/report.nf'" in workflow


def test_plot_module_runs_r_scripts_through_configured_r_bin():
    module = Path("workflows/modules/plots.nf").read_text(encoding="utf-8")

    assert "process PLOT_FAMILY_COUNTS" in module
    assert 'publishDir "${params.outdir}", mode: "copy", overwrite: true' in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_family_counts.R" in module
    assert "--args ${family_counts} plots" in module
    assert 'path "plots/family_counts.pdf"' in module
    assert 'path "plots/family_counts.png"' in module

    assert "process PLOT_KAKS" in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_kaks.R" in module
    assert "--args ${kaks_pairs} ${kaks_annotations} plots" in module
    assert 'path "plots/ks_distribution.pdf"' in module
    assert 'path "plots/ks_distribution.png"' in module

    assert "process PLOT_EXPRESSION_HEATMAP" in module
    assert "build_expression_summary.py" in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_expression_heatmap.R" in module
    assert "--expression ${expression_matrix}" in module
    assert "--metadata ${sample_metadata}" in module
    assert 'path "plots/expression_heatmap.pdf"' in module
    assert 'path "plots/expression_heatmap.png"' in module
    assert 'path "tables/expression_sample_metadata.tsv"' in module
    assert 'path "tables/expression_group_matrix.tsv"' in module
    assert 'path "tables/expression_gene_summary.tsv"' in module

    assert "process PLOT_FEATURE_SUMMARY" in module
    assert "summarize_feature_tables.py" in module
    assert "plot_feature_summary.R" in module
    assert "--domains ${domains}" in module
    assert 'path "tables/feature_summary.tsv"' in module
    assert 'path "plots/feature_summary.pdf"' in module
    assert 'path "plots/feature_summary.png"' in module

    assert "process PLOT_GENE_FAMILY_INFO" in module
    assert "build_gene_family_info.py" in module
    assert "plot_gene_family_info.R" in module
    assert "--family-counts ${family_counts}" in module
    assert "--family-members-faa ${family_members_faa}" in module
    assert 'path "tables/gene_family_copy_number.tsv"' in module
    assert 'path "tables/gene_family_copy_number_summary.tsv"' in module
    assert 'path "tables/gene_family_species_order.tsv"' in module
    assert 'path "tables/gene_family_copy_number_expansion.tsv"' in module
    assert 'path "tables/gene_family_pangenome_summary.tsv"' in module
    assert 'path "tables/gene_family_protein_properties.tsv"' in module
    assert 'path "plots/gene_family_info_summary.pdf"' in module
    assert 'path "plots/gene_family_info_summary.png"' in module
    assert 'speciesOrderArg=""' in module
    assert 'speciesOrderParam="${params.gene_family_species_order}"' in module
    assert "params.gene_family_species_order" in module
    assert '[ "\\${speciesOrderParam}" != "null" ]' in module
    assert 'speciesOrderArg="--species-order ${params.gene_family_species_order}"' in module
    assert "${speciesOrderArg}" in module
    assert "--args tables/gene_family_copy_number.tsv tables/gene_family_copy_number_summary.tsv tables/gene_family_protein_properties.tsv tables/gene_family_species_order.tsv tables/gene_family_copy_number_expansion.tsv tables/gene_family_pangenome_summary.tsv plots" in module

    assert "process PLOT_PROMOTER_CIS_ELEMENTS" in module
    assert "build_promoter_cis_elements.py" in module
    assert "plot_promoter_cis_elements.R" in module
    assert "--cis-elements ${cis_elements}" in module
    assert 'def descriptionsArg = element_descriptions ? "--element-descriptions ${element_descriptions}" : ""' in module
    assert "${descriptionsArg}" in module
    assert 'path "tables/promoter_cis_elements.tsv"' in module
    assert 'path "tables/promoter_cis_gene_matrix.tsv"' in module
    assert 'path "tables/promoter_cis_gene_element_matrix.tsv"' in module
    assert 'path "tables/promoter_cis_category_summary.tsv"' in module
    assert 'path "tables/promoter_cis_element_annotations.tsv"' in module
    assert "--args tables/promoter_cis_gene_matrix.tsv tables/promoter_cis_category_summary.tsv tables/promoter_cis_gene_element_matrix.tsv tables/promoter_cis_element_annotations.tsv plots" in module
    assert 'path "plots/promoter_cis_elements.pdf"' in module
    assert 'path "plots/promoter_cis_elements.png"' in module
    assert 'path "plots/promoter1.pdf"' in module
    assert 'path "plots/promoter1.png"' in module
    assert 'path "plots/species_promoter2.pdf"' in module
    assert 'path "plots/species_promoter2.png"' in module

    assert "process PLOT_TREE_FEATURES" in module
    assert "build_tree_feature_matrix.py" in module
    assert "plot_tree_features.R" in module
    assert "--tree ${phylogeny_tree}" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--gene-structures ${gene_structures}" in module
    assert 'path "tables/tree_feature_matrix.tsv"' in module
    assert 'path "plots/tree_features.pdf"' in module
    assert 'path "plots/tree_features.png"' in module

    assert "process PLOT_MCSCANX_CIRCLIZE" in module
    assert "build_circlize_inputs.py" in module
    assert "plot_mcscanx_circlize.R" in module
    assert "--chromosome-locations ${chromosome_locations}" in module
    assert "--syntenic-pairs ${syntenic_pairs}" in module
    assert 'path "tables/circlize_chromosomes.tsv"' in module
    assert 'path "tables/circlize_link_density.tsv"' in module
    assert 'path "tables/circlize_duplicate_type_tracks.tsv"' in module
    assert "--out-density tables/circlize_link_density.tsv" in module
    assert "--out-duplicate-tracks tables/circlize_duplicate_type_tracks.tsv" in module
    assert "--args tables/circlize_chromosomes.tsv tables/circlize_links.tsv tables/circlize_link_density.tsv tables/circlize_duplicate_type_tracks.tsv plots" in module
    assert 'path "plots/mcscanx_circlize.pdf"' in module

    assert "process PLOT_PPI_GGNETVIEW" in module
    assert "build_ppi_tables.py" in module
    assert "plot_ppi_ggnetview.R" in module
    assert "--edges ${ppi_edges}" in module
    assert 'path "tables/ppi_edges.tsv"' in module
    assert 'path "tables/ppi_nodes.tsv"' in module
    assert 'path "tables/ppi_hubs.tsv"' in module
    assert 'path "tables/ppi_input_evidence.tsv"' in module
    assert 'path "tables/ppi_network_qc.tsv"' in module
    assert 'path "tables/node_annotation.tsv"' in module
    assert 'path "tables/species_ppi_annotation.tsv"' in module
    assert 'path "tables/ppi_overview_status.tsv"' in module
    assert 'path "tables/ppi_ggnetview_status.tsv"' in module
    assert 'path "plots/ppi.pdf"' in module
    assert 'path "plots/ppi.png"' in module
    assert 'path "plots/ppi_ggnetview.pdf"' in module
    assert 'path "plots/ppi_ggnetview.png"' in module
    assert "process BUILD_ARANET_PPI_FROM_RECIPROCAL_BLAST" in module
    assert "build_aranet_ppi_from_reciprocal_blast.py" in module
    assert 'path "tables/ppi_transferred_edges.tsv"' in module
    assert 'path "tables/ppi_transferred_nodes.tsv"' in module
    assert 'path "tables/ppi_transfer_evidence.tsv"' in module
    assert 'path "tables/ppi_homology_best_hits.tsv"' in module
    assert 'path "tables/ppi_blast_manifest.tsv"' in module
    assert 'path "tables/ppi_blast/*/*.tsv"' in module
    assert "--workdir tables/ppi_blast" in module

    assert "process BUILD_PLOT_MANIFEST" in module
    assert 'publishDir "${params.outdir}/report", mode: "copy", overwrite: true' in module
    assert "build_plot_manifest.py" in module
    assert "plotArgs=(" in module
    assert '--plot "family_counts=plots/family_counts.pdf=Family member counts by species"' in module
    assert '--plot "gene_family_info_summary=plots/gene_family_info_summary.pdf=Gene family copy-number and protein-property summary"' in module
    assert '--plot "gene_family_pangenome_summary=plots/gene_family_info_summary.pdf=Gene family pangenome presence and copy-number balance"' in module
    assert '--plot "tree_features=plots/tree_features.pdf=Tree, motif, gene-structure, and domain composite plot"' in module
    assert "val run_feature_summary" in module
    assert "val run_kaks_wgd" in module
    assert 'if [ "${run_feature_summary}" = "true" ]; then' in module
    assert '--plot "feature_summary=plots/feature_summary.pdf=Integrated domain, motif, gene-structure, synteny, promoter, and expression feature summary"' in module
    assert 'if [ "${run_mcscanx_circlize}" = "true" ]; then' in module
    assert '--plot "mcscanx_circlize=plots/mcscanx_circlize.pdf=MCScanX self intra-species collinearity and chromosome-scale circlize plot"' in module
    assert 'if [ "${run_promoter_cis}" = "true" ]; then' in module
    assert '--plot "promoter_cis_elements=plots/promoter_cis_elements.pdf=Promoter cis-element category matrix and top element summary"' in module
    assert '--plot "promoter1=plots/promoter1.pdf=Reference-style promoter cis-element gene matrix"' in module
    assert '--plot "species_promoter2=plots/species_promoter2.pdf=Reference-style species-level promoter cis-element summary"' in module
    assert 'if [ "${run_ppi}" = "true" ]; then' in module
    assert '--plot "ppi=plots/ppi.pdf=Reference-style PPI network overview"' in module
    assert '--plot "ppi_ggnetview=plots/ppi_ggnetview.pdf=PPI network generated with ggNetView"' in module
    assert 'if [ -n "${expression_matrix}" ] && [ "${expression_matrix}" != "null" ]; then' in module
    assert '--plot "expression_heatmap=plots/expression_heatmap.pdf=Family member expression heatmap"' in module
    assert 'if [ "${run_kaks_wgd}" = "true" ]; then' in module
    assert '--plot "ks_distribution=plots/ks_distribution.pdf=Ks distribution for duplicated pairs and WGD layer interpretation"' in module
    assert '--plot "duplicate_type_kaks=plots/duplicate_type_kaks.pdf=MCScanX self duplicate-type grouped Ka/Ks and Ks overview"' in module
    assert "--out plot_manifest.tsv" in module


def test_jcvi_collinearity_module_prepares_reference_step8_inputs():
    module = Path("workflows/modules/jcvi_collinearity.nf").read_text(encoding="utf-8")

    assert "process PREPARE_JCVI_COLLINEARITY" in module
    assert 'publishDir "${params.outdir}", mode: "copy", overwrite: true' in module
    assert 'path "jcvi_collinearity"' in module
    assert "prepare_jcvi_collinearity.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--outdir jcvi_collinearity" in module
    assert "jcvi_dependency_status.tsv" in module
    assert "missing_dependency" in module
    assert "commands/jcvi_commands.sh" in module


def test_mcscanx_self_circos_module_prepares_reference_step9_inputs():
    module = Path("workflows/modules/mcscanx_self_circos.nf").read_text(encoding="utf-8")

    assert "process PREPARE_MCSCANX_SELF_CIRCOS" in module
    assert 'publishDir "${params.outdir}", mode: "copy", overwrite: true' in module
    assert 'path "mcscanx_self_circos", emit: package_dir' in module
    assert "build_mcscanx_self_inputs.py" in module
    assert "run_mcscanx_self.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--outdir mcscanx_self_circos" in module
    assert "--search-tool ${mcscanx_self_search_tool}" in module
    assert "--mcscanx-self-dir ${mcscanx_self_dir}" in module
    assert "mcscanx_run_status.tsv" in module
    assert "commands/mcscanx_self_commands.sh" in module
    assert "--prepared-dir mcscanx_self_circos" in module
    assert "${executeArg}" in module
    assert "--mcscanx-self-dir mcscanx_self_circos/mcscanx_run" in module
    assert "grep -q '^executed" in module


def test_nextflow_config_exposes_mcscanx_self_execution_toggle():
    config = Path("workflows/nextflow.config").read_text(encoding="utf-8")

    assert 'params.mcscanx_execute_self = true' in config
    assert 'params.mcscanx_self_search_tool = "diamond"' in config


def test_annotation_module_extracts_promoters_for_standard_branch():
    module = Path("workflows/modules/annotation_integration.nf").read_text(encoding="utf-8")

    assert "process EXTRACT_PROMOTERS" in module
    assert "extract_promoters.py" in module
    assert "split_promoter_fasta_for_plantcare.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--upstream-bp ${upstream_bp}" in module
    assert "--downstream-bp ${downstream_bp}" in module
    assert "--out-bed tables/promoters.bed" in module
    assert "--out-fasta sequences/promoters.fa" in module
    assert "--promoter-fasta sequences/promoters.fa" in module
    assert "--records-per-file ${params.plantcare_records_per_file}" in module
    assert "--prefix ${params.gene_family}_promoters" in module
    assert 'path "plantcare_submission"' in module


def test_standard_nextflow_modules_publish_user_facing_outputs():
    expected = {
        "workflows/modules/prepare_species.nf": ['publishDir "${params.outdir}/tables", mode: "copy", overwrite: true'],
        "workflows/modules/family_summary.nf": ['publishDir "${params.outdir}/tables", mode: "copy", overwrite: true'],
        "workflows/modules/alignment_phylogeny.nf": [
            'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true'
        ],
        "workflows/modules/annotation_integration.nf": [
            'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true'
        ],
    }

    for module_path, snippets in expected.items():
        module = Path(module_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in module, module_path


def test_main_workflow_includes_plot_processes():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "PLOT_FAMILY_COUNTS" in workflow
    assert "PLOT_KAKS" in workflow
    assert "PLOT_EXPRESSION_HEATMAP" in workflow
    assert "PLOT_EXPRESSION_HEATMAP(SUBSET_EXPRESSION_MATRIX.out, expression_metadata_ch)" in workflow
    assert "PLOT_GENE_FAMILY_INFO" in workflow
    assert "PLOT_GENE_FAMILY_INFO.out[2]," in workflow
    assert "PLOT_GENE_FAMILY_INFO.out[3]," in workflow
    assert "PLOT_GENE_FAMILY_INFO.out[4]," in workflow
    assert "PLOT_GENE_FAMILY_INFO.out[5]," in workflow
    assert "PLOT_GENE_FAMILY_INFO.out[6]," in workflow
    assert "PLOT_GENE_FAMILY_INFO.out[7]," in workflow
    assert "PLOT_TREE_FEATURES" in workflow
    assert "PLOT_PROMOTER_CIS_ELEMENTS" in workflow
    assert "EMPTY_PROMOTER_CIS_ELEMENTS()" in workflow
    assert "promoter_element_descriptions_value = params.promoter_element_descriptions ?: (yaml_promoter.element_descriptions ?: \"\")" in workflow
    assert "promoter_element_descriptions_ch = Channel.value(promoter_element_descriptions_value ? file(promoter_element_descriptions_value) : \"\")" in workflow
    assert "PLOT_PROMOTER_CIS_ELEMENTS(promoter_cis_input_ch, promoter_element_descriptions_ch)" in workflow
    assert "promoter_cis_gene_element_matrix_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[2]" in workflow
    assert "promoter_cis_category_summary_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[3]" in workflow
    assert "promoter_cis_element_annotations_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[4]" in workflow
    assert "promoter_cis_pdf_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[5]" in workflow
    assert "promoter_cis_png_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[6]" in workflow
    assert "promoter1_pdf_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[7]" in workflow
    assert "promoter1_png_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[8]" in workflow
    assert "species_promoter2_pdf_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[9]" in workflow
    assert "species_promoter2_png_ch = PLOT_PROMOTER_CIS_ELEMENTS.out[10]" in workflow
    assert "BUILD_PLOT_MANIFEST" in workflow


def test_alignment_phylogeny_module_covers_alignment_tree_and_motif_steps():
    module = Path("workflows/modules/alignment_phylogeny.nf").read_text(encoding="utf-8")

    assert "process PREPARE_ALIGNMENT_INPUTS" in module
    assert "prepare_alignment_inputs.py" in module
    assert "--family-name ${family_name}" in module
    assert "--fasta ${family_members_faa}" in module
    assert "--aligner ${aligner}" in module
    assert "--out alignment_manifest.tsv" in module

    assert "process RUN_ALIGNMENT" in module
    assert "val family_name" in module
    assert "val aligner" in module
    assert "mafft --quiet --auto ${family_members_faa} > ${family_name}.${aligner}.aln.faa" in module
    assert 'path "${family_name}.${aligner}.aln.faa"' in module

    assert "process PREPARE_PHYLOGENY_INPUTS" in module
    assert "prepare_phylogeny_inputs.py" in module
    assert "--tree-builder ${tree_builder}" in module
    assert "--out phylogeny_manifest.tsv" in module

    assert "process RUN_PHYLOGENY" in module
    assert "val family_name" in module
    assert "val tree_builder" in module
    assert 'if [ "${tree_builder}" = "fasttree" ]; then' in module
    assert "FASTTREE_BIN=\\$(command -v FastTree || command -v fasttree)" in module
    assert '"\\${FASTTREE_BIN}" -wag ${alignment} > ${family_name}.${tree_builder}.treefile' in module
    assert "IQTREE_BIN=\\$(command -v iqtree2 || command -v iqtree)" in module
    assert '"\\${IQTREE_BIN}" -s ${alignment} -m MFP -bb 1000 -nt AUTO' in module
    assert "cp ${alignment}.treefile ${family_name}.${tree_builder}.treefile" in module
    assert 'path "${family_name}.${tree_builder}.treefile"' in module

    assert "process PARSE_MEME_MOTIFS" in module
    assert "parse_meme_motifs.py" in module
    assert "--meme-txt ${meme_output}/meme.txt" in module
    assert "--out motif_summary.tsv" in module


def test_annotation_integration_module_covers_chromosome_and_expression_steps():
    module = Path("workflows/modules/annotation_integration.nf").read_text(encoding="utf-8")

    assert "process EXTRACT_CHROMOSOME_LOCATIONS" in module
    assert "extract_chromosome_locations.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--out chromosome_locations.tsv" in module

    assert "process EXTRACT_GENE_STRUCTURE" in module
    assert "extract_gene_structure.py" in module
    assert "--out gene_structure_summary.tsv" in module

    assert "process SUBSET_EXPRESSION_MATRIX" in module
    assert "subset_expression_matrix.py" in module
    assert 'path expression_matrix, stageAs: "input_expression_matrix.tsv"' in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--expression ${expression_matrix}" in module
    assert "--out family_expression.tsv" in module
    assert "process EMPTY_EXPRESSION_STATUS" in module
    assert 'path "expression_status.tsv"' in module
    assert "RNA-seq expression matrix not provided; expression module skipped" in module


def test_main_workflow_includes_remaining_standard_analysis_processes():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "PREPARE_ALIGNMENT_INPUTS" in workflow
    assert "RUN_ALIGNMENT" in workflow
    assert "RUN_ALIGNMENT(family_name_ch, aligner_ch, EXTRACT_FAMILY_SEQUENCES.out)" in workflow
    assert "PREPARE_PHYLOGENY_INPUTS" in workflow
    assert "RUN_PHYLOGENY" in workflow
    assert "RUN_PHYLOGENY(family_name_ch, RUN_ALIGNMENT.out, tree_builder_ch)" in workflow
    assert "RUN_ALIGNMENT.out," in workflow
    assert "RUN_PHYLOGENY.out," in workflow
    assert "PARSE_MEME_MOTIFS" in workflow
    assert "PARSE_MEME_MOTIFS(" in workflow
    assert "PARSE_MEME_MOTIFS.out" in workflow
    assert "EXTRACT_GENE_STRUCTURE(CONCAT_FAMILY_CANDIDATES.out, PREPROCESS_SPECIES.out[1])" in workflow
    assert "EXTRACT_GENE_STRUCTURE.out" in workflow
    assert "RUN_MEME_MOTIFS(EXTRACT_FAMILY_SEQUENCES.out)" in workflow
    assert "PARSE_MEME_MOTIFS(RUN_MEME_MOTIFS.out, family_name_ch)" in workflow
    assert "EXTRACT_CHROMOSOME_LOCATIONS" in workflow
    assert "SUBSET_EXPRESSION_MATRIX" in workflow
    assert "EMPTY_EXPRESSION_STATUS" in workflow
    assert "EXTRACT_CHROMOSOME_LOCATIONS(CONCAT_FAMILY_CANDIDATES.out, PREPROCESS_SPECIES.out[1])" in workflow
    assert "BUILD_STANDARD_REPORT_INDEX(" in workflow
    assert "motif_summary" in Path("workflows/modules/standard_postprocess.nf").read_text(encoding="utf-8")
    assert "--motif-summary ${motif_summary}" in Path("workflows/modules/standard_postprocess.nf").read_text(
        encoding="utf-8"
    )
    assert "PARSE_MEME_MOTIFS.out" in workflow
    assert "EXTRACT_CHROMOSOME_LOCATIONS.out" in workflow
