process BUILD_IDENTIFICATION_INPUTS {
    tag "identification inputs"

    input:
    path config_file
    path species_manifest

    output:
    path "identification_inputs/hmmer_inputs.tsv"
    path "identification_inputs/diamond_inputs.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_identification_inputs.py \\
      --config ${config_file} \\
      --species-manifest ${species_manifest} \\
      --base-dir ${projectDir}/.. \\
      --outdir identification_inputs
    """
}
