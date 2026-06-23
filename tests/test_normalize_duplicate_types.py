from bin.genefam.normalize_duplicate_types import normalize_duplicate_rows


def test_normalize_duplicate_rows_accepts_common_duplicate_type_aliases():
    rows = [
        {"gene_id": "g1", "duplicate_type": "WGD"},
        {"gene_id": "g2", "duplicate_type": "segmental"},
        {"gene_id": "g3", "duplicate_type": "Tandem"},
        {"gene_id": "g4", "duplicate_type": "proximal"},
        {"gene_id": "g5", "duplicate_type": "dispersed"},
        {"gene_id": "g6", "duplicate_type": "singleton"},
    ]

    normalized = normalize_duplicate_rows(rows)

    assert normalized == [
        {"gene_id": "g1", "duplicate_type": "WGD/segmental", "raw_duplicate_type": "WGD"},
        {"gene_id": "g2", "duplicate_type": "WGD/segmental", "raw_duplicate_type": "segmental"},
        {"gene_id": "g3", "duplicate_type": "tandem", "raw_duplicate_type": "Tandem"},
        {"gene_id": "g4", "duplicate_type": "proximal", "raw_duplicate_type": "proximal"},
        {"gene_id": "g5", "duplicate_type": "dispersed", "raw_duplicate_type": "dispersed"},
        {"gene_id": "g6", "duplicate_type": "singleton", "raw_duplicate_type": "singleton"},
    ]


def test_normalize_duplicate_rows_supports_type_column():
    rows = [{"gene_id": "g1", "type": "whole_genome"}]

    normalized = normalize_duplicate_rows(rows)

    assert normalized[0]["duplicate_type"] == "WGD/segmental"


def test_normalize_duplicate_rows_fails_on_unknown_type():
    rows = [{"gene_id": "g1", "duplicate_type": "mystery"}]

    try:
        normalize_duplicate_rows(rows)
    except ValueError as error:
        assert "Unknown duplicate type for gene g1: mystery" in str(error)
    else:
        raise AssertionError("Expected ValueError for unknown duplicate type")
