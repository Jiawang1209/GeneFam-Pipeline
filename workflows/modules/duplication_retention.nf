process BUILD_WGD_RUN_CONFIG_SNAPSHOT {
    tag "WGD run config snapshot"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path duplicates
    path family_members
    path kaks_pairs
    path events_config
    val ks_bins
    val event_args

    output:
    path "wgd_run_config_snapshot.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_wgd_run_config_snapshot.py \\
      --events-config ${events_config} \\
      --ks-bins ${ks_bins} \\
      --event-args "${event_args}" \\
      --duplicates ${duplicates} \\
      --family-members ${family_members} \\
      --kaks-pairs ${kaks_pairs} \\
      --out wgd_run_config_snapshot.tsv
    """
}

process NORMALIZE_DUPLICATE_TYPES {
    tag "normalize duplicate types"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path duplicates

    output:
    path "normalized_duplicate_types.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/normalize_duplicate_types.py \\
      --duplicates ${duplicates} \\
      --out normalized_duplicate_types.tsv
    """
}

process JOIN_FAMILY_DUPLICATES {
    tag "family duplicate classification"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path family_members
    path normalized_duplicates

    output:
    path "family_duplicate_classification.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/join_family_duplicates.py \\
      --family-members ${family_members} \\
      --duplicates ${normalized_duplicates} \\
      --out family_duplicate_classification.tsv
    """
}

process CLASSIFY_WGD_LAYERS {
    tag "classify WGD layers"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path kaks_pairs
    val ks_bins
    val event_args

    output:
    path "wgd_layers.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/classify_wgd_layers.py \\
      --pairs ${kaks_pairs} \\
      --bins ${ks_bins} \\
      ${event_args} \\
      --out wgd_layers.tsv
    """
}

process BUILD_WGD_EVENT_EVIDENCE {
    tag "WGD event evidence"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path classified_pairs
    path events_config

    output:
    path "wgd_event_evidence.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_wgd_event_evidence.py \\
      --classified-pairs ${classified_pairs} \\
      --events-config ${events_config} \\
      --out wgd_event_evidence.tsv
    """
}

process ANNOTATE_FAMILY_WGD_EVENTS {
    tag "family WGD event membership"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path family_duplicates
    path classified_pairs

    output:
    path "family_wgd_event_membership.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/annotate_family_wgd_events.py \\
      --family-duplicates ${family_duplicates} \\
      --classified-pairs ${classified_pairs} \\
      --out family_wgd_event_membership.tsv
    """
}

process SUMMARIZE_FAMILY_EVENT_RETENTION {
    tag "family event retention summary"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path family_wgd_events

    output:
    path "family_event_retention_summary.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/summarize_family_event_retention.py \\
      --family-wgd-events ${family_wgd_events} \\
      --out family_event_retention_summary.tsv
    """
}

process RETENTION_ENRICHMENT {
    tag "duplicate retention enrichment"
    publishDir "${params.outdir}/tables", mode: "copy", overwrite: true

    input:
    path family_duplicates
    path background_duplicates

    output:
    path "retention_enrichment.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/retention_enrichment.py \\
      --family-duplicates ${family_duplicates} \\
      --background-duplicates ${background_duplicates} \\
      --out retention_enrichment.tsv
    """
}

process BUILD_WGD_REPORT_INDEX {
    tag "WGD report index"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    input:
    val published_outdir

    output:
    path "report_index.tsv"

    script:
    """
    python ${projectDir}/../bin/genefam/build_wgd_report_index.py \\
      --published-outdir ${published_outdir} \\
      --out report_index.tsv
    """
}

process ASSEMBLE_WGD_REPORT {
    tag "WGD final report"
    publishDir "${params.outdir}/report", mode: "copy", overwrite: true

    input:
    val project_name
    val gene_family
    path report_index
    path wgd_run_config_snapshot
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
      --run-config-snapshot ${wgd_run_config_snapshot} \\
      --wgd-event-evidence ${wgd_event_evidence} \\
      --family-event-retention ${family_event_retention} \\
      --retention-enrichment ${retention_enrichment} \\
      --out final_report.md
    """
}
