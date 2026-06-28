process BUILD_REBUILT_HMMER_INPUTS {
    tag "Reference two-pass HMM rebuild"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path first_pass_hmmer_tables
    path species_manifest
    val family_name

    output:
    path "two_pass_hmmer/rebuilt_hmmer_inputs.tsv", emit: inputs
    path "two_pass_hmmer", emit: package_dir

    script:
    """
    mkdir -p two_pass_hmmer
    hmmerArgs=()
    for table in ${first_pass_hmmer_tables}; do
      hmmerArgs+=(--hmmer-table "\${table}")
    done
    python ${projectDir}/../bin/genefam/build_rebuilt_hmmer_inputs.py \\
      "\${hmmerArgs[@]}" \\
      --species-manifest ${species_manifest} \\
      --family-name ${family_name} \\
      --outdir two_pass_hmmer
    hit_count=\$(awk -F '\\t' 'NR == 2 {print \$2}' two_pass_hmmer/rebuilt_hmmer_status.tsv)
    if [ "\${hit_count:-0}" -lt 2 ]; then
      echo "Need at least two first-pass HMMER hits to rebuild a family HMM; got \${hit_count:-0}" >&2
      exit 1
    fi
    mafft --auto two_pass_hmmer/first_pass_hits.faa > two_pass_hmmer/first_pass_hits.aln.faa
    hmmbuild two_pass_hmmer/${family_name}.rebuilt.hmm two_pass_hmmer/first_pass_hits.aln.faa > two_pass_hmmer/hmmbuild.log
    """
}

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

    python ${projectDir}/../bin/genefam/parse_hmmer_domtbl.py \\
      --input ${species_id}.${hmm_id}.domtblout \\
      --species-id ${species_id} \\
      --out ${species_id}.${hmm_id}.hmmer.raw.tsv

    python ${projectDir}/../bin/genefam/filter_hmmer_domains.py \\
      --input ${species_id}.${hmm_id}.hmmer.raw.tsv \\
      --max-evalue ${params.hmmer_max_evalue} \\
      --min-bitscore ${params.hmmer_min_bitscore} \\
      --min-domain-coverage ${params.hmmer_min_domain_coverage} \\
      --out ${species_id}.${hmm_id}.hmmer.tsv
    """
}
