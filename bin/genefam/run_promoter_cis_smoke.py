#!/usr/bin/env python3
"""Run promoter cis-element normalization and visualization smoke."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_promoter_cis_elements import build_promoter_cis_tables, read_tsv, write_tables


def _write_demo_plantcare(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "Species\tGene ID\tCAREs\tFunction\tSite",
                "Ath\tAT1G01010\tABRE\tabscisic acid responsiveness\t-210",
                "Ath\tAT1G01010\tLTR\tlow-temperature responsiveness\t-450",
                "Ath\tAT1G01020\tG-box\tlight responsiveness\t-95",
                "Bra\tBnaA01G0001\tMYB\tdrought inducibility\t-360",
                "Bra\tBnaA01G0001\tTATA-box\tcore promoter element\t-31",
                "Bra\tBnaA02G0042\tBox 4\tlight responsiveness\t-155",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def run_promoter_cis_smoke(r_bin: str, outdir: Path) -> dict[str, Path]:
    input_path = _write_demo_plantcare(outdir / "inputs/plantcare_cis_elements.tsv")
    table_dir = outdir / "tables"
    plot_dir = outdir / "plots"
    tables = build_promoter_cis_tables(read_tsv(input_path))
    outputs = write_tables(tables, table_dir)
    subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            "scripts/plot_promoter_cis_elements.R",
            "--args",
            str(outputs["promoter_cis_gene_matrix"]),
            str(outputs["promoter_cis_category_summary"]),
            str(plot_dir),
        ],
        check=True,
    )

    summary_md = outdir / "promoter_cis_smoke.md"
    summary_md.write_text(
        "\n".join(
            [
                "# Promoter Cis-Element Smoke",
                "",
                f"Input PlantCARE-style table: `{input_path}`",
                f"Normalized cis-elements: `{outputs['promoter_cis_elements']}`",
                f"Gene-category matrix: `{outputs['promoter_cis_gene_matrix']}`",
                f"Category summary: `{outputs['promoter_cis_category_summary']}`",
                f"PDF plot: `{plot_dir / 'promoter_cis_elements.pdf'}`",
                f"PNG plot: `{plot_dir / 'promoter_cis_elements.png'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    outputs = dict(outputs)
    outputs["promoter_cis_pdf"] = plot_dir / "promoter_cis_elements.pdf"
    outputs["promoter_cis_png"] = plot_dir / "promoter_cis_elements.png"
    outputs["summary"] = summary_md
    return outputs


def _print_outputs(outputs: dict[str, Path]) -> None:
    print("output\tpath")
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/promoter_cis_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(run_promoter_cis_smoke(args.r_bin, args.outdir))


if __name__ == "__main__":
    main()
