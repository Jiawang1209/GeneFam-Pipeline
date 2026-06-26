import csv
import subprocess
import sys
from pathlib import Path

from bin.genefam.build_expression_summary import build_expression_summary, read_tsv


def _write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def test_build_expression_summary_normalizes_metadata_and_averages_replicates(tmp_path):
    expression = tmp_path / "family_expression.tsv"
    metadata = tmp_path / "sample_metadata.tsv"
    outdir = tmp_path / "tables"
    _write_tsv(
        expression,
        [
            {"gene_id": "AT1", "cold_0h_rep1": "1.0", "cold_0h_rep2": "3.0", "cold_6h_rep1": "7.0"},
            {"gene_id": "AT2", "cold_0h_rep1": "2.0", "cold_0h_rep2": "4.0", "cold_6h_rep1": "8.0"},
        ],
        ["gene_id", "cold_0h_rep1", "cold_0h_rep2", "cold_6h_rep1"],
    )
    _write_tsv(
        metadata,
        [
            {"sample_id": "cold_6h_rep1", "condition": "cold", "timepoint": "6h", "replicate": "1", "group": "cold_6h"},
            {"sample_id": "cold_0h_rep2", "condition": "cold", "timepoint": "0h", "replicate": "2", "group": "cold_0h"},
            {"sample_id": "cold_0h_rep1", "condition": "cold", "timepoint": "0h", "replicate": "1", "group": "cold_0h"},
        ],
        ["sample_id", "condition", "timepoint", "replicate", "group"],
    )

    outputs = build_expression_summary(expression=expression, metadata=metadata, outdir=outdir)

    normalized = read_tsv(outputs["sample_metadata"])
    assert [row["sample_id"] for row in normalized] == ["cold_0h_rep1", "cold_0h_rep2", "cold_6h_rep1"]
    assert normalized[0]["plot_label"] == "cold|0h|r1"

    group_matrix = read_tsv(outputs["group_matrix"])
    assert group_matrix == [
        {"gene_id": "AT1", "cold_0h": "2", "cold_6h": "7"},
        {"gene_id": "AT2", "cold_0h": "3", "cold_6h": "8"},
    ]

    gene_summary = read_tsv(outputs["gene_summary"])
    by_gene = {row["gene_id"]: row for row in gene_summary}
    assert by_gene["AT1"]["max_group"] == "cold_6h"
    assert by_gene["AT1"]["fold_change_max_min"] == "3.5"
    assert by_gene["AT2"]["detected_sample_count"] == "3"


def test_build_expression_summary_cli_writes_expected_tables(tmp_path):
    expression = tmp_path / "family_expression.tsv"
    _write_tsv(
        expression,
        [{"gene_id": "g1", "s1": "1.0", "s2": "2.0"}],
        ["gene_id", "s1", "s2"],
    )
    outdir = tmp_path / "out"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_expression_summary.py",
            "--expression",
            str(expression),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "expression_group_matrix" in completed.stdout
    assert (outdir / "expression_sample_metadata.tsv").exists()
    assert (outdir / "expression_group_matrix.tsv").exists()
    assert (outdir / "expression_gene_summary.tsv").exists()
