process DIAMOND_SEARCH {
    tag "${species_id}"

    input:
    tuple val(species_id), path(pep), path(reference_peptides)

    output:
    tuple val(species_id), path("${species_id}.diamond.tsv")

    script:
    """
    diamond makedb --in ${pep} --db ${species_id}.dmnd --quiet
    diamond blastp \\
      --query ${reference_peptides} \\
      --db ${species_id}.dmnd \\
      --out ${species_id}.diamond.raw.tsv \\
      --outfmt 6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore \\
      --quiet

    python ${projectDir}/bin/genefam/parse_diamond_outfmt6.py \\
      --outfmt6 ${species_id}.diamond.raw.tsv \\
      --species-id ${species_id} \\
      --out ${species_id}.diamond.tsv
    """
}
