process EXTRACT_CHROMOSOME_LOCATIONS {
    tag "chromosome locations"

    input:
    path family_members
    path gff3

    output:
    path "chromosome_locations.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/extract_chromosome_locations.py \\
      --family-members ${family_members} \\
      --gff3 ${gff3} \\
      --out chromosome_locations.tsv
    """
}

process SUBSET_EXPRESSION_MATRIX {
    tag "family expression matrix"

    input:
    path family_members
    path expression_matrix

    output:
    path "family_expression.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/subset_expression_matrix.py \\
      --family-members ${family_members} \\
      --expression ${expression_matrix} \\
      --out family_expression.tsv
    """
}
