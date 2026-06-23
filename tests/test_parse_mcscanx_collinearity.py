from bin.genefam.parse_mcscanx_collinearity import parse_collinearity


def test_parse_collinearity_extracts_blocks_and_gene_pairs(tmp_path):
    collinearity = tmp_path / "sample.collinearity"
    collinearity.write_text(
        "## Alignment 0: score=123.4 e_value=1e-20 N=2 Chr1&Chr2 plus\n"
        "  0-  0: AT1G01010 BraA010001 1e-50\n"
        "  0-  1: AT1G01020 BraA010002 2e-40\n",
        encoding="utf-8",
    )

    rows = parse_collinearity(collinearity)

    assert rows == [
        {
            "block_id": "0",
            "block_score": "123.4",
            "block_evalue": "1e-20",
            "block_pair_count": "2",
            "gene_a": "AT1G01010",
            "gene_b": "BraA010001",
            "pair_evalue": "1e-50",
        },
        {
            "block_id": "0",
            "block_score": "123.4",
            "block_evalue": "1e-20",
            "block_pair_count": "2",
            "gene_a": "AT1G01020",
            "gene_b": "BraA010002",
            "pair_evalue": "2e-40",
        },
    ]
