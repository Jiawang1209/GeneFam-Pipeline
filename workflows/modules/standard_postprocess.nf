process EXTRACT_FAMILY_SEQUENCES {
    tag "family member FASTA"

    input:
    path family_candidates
    path species_manifest

    output:
    path "family_members.faa"

    script:
    """
    python ${projectDir}/bin/genefam/extract_family_sequences.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --out family_members.faa
    """
}

process BUILD_STANDARD_REPORT_INDEX {
    tag "standard report index"

    input:
    path species_manifest
    path family_candidates
    path family_counts
    path family_members_faa
    path alignment_manifest
    path phylogeny_manifest
    path plot_manifest

    output:
    path "report_index.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/build_standard_report_index.py \\
      --species-manifest ${species_manifest} \\
      --family-candidates ${family_candidates} \\
      --family-counts ${family_counts} \\
      --family-members-faa ${family_members_faa} \\
      --alignment-manifest ${alignment_manifest} \\
      --phylogeny-manifest ${phylogeny_manifest} \\
      --plot-manifest ${plot_manifest} \\
      --out report_index.tsv
    """
}

process ASSEMBLE_STANDARD_REPORT {
    tag "standard final report"

    input:
    val project_name
    val gene_family
    path report_index
    path plot_manifest

    output:
    path "final_report.md"

    script:
    """
    python ${projectDir}/bin/genefam/assemble_report.py \\
      --project-name ${project_name} \\
      --gene-family ${gene_family} \\
      --report-index ${report_index} \\
      --plot-manifest ${plot_manifest} \\
      --out final_report.md
    """
}
