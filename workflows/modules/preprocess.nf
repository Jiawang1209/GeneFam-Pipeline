process PREPROCESS_SPECIES {
    tag "01_preprocess species"
    publishDir "${params.preprocess_outdir}", mode: "copy", overwrite: true

    input:
    path species_manifest

    output:
    path "species_manifest.raw.tsv"
    path "species_manifest.clean.tsv"
    path "species_bank_clean"
    path "all_transcript_gene_map.tsv"
    path "all_representative_transcripts.tsv"
    path "all_preprocess_warnings.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/preprocess_species.py \\
      --species-manifest ${species_manifest} \\
      --outdir .
    """
}

process BUILD_REFERENCE_FROM_TAIR_DOMAINS {
    tag "01_preprocess reference"
    publishDir "${params.preprocess_outdir}", mode: "copy", overwrite: true

    input:
    path config_file
    path clean_species_manifest

    output:
    path "reference/*.reference.pep.fa"
    path "reference/reference_generation.tsv"
    path "reference/*.TAIR.ID"
    path "reference/*.missing_ids.txt"

    script:
    """
    python ${projectDir}/../bin/genefam/build_reference_from_config.py \\
      --config ${config_file} \\
      --species-manifest ${clean_species_manifest} \\
      --base-dir ${projectDir}/.. \\
      --outdir reference
    """
}
