process EXTRACT_CHROMOSOME_LOCATIONS {
    tag "chromosome locations"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path family_candidates
    path species_manifest

    output:
    path "chromosome_locations.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/extract_chromosome_locations.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --out chromosome_locations.tsv
    """
}

process EXTRACT_GENE_STRUCTURE {
    tag "gene structure summary"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path family_candidates
    path species_manifest

    output:
    path "gene_structure_summary.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/extract_gene_structure.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --out gene_structure_summary.tsv
    """
}

process SUBSET_EXPRESSION_MATRIX {
    tag "family expression matrix"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path family_candidates
    path expression_matrix

    output:
    path "family_expression.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/subset_expression_matrix.py \\
      --family-candidates ${family_candidates} \\
      --expression ${expression_matrix} \\
      --out family_expression.tsv
    """
}

process EXTRACT_PROMOTERS {
    tag "promoters"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path family_candidates
    path species_manifest
    val upstream_bp
    val downstream_bp

    output:
    path "tables/promoters.bed"
    path "sequences/promoters.fa"

    script:
    """
    mkdir -p tables sequences
    python ${projectDir}/../bin/genefam/extract_promoters.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --upstream-bp ${upstream_bp} \\
      --downstream-bp ${downstream_bp} \\
      --out-bed tables/promoters.bed \\
      --out-fasta sequences/promoters.fa
    """
}
