from pathlib import Path


def test_hmmer_module_writes_normalized_tsv():
    module = Path("workflows/modules/hmmer_search.nf").read_text(encoding="utf-8")

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
    assert 'path "identification_inputs/hmmer_inputs.tsv"' in module
    assert 'path "identification_inputs/diamond_inputs.tsv"' in module


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

    assert "process BUILD_WGD_HANDOFF_MANIFEST" in module
    assert 'publishDir "${params.outdir}/tables", mode: "copy", overwrite: true' in module
    assert "build_wgd_handoff_manifest.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--events-config ${params.events_config}" in module
    assert "--ks-bins ${params.ks_bins}" in module
    assert '--wgd-event-args "${params.wgd_event_args}"' in module
    assert "--out wgd_handoff_manifest.tsv" in module

    assert "process BUILD_STANDARD_REPORT_INDEX" in module
    assert 'publishDir "${params.outdir}/report", mode: "copy", overwrite: true' in module
    assert "build_standard_report_index.py" in module
    assert "--run-config-snapshot ${run_config_snapshot}" in module
    assert "--family-members-faa ${family_members_faa}" in module
    assert "--phylogeny-manifest ${phylogeny_manifest}" in module
    assert "--alignment-file ${alignment_file}" in module
    assert "--phylogeny-tree ${phylogeny_tree}" in module
    assert "--tree-feature-matrix ${tree_feature_matrix}" in module
    assert "--tree-features-pdf ${tree_features_pdf}" in module
    assert "--tree-features-png ${tree_features_png}" in module
    assert '--promoters-bed "${promoters_bed}"' in module
    assert '--promoters-fasta "${promoters_fasta}"' in module
    assert '--feature-summary "${feature_summary}"' in module
    assert '--feature-summary-pdf "${feature_summary_pdf}"' in module
    assert '--feature-summary-png "${feature_summary_png}"' in module
    assert '--mcscanx-circlize-pdf "${mcscanx_circlize_pdf}"' in module
    assert '--mcscanx-circlize-png "${mcscanx_circlize_png}"' in module
    assert '--ppi-edges "${ppi_edges}"' in module
    assert '--ppi-nodes "${ppi_nodes}"' in module
    assert '--ppi-hubs "${ppi_hubs}"' in module
    assert '--ppi-ggnetview-status "${ppi_ggnetview_status}"' in module
    assert '--ppi-ggnetview-pdf "${ppi_ggnetview_pdf}"' in module
    assert '--ppi-ggnetview-png "${ppi_ggnetview_png}"' in module
    assert "--wgd-handoff-manifest ${wgd_handoff_manifest}" in module
    assert "--software-versions ${software_versions}" in module
    assert "--figure-interpretations ${figure_interpretations}" in module
    assert "--published-outdir ${params.outdir}" in module
    assert "--out report_index.tsv" in module

    assert "process ASSEMBLE_STANDARD_REPORT" in module
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
    assert "--plot-manifest ${plot_manifest}" in module
    assert "--software-versions ${software_versions}" in module
    assert "--figure-interpretations ${figure_interpretations}" in module
    assert "--out final_report.md" in module


def test_main_workflow_wires_standard_identification_branch():
    workflow = Path("workflows/main.nf").read_text(encoding="utf-8")

    assert "def asBooleanParam(value)" in workflow
    assert "include { VALIDATE_CONFIG } from './modules/config_validation.nf'" in workflow
    assert "VALIDATE_CONFIG(config_ch)" in workflow
    assert "validated_config_ch = VALIDATE_CONFIG.out" in workflow
    assert "if (asBooleanParam(params.mock_external_tools))" in workflow
    assert "include { BUILD_IDENTIFICATION_INPUTS } from './modules/identification_inputs.nf'" in workflow
    assert "BUILD_RUN_CONFIG_SNAPSHOT;" in workflow
    assert "EXTRACT_FAMILY_SEQUENCES;" in workflow
    assert "BUILD_WGD_HANDOFF_MANIFEST;" in workflow
    assert "BUILD_STANDARD_REPORT_INDEX;" in workflow
    assert "ASSEMBLE_STANDARD_REPORT" in workflow
    assert "EXTRACT_PROMOTERS;" in workflow
    assert "PLOT_FEATURE_SUMMARY;" in workflow
    assert "PLOT_TREE_FEATURES;" in workflow
    assert "PLOT_MCSCANX_CIRCLIZE;" in workflow
    assert "PLOT_PPI_GGNETVIEW;" in workflow
    assert "COLLECT_SOFTWARE_VERSIONS" in workflow
    assert "BUILD_FIGURE_INTERPRETATIONS" in workflow
    assert "include { HMMER_SEARCH } from './modules/hmmer_search.nf'" in workflow
    assert "include { DIAMOND_SEARCH } from './modules/diamond_search.nf'" in workflow
    assert "DOMAIN_FILTER;" in workflow
    assert "CONCAT_FAMILY_CANDIDATES;" in workflow
    assert "MOCK_IDENTIFICATION_EVIDENCE;" in workflow
    assert "EMPTY_HMMER_EVIDENCE;" in workflow
    assert "EMPTY_DIAMOND_EVIDENCE" in workflow
    assert "} from './modules/domain_filter.nf'" in workflow
    assert "include { FAMILY_SUMMARY } from './modules/family_summary.nf'" in workflow
    assert "} else if (params.run_identification) {" in workflow
    assert "BUILD_IDENTIFICATION_INPUTS(validated_config_ch, PREPARE_SPECIES.out)" in workflow
    assert "species_ids_ch = PREPARE_SPECIES.out" in workflow
    assert "if (asBooleanParam(params.use_hmmer))" in workflow
    assert "if (asBooleanParam(params.use_diamond))" in workflow
    assert "HMMER_SEARCH(hmmer_inputs_ch)" in workflow
    assert "EMPTY_HMMER_EVIDENCE(species_ids_ch)" in workflow
    assert "DIAMOND_SEARCH(diamond_inputs_ch)" in workflow
    assert "EMPTY_DIAMOND_EVIDENCE(species_ids_ch)" in workflow
    assert "joined_evidence_ch = hmmer_evidence_ch" in workflow
    assert ".join(diamond_evidence_ch, by: 0)" in workflow
    assert "if (asBooleanParam(params.mock_external_tools))" in workflow
    assert "MOCK_IDENTIFICATION_EVIDENCE(mock_evidence_ch)" in workflow
    assert "joined_evidence_ch = MOCK_IDENTIFICATION_EVIDENCE.out" in workflow
    assert "DOMAIN_FILTER(joined_evidence_ch, final_rule_ch)" in workflow
    assert "CONCAT_FAMILY_CANDIDATES(candidate_tables_ch.collect())" in workflow
    assert "if (!asBooleanParam(params.standard_stop_after_family_candidates))" in workflow
    assert "BUILD_RUN_CONFIG_SNAPSHOT(validated_config_ch, PREPARE_SPECIES.out)" in workflow
    assert "BUILD_WGD_HANDOFF_MANIFEST(CONCAT_FAMILY_CANDIDATES.out)" in workflow
    assert "FAMILY_SUMMARY(CONCAT_FAMILY_CANDIDATES.out)" in workflow
    assert "EXTRACT_FAMILY_SEQUENCES(CONCAT_FAMILY_CANDIDATES.out, PREPARE_SPECIES.out)" in workflow
    assert "if (asBooleanParam(params.run_promoter))" in workflow
    assert "EXTRACT_PROMOTERS(" in workflow
    assert "CONCAT_FAMILY_CANDIDATES.out," in workflow
    assert "PREPARE_SPECIES.out," in workflow
    assert "if (asBooleanParam(params.run_feature_summary))" in workflow
    assert "PLOT_TREE_FEATURES(" in workflow
    assert "PLOT_FEATURE_SUMMARY(" in workflow
    assert "if (asBooleanParam(params.run_mcscanx_circlize))" in workflow
    assert "PLOT_MCSCANX_CIRCLIZE(" in workflow
    assert "if (asBooleanParam(params.run_ppi))" in workflow
    assert 'error "Missing required parameter for --run_ppi true: --ppi_edges"' in workflow
    assert "PLOT_PPI_GGNETVIEW(ppi_edges_input_ch, ppi_nodes_input_ch)" in workflow
    assert "PREPARE_ALIGNMENT_INPUTS(family_name_ch, EXTRACT_FAMILY_SEQUENCES.out, aligner_ch, alignment_outdir_ch)" in workflow
    assert "PREPARE_PHYLOGENY_INPUTS(PREPARE_ALIGNMENT_INPUTS.out, tree_builder_ch, phylogeny_outdir_ch)" in workflow
    assert "PLOT_FAMILY_COUNTS(FAMILY_SUMMARY.out)" in workflow
    assert "BUILD_PLOT_MANIFEST()" in workflow
    assert "COLLECT_SOFTWARE_VERSIONS()" in workflow
    assert "BUILD_FIGURE_INTERPRETATIONS(BUILD_PLOT_MANIFEST.out)" in workflow
    assert "BUILD_STANDARD_REPORT_INDEX(" in workflow
    assert "BUILD_RUN_CONFIG_SNAPSHOT.out" in workflow
    assert "PLOT_TREE_FEATURES.out[0]" in workflow
    assert "PLOT_TREE_FEATURES.out[1]" in workflow
    assert "PLOT_TREE_FEATURES.out[2]" in workflow
    assert "ppi_ggnetview_pdf_ch" in workflow
    assert "BUILD_WGD_HANDOFF_MANIFEST.out" in workflow
    assert "ASSEMBLE_STANDARD_REPORT(project_name_ch, family_name_ch, BUILD_STANDARD_REPORT_INDEX.out, BUILD_RUN_CONFIG_SNAPSHOT.out, BUILD_PLOT_MANIFEST.out, COLLECT_SOFTWARE_VERSIONS.out, BUILD_FIGURE_INTERPRETATIONS.out[0])" in workflow


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
    assert "--out final_report.md" in module


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
    assert "PLOT_KAKS(kaks_pairs_ch)" in workflow
    assert "BUILD_WGD_EVENT_EVIDENCE" in workflow
    assert "ANNOTATE_FAMILY_WGD_EVENTS" in workflow
    assert "SUMMARIZE_FAMILY_EVENT_RETENTION" in workflow
    assert "RETENTION_ENRICHMENT" in workflow
    assert "BUILD_WGD_REPORT_INDEX(outdir_ch)" in workflow
    assert "BUILD_WGD_RUN_CONFIG_SNAPSHOT.out," in workflow
    assert "ASSEMBLE_WGD_REPORT(" in workflow


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
    assert "--args ${kaks_pairs} plots" in module
    assert 'path "plots/ks_distribution.pdf"' in module
    assert 'path "plots/ks_distribution.png"' in module

    assert "process PLOT_EXPRESSION_HEATMAP" in module
    assert "${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_expression_heatmap.R" in module
    assert "--args ${expression_matrix} plots" in module
    assert 'path "plots/expression_heatmap.pdf"' in module

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
    assert 'path "tables/gene_family_protein_properties.tsv"' in module
    assert 'path "plots/gene_family_info_summary.pdf"' in module
    assert 'path "plots/gene_family_info_summary.png"' in module

    assert "process PLOT_PROMOTER_CIS_ELEMENTS" in module
    assert "build_promoter_cis_elements.py" in module
    assert "plot_promoter_cis_elements.R" in module
    assert "--cis-elements ${cis_elements}" in module
    assert 'path "tables/promoter_cis_elements.tsv"' in module
    assert 'path "tables/promoter_cis_gene_matrix.tsv"' in module
    assert 'path "tables/promoter_cis_category_summary.tsv"' in module
    assert 'path "plots/promoter_cis_elements.pdf"' in module
    assert 'path "plots/promoter_cis_elements.png"' in module

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
    assert 'path "plots/mcscanx_circlize.pdf"' in module

    assert "process PLOT_PPI_GGNETVIEW" in module
    assert "build_ppi_tables.py" in module
    assert "plot_ppi_ggnetview.R" in module
    assert "--edges ${ppi_edges}" in module
    assert 'path "tables/ppi_edges.tsv"' in module
    assert 'path "tables/ppi_nodes.tsv"' in module
    assert 'path "tables/ppi_hubs.tsv"' in module
    assert 'path "tables/ppi_ggnetview_status.tsv"' in module
    assert 'path "plots/ppi_ggnetview.pdf"' in module
    assert 'path "plots/ppi_ggnetview.png"' in module

    assert "process BUILD_PLOT_MANIFEST" in module
    assert 'publishDir "${params.outdir}/report", mode: "copy", overwrite: true' in module
    assert "build_plot_manifest.py" in module
    assert '--plot "family_counts=plots/family_counts.pdf=Family member counts by species"' in module
    assert '--plot "gene_family_info_summary=plots/gene_family_info_summary.pdf=Gene family copy-number and protein-property summary"' in module
    assert '--plot "tree_features=plots/tree_features.pdf=Tree, motif, gene-structure, and domain composite plot"' in module
    assert '--plot "promoter_cis_elements=plots/promoter_cis_elements.pdf=Promoter cis-element category matrix and top element summary"' in module
    assert '--plot "ppi_ggnetview=plots/ppi_ggnetview.pdf=PPI network generated with ggNetView"' in module
    assert '--plot "ks_distribution=plots/ks_distribution.pdf=Ks distribution for duplicated pairs"' in module
    assert '--plot "expression_heatmap=plots/expression_heatmap.pdf=Family member expression heatmap"' in module
    assert "--out plot_manifest.tsv" in module


def test_annotation_module_extracts_promoters_for_standard_branch():
    module = Path("workflows/modules/annotation_integration.nf").read_text(encoding="utf-8")

    assert "process EXTRACT_PROMOTERS" in module
    assert "extract_promoters.py" in module
    assert "--family-candidates ${family_candidates}" in module
    assert "--species-manifest ${species_manifest}" in module
    assert "--upstream-bp ${upstream_bp}" in module
    assert "--downstream-bp ${downstream_bp}" in module
    assert "--out-bed tables/promoters.bed" in module
    assert "--out-fasta sequences/promoters.fa" in module


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
    assert "PLOT_GENE_FAMILY_INFO" in workflow
    assert "PLOT_TREE_FEATURES" in workflow
    assert "PLOT_PROMOTER_CIS_ELEMENTS" in workflow
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
    assert "--meme-txt ${meme_txt}" in module
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
    assert "--family-candidates ${family_candidates}" in module
    assert "--expression ${expression_matrix}" in module
    assert "--out family_expression.tsv" in module


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
    assert "EXTRACT_GENE_STRUCTURE(CONCAT_FAMILY_CANDIDATES.out, PREPARE_SPECIES.out)" in workflow
    assert "EXTRACT_GENE_STRUCTURE.out" in workflow
    assert "file(params.meme_txt)" in workflow
    assert "EXTRACT_CHROMOSOME_LOCATIONS" in workflow
    assert "SUBSET_EXPRESSION_MATRIX" in workflow
    assert "EXTRACT_CHROMOSOME_LOCATIONS(CONCAT_FAMILY_CANDIDATES.out, PREPARE_SPECIES.out)" in workflow
    assert "BUILD_STANDARD_REPORT_INDEX(" in workflow
    assert "motif_summary" in Path("workflows/modules/standard_postprocess.nf").read_text(encoding="utf-8")
    assert "--motif-summary ${motif_summary}" in Path("workflows/modules/standard_postprocess.nf").read_text(
        encoding="utf-8"
    )
    assert "PARSE_MEME_MOTIFS.out" in workflow
    assert "EXTRACT_CHROMOSOME_LOCATIONS.out" in workflow
