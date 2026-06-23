from bin.genefam.parse_kaks_results import parse_kaks_table


def test_parse_kaks_table_normalizes_sequence_pair_and_selection_category(tmp_path):
    kaks = tmp_path / "kaks.tsv"
    kaks.write_text(
        "Sequence\tKa\tKs\tKa/Ks\tP-Value(Fisher)\n"
        "AT1G01010-BraA010001\t0.02\t0.10\t0.2\t0.01\n"
        "AT1G01020-BraA010002\t0.30\t0.20\t1.5\t0.02\n",
        encoding="utf-8",
    )

    rows = parse_kaks_table(kaks)

    assert rows == [
        {
            "gene_a": "AT1G01010",
            "gene_b": "BraA010001",
            "ka": "0.02",
            "ks": "0.10",
            "ka_ks": "0.2",
            "p_value": "0.01",
            "selection_category": "purifying",
        },
        {
            "gene_a": "AT1G01020",
            "gene_b": "BraA010002",
            "ka": "0.30",
            "ks": "0.20",
            "ka_ks": "1.5",
            "p_value": "0.02",
            "selection_category": "positive",
        },
    ]


def test_parse_kaks_table_marks_neutral_selection(tmp_path):
    kaks = tmp_path / "kaks.tsv"
    kaks.write_text("Sequence\tKa\tKs\tKa/Ks\nA-B\t0.10\t0.10\t1.0\n", encoding="utf-8")

    rows = parse_kaks_table(kaks)

    assert rows[0]["selection_category"] == "neutral"
    assert rows[0]["p_value"] == ""
