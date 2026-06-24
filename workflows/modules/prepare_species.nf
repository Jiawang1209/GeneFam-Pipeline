process PREPARE_SPECIES {
    tag "species manifest"

    input:
    path config_file
    path groups_file

    output:
    path "species_manifest.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/discover_species.py \\
      --config ${config_file} \\
      --groups ${groups_file} \\
      --base-dir ${projectDir}/.. \\
      --out species_manifest.tsv
    """
}
