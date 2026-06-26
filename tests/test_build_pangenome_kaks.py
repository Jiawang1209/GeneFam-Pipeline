import csv
import subprocess
import sys
from pathlib import Path

from bin.genefam.build_pangenome_kaks import build_pangenome_kaks, read_tsv


def _write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_build_pangenome_kaks_groups_pair_metrics_by_presence_class(tmp_path):
    pangenome_classes = tmp_path / "pangenome_classes.tsv"
    kaks_pairs = tmp_path / "kaks_pairs.tsv"
    outdir = tmp_path / "pangenome_kaks"
    _write_tsv(
        pangenome_classes,
        [
            {"gene_id": "AT1", "pangenome_class": "core"},
            {"gene_id": "AT2", "pangenome_class": "core"},
            {"gene_id": "AT3", "pangenome_class": "dispensable"},
            {"gene_id": "AT4", "pangenome_class": "dispensable"},
            {"gene_id": "AT5", "pangenome_class": "rare"},
        ],
        ["gene_id", "pangenome_class"],
    )
    _write_tsv(
        kaks_pairs,
        [
            {"gene_a": "AT1", "gene_b": "AT2", "ks": "0.10", "ka": "0.01", "ka_ks": "0.10"},
            {"gene_a": "AT3", "gene_b": "AT4", "ks": "0.80", "ka": "0.20", "ka_ks": "0.25"},
            {"gene_a": "AT1", "gene_b": "AT3", "ks": "1.20", "ka": "0.40", "ka_ks": "0.33"},
            {"gene_a": "AT5", "gene_b": "MISSING", "ks": "1.50", "ka": "0.50", "ka_ks": "0.33"},
        ],
        ["gene_a", "gene_b", "ks", "ka", "ka_ks"],
    )

    outputs = build_pangenome_kaks(pangenome_classes=pangenome_classes, kaks_pairs=kaks_pairs, outdir=outdir)

    pair_rows = read_tsv(outputs["pair_table"])
    assert pair_rows == [
        {
            "gene_a": "AT1",
            "gene_b": "AT2",
            "pangenome_class_a": "core",
            "pangenome_class_b": "core",
            "pair_pangenome_class": "core",
            "ks": "0.10",
            "ka": "0.01",
            "ka_ks": "0.10",
            "selection_category": "",
        },
        {
            "gene_a": "AT3",
            "gene_b": "AT4",
            "pangenome_class_a": "dispensable",
            "pangenome_class_b": "dispensable",
            "pair_pangenome_class": "dispensable",
            "ks": "0.80",
            "ka": "0.20",
            "ka_ks": "0.25",
            "selection_category": "",
        },
        {
            "gene_a": "AT1",
            "gene_b": "AT3",
            "pangenome_class_a": "core",
            "pangenome_class_b": "dispensable",
            "pair_pangenome_class": "mixed",
            "ks": "1.20",
            "ka": "0.40",
            "ka_ks": "0.33",
            "selection_category": "",
        },
    ]

    by_class = {row["pair_pangenome_class"]: row for row in read_tsv(outputs["summary_table"])}
    assert by_class["core"]["pair_count"] == "1"
    assert by_class["dispensable"]["median_ks"] == "0.8"
    assert by_class["mixed"]["mean_ka_ks"] == "0.33"
    assert read_tsv(outputs["skipped_pairs"]) == [
        {
            "gene_a": "AT5",
            "gene_b": "MISSING",
            "reason": "missing_pangenome_class",
            "missing_genes": "MISSING",
        }
    ]


def test_build_pangenome_kaks_cli_writes_tables(tmp_path):
    pangenome_classes = tmp_path / "pangenome_classes.tsv"
    kaks_pairs = tmp_path / "kaks_pairs.tsv"
    outdir = tmp_path / "out"
    _write_tsv(
        pangenome_classes,
        [{"gene_id": "g1", "pangenome_class": "core"}, {"gene_id": "g2", "pangenome_class": "core"}],
        ["gene_id", "pangenome_class"],
    )
    _write_tsv(kaks_pairs, [{"gene_a": "g1", "gene_b": "g2", "ks": "0.2", "ka_ks": "0.4"}], ["gene_a", "gene_b", "ks", "ka_ks"])

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_pangenome_kaks.py",
            "--pangenome-classes",
            str(pangenome_classes),
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
    assert (outdir / "pangenome_kaks.tsv").exists()
    assert (outdir / "pangenome_kaks_summary.tsv").exists()
