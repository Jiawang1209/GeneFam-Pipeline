process PLOT_FAMILY_COUNTS {
    tag "plot family counts"

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

    input:
    path expression_matrix

    output:
    path "plots/expression_heatmap.pdf"

    script:
    """
    ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_expression_heatmap.R --args ${expression_matrix} plots
    """
}

process BUILD_PLOT_MANIFEST {
    tag "plot manifest"

    output:
    path "plot_manifest.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_plot_manifest.py \\
      --plot family_counts=plots/family_counts.pdf=Family member counts by species \\
      --plot ks_distribution=plots/ks_distribution.pdf=Ks distribution for duplicated pairs \\
      --plot expression_heatmap=plots/expression_heatmap.pdf=Family member expression heatmap \\
      --out plot_manifest.tsv
    """
}
