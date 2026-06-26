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

process BUILD_STANDARD_REPORT_INDEX {
    tag "standard report index"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    input:
    path species_manifest
    path run_config_snapshot
    path family_candidates
    path family_counts
    path family_members_faa
    path gene_family_copy_number
    path gene_family_copy_number_summary
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
    val promoter_cis_category_summary
    val promoter_cis_pdf
    val promoter_cis_png
    val feature_summary
    val feature_summary_pdf
    val feature_summary_png
    val mcscanx_circlize_pdf
    val mcscanx_circlize_png
    val ppi_edges
    val ppi_nodes
    val ppi_hubs
    val ppi_ggnetview_status
    val ppi_ggnetview_pdf
    val ppi_ggnetview_png
    val family_expression
    val expression_sample_metadata
    val expression_group_matrix
    val expression_gene_summary
    val expression_heatmap_pdf
    val expression_heatmap_png
    path wgd_handoff_manifest
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
      --family-members-faa ${family_members_faa} \\
      --gene-family-copy-number ${gene_family_copy_number} \\
      --gene-family-copy-number-summary ${gene_family_copy_number_summary} \\
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
      --promoter-cis-category-summary "${promoter_cis_category_summary}" \\
      --promoter-cis-pdf "${promoter_cis_pdf}" \\
      --promoter-cis-png "${promoter_cis_png}" \\
      --feature-summary "${feature_summary}" \\
      --feature-summary-pdf "${feature_summary_pdf}" \\
      --feature-summary-png "${feature_summary_png}" \\
      --mcscanx-circlize-pdf "${mcscanx_circlize_pdf}" \\
      --mcscanx-circlize-png "${mcscanx_circlize_png}" \\
      --ppi-edges "${ppi_edges}" \\
      --ppi-nodes "${ppi_nodes}" \\
      --ppi-hubs "${ppi_hubs}" \\
      --ppi-ggnetview-status "${ppi_ggnetview_status}" \\
      --ppi-ggnetview-pdf "${ppi_ggnetview_pdf}" \\
      --ppi-ggnetview-png "${ppi_ggnetview_png}" \\
      --family-expression "${family_expression}" \\
      --expression-sample-metadata "${expression_sample_metadata}" \\
      --expression-group-matrix "${expression_group_matrix}" \\
      --expression-gene-summary "${expression_gene_summary}" \\
      --expression-heatmap-pdf "${expression_heatmap_pdf}" \\
      --expression-heatmap-png "${expression_heatmap_png}" \\
      --wgd-handoff-manifest ${wgd_handoff_manifest} \\
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
    path plot_manifest
    path software_versions
    path figure_interpretations

    output:
    path "final_report.md"

    script:
    """
    python ${projectDir}/../bin/genefam/assemble_report.py \\
      --project-name ${project_name} \\
      --gene-family ${gene_family} \\
      --report-index ${report_index} \\
      --run-config-snapshot ${run_config_snapshot} \\
      --plot-manifest ${plot_manifest} \\
      --software-versions ${software_versions} \\
      --figure-interpretations ${figure_interpretations} \\
      --out final_report.md
    """
}
