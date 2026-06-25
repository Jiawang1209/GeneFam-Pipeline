process PREPARE_ALIGNMENT_INPUTS {
    tag "prepare alignment inputs"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    val family_name
    path family_members_faa
    val aligner
    val outdir

    output:
    path "alignment_manifest.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/prepare_alignment_inputs.py \\
      --family-name ${family_name} \\
      --fasta ${family_members_faa} \\
      --outdir ${outdir} \\
      --aligner ${aligner} \\
      --out alignment_manifest.tsv
    """
}

process RUN_ALIGNMENT {
    tag "run MAFFT alignment"
    publishDir "${params.outdir}/alignment", mode: "copy", overwrite: true

    input:
    val family_name
    val aligner
    path family_members_faa

    output:
    path "${family_name}.${aligner}.aln.faa"

    script:
    """
    mafft --auto ${family_members_faa} > ${family_name}.${aligner}.aln.faa
    """
}

process PREPARE_PHYLOGENY_INPUTS {
    tag "prepare phylogeny inputs"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path alignment_manifest
    val tree_builder
    val outdir

    output:
    path "phylogeny_manifest.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/prepare_phylogeny_inputs.py \\
      --alignment-manifest ${alignment_manifest} \\
      --tree-builder ${tree_builder} \\
      --outdir ${outdir} \\
      --out phylogeny_manifest.tsv
    """
}

process RUN_PHYLOGENY {
    tag "run ${tree_builder} phylogeny"
    publishDir "${params.outdir}/phylogeny", mode: "copy", overwrite: true

    input:
    val family_name
    path alignment
    val tree_builder

    output:
    path "${family_name}.${tree_builder}.treefile"

    script:
    """
    if [ "${tree_builder}" = "fasttree" ]; then
      FASTTREE_BIN=\$(command -v FastTree || command -v fasttree)
      "\${FASTTREE_BIN}" -wag ${alignment} > ${family_name}.${tree_builder}.treefile
    else
      IQTREE_BIN=\$(command -v iqtree2 || command -v iqtree)
      "\${IQTREE_BIN}" -s ${alignment} -m MFP -bb 1000 -nt AUTO
      cp ${alignment}.treefile ${family_name}.${tree_builder}.treefile
    fi
    """
}

process PARSE_MEME_MOTIFS {
    tag "parse MEME motifs"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path meme_txt
    val family_name

    output:
    path "motif_summary.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/parse_meme_motifs.py \\
      --meme-txt ${meme_txt} \\
      --family-name ${family_name} \\
      --out motif_summary.tsv
    """
}
