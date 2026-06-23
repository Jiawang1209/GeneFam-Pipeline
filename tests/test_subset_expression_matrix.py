import pytest

from bin.genefam.subset_expression_matrix import subset_expression


def test_subset_expression_keeps_requested_genes_and_sample_columns():
    rows = [
        {"gene_id": "gene1", "cold_0h": "1.0", "cold_3h": "3.0"},
        {"gene_id": "gene2", "cold_0h": "0.5", "cold_3h": "0.8"},
        {"gene_id": "gene3", "cold_0h": "4.0", "cold_3h": "8.0"},
    ]

    subset = subset_expression(rows, gene_ids={"gene3", "gene1"})

    assert subset == [
        {"gene_id": "gene1", "cold_0h": "1.0", "cold_3h": "3.0"},
        {"gene_id": "gene3", "cold_0h": "4.0", "cold_3h": "8.0"},
    ]


def test_subset_expression_fails_for_missing_requested_genes():
    rows = [{"gene_id": "gene1", "cold_0h": "1.0"}]

    with pytest.raises(ValueError, match="Missing expression gene IDs: gene2"):
        subset_expression(rows, gene_ids={"gene2"})
