#!/usr/bin/env python3
"""Run gene family information and copy-number visualization smoke."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_gene_family_info import build_gene_family_info_tables, read_fasta, read_tsv, write_tables


def _write_demo_inputs(input_dir: Path) -> tuple[Path, Path, Path]:
    input_dir.mkdir(parents=True, exist_ok=True)
    family_counts = input_dir / "family_counts.tsv"
    family_members = input_dir / "family_members.faa"
    species_order = input_dir / "species_tree_order.tsv"
    family_counts.write_text(
        "\n".join(
            [
                "species_id\tmember_count\thmmer_count\tdiamond_count\tintersection_count",
                "Ath\t1\t1\t1\t1",
                "Bra\t4\t4\t3\t3",
                "Bna\t9\t9\t8\t8",
                "Osa\t0\t0\t0\t0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    family_members.write_text(
        "\n".join(
            [
                ">Ath|AT1G01010",
                "MAAAAA",
                ">Bra|BnaA01G0001",
                "MKWVTFISLL",
                ">Bna|BnaA02G0002",
                "MDEKRR",
                ">Bna|BnaA02G0003",
                "MFGVVVV",
                "",
            ]
        ),
        encoding="utf-8",
    )
    species_order.write_text(
        "\n".join(
            [
                "species_id\tplot_order\tclade",
                "Osa\t1\tmonocot",
                "Ath\t2\tbrassicaceae",
                "Bra\t3\tbrassicaceae",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return family_counts, family_members, species_order


def run_gene_family_info_smoke(r_bin: str, outdir: Path) -> dict[str, Path]:
    table_dir = outdir / "tables"
    plot_dir = outdir / "plots"
    family_counts, family_members, species_order = _write_demo_inputs(outdir / "inputs")
    tables = build_gene_family_info_tables(read_tsv(family_counts), read_fasta(family_members), read_tsv(species_order))
    outputs = write_tables(tables, table_dir)
    subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            "scripts/plot_gene_family_info.R",
            "--args",
            str(outputs["gene_family_copy_number"]),
            str(outputs["gene_family_copy_number_summary"]),
            str(outputs["gene_family_protein_properties"]),
            str(outputs["gene_family_species_order"]),
            str(outputs["gene_family_copy_number_expansion"]),
            str(outputs["gene_family_pangenome_summary"]),
            str(plot_dir),
        ],
        check=True,
    )
    outputs = dict(outputs)
    outputs["gene_family_info_pdf"] = plot_dir / "gene_family_info_summary.pdf"
    outputs["gene_family_info_png"] = plot_dir / "gene_family_info_summary.png"
    outputs["protein_properties_by_species_pdf"] = plot_dir / "protein_properties_by_species.pdf"
    outputs["protein_properties_by_species_png"] = plot_dir / "protein_properties_by_species.png"
    summary = outdir / "gene_family_info_smoke.md"
    summary.write_text(
        "\n".join(
            [
                "# Gene Family Information Smoke",
                "",
                f"Copy number table: `{outputs['gene_family_copy_number']}`",
                f"Copy number summary: `{outputs['gene_family_copy_number_summary']}`",
                f"Species plot order: `{outputs['gene_family_species_order']}`",
                f"External species order: `{species_order}`",
                f"Copy-number expansion: `{outputs['gene_family_copy_number_expansion']}`",
                f"Pangenome summary: `{outputs['gene_family_pangenome_summary']}`",
                f"Protein properties: `{outputs['gene_family_protein_properties']}`",
                f"PDF plot: `{outputs['gene_family_info_pdf']}`",
                f"PNG plot: `{outputs['gene_family_info_png']}`",
                f"Protein properties by species PDF: `{outputs['protein_properties_by_species_pdf']}`",
                f"Protein properties by species PNG: `{outputs['protein_properties_by_species_png']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    outputs["summary"] = summary
    return outputs


def _print_outputs(outputs: dict[str, Path]) -> None:
    print("output\tpath")
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/gene_family_info_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(run_gene_family_info_smoke(args.r_bin, args.outdir))


if __name__ == "__main__":
    main()
