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

process DOMAIN_FILTER {
    tag "${species_id}"

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
