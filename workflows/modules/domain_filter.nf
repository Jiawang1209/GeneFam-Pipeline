process DOMAIN_FILTER {
    tag "${species_id}"

    input:
    tuple val(species_id), path(hmmer_tsv), path(diamond_tsv)
    val final_rule

    output:
    tuple val(species_id), path("${species_id}.family_candidates.tsv")

    script:
    """
    python ${projectDir}/bin/genefam/merge_identification_evidence.py \\
      --hmmer ${hmmer_tsv} \\
      --diamond ${diamond_tsv} \\
      --final-rule ${final_rule} \\
      --out ${species_id}.family_candidates.tsv
    """
}
