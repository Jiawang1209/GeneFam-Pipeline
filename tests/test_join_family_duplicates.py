import subprocess
import sys
from pathlib import Path

import pytest

from bin.genefam.join_family_duplicates import join_family_duplicates


def test_join_family_duplicates_keeps_family_members_with_duplicate_types():
    family_rows = [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA010001"},
    ]
    duplicate_rows = [
        {"gene_id": "AT1G01010", "duplicate_type": "WGD/segmental", "raw_duplicate_type": "WGD"},
        {"gene_id": "BraA010001", "duplicate_type": "tandem", "raw_duplicate_type": "Tandem"},
        {"gene_id": "OTHER", "duplicate_type": "singleton", "raw_duplicate_type": "singleton"},
    ]

    assert join_family_duplicates(family_rows, duplicate_rows) == [
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01010",
            "duplicate_type": "WGD/segmental",
            "raw_duplicate_type": "WGD",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA010001",
            "duplicate_type": "tandem",
            "raw_duplicate_type": "Tandem",
        },
    ]


def test_join_family_duplicates_fails_for_missing_classification():
    family_rows = [{"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010"}]
    duplicate_rows = [{"gene_id": "OTHER", "duplicate_type": "singleton", "raw_duplicate_type": "singleton"}]

    with pytest.raises(ValueError, match="Missing duplicate classification for family genes: AT1G01010"):
        join_family_duplicates(family_rows, duplicate_rows)


def test_join_family_duplicates_cli_writes_joined_table(tmp_path):
    family_path = tmp_path / "family.tsv"
    duplicates_path = tmp_path / "duplicates.tsv"
    out_path = tmp_path / "family_duplicates.tsv"
    family_path.write_text(
        "species_id\tgene_id\nArabidopsis_thaliana\tAT1G01010\n",
        encoding="utf-8",
    )
    duplicates_path.write_text(
        "gene_id\tduplicate_type\traw_duplicate_type\nAT1G01010\tWGD/segmental\tWGD\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/join_family_duplicates.py",
            "--family-members",
            str(family_path),
            "--duplicates",
            str(duplicates_path),
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert out_path.read_text(encoding="utf-8") == (
        "species_id\tgene_id\tduplicate_type\traw_duplicate_type\n"
        "Arabidopsis_thaliana\tAT1G01010\tWGD/segmental\tWGD\n"
    )
