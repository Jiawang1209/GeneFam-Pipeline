from bin.genefam.retention_enrichment import compute_enrichment


def test_compute_enrichment_reports_duplicate_type_overrepresentation():
    background_rows = [
        {"gene_id": "g1", "duplicate_type": "WGD/segmental"},
        {"gene_id": "g2", "duplicate_type": "WGD/segmental"},
        {"gene_id": "g3", "duplicate_type": "tandem"},
        {"gene_id": "g4", "duplicate_type": "tandem"},
        {"gene_id": "g5", "duplicate_type": "dispersed"},
        {"gene_id": "g6", "duplicate_type": "dispersed"},
        {"gene_id": "g7", "duplicate_type": "singleton"},
        {"gene_id": "g8", "duplicate_type": "singleton"},
        {"gene_id": "g9", "duplicate_type": "proximal"},
        {"gene_id": "g10", "duplicate_type": "proximal"},
    ]
    family_rows = [
        {"gene_id": "g1", "duplicate_type": "WGD/segmental"},
        {"gene_id": "g2", "duplicate_type": "WGD/segmental"},
        {"gene_id": "g11", "duplicate_type": "WGD/segmental"},
        {"gene_id": "g12", "duplicate_type": "tandem"},
    ]

    rows = compute_enrichment(family_rows, background_rows)
    by_type = {row["duplicate_type"]: row for row in rows}

    assert by_type["WGD/segmental"]["family_count"] == "3"
    assert by_type["WGD/segmental"]["background_count"] == "2"
    assert float(by_type["WGD/segmental"]["fold_enrichment"]) > 1
    assert 0 <= float(by_type["WGD/segmental"]["p_value"]) <= 1
    assert by_type["singleton"]["family_count"] == "0"
