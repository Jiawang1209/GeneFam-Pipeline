process PLOT_FAMILY_COUNTS {
    tag "plot family counts"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path family_counts

    output:
    path "plots/family_counts.pdf"
    path "plots/family_counts.png"

    script:
    """
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_family_counts.R --args ${family_counts} plots
    """
}

process PLOT_KAKS {
    tag "plot Ka/Ks"
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

process PLOT_EXPRESSION_HEATMAP {
    tag "plot expression heatmap"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path expression_matrix
    val sample_metadata

    output:
    path "tables/expression_sample_metadata.tsv"
    path "tables/expression_group_matrix.tsv"
    path "tables/expression_gene_summary.tsv"
    path "plots/expression_heatmap.pdf"
    path "plots/expression_heatmap.png"

    script:
    def metadataArg = sample_metadata ? "--metadata ${sample_metadata}" : ""
    """
    mkdir -p tables plots
    python ${projectDir}/../bin/genefam/build_expression_summary.py \\
      --expression ${expression_matrix} \\
      ${metadataArg} \\
      --outdir tables
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_expression_heatmap.R --args tables/expression_group_matrix.tsv tables/expression_sample_metadata.tsv tables/expression_gene_summary.tsv plots
    """
}

process PLOT_FEATURE_SUMMARY {
    tag "plot feature summary"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    val domains
    path motifs
    path gene_structures
    val synteny
    val promoters

    output:
    path "tables/feature_summary.tsv"
    path "plots/feature_summary.pdf"
    path "plots/feature_summary.png"

    script:
    def domainArg = domains ? "--domains ${domains}" : ""
    def syntenyArg = synteny ? "--synteny ${synteny}" : ""
    def promoterArg = promoters ? "--promoters ${promoters}" : ""
    """
    mkdir -p tables plots
    python ${projectDir}/../bin/genefam/summarize_feature_tables.py \\
      ${domainArg} \\
      --motifs ${motifs} \\
      --gene-structures ${gene_structures} \\
      ${syntenyArg} \\
      ${promoterArg} \\
      --out tables/feature_summary.tsv
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_feature_summary.R --args tables/feature_summary.tsv plots
    """
}

process PLOT_TREE_FEATURES {
    tag "plot tree features"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path phylogeny_tree
    path family_candidates
    path motifs
    path gene_structures
    val domains

    output:
    path "tables/tree_feature_matrix.tsv"
    path "plots/tree_features.pdf"
    path "plots/tree_features.png"

    script:
    def domainArg = domains ? "--domains ${domains}" : ""
    """
    mkdir -p tables plots
    python ${projectDir}/../bin/genefam/build_tree_feature_matrix.py \\
      --tree ${phylogeny_tree} \\
      --family-candidates ${family_candidates} \\
      --motifs ${motifs} \\
      --gene-structures ${gene_structures} \\
      ${domainArg} \\
      --out tables/tree_feature_matrix.tsv
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_tree_features.R --args tables/tree_feature_matrix.tsv plots
    """
}

process PLOT_GENE_FAMILY_INFO {
    tag "plot gene family information"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path family_counts
    path family_members_faa

    output:
    path "tables/gene_family_copy_number.tsv"
    path "tables/gene_family_copy_number_summary.tsv"
    path "tables/gene_family_species_order.tsv"
    path "tables/gene_family_copy_number_expansion.tsv"
    path "tables/gene_family_protein_properties.tsv"
    path "plots/gene_family_info_summary.pdf"
    path "plots/gene_family_info_summary.png"

    script:
    """
    mkdir -p tables plots
    python ${projectDir}/../bin/genefam/build_gene_family_info.py \\
      --family-counts ${family_counts} \\
      --family-members-faa ${family_members_faa} \\
      --outdir tables
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_gene_family_info.R --args tables/gene_family_copy_number.tsv tables/gene_family_copy_number_summary.tsv tables/gene_family_protein_properties.tsv tables/gene_family_species_order.tsv tables/gene_family_copy_number_expansion.tsv plots
    """
}

process PLOT_PROMOTER_CIS_ELEMENTS {
    tag "plot promoter cis-elements"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path cis_elements

    output:
    path "tables/promoter_cis_elements.tsv"
    path "tables/promoter_cis_gene_matrix.tsv"
    path "tables/promoter_cis_gene_element_matrix.tsv"
    path "tables/promoter_cis_category_summary.tsv"
    path "tables/promoter_cis_element_annotations.tsv"
    path "plots/promoter_cis_elements.pdf"
    path "plots/promoter_cis_elements.png"

    script:
    """
    mkdir -p tables plots
    python ${projectDir}/../bin/genefam/build_promoter_cis_elements.py \\
      --cis-elements ${cis_elements} \\
      --outdir tables
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_promoter_cis_elements.R --args tables/promoter_cis_gene_matrix.tsv tables/promoter_cis_category_summary.tsv tables/promoter_cis_gene_element_matrix.tsv tables/promoter_cis_element_annotations.tsv plots
    """
}

process PLOT_MCSCANX_CIRCLIZE {
    tag "plot MCScanX circlize"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path chromosome_locations
    path syntenic_pairs

    output:
    path "tables/circlize_chromosomes.tsv"
    path "tables/circlize_links.tsv"
    path "tables/circlize_link_density.tsv"
    path "tables/circlize_duplicate_type_tracks.tsv"
    path "tables/circlize_skipped_links.tsv"
    path "plots/mcscanx_circlize.pdf"
    path "plots/mcscanx_circlize.png"

    script:
    """
    mkdir -p tables plots
    python ${projectDir}/../bin/genefam/build_circlize_inputs.py \\
      --chromosome-locations ${chromosome_locations} \\
      --syntenic-pairs ${syntenic_pairs} \\
      --out-chromosomes tables/circlize_chromosomes.tsv \\
      --out-links tables/circlize_links.tsv \\
      --out-skipped tables/circlize_skipped_links.tsv \\
      --out-density tables/circlize_link_density.tsv \\
      --out-duplicate-tracks tables/circlize_duplicate_type_tracks.tsv
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_mcscanx_circlize.R --args tables/circlize_chromosomes.tsv tables/circlize_links.tsv tables/circlize_link_density.tsv tables/circlize_duplicate_type_tracks.tsv plots
    """
}

process PLOT_PPI_GGNETVIEW {
    tag "plot PPI ggNetView"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path ppi_edges
    val ppi_nodes

    output:
    path "tables/ppi_edges.tsv"
    path "tables/ppi_nodes.tsv"
    path "tables/ppi_hubs.tsv"
    path "tables/ppi_input_evidence.tsv"
    path "tables/ppi_network_qc.tsv"
    path "tables/ppi_ggnetview_status.tsv"
    path "plots/ppi_ggnetview.pdf"
    path "plots/ppi_ggnetview.png"

    script:
    def nodesArg = ppi_nodes ? "--nodes ${ppi_nodes}" : ""
    """
    mkdir -p tables plots
    python ${projectDir}/../bin/genefam/build_ppi_tables.py \\
      --edges ${ppi_edges} \\
      ${nodesArg} \\
      --outdir tables
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_ppi_ggnetview.R --args tables/ppi_edges.tsv tables/ppi_nodes.tsv plots tables/ppi_ggnetview_status.tsv
    """
}

process BUILD_PLOT_MANIFEST {
    tag "plot manifest"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    output:
    path "plot_manifest.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_plot_manifest.py \\
      --plot "family_counts=plots/family_counts.pdf=Family member counts by species" \\
      --plot "gene_family_info_summary=plots/gene_family_info_summary.pdf=Gene family copy-number and protein-property summary" \\
      --plot "tree_features=plots/tree_features.pdf=Tree, motif, gene-structure, and domain composite plot" \\
      --plot "promoter_cis_elements=plots/promoter_cis_elements.pdf=Promoter cis-element category matrix and top element summary" \\
      --plot "ppi_ggnetview=plots/ppi_ggnetview.pdf=PPI network generated with ggNetView" \\
      --plot "ks_distribution=plots/ks_distribution.pdf=Ks distribution for duplicated pairs" \\
      --plot "expression_heatmap=plots/expression_heatmap.pdf=Family member expression heatmap" \\
      --out plot_manifest.tsv
    """
}
