import csv
import subprocess
import sys
from pathlib import Path

from bin.genefam.build_duplicate_type_kaks import build_duplicate_type_kaks, read_tsv


def _write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_build_duplicate_type_kaks_joins_pair_metrics_to_duplicate_classes(tmp_path):
    duplicates = tmp_path / "duplicates.tsv"
    kaks_pairs = tmp_path / "kaks_pairs.tsv"
    outdir = tmp_path / "duplicate_type_kaks"

    _write_tsv(
        duplicates,
        [
            {"gene_id": "AT1", "duplicate_type": "WGD/segmental"},
            {"gene_id": "AT2", "duplicate_type": "WGD/segmental"},
            {"gene_id": "AT3", "duplicate_type": "tandem"},
            {"gene_id": "AT4", "duplicate_type": "tandem"},
            {"gene_id": "AT5", "duplicate_type": "proximal"},
        ],
        ["gene_id", "duplicate_type"],
    )
    _write_tsv(
        kaks_pairs,
        [
            {"gene_a": "AT1", "gene_b": "AT2", "ks": "0.12", "ka": "0.02", "ka_ks": "0.17"},
            {"gene_a": "AT3", "gene_b": "AT4", "ks": "0.45", "ka": "0.10", "ka_ks": "0.22"},
            {"gene_a": "AT1", "gene_b": "AT3", "ks": "0.90", "ka": "0.30", "ka_ks": "0.33"},
            {"gene_a": "AT5", "gene_b": "MISSING", "ks": "1.20", "ka": "0.50", "ka_ks": "0.42"},
        ],
        ["gene_a", "gene_b", "ks", "ka", "ka_ks"],
    )

    outputs = build_duplicate_type_kaks(duplicates=duplicates, kaks_pairs=kaks_pairs, outdir=outdir)

    pair_rows = read_tsv(outputs["pair_table"])
    assert pair_rows == [
        {
            "gene_a": "AT1",
            "gene_b": "AT2",
            "duplicate_type_a": "WGD/segmental",
            "duplicate_type_b": "WGD/segmental",
            "pair_duplicate_type": "WGD/segmental",
            "ks": "0.12",
            "ka": "0.02",
            "ka_ks": "0.17",
            "selection_category": "",
        },
        {
            "gene_a": "AT3",
            "gene_b": "AT4",
            "duplicate_type_a": "tandem",
            "duplicate_type_b": "tandem",
            "pair_duplicate_type": "tandem",
            "ks": "0.45",
            "ka": "0.10",
            "ka_ks": "0.22",
            "selection_category": "",
        },
        {
            "gene_a": "AT1",
            "gene_b": "AT3",
            "duplicate_type_a": "WGD/segmental",
            "duplicate_type_b": "tandem",
            "pair_duplicate_type": "mixed",
            "ks": "0.90",
            "ka": "0.30",
            "ka_ks": "0.33",
            "selection_category": "",
        },
    ]

    summary_rows = read_tsv(outputs["summary_table"])
    by_type = {row["pair_duplicate_type"]: row for row in summary_rows}
    assert by_type["WGD/segmental"]["pair_count"] == "1"
    assert by_type["WGD/segmental"]["median_ks"] == "0.12"
    assert by_type["tandem"]["mean_ka_ks"] == "0.22"
    assert by_type["mixed"]["gene_pair_examples"] == "AT1-AT3"

    skipped = read_tsv(outputs["skipped_pairs"])
    assert skipped == [
        {
            "gene_a": "AT5",
            "gene_b": "MISSING",
            "reason": "missing_duplicate_type",
            "missing_genes": "MISSING",
        }
    ]


def test_build_duplicate_type_kaks_cli_writes_tables(tmp_path):
    duplicates = tmp_path / "duplicates.tsv"
    kaks_pairs = tmp_path / "kaks_pairs.tsv"
    outdir = tmp_path / "out"
    _write_tsv(
        duplicates,
        [
            {"gene_id": "g1", "duplicate_type": "WGD/segmental"},
            {"gene_id": "g2", "duplicate_type": "WGD/segmental"},
        ],
        ["gene_id", "duplicate_type"],
    )
    _write_tsv(
        kaks_pairs,
        [{"gene_a": "g1", "gene_b": "g2", "ks": "0.2", "ka_ks": "0.4"}],
        ["gene_a", "gene_b", "ks", "ka_ks"],
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_duplicate_type_kaks.py",
            "--duplicates",
            str(duplicates),
            "--kaks-pairs",
            str(kaks_pairs),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "pair_table" in completed.stdout
    assert (outdir / "duplicate_type_kaks.tsv").exists()
    assert (outdir / "duplicate_type_kaks_summary.tsv").exists()
