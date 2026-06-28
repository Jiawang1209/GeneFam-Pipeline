process BUILD_RUN_CONFIG_SNAPSHOT {
    tag "run config snapshot"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path config
    path species_manifest

    output:
    path "run_config_snapshot.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_run_config_snapshot.py \\
      --config ${config} \\
      --species-manifest ${species_manifest} \\
      --out run_config_snapshot.tsv
    """
}

process PUBLISH_PREPROCESS_AUDIT {
    tag "publish preprocess audit"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path clean_species_manifest
    path transcript_gene_map
    path representative_transcripts
    path preprocess_warnings
    path clean_species_bank, stageAs: "clean_species_bank_input"

    output:
    path "tables/species_manifest.tsv"
    path "tables/all_transcript_gene_map.tsv"
    path "tables/all_representative_transcripts.tsv"
    path "tables/all_preprocess_warnings.tsv"
    path "species_bank_clean"

    script:
    """
    mkdir -p tables
    cp ${clean_species_manifest} tables/species_manifest.tsv
    cp ${transcript_gene_map} tables/all_transcript_gene_map.tsv
    cp ${representative_transcripts} tables/all_representative_transcripts.tsv
    cp ${preprocess_warnings} tables/all_preprocess_warnings.tsv
    mkdir -p species_bank_clean
    cp -RL clean_species_bank_input/. species_bank_clean/
    """
}

process EXTRACT_FAMILY_SEQUENCES {
    tag "family member FASTA"
    publishDir "${params.outdir}/sequences", mode: "copy", overwrite: true

    input:
    path family_candidates
    path species_manifest

    output:
    path "family_members.faa"

    script:
    """
    python ${projectDir}/../bin/genefam/extract_family_sequences.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --out family_members.faa
    """
}

process BUILD_WGD_HANDOFF_MANIFEST {
    tag "standard to WGD handoff manifest"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path family_candidates

    output:
    path "wgd_handoff_manifest.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_wgd_handoff_manifest.py \\
      --family-candidates ${family_candidates} \\
      --events-config ${params.events_config} \\
      --ks-bins ${params.ks_bins} \\
      --wgd-event-args "${params.wgd_event_args}" \\
      --out wgd_handoff_manifest.tsv
    """
}

process EMPTY_REFERENCE_MANIFEST {
    tag "mock reference manifest"

    output:
    path "reference_generation.tsv"

    script:
    """
    printf 'status\\tnote\\nmock_external_tools\\tReference generation skipped because mock evidence was supplied.\\n' > reference_generation.tsv
    """
}

process PREPARE_REFERENCE_KAKS_INPUTS {
    tag "prepare Reference KaKs inputs"
    publishDir "${params.outdir}/kaks_inputs", mode: "copy", overwrite: true

    input:
    path species_manifest
    path jcvi_collinearity
    path mcscanx_self_circos

    output:
    path "KaKs_Gene_Pair.tsv"
    path "kaks_input_manifest.tsv"
    path "kaks_missing_sequences.tsv"
    path "kaks_input_status.tsv"
    path "pair_fastas"

    script:
    """
    mkdir -p pair_fastas
    python ${projectDir}/../bin/genefam/prepare_reference_kaks_inputs.py \\
      --species-manifest ${species_manifest} \\
      --jcvi-dir ${jcvi_collinearity} \\
      --pair-source mcscanx=${mcscanx_self_circos}/mcscanx_gene_pairs.tsv \\
      --outdir .
    """
}

process RUN_REFERENCE_KAKS_CALCULATOR {
    tag "run Reference KaKs_Calculator"
    publishDir "${params.outdir}/kaks_inputs", mode: "copy", overwrite: true

    input:
    path kaks_input_manifest
    path kaks_pair_fastas

    output:
    path "kaks_calculator_status.tsv"
    path "kaks_calculator_commands.tsv"
    path "kaks_calculator_results.tsv"
    path "kaks_calculator_qc.tsv"
    path "kaks_results", optional: true
    path "kaks_failure_summary.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/run_reference_kaks_calculator.py \\
      --manifest ${kaks_input_manifest} \\
      --outdir . \\
      --executable ${params.kaks_calculator_bin}
    """
}

process NORMALIZE_REFERENCE_KAKS_RESULTS {
    tag "normalize Reference KaKs results"
    publishDir "${params.outdir}/kaks_inputs", mode: "copy", overwrite: true

    input:
    path kaks_calculator_results
    path kaks_results

    output:
    path "kaks_pairs.tsv"
    path "kaks_pairs_skipped.tsv"
    path "kaks_pairs_summary.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/normalize_reference_kaks_results.py \\
      --calculator-results ${kaks_calculator_results} \\
      --outdir .
    """
}

process CLASSIFY_STANDARD_WGD_LAYERS {
    tag "classify standard WGD layers"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path kaks_pairs
    val ks_bins
    val event_args

    output:
    path "wgd_layers.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/classify_wgd_layers.py \\
      --pairs ${kaks_pairs} \\
      --bins ${ks_bins} \\
      ${event_args} \\
      --out wgd_layers.tsv
    """
}

process BUILD_STANDARD_KAKS_WGD_ANNOTATIONS {
    tag "standard Ka/Ks WGD plot annotations"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path classified_pairs

    output:
    path "kaks_wgd_annotations.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_kaks_plot_annotations.py \\
      --classified-pairs ${classified_pairs} \\
      --out kaks_wgd_annotations.tsv
    """
}

process BUILD_STANDARD_WGD_EVENT_EVIDENCE {
    tag "standard WGD event evidence"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path classified_pairs
    path events_config

    output:
    path "wgd_event_evidence.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_wgd_event_evidence.py \\
      --classified-pairs ${classified_pairs} \\
      --events-config ${events_config} \\
      --out wgd_event_evidence.tsv
    """
}

process PLOT_STANDARD_KAKS_WGD {
    tag "plot standard Ka/Ks WGD"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path kaks_pairs
    path kaks_annotations

    output:
    path "plots/ks_distribution.pdf"
    path "plots/ks_distribution.png"

    script:
    """
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_kaks.R --args ${kaks_pairs} ${kaks_annotations} plots
    """
}

process BUILD_STANDARD_MCSCANX_DUPLICATE_TYPES {
    tag "derive MCScanX self duplicate types"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path mcscanx_self_circos

    output:
    path "tables/mcscanx_duplicate_types.tsv"

    script:
    """
    mkdir -p tables
    python ${projectDir}/../bin/genefam/build_mcscanx_duplicate_types.py \\
      --mcscanx-pairs ${mcscanx_self_circos}/mcscanx_gene_pairs.tsv \\
      --out tables/mcscanx_duplicate_types.tsv
    """
}

process PLOT_STANDARD_DUPLICATE_TYPE_KAKS {
    tag "plot MCScanX self duplicate-type KaKs"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path duplicate_types
    path kaks_pairs

    output:
    path "tables/duplicate_type_kaks.tsv"
    path "tables/duplicate_type_kaks_summary.tsv"
    path "tables/duplicate_type_kaks_skipped.tsv"
    path "plots/duplicate_type_kaks.pdf"
    path "plots/duplicate_type_kaks.png"

    script:
    """
    mkdir -p tables plots
    python ${projectDir}/../bin/genefam/build_duplicate_type_kaks.py \\
      --duplicates ${duplicate_types} \\
      --kaks-pairs ${kaks_pairs} \\
      --outdir tables
    pair_count=\$(tail -n +2 tables/duplicate_type_kaks.tsv | wc -l | tr -d ' ')
    if [ "\${pair_count}" -gt 0 ]; then
      ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_duplicate_type_kaks.R --args \\
        tables/duplicate_type_kaks.tsv \\
        tables/duplicate_type_kaks_summary.tsv \\
        plots
    else
      ${params.r_bin} --vanilla --slave <<'RSCRIPT'
      dir.create("plots", recursive = TRUE, showWarnings = FALSE)
      pdf("plots/duplicate_type_kaks.pdf", width = 8, height = 5)
      plot.new()
      text(0.5, 0.5, "No MCScanX self duplicate-type Ka/Ks pairs available")
      dev.off()
      png("plots/duplicate_type_kaks.png", width = 1200, height = 800, res = 150)
      plot.new()
      text(0.5, 0.5, "No MCScanX self duplicate-type Ka/Ks pairs available")
      dev.off()
RSCRIPT
    fi
    """
}

process RUN_PFAM_CONFIRMATION {
    tag "Reference Step4 Pfam confirmation"
    publishDir "${params.outdir}/tables/pfam_confirmation", mode: "copy", overwrite: true

    input:
    path family_candidates
    path family_members_faa
    val hmm_id
    val pfam_db
    val hmmscan_domtbl

    output:
    path "pfam_confirmation_status.tsv"
    path "inter.ID"
    path "union.ID"
    path "pfam.ID"
    path "pfam_scan.id"
    path "identify.ID.fa"
    path "pfam_scan.domtblout", optional: true
    path "pfam_scan.log", optional: true

    script:
    def pfamDbArg = pfam_db ? "--pfam-db ${pfam_db}" : ""
    def domtblArg = hmmscan_domtbl ? "--hmmscan-domtbl ${hmmscan_domtbl}" : ""
    """
    python ${projectDir}/../bin/genefam/run_pfam_confirmation.py \\
      --family-candidates ${family_candidates} \\
      --family-members ${family_members_faa} \\
      --hmm-id ${hmm_id} \\
      ${pfamDbArg} \\
      ${domtblArg} \\
      --executable ${params.hmmscan_bin} \\
      --outdir .
    """
}

process BUILD_STANDARD_REPORT_INDEX {
    tag "standard report index"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    input:
    path species_manifest
    path run_config_snapshot
    path family_candidates
    path family_counts
    path family_counts_pdf
    path family_counts_png
    path family_members_faa
    path gene_family_copy_number
    path gene_family_copy_number_summary
    path gene_family_species_order
    path gene_family_copy_number_expansion
    path gene_family_pangenome_summary
    path gene_family_protein_properties
    path gene_family_info_pdf
    path gene_family_info_png
    path alignment_manifest
    path alignment_file
    path phylogeny_manifest
    path phylogeny_tree
    path motif_summary
    path gene_structure_summary
    path tree_feature_matrix
    path tree_features_pdf
    path tree_features_png
    path chromosome_locations
    val promoters_bed
    val promoters_fasta
    val promoter_cis_elements
    val promoter_cis_gene_matrix
    val promoter_cis_gene_element_matrix
    val promoter_cis_category_summary
    val promoter_cis_element_annotations
    val promoter_cis_pdf
    val promoter_cis_png
    val promoter1_pdf
    val promoter1_png
    val species_promoter2_pdf
    val species_promoter2_png
    val promoter_cis_status
    val feature_summary
    val feature_summary_pdf
    val feature_summary_png
    val circlize_link_density
    val circlize_duplicate_type_tracks
    val mcscanx_circlize_pdf
    val mcscanx_circlize_png
    val ppi_edges
    val ppi_nodes
    val ppi_hubs
    val ppi_input_evidence
    val ppi_network_qc
    val ppi_node_annotation
    val ppi_species_annotation
    val ppi_overview_status
    val ppi_ggnetview_status
    val ppi_pdf
    val ppi_png
    val ppi_ggnetview_pdf
    val ppi_ggnetview_png
    val family_expression
    val expression_sample_metadata
    val expression_group_matrix
    val expression_gene_summary
    val expression_heatmap_pdf
    val expression_heatmap_png
    val expression_status
    path wgd_handoff_manifest
    val kaks_failure_summary
    val wgd_layers
    val kaks_wgd_annotations
    val wgd_event_evidence
    val ks_distribution_pdf
    val ks_distribution_png
    val mcscanx_duplicate_types
    val duplicate_type_kaks
    val duplicate_type_kaks_summary
    val duplicate_type_kaks_pdf
    val duplicate_type_kaks_png
    path plot_manifest
    path software_versions
    path figure_interpretations

    output:
    path "report_index.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_standard_report_index.py \\
      --species-manifest ${species_manifest} \\
      --run-config-snapshot ${run_config_snapshot} \\
      --family-candidates ${family_candidates} \\
      --family-counts ${family_counts} \\
      --family-counts-pdf ${family_counts_pdf} \\
      --family-counts-png ${family_counts_png} \\
      --family-members-faa ${family_members_faa} \\
      --gene-family-copy-number ${gene_family_copy_number} \\
      --gene-family-copy-number-summary ${gene_family_copy_number_summary} \\
      --gene-family-species-order ${gene_family_species_order} \\
      --gene-family-copy-number-expansion ${gene_family_copy_number_expansion} \\
      --gene-family-pangenome-summary ${gene_family_pangenome_summary} \\
      --gene-family-protein-properties ${gene_family_protein_properties} \\
      --gene-family-info-pdf ${gene_family_info_pdf} \\
      --gene-family-info-png ${gene_family_info_png} \\
      --alignment-manifest ${alignment_manifest} \\
      --alignment-file ${alignment_file} \\
      --phylogeny-manifest ${phylogeny_manifest} \\
      --phylogeny-tree ${phylogeny_tree} \\
      --motif-summary ${motif_summary} \\
      --gene-structure-summary ${gene_structure_summary} \\
      --tree-feature-matrix ${tree_feature_matrix} \\
      --tree-features-pdf ${tree_features_pdf} \\
      --tree-features-png ${tree_features_png} \\
      --chromosome-locations ${chromosome_locations} \\
      --promoters-bed "${promoters_bed}" \\
      --promoters-fasta "${promoters_fasta}" \\
      --promoter-cis-elements "${promoter_cis_elements}" \\
      --promoter-cis-gene-matrix "${promoter_cis_gene_matrix}" \\
      --promoter-cis-gene-element-matrix "${promoter_cis_gene_element_matrix}" \\
      --promoter-cis-category-summary "${promoter_cis_category_summary}" \\
      --promoter-cis-element-annotations "${promoter_cis_element_annotations}" \\
      --promoter-cis-pdf "${promoter_cis_pdf}" \\
      --promoter-cis-png "${promoter_cis_png}" \\
      --promoter1-pdf "${promoter1_pdf}" \\
      --promoter1-png "${promoter1_png}" \\
      --species-promoter2-pdf "${species_promoter2_pdf}" \\
      --species-promoter2-png "${species_promoter2_png}" \\
      --promoter-cis-status "${promoter_cis_status}" \\
      --feature-summary "${feature_summary}" \\
      --feature-summary-pdf "${feature_summary_pdf}" \\
      --feature-summary-png "${feature_summary_png}" \\
      --circlize-link-density "${circlize_link_density}" \\
      --circlize-duplicate-type-tracks "${circlize_duplicate_type_tracks}" \\
      --mcscanx-circlize-pdf "${mcscanx_circlize_pdf}" \\
      --mcscanx-circlize-png "${mcscanx_circlize_png}" \\
      --ppi-edges "${ppi_edges}" \\
      --ppi-nodes "${ppi_nodes}" \\
      --ppi-hubs "${ppi_hubs}" \\
      --ppi-input-evidence "${ppi_input_evidence}" \\
      --ppi-network-qc "${ppi_network_qc}" \\
      --ppi-node-annotation "${ppi_node_annotation}" \\
      --ppi-species-annotation "${ppi_species_annotation}" \\
      --ppi-overview-status "${ppi_overview_status}" \\
      --ppi-ggnetview-status "${ppi_ggnetview_status}" \\
      --ppi-pdf "${ppi_pdf}" \\
      --ppi-png "${ppi_png}" \\
      --ppi-ggnetview-pdf "${ppi_ggnetview_pdf}" \\
      --ppi-ggnetview-png "${ppi_ggnetview_png}" \\
      --family-expression "${family_expression}" \\
      --expression-sample-metadata "${expression_sample_metadata}" \\
      --expression-group-matrix "${expression_group_matrix}" \\
      --expression-gene-summary "${expression_gene_summary}" \\
      --expression-heatmap-pdf "${expression_heatmap_pdf}" \\
      --expression-heatmap-png "${expression_heatmap_png}" \\
      --expression-status "${expression_status}" \\
      --wgd-handoff-manifest ${wgd_handoff_manifest} \\
      --kaks-failure-summary "${kaks_failure_summary}" \\
      --wgd-layers "${wgd_layers}" \\
      --kaks-wgd-annotations "${kaks_wgd_annotations}" \\
      --wgd-event-evidence "${wgd_event_evidence}" \\
      --ks-distribution-pdf "${ks_distribution_pdf}" \\
      --ks-distribution-png "${ks_distribution_png}" \\
      --mcscanx-duplicate-types "${mcscanx_duplicate_types}" \\
      --duplicate-type-kaks "${duplicate_type_kaks}" \\
      --duplicate-type-kaks-summary "${duplicate_type_kaks_summary}" \\
      --duplicate-type-kaks-pdf "${duplicate_type_kaks_pdf}" \\
      --duplicate-type-kaks-png "${duplicate_type_kaks_png}" \\
      --plot-manifest ${plot_manifest} \\
      --software-versions ${software_versions} \\
      --figure-interpretations ${figure_interpretations} \\
      --published-outdir ${params.outdir} \\
      --out report_index.tsv
    """
}

process COLLECT_SOFTWARE_VERSIONS {
    tag "software version table"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    output:
    path "software_versions.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/collect_software_versions.py \\
      --r-bin ${params.r_bin} \\
      --out software_versions.tsv
    """
}

process BUILD_FIGURE_INTERPRETATIONS {
    tag "figure interpretation notes"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    input:
    path plot_manifest

    output:
    path "figure_interpretations.tsv"
    path "figure_interpretations.md"

    script:
    """
    python ${projectDir}/../bin/genefam/build_figure_interpretations.py \\
      --plot-manifest ${plot_manifest} \\
      --out-tsv figure_interpretations.tsv \\
      --out-md figure_interpretations.md
    """
}

process ASSEMBLE_STANDARD_REPORT {
    tag "standard final report"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    input:
    val project_name
    val gene_family
    path report_index
    path run_config_snapshot
    val wgd_event_evidence
    val kaks_failure_summary
    path plot_manifest
    path software_versions
    path figure_interpretations

    output:
    path "final_report.md"

    script:
    def wgdEvidenceArg = wgd_event_evidence ? "--wgd-event-evidence ${wgd_event_evidence}" : ""
    def kaksFailureSummaryArg = kaks_failure_summary ? "--kaks-failure-summary ${kaks_failure_summary}" : ""
    """
    python ${projectDir}/../bin/genefam/assemble_report.py \\
      --project-name ${project_name} \\
      --gene-family ${gene_family} \\
      --report-index ${report_index} \\
      --run-config-snapshot ${run_config_snapshot} \\
      ${wgdEvidenceArg} \\
      ${kaksFailureSummaryArg} \\
      --plot-manifest ${plot_manifest} \\
      --software-versions ${software_versions} \\
      --figure-interpretations ${figure_interpretations} \\
      --out final_report.md
    """
}

process ORGANIZE_MODULE_RESULTS {
    tag "module result package"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path final_report
    path package_inputs

    output:
    path "analysis_modules"

    script:
    def sourceDir = params.outdir.toString().startsWith("/") ? params.outdir : "${projectDir}/../${params.outdir}"
    """
    mkdir -p organize_source
    cp -RL ${sourceDir}/. organize_source/
    for item in ${package_inputs}; do
      if [ -d "\$item" ] && [ "\$(basename "\$item")" = "mcscanx_self_circos" ]; then
        rm -rf organize_source/mcscanx_self_circos
        cp -RL "\$item" organize_source/mcscanx_self_circos
      fi
      if [ -d "\$item" ] && [ "\$(basename "\$item")" = "jcvi_collinearity" ]; then
        rm -rf organize_source/jcvi_collinearity
        cp -RL "\$item" organize_source/jcvi_collinearity
      fi
    done
    python ${projectDir}/../bin/genefam/organize_module_results.py \\
      --source organize_source \\
      --outdir analysis_modules \\
      --final-report ${final_report}
    """
}

process AUDIT_REAL_REFERENCE_PACKAGE {
    tag "real Reference MVP package audit"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path analysis_modules

    output:
    path "analysis_modules", emit: package_dir
    path "report/reference_mvp_package_audit.tsv", emit: tsv
    path "report/reference_mvp_package_audit.md", emit: md

    script:
    """
    cp -RL ${analysis_modules} audited_analysis_modules
    mkdir -p audited_analysis_modules/report report
    python ${projectDir}/../bin/genefam/audit_real_reference_package.py \\
      --analysis-modules audited_analysis_modules \\
      --out-tsv audited_analysis_modules/report/reference_mvp_package_audit.tsv \\
      --out-md audited_analysis_modules/report/reference_mvp_package_audit.md \\
      --allow-incomplete
    cp audited_analysis_modules/report/reference_mvp_package_audit.tsv audited_analysis_modules/report/reference_mvp_package_audit.md report/
    rm -rf analysis_modules
    mv audited_analysis_modules analysis_modules
    """
}

process BUILD_REPRODUCIBILITY_CODE {
    tag "reproducibility code"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    input:
    path config
    path clean_species_manifest
    path reference_manifest
    path family_candidates

    output:
    path "reproducibility_code.md"

    script:
    """
    python ${projectDir}/../bin/genefam/build_reproducibility_code.py \\
      --config ${config} \\
      --clean-species-manifest ${clean_species_manifest} \\
      --reference-manifest ${reference_manifest} \\
      --family-candidates ${family_candidates} \\
      --config-label ${params.config} \\
      --groups-label ${params.groups} \\
      --outdir ${params.outdir} \\
      --preprocess-outdir ${params.preprocess_outdir} \\
      --clean-species-manifest-label ${params.preprocess_outdir}/species_manifest.clean.tsv \\
      --reference-manifest-label ${params.preprocess_outdir}/reference/reference_generation.tsv \\
      --family-candidates-label ${params.outdir}/tables/family_candidates.tsv \\
      --out reproducibility_code.md
    """
}
