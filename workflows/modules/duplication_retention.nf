process NORMALIZE_DUPLICATE_TYPES {
    tag "normalize duplicate types"

    input:
    path duplicates

    output:
    path "normalized_duplicate_types.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/normalize_duplicate_types.py \\
      --duplicates ${duplicates} \\
      --out normalized_duplicate_types.tsv
    """
}

process JOIN_FAMILY_DUPLICATES {
    tag "family duplicate classification"

    input:
    path family_members
    path normalized_duplicates

    output:
    path "family_duplicate_classification.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/join_family_duplicates.py \\
      --family-members ${family_members} \\
      --duplicates ${normalized_duplicates} \\
      --out family_duplicate_classification.tsv
    """
}

process CLASSIFY_WGD_LAYERS {
    tag "classify WGD layers"

    input:
    path kaks_pairs
    val ks_bins
    val event_args

    output:
    path "wgd_layers.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/classify_wgd_layers.py \\
      --pairs ${kaks_pairs} \\
      --bins ${ks_bins} \\
      ${event_args} \\
      --out wgd_layers.tsv
    """
}

process BUILD_WGD_EVENT_EVIDENCE {
    tag "WGD event evidence"

    input:
    path classified_pairs
    path events_config

    output:
    path "wgd_event_evidence.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/build_wgd_event_evidence.py \\
      --classified-pairs ${classified_pairs} \\
      --events-config ${events_config} \\
      --out wgd_event_evidence.tsv
    """
}

process ANNOTATE_FAMILY_WGD_EVENTS {
    tag "family WGD event membership"

    input:
    path family_duplicates
    path classified_pairs

    output:
    path "family_wgd_event_membership.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/annotate_family_wgd_events.py \\
      --family-duplicates ${family_duplicates} \\
      --classified-pairs ${classified_pairs} \\
      --out family_wgd_event_membership.tsv
    """
}

process SUMMARIZE_FAMILY_EVENT_RETENTION {
    tag "family event retention summary"

    input:
    path family_wgd_events

    output:
    path "family_event_retention_summary.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/summarize_family_event_retention.py \\
      --family-wgd-events ${family_wgd_events} \\
      --out family_event_retention_summary.tsv
    """
}

process RETENTION_ENRICHMENT {
    tag "duplicate retention enrichment"

    input:
    path family_duplicates
    path background_duplicates

    output:
    path "retention_enrichment.tsv"

    script:
    """
    python ${projectDir}/bin/genefam/retention_enrichment.py \\
      --family-duplicates ${family_duplicates} \\
      --background-duplicates ${background_duplicates} \\
      --out retention_enrichment.tsv
    """
}
