process FAMILY_SUMMARY {
    tag "family summary"

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
