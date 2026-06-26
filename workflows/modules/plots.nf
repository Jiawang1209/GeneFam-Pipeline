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

    output:
    path "plots/ks_distribution.pdf"

    script:
    """
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_kaks.R --args ${kaks_pairs} plots
    """
}

process PLOT_EXPRESSION_HEATMAP {
    tag "plot expression heatmap"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path expression_matrix

    output:
    path "plots/expression_heatmap.pdf"

    script:
    """
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_expression_heatmap.R --args ${expression_matrix} plots
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

process PLOT_MCSCANX_CIRCLIZE {
    tag "plot MCScanX circlize"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path chromosome_locations
    path syntenic_pairs

    output:
    path "tables/circlize_chromosomes.tsv"
    path "tables/circlize_links.tsv"
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
      --out-skipped tables/circlize_skipped_links.tsv
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_mcscanx_circlize.R --args tables/circlize_chromosomes.tsv tables/circlize_links.tsv plots
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
      --plot "ks_distribution=plots/ks_distribution.pdf=Ks distribution for duplicated pairs" \\
      --plot "expression_heatmap=plots/expression_heatmap.pdf=Family member expression heatmap" \\
      --out plot_manifest.tsv
    """
}
