process PREPARE_SPECIES {
    tag "species manifest"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

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
