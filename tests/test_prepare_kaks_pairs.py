from bin.genefam.prepare_kaks_pairs import prepare_kaks_pairs


def test_prepare_kaks_pairs_writes_pair_fastas_and_manifest(tmp_path):
    syntenic_pairs = [
        {"gene_a": "AT1G01010", "gene_b": "BraA010001"},
        {"gene_a": "AT1G01020", "gene_b": "BraA010002"},
    ]
    cds_a = tmp_path / "a.cds.fa"
    cds_b = tmp_path / "b.cds.fa"
    cds_a.write_text(">AT1G01010\nATGAAA\n>AT1G01020\nATGCCC\n", encoding="utf-8")
    cds_b.write_text(">BraA010001\nATGTTT\n>BraA010002\nATGGGG\n", encoding="utf-8")
    outdir = tmp_path / "kaks_pairs"

    rows = prepare_kaks_pairs(syntenic_pairs, cds_a, cds_b, outdir)

    assert rows == [
        {
            "gene_a": "AT1G01010",
            "gene_b": "BraA010001",
            "pair_fasta": str(outdir / "AT1G01010__BraA010001.cds.fa"),
            "expected_kaks": str(outdir / "AT1G01010__BraA010001.kaks.tsv"),
        },
        {
            "gene_a": "AT1G01020",
            "gene_b": "BraA010002",
            "pair_fasta": str(outdir / "AT1G01020__BraA010002.cds.fa"),
            "expected_kaks": str(outdir / "AT1G01020__BraA010002.kaks.tsv"),
        },
    ]
    assert (outdir / "AT1G01010__BraA010001.cds.fa").read_text(encoding="utf-8") == (
        ">AT1G01010\nATGAAA\n>BraA010001\nATGTTT\n"
    )


def test_prepare_kaks_pairs_fails_for_missing_cds(tmp_path):
    cds_a = tmp_path / "a.cds.fa"
    cds_b = tmp_path / "b.cds.fa"
    cds_a.write_text(">AT1G01010\nATGAAA\n", encoding="utf-8")
    cds_b.write_text(">BraA010001\nATGTTT\n", encoding="utf-8")

    try:
        prepare_kaks_pairs([{"gene_a": "AT1G99999", "gene_b": "BraA010001"}], cds_a, cds_b, tmp_path)
    except ValueError as error:
        assert "Missing CDS IDs in first FASTA: AT1G99999" in str(error)
    else:
        raise AssertionError("Expected ValueError for missing CDS")
