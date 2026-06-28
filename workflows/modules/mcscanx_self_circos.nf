process PREPARE_MCSCANX_SELF_CIRCOS {
    tag "prepare MCScanX self circos"

    input:
    path family_candidates
    path species_manifest
    val mcscanx_self_dir
    val mcscanx_self_search_tool

    output:
    path "mcscanx_self_circos"

    script:
    def selfDirArg = mcscanx_self_dir ? "--mcscanx-self-dir ${mcscanx_self_dir}" : ""
    def executeArg = params.mcscanx_execute_self ? "--execute" : ""
    """
    mkdir -p mcscanx_self_circos
    python ${projectDir}/../bin/genefam/build_mcscanx_self_inputs.py \\
      --family-candidates ${family_candidates} \\
      --species-manifest ${species_manifest} \\
      --outdir mcscanx_self_circos \\
      --search-tool ${mcscanx_self_search_tool} \\
      ${selfDirArg}
    python ${projectDir}/../bin/genefam/run_mcscanx_self.py \\
      --prepared-dir mcscanx_self_circos \\
      ${executeArg}
    if grep -q '^executed' mcscanx_self_circos/mcscanx_execution_status.tsv; then
      python ${projectDir}/../bin/genefam/build_mcscanx_self_inputs.py \\
        --family-candidates ${family_candidates} \\
        --species-manifest ${species_manifest} \\
        --outdir mcscanx_self_circos \\
        --mcscanx-self-dir mcscanx_self_circos/mcscanx_run
    fi
    test -s mcscanx_self_circos/mcscanx_run_status.tsv
    test -s mcscanx_self_circos/commands/mcscanx_self_commands.sh
    """
}

process PLOT_MCSCANX_SELF_CIRCOS {
    tag "plot MCScanX self circos"
    publishDir "${params.outdir}", mode: "copy", overwrite: true

    input:
    path chromosome_locations
    path prepared_mcscanx_self_circos, stageAs: "prepared_mcscanx_self_circos"

    output:
    path "mcscanx_self_circos", emit: package_dir
    path "tables/circlize_link_density.tsv", emit: link_density
    path "tables/circlize_duplicate_type_tracks.tsv", emit: duplicate_type_tracks
    path "plots/mcscanx_circlize.pdf", optional: true, emit: pdf
    path "plots/mcscanx_circlize.png", optional: true, emit: png
    path "plots/species", optional: true, emit: species_plots

    script:
    """
    cp -R ${prepared_mcscanx_self_circos} mcscanx_self_circos
    mkdir -p mcscanx_self_circos/tables mcscanx_self_circos/plots

    python ${projectDir}/../bin/genefam/build_circlize_inputs.py \\
      --chromosome-locations ${chromosome_locations} \\
      --syntenic-pairs mcscanx_self_circos/mcscanx_gene_pairs.tsv \\
      --out-chromosomes mcscanx_self_circos/tables/circlize_chromosomes.tsv \\
      --out-links mcscanx_self_circos/tables/circlize_links.tsv \\
      --out-skipped mcscanx_self_circos/tables/circlize_skipped_links.tsv \\
      --out-density mcscanx_self_circos/tables/circlize_link_density.tsv \\
      --out-duplicate-tracks mcscanx_self_circos/tables/circlize_duplicate_type_tracks.tsv

    link_count=\$(tail -n +2 mcscanx_self_circos/tables/circlize_links.tsv | wc -l | tr -d ' ')
    if [ "\${link_count}" -gt 0 ]; then
      ${params.r_bin} --vanilla --slave -f ${projectDir}/../scripts/plot_mcscanx_circlize.R --args \\
        mcscanx_self_circos/tables/circlize_chromosomes.tsv \\
        mcscanx_self_circos/tables/circlize_links.tsv \\
        mcscanx_self_circos/tables/circlize_link_density.tsv \\
        mcscanx_self_circos/tables/circlize_duplicate_type_tracks.tsv \\
        mcscanx_self_circos/plots
      printf 'status\\tlink_count\\tnote\\navailable\\t%s\\tok\\n' "\${link_count}" > mcscanx_self_circos/mcscanx_circlize_status.tsv
    else
      printf 'status\\tlink_count\\tnote\\nmissing_input\\t0\\tNo MCScanX self gene pairs available for circlize plotting\\n' > mcscanx_self_circos/mcscanx_circlize_status.tsv
    fi
    mkdir -p tables plots
    cp mcscanx_self_circos/tables/circlize_link_density.tsv tables/circlize_link_density.tsv
    cp mcscanx_self_circos/tables/circlize_duplicate_type_tracks.tsv tables/circlize_duplicate_type_tracks.tsv
    if [ -s mcscanx_self_circos/plots/mcscanx_circlize.pdf ]; then
      cp mcscanx_self_circos/plots/mcscanx_circlize.pdf plots/mcscanx_circlize.pdf
    fi
    if [ -s mcscanx_self_circos/plots/mcscanx_circlize.png ]; then
      cp mcscanx_self_circos/plots/mcscanx_circlize.png plots/mcscanx_circlize.png
    fi
    if [ -d mcscanx_self_circos/plots/species ]; then
      cp -R mcscanx_self_circos/plots/species plots/species
    fi
    """
}
