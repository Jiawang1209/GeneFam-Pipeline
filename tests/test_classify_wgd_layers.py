from bin.genefam.classify_wgd_layers import classify_pairs


def test_classify_pairs_assigns_layers_by_ks_bins():
    rows = [
        {"gene_a": "a1", "gene_b": "a2", "ks": "0.12"},
        {"gene_a": "b1", "gene_b": "b2", "ks": "0.48"},
        {"gene_a": "c1", "gene_b": "c2", "ks": "1.10"},
    ]

    classified = classify_pairs(rows, bins=[0.3, 0.8], named_events={})

    assert [row["wgd_layer"] for row in classified] == ["WGD_layer_1", "WGD_layer_2", "WGD_layer_3"]
    assert {row["event_name"] for row in classified} == {"unannotated"}


def test_classify_pairs_uses_named_events_when_configured():
    rows = [{"gene_a": "a1", "gene_b": "a2", "ks": "0.12"}]

    classified = classify_pairs(rows, bins=[0.3], named_events={"WGD_layer_1": "alpha"})

    assert classified[0]["wgd_layer"] == "WGD_layer_1"
    assert classified[0]["event_name"] == "alpha"
    assert classified[0]["confidence"] == "configured"
