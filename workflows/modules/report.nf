process ASSEMBLE_REPORT {
    tag "final report"

    input:
    val project_name
    val gene_family
    path report_index
    path wgd_event_evidence
    path family_event_retention
    path retention_enrichment

    output:
    path "final_report.md"

    script:
    """
    python ${projectDir}/../bin/genefam/assemble_report.py \\
      --project-name ${project_name} \\
      --gene-family ${gene_family} \\
      --report-index ${report_index} \\
      --wgd-event-evidence ${wgd_event_evidence} \\
      --family-event-retention ${family_event_retention} \\
      --retention-enrichment ${retention_enrichment} \\
      --out final_report.md
    """
}
