process HMMER_SEARCH {
    tag "${species_id}:${hmm_id}"

    input:
    tuple val(species_id), path(pep), val(hmm_id), path(hmm_profile)

    output:
    tuple val(species_id), path("${species_id}.${hmm_id}.hmmer.tsv")

    script:
    """
    hmmsearch \\
      --domtblout ${species_id}.${hmm_id}.domtblout \\
      ${hmm_profile} \\
      ${pep} \\
      > ${species_id}.${hmm_id}.hmmout

    python ${projectDir}/bin/genefam/parse_hmmer_domtbl.py \\
      --input ${species_id}.${hmm_id}.domtblout \\
      --species-id ${species_id} \\
      --out ${species_id}.${hmm_id}.hmmer.tsv
    """
}
