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
    path expression_matrix, stageAs: "input_expression_matrix.tsv"

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

process EMPTY_EXPRESSION_STATUS {
    tag "expression missing input"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    output:
    path "expression_status.tsv"
    path "family_expression.tsv"
    path "expression_sample_metadata.tsv"
    path "expression_group_matrix.tsv"
    path "expression_gene_summary.tsv"

    script:
    """
    printf 'status\\tnote\\n' > expression_status.tsv
    printf 'skipped_optional\\tRNA-seq expression matrix not provided; expression module skipped\\n' >> expression_status.tsv
    printf 'gene_id\\n' > family_expression.tsv
    printf 'sample_id\\tgroup\\n' > expression_sample_metadata.tsv
    printf 'gene_id\\n' > expression_group_matrix.tsv
    printf 'gene_id\\tmean_expression\\tmax_expression\\tresponsive_status\\n' > expression_gene_summary.tsv
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
    path "plantcare_submission"

    script:
    """
    mkdir -p tables sequences plantcare_submission
    python ${projectDir}/../bin/genefam/extract_promoters.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --upstream-bp ${upstream_bp} \\
      --downstream-bp ${downstream_bp} \\
      --out-bed tables/promoters.bed \\
      --out-fasta sequences/promoters.fa
    python ${projectDir}/../bin/genefam/split_promoter_fasta_for_plantcare.py \\
      --promoter-fasta sequences/promoters.fa \\
      --outdir plantcare_submission \\
      --records-per-file ${params.plantcare_records_per_file} \\
      --prefix ${params.gene_family}_promoters
    """
}
