from pathlib import Path

import pytest

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


def test_build_event_evidence_rejects_named_event_without_metadata():
    rows = [
        {
            "gene_a": "a1",
            "gene_b": "a2",
            "ks": "0.12",
            "wgd_layer": "WGD_layer_1",
            "event_name": "alhpa",
            "confidence": "configured",
        }
    ]

    with pytest.raises(ValueError, match="No metadata configured for WGD event: alhpa"):
        build_event_evidence(rows, event_metadata={"alpha": {"scope": "Arabidopsis_Brassicaceae"}})


def test_load_event_metadata_reads_brassicaceae_named_events():
    metadata = load_event_metadata(Path("configs/wgd_events.brassicaceae.yaml"))

    assert set(metadata) == {"gamma", "beta", "alpha", "theta"}
    assert metadata["gamma"]["scope"] == "core_eudicots"
    assert metadata["theta"]["expected_relative_age"] == "lineage_specific_recent"


def test_load_event_metadata_rejects_duplicate_named_events(tmp_path):
    events_config = tmp_path / "wgd_events.yaml"
    events_config.write_text(
        "\n".join(
            [
                "wgd_events:",
                "  - name: alpha",
                "    scope: Arabidopsis_Brassicaceae",
                "    evidence: literature",
                "    expected_relative_age: recent",
                "  - name: alpha",
                "    scope: duplicate_scope",
                "    evidence: literature",
                "    expected_relative_age: duplicate",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate WGD event name: alpha"):
        load_event_metadata(events_config)


def test_load_event_metadata_rejects_named_events_missing_required_fields(tmp_path):
    events_config = tmp_path / "wgd_events.yaml"
    events_config.write_text(
        "\n".join(
            [
                "wgd_events:",
                "  - name: alpha",
                "    evidence: literature",
                "    expected_relative_age: recent",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="WGD event alpha is missing required field: scope"):
        load_event_metadata(events_config)


def test_load_event_metadata_rejects_events_missing_name(tmp_path):
    events_config = tmp_path / "wgd_events.yaml"
    events_config.write_text(
        "\n".join(
            [
                "wgd_events:",
                "  - scope: Brassicaceae",
                "    evidence: literature",
                "    expected_relative_age: recent",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="WGD event entry 1 is missing required field: name"):
        load_event_metadata(events_config)
