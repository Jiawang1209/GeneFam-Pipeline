import pytest

from bin.genefam.extract_sequences import extract_fasta_records


def test_extract_fasta_records_returns_requested_ids(tmp_path):
    fasta = tmp_path / "input.fa"
    fasta.write_text(">gene1 extra\nMAAA\n>gene2\nMCCC\n", encoding="utf-8")

    records = extract_fasta_records(fasta, {"gene2"})

    assert records == [("gene2", "MCCC")]


def test_extract_fasta_records_fails_for_missing_ids(tmp_path):
    fasta = tmp_path / "input.fa"
    fasta.write_text(">gene1\nMAAA\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing sequence IDs: gene2"):
        extract_fasta_records(fasta, {"gene2"})
