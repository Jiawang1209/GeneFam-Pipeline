#!/usr/bin/env python3
"""Run pangenome-class Ka/Ks table and plot smoke."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_pangenome_kaks import build_pangenome_kaks, read_tsv, write_tsv


def _write_demo_inputs(input_dir: Path) -> tuple[Path, Path]:
    input_dir.mkdir(parents=True, exist_ok=True)
    pangenome_classes = input_dir / "pangenome_classes.tsv"
    kaks_pairs = input_dir / "kaks_pairs.tsv"
    write_tsv(
        [
            {"gene_id": "AT1", "pangenome_class": "core"},
            {"gene_id": "AT2", "pangenome_class": "core"},
            {"gene_id": "AT3", "pangenome_class": "dispensable"},
            {"gene_id": "AT4", "pangenome_class": "dispensable"},
            {"gene_id": "AT5", "pangenome_class": "rare"},
        ],
        pangenome_classes,
        ["gene_id", "pangenome_class"],
    )
    write_tsv(
        [
            {"gene_a": "AT1", "gene_b": "AT2", "ks": "0.10", "ka": "0.01", "ka_ks": "0.10"},
            {"gene_a": "AT3", "gene_b": "AT4", "ks": "0.80", "ka": "0.20", "ka_ks": "0.25"},
            {"gene_a": "AT1", "gene_b": "AT3", "ks": "1.20", "ka": "0.40", "ka_ks": "0.33"},
            {"gene_a": "AT5", "gene_b": "MISSING", "ks": "1.50", "ka": "0.50", "ka_ks": "0.33"},
        ],
        kaks_pairs,
        ["gene_a", "gene_b", "ks", "ka", "ka_ks"],
    )
    return pangenome_classes, kaks_pairs


def run_pangenome_kaks_smoke(*, r_bin: str, outdir: Path) -> dict[str, Path]:
    tables_dir = outdir / "tables"
    plots_dir = outdir / "plots"
    summary = outdir / "pangenome_kaks_smoke.md"
    pangenome_classes, kaks_pairs = _write_demo_inputs(outdir / "inputs")
    outputs = build_pangenome_kaks(pangenome_classes=pangenome_classes, kaks_pairs=kaks_pairs, outdir=tables_dir)
    subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            str(REPO_ROOT / "scripts/plot_pangenome_kaks.R"),
            "--args",
            str(outputs["pair_table"]),
            str(outputs["summary_table"]),
            str(plots_dir),
        ],
        check=True,
    )
    input_pairs = len(read_tsv(kaks_pairs))
    pair_rows = len(read_tsv(outputs["pair_table"]))
    summary.write_text(
        "\n".join(
            [
                "# Pangenome Ka/Ks Smoke",
                "",
                f"Input pairs: {input_pairs}",
                f"Grouped pair rows: {pair_rows}",
                f"Pair table: `{outputs['pair_table']}`",
                f"Summary table: `{outputs['summary_table']}`",
                f"Skipped pairs: `{outputs['skipped_pairs']}`",
                f"PDF plot: `{plots_dir / 'pangenome_kaks.pdf'}`",
                f"PNG plot: `{plots_dir / 'pangenome_kaks.png'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "pangenome_kaks": outputs["pair_table"],
        "pangenome_kaks_summary": outputs["summary_table"],
        "pangenome_kaks_skipped": outputs["skipped_pairs"],
        "pangenome_kaks_pdf": plots_dir / "pangenome_kaks.pdf",
        "pangenome_kaks_png": plots_dir / "pangenome_kaks.png",
        "summary": summary,
    }


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key, path in outputs.items():
        writer.writerow([key, path])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/pangenome_kaks_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(run_pangenome_kaks_smoke(r_bin=args.r_bin, outdir=args.outdir))


if __name__ == "__main__":
    main()
