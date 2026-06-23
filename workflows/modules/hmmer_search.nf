process HMMER_SEARCH {
    tag "${species_id}:${hmm_id}"

    input:
    tuple val(species_id), path(pep), val(hmm_id), path(hmm_profile)

    output:
    tuple val(species_id), val(hmm_id), path("${species_id}.${hmm_id}.domtblout")

    script:
    """
    hmmsearch \\
      --domtblout ${species_id}.${hmm_id}.domtblout \\
      ${hmm_profile} \\
      ${pep} \\
      > ${species_id}.${hmm_id}.hmmout
    """
}
