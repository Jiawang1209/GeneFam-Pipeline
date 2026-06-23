from pathlib import Path

from bin.genefam.build_wgd_event_evidence import build_event_evidence, load_event_metadata


def test_build_event_evidence_keeps_unannotated_layers_neutral():
    rows = [
        {
            "gene_a": "a1",
            "gene_b": "a2",
            "ks": "0.12",
            "wgd_layer": "WGD_layer_1",
            "event_name": "unannotated",
            "confidence": "layer_only",
        }
    ]

    evidence = build_event_evidence(rows, event_metadata={})

    assert evidence == [
        {
            "wgd_layer": "WGD_layer_1",
            "pair_count": "1",
            "ks_min": "0.1200",
            "ks_median": "0.1200",
            "ks_max": "0.1200",
            "event_name": "unannotated",
            "interpretation_status": "inferred_layer_only",
            "evidence_source": "",
            "species_scope": "",
            "expected_relative_age": "",
        }
    ]


def test_build_event_evidence_adds_metadata_only_for_configured_named_events():
    rows = [
        {
            "gene_a": "a1",
            "gene_b": "a2",
            "ks": "0.12",
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "confidence": "configured",
        },
        {
            "gene_a": "a3",
            "gene_b": "a4",
            "ks": "0.20",
            "wgd_layer": "WGD_layer_1",
            "event_name": "alpha",
            "confidence": "configured",
        },
    ]

    evidence = build_event_evidence(
        rows,
        event_metadata={
            "alpha": {
                "scope": "Arabidopsis_Brassicaceae",
                "evidence": "literature",
                "expected_relative_age": "recent",
            }
        },
    )

    assert evidence[0]["event_name"] == "alpha"
    assert evidence[0]["interpretation_status"] == "configured_named_event"
    assert evidence[0]["evidence_source"] == "literature"
    assert evidence[0]["species_scope"] == "Arabidopsis_Brassicaceae"
    assert evidence[0]["ks_median"] == "0.1600"


def test_load_event_metadata_reads_brassicaceae_named_events():
    metadata = load_event_metadata(Path("configs/wgd_events.brassicaceae.yaml"))

    assert set(metadata) == {"gamma", "beta", "alpha", "theta"}
    assert metadata["gamma"]["scope"] == "core_eudicots"
    assert metadata["theta"]["expected_relative_age"] == "lineage_specific_recent"
