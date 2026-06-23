process EXTRACT_CHROMOSOME_LOCATIONS {
    tag "chromosome locations"

    input:
    path family_candidates
    path species_manifest

    output:
    path "chromosome_locations.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/extract_chromosome_locations.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --out chromosome_locations.tsv
    """
}

process SUBSET_EXPRESSION_MATRIX {
    tag "family expression matrix"

    input:
    path family_candidates
    path expression_matrix

    output:
    path "family_expression.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/subset_expression_matrix.py \\
      --family-candidates ${family_candidates} \\
      --expression ${expression_matrix} \\
      --out family_expression.tsv
    """
}
