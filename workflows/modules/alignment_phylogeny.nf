process PREPARE_ALIGNMENT_INPUTS {
    tag "prepare alignment inputs"

    input:
    val family_name
    path family_members_faa
    val aligner
    val outdir

    output:
    path "alignment_manifest.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/prepare_alignment_inputs.py \\
      --family-name ${family_name} \\
      --fasta ${family_members_faa} \\
      --outdir ${outdir} \\
      --aligner ${aligner} \\
      --out alignment_manifest.tsv
    """
}

process RUN_ALIGNMENT {
    tag "run MAFFT alignment"

    input:
    path family_members_faa

    output:
    path "raw_alignment.faa"

    script:
    """
    mafft --auto ${family_members_faa} > raw_alignment.faa
    """
}

process PREPARE_PHYLOGENY_INPUTS {
    tag "prepare phylogeny inputs"

    input:
    path alignment_manifest
    val tree_builder
    val outdir

    output:
    path "phylogeny_manifest.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/prepare_phylogeny_inputs.py \\
      --alignment-manifest ${alignment_manifest} \\
      --tree-builder ${tree_builder} \\
      --outdir ${outdir} \\
      --out phylogeny_manifest.tsv
    """
}

process RUN_PHYLOGENY {
    tag "run IQ-TREE phylogeny"

    input:
    path alignment

    output:
    path "treefile.nwk"

    script:
    """
    iqtree2 -s ${alignment} -m MFP -bb 1000 -nt AUTO
    cp ${alignment}.treefile treefile.nwk
    """
}

process PARSE_MEME_MOTIFS {
    tag "parse MEME motifs"

    input:
    path meme_txt
    val family_name

    output:
    path "motif_summary.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/parse_meme_motifs.py \\
      --meme-txt ${meme_txt} \\
      --family-name ${family_name} \\
      --out motif_summary.tsv
    """
}
