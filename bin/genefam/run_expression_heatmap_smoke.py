#!/usr/bin/env python3
"""Run an expression heatmap smoke with optional sample metadata."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_expression_summary import build_expression_summary, read_tsv


def run_expression_heatmap_smoke(*, expression: Path, metadata: Path | None, r_bin: str, outdir: Path) -> dict[str, Path]:
    tables_dir = outdir / "tables"
    plots_dir = outdir / "plots"
    summary = outdir / "expression_heatmap_smoke.md"
    outputs = build_expression_summary(expression=expression, metadata=metadata, outdir=tables_dir)
    completed = subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            str(REPO_ROOT / "scripts/plot_expression_heatmap.R"),
            "--args",
            str(outputs["group_matrix"]),
            str(outputs["sample_metadata"]),
            str(outputs["gene_summary"]),
            str(plots_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
        raise RuntimeError(f"Expression heatmap plotting failed with {r_bin}: {output}")
    summary.write_text(
        "\n".join(
            [
                "# Expression Heatmap Smoke",
                "",
                f"Expression matrix: `{expression}`",
                f"Sample metadata: `{metadata}`" if metadata else "Sample metadata: generated from expression columns",
                f"Genes: {len(read_tsv(outputs['group_matrix']))}",
                f"Sample annotations: `{outputs['sample_metadata']}`",
                f"Group matrix: `{outputs['group_matrix']}`",
                f"Gene summary: `{outputs['gene_summary']}`",
                f"PDF plot: `{plots_dir / 'expression_heatmap.pdf'}`",
                f"PNG plot: `{plots_dir / 'expression_heatmap.png'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "expression_sample_metadata": outputs["sample_metadata"],
        "expression_group_matrix": outputs["group_matrix"],
        "expression_gene_summary": outputs["gene_summary"],
        "expression_heatmap_pdf": plots_dir / "expression_heatmap.pdf",
        "expression_heatmap_png": plots_dir / "expression_heatmap.png",
        "summary": summary,
    }


def _print_outputs(outputs: dict[str, Path]) -> None:
    print("output\tpath")
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expression", required=True, type=Path)
    parser.add_argument("--metadata", default=None, type=Path)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/expression_heatmap_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(run_expression_heatmap_smoke(expression=args.expression, metadata=args.metadata, r_bin=args.r_bin, outdir=args.outdir))


if __name__ == "__main__":
    main()
