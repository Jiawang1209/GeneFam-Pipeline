import subprocess
import sys

from bin.genefam.concat_tsv import concat_tsv, read_tsv


def test_concat_tsv_keeps_one_header_and_preserves_rows(tmp_path):
    first = tmp_path / "ath.tsv"
    second = tmp_path / "bra.tsv"
    first.write_text("species_id\tgene_id\nArabidopsis_thaliana\tAT1G01010\n", encoding="utf-8")
    second.write_text("species_id\tgene_id\nBrassica_rapa\tBraA010001\n", encoding="utf-8")

    rows, fieldnames = concat_tsv([first, second])

    assert fieldnames == ["species_id", "gene_id"]
    assert rows == [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA010001"},
    ]


def test_concat_tsv_cli_writes_combined_table(tmp_path):
    first = tmp_path / "ath.tsv"
    second = tmp_path / "bra.tsv"
    out = tmp_path / "family_candidates.tsv"
    first.write_text("species_id\tgene_id\nArabidopsis_thaliana\tAT1G01010\n", encoding="utf-8")
    second.write_text("species_id\tgene_id\nBrassica_rapa\tBraA010001\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/concat_tsv.py",
            "--inputs",
            str(first),
            str(second),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert read_tsv(out) == [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA010001"},
    ]
