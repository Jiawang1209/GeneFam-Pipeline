process FAMILY_SUMMARY {
    tag "family summary"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path candidates

    output:
    path "family_counts.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/summarize_family.py \\
      --candidates ${candidates} \\
      --out family_counts.tsv
    """
}
