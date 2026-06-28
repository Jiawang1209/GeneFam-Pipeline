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
    path "tables/gene_family_pangenome_summary.tsv"
    path "tables/gene_family_protein_properties.tsv"
    path "plots/gene_family_info_summary.pdf"
    path "plots/gene_family_info_summary.png"

    script:
    """
    mkdir -p tables plots
    speciesOrderArg=""
    speciesOrderParam="${params.gene_family_species_order}"
    if [ -n "\${speciesOrderParam}" ] && [ "\${speciesOrderParam}" != "null" ]; then
      speciesOrderArg="--species-order ${params.gene_family_species_order}"
    fi
    python ${projectDir}/../bin/genefam/build_gene_family_info.py \\
      --family-counts ${family_counts} \\
      --family-members-faa ${family_members_faa} \\
      \${speciesOrderArg} \\
      --outdir tables
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_gene_family_info.R --args tables/gene_family_copy_number.tsv tables/gene_family_copy_number_summary.tsv tables/gene_family_protein_properties.tsv tables/gene_family_species_order.tsv tables/gene_family_copy_number_expansion.tsv tables/gene_family_pangenome_summary.tsv plots
    """
}

process PLOT_PROMOTER_CIS_ELEMENTS {
    tag "plot promoter cis-elements"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path cis_elements
    val element_descriptions

    output:
    path "tables/promoter_cis_elements.tsv"
    path "tables/promoter_cis_gene_matrix.tsv"
    path "tables/promoter_cis_gene_element_matrix.tsv"
    path "tables/promoter_cis_category_summary.tsv"
    path "tables/promoter_cis_element_annotations.tsv"
    path "plots/promoter_cis_elements.pdf"
    path "plots/promoter_cis_elements.png"
    path "plots/promoter1.pdf"
    path "plots/promoter1.png"
    path "plots/species_promoter2.pdf"
    path "plots/species_promoter2.png"

    script:
    def descriptionsArg = element_descriptions ? "--element-descriptions ${element_descriptions}" : ""
    """
    mkdir -p tables plots
    python ${projectDir}/../bin/genefam/build_promoter_cis_elements.py \\
      --cis-elements ${cis_elements} \\
      ${descriptionsArg} \\
      --outdir tables
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_promoter_cis_elements.R --args tables/promoter_cis_gene_matrix.tsv tables/promoter_cis_category_summary.tsv tables/promoter_cis_gene_element_matrix.tsv tables/promoter_cis_element_annotations.tsv plots
    """
}

process EMPTY_PROMOTER_CIS_ELEMENTS {
    tag "promoter cis-elements missing input"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    output:
    path "tables/promoter_cis_elements.tsv"
    path "tables/promoter_cis_gene_matrix.tsv"
    path "tables/promoter_cis_gene_element_matrix.tsv"
    path "tables/promoter_cis_category_summary.tsv"
    path "tables/promoter_cis_element_annotations.tsv"
    path "tables/promoter_cis_status.tsv"

    script:
    """
    mkdir -p tables
    printf 'species_id\\tgene_id\\telement\\tcategory\\tposition\\tstrand\\tdescription\\n' > tables/promoter_cis_elements.tsv
    printf 'species_id\\tgene_id\\tcategory\\tcount\\n' > tables/promoter_cis_gene_matrix.tsv
    printf 'species_id\\tgene_id\\telement\\tcategory\\tcount\\tpositions\\n' > tables/promoter_cis_gene_element_matrix.tsv
    printf 'category\\telement\\ttotal_count\\tgene_count\\tspecies_count\\tdescription\\n' > tables/promoter_cis_category_summary.tsv
    printf 'element\\tcategory\\tgene_count\\tspecies_count\\ttotal_count\\tposition_min\\tposition_median\\tposition_max\\tdescription\\n' > tables/promoter_cis_element_annotations.tsv
    printf 'status\\tnote\\nmissing_input\\tPlantCARE gene-level hit table not provided; set promoter.cis_elements to enable this module\\n' > tables/promoter_cis_status.tsv
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
    path "tables/ppi_overview_status.tsv"
    path "tables/ppi_ggnetview_status.tsv"
    path "plots/ppi.pdf"
    path "plots/ppi.png"
    path "plots/ppi_ggnetview.pdf"
    path "plots/ppi_ggnetview.png"
    path "tables/node_annotation.tsv"
    path "tables/species_ppi_annotation.tsv"

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

process BUILD_ARANET_PPI_EDGES {
    tag "transfer AraNet PPI"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path family_candidates
    path aranet

    output:
    path "tables/ppi_edges.tsv"
    path "tables/ppi_nodes.tsv"
    path "tables/ppi_transfer_evidence.tsv"

    script:
    """
    mkdir -p tables
    python ${projectDir}/../bin/genefam/build_aranet_ppi_edges.py \\
      --family-candidates ${family_candidates} \\
      --aranet ${aranet} \\
      --outdir tables
    """
}

process BUILD_ARANET_PPI_FROM_RECIPROCAL_BLAST {
    tag "Reference-style AraNet PPI transfer"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path family_candidates
    path species_manifest
    path aranet
    val reference_species

    output:
    path "tables/ppi_transferred_edges.tsv"
    path "tables/ppi_transferred_nodes.tsv"
    path "tables/ppi_transfer_evidence.tsv"
    path "tables/ppi_homology_best_hits.tsv"
    path "tables/ppi_blast_manifest.tsv"
    path "tables/ppi_blast/*/*.tsv"

    script:
    """
    mkdir -p tables tables/ppi_blast
    python ${projectDir}/../bin/genefam/build_aranet_ppi_from_reciprocal_blast.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --aranet ${aranet} \\
      --reference-species ${reference_species} \\
      --outdir tables \\
      --workdir tables/ppi_blast \\
      --threads ${task.cpus}
    """
}

process BUILD_PLOT_MANIFEST {
    tag "plot manifest"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    input:
    val run_feature_summary
    val run_mcscanx_circlize
    val run_kaks_wgd
    val run_promoter_cis
    val run_ppi
    val expression_matrix

    output:
    path "plot_manifest.tsv"

    script:
    """
    plotArgs=(
      --plot "family_counts=plots/family_counts.pdf=Family member counts by species"
      --plot "gene_family_info_summary=plots/gene_family_info_summary.pdf=Gene family copy-number and protein-property summary"
      --plot "gene_family_pangenome_summary=plots/gene_family_info_summary.pdf=Gene family pangenome presence and copy-number balance"
      --plot "tree_features=plots/tree_features.pdf=Tree, motif, gene-structure, and domain composite plot"
    )
    if [ "${run_feature_summary}" = "true" ]; then
      plotArgs+=(--plot "feature_summary=plots/feature_summary.pdf=Integrated domain, motif, gene-structure, synteny, promoter, and expression feature summary")
    fi
    if [ "${run_mcscanx_circlize}" = "true" ]; then
      plotArgs+=(--plot "mcscanx_circlize=plots/mcscanx_circlize.pdf=MCScanX self intra-species collinearity and chromosome-scale circlize plot")
    fi
    if [ "${run_kaks_wgd}" = "true" ]; then
      plotArgs+=(--plot "ks_distribution=plots/ks_distribution.pdf=Ks distribution for duplicated pairs and WGD layer interpretation")
      plotArgs+=(--plot "duplicate_type_kaks=plots/duplicate_type_kaks.pdf=MCScanX self duplicate-type grouped Ka/Ks and Ks overview")
    fi
    if [ "${run_promoter_cis}" = "true" ]; then
      plotArgs+=(--plot "promoter_cis_elements=plots/promoter_cis_elements.pdf=Promoter cis-element category matrix and top element summary")
      plotArgs+=(--plot "promoter1=plots/promoter1.pdf=Reference-style promoter cis-element gene matrix")
      plotArgs+=(--plot "species_promoter2=plots/species_promoter2.pdf=Reference-style species-level promoter cis-element summary")
    fi
    if [ "${run_ppi}" = "true" ]; then
      plotArgs+=(--plot "ppi=plots/ppi.pdf=Reference-style PPI network overview")
      plotArgs+=(--plot "ppi_ggnetview=plots/ppi_ggnetview.pdf=PPI network generated with ggNetView")
    fi
    if [ -n "${expression_matrix}" ] && [ "${expression_matrix}" != "null" ]; then
      plotArgs+=(--plot "expression_heatmap=plots/expression_heatmap.pdf=Family member expression heatmap")
    fi
    python ${projectDir}/../bin/genefam/build_plot_manifest.py \\
      "\${plotArgs[@]}" \\
      --out plot_manifest.tsv
    """
}
