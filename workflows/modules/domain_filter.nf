process MOCK_IDENTIFICATION_EVIDENCE {
    tag "mock identification evidence"

    input:
    path mock_evidence_dir

    output:
    tuple val("mock"), path("hmmer.tsv"), path("diamond.tsv")

    script:
    """
    cp ${mock_evidence_dir}/hmmer.tsv hmmer.tsv
    cp ${mock_evidence_dir}/diamond.tsv diamond.tsv
    """
}

process EMPTY_HMMER_EVIDENCE {
    tag "${species_id}:empty hmmer"

    input:
    val species_id

    output:
    tuple val(species_id), path("${species_id}.hmmer.tsv")

    script:
    """
    printf 'species_id\tgene_id\thmm_id\tevalue\thmm_from\thmm_to\thmm_length\tbitscore\n' > ${species_id}.hmmer.tsv
    """
}

process EMPTY_DIAMOND_EVIDENCE {
    tag "${species_id}:empty diamond"

    input:
    val species_id

    output:
    tuple val(species_id), path("${species_id}.diamond.tsv")

    script:
    """
    printf 'species_id\tgene_id\treference_hit\tevalue\n' > ${species_id}.diamond.tsv
    """
}

process DOMAIN_FILTER {
    tag "${species_id}"
    publishDir "${params.outdir}/tables/domain_filter", mode: "copy", overwrite: true

    input:
    tuple val(species_id), path(hmmer_tsv), path(diamond_tsv)
    val final_rule

    output:
    tuple val(species_id), path("${species_id}.family_candidates.tsv")

    script:
    """
    python ${projectDir}/../bin/genefam/merge_identification_evidence.py \\
      --hmmer ${hmmer_tsv} \\
      --diamond ${diamond_tsv} \\
      --final-rule ${final_rule} \\
      --out ${species_id}.family_candidates.tsv
    """
}

process CONCAT_FAMILY_CANDIDATES {
    tag "concat family candidates"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path candidate_tables

    output:
    path "family_candidates.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/concat_tsv.py \\
      --inputs ${candidate_tables} \\
      --out family_candidates.tsv
    """
}
