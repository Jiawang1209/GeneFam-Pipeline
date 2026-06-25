#!/usr/bin/env python3
"""Run feature statistics and visualization smoke for report-scale outputs."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.summarize_feature_tables import read_tsv, summarize_feature_tables, write_tsv


def run_feature_summary_smoke(
    domains: Path | None,
    motifs: Path | None,
    gene_structures: Path | None,
    synteny: Path | None,
    promoters: Path | None,
    r_bin: str,
    outdir: Path,
) -> dict[str, Path]:
    table_dir = outdir / "tables"
    plot_dir = outdir / "plots"
    summary_tsv = table_dir / "feature_summary.tsv"
    summary_md = outdir / "feature_summary_smoke.md"
    rows = summarize_feature_tables(
        domains=read_tsv(domains),
        motifs=read_tsv(motifs),
        gene_structures=read_tsv(gene_structures),
        synteny=read_tsv(synteny),
        promoters=read_tsv(promoters),
    )
    write_tsv(rows, summary_tsv)
    subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            "scripts/plot_feature_summary.R",
            "--args",
            str(summary_tsv),
            str(plot_dir),
        ],
        check=True,
    )
    summary_md.parent.mkdir(parents=True, exist_ok=True)
    summary_md.write_text(
        "\n".join(
            [
                "# Feature Summary Smoke",
                "",
                f"Summary rows: {len(rows)}",
                f"Summary table: `{summary_tsv}`",
                f"PDF plot: `{plot_dir / 'feature_summary.pdf'}`",
                f"PNG plot: `{plot_dir / 'feature_summary.png'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "feature_summary": summary_tsv,
        "feature_summary_pdf": plot_dir / "feature_summary.pdf",
        "feature_summary_png": plot_dir / "feature_summary.png",
        "summary": summary_md,
    }


def _print_outputs(outputs: dict[str, Path]) -> None:
    print("output\tpath")
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domains", default=None, type=Path)
    parser.add_argument("--motifs", default=None, type=Path)
    parser.add_argument("--gene-structures", default=None, type=Path)
    parser.add_argument("--synteny", default=None, type=Path)
    parser.add_argument("--promoters", default=None, type=Path)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/feature_summary_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(
        run_feature_summary_smoke(
            domains=args.domains,
            motifs=args.motifs,
            gene_structures=args.gene_structures,
            synteny=args.synteny,
            promoters=args.promoters,
            r_bin=args.r_bin,
            outdir=args.outdir,
        )
    )


if __name__ == "__main__":
    main()
