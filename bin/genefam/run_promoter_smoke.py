#!/usr/bin/env python3
"""Run promoter extraction and visualization smoke."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.extract_promoters import extract_promoters, read_tsv, write_fasta, write_tsv
from bin.genefam.summarize_feature_tables import summarize_feature_tables, write_tsv as write_summary_tsv


def _write_inputs(input_dir: Path) -> tuple[Path, Path]:
    input_dir.mkdir(parents=True, exist_ok=True)
    genome = input_dir / "Demo.genome.fa"
    gff3 = input_dir / "Demo.gff3"
    genome.write_text(
        ">Chr1\n" + "AACCGGTTAACCGGTTAACCGGTTAACCGGTTAACCGGTTAACCGGTT\n",
        encoding="utf-8",
    )
    gff3.write_text(
        "\n".join(
            [
                "##gff-version 3",
                "Chr1\tsmoke\tgene\t5\t9\t.\t+\t.\tID=gene_plus",
                "Chr1\tsmoke\tgene\t31\t36\t.\t-\t.\tID=gene_minus",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return genome, gff3


def _write_manifest(manifest_path: Path, genome: Path, gff3: Path) -> Path:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        "\n".join(
            [
                "species_id\tprotein\tgenome\tgff3",
                f"Demo\t\t{genome}\t{gff3}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return manifest_path


def _write_family_candidates(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "species_id\tgene_id",
                "Demo\tgene_plus",
                "Demo\tgene_minus",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def run_promoter_smoke(r_bin: str, outdir: Path) -> dict[str, Path]:
    input_dir = outdir / "inputs"
    table_dir = outdir / "tables"
    sequence_dir = outdir / "sequences"
    plot_dir = outdir / "plots"
    genome, gff3 = _write_inputs(input_dir)
    manifest = _write_manifest(input_dir / "species_manifest.tsv", genome, gff3)
    family_candidates = _write_family_candidates(input_dir / "family_candidates.tsv")

    promoters, promoter_records = extract_promoters(
        read_tsv(family_candidates),
        read_tsv(manifest),
        upstream_bp=12,
        downstream_bp=2,
    )
    promoter_bed = table_dir / "promoters.bed"
    promoter_fasta = sequence_dir / "promoters.fa"
    write_tsv(promoters, promoter_bed)
    write_fasta(promoter_records, promoter_fasta)

    feature_summary = table_dir / "feature_summary.tsv"
    rows = summarize_feature_tables(promoters=promoters)
    write_summary_tsv(rows, feature_summary)
    subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            "scripts/plot_feature_summary.R",
            "--args",
            str(feature_summary),
            str(plot_dir),
        ],
        check=True,
    )

    summary_md = outdir / "promoter_smoke.md"
    summary_md.write_text(
        "\n".join(
            [
                "# Promoter Smoke",
                "",
                f"Promoter BED: `{promoter_bed}`",
                f"Promoter FASTA: `{promoter_fasta}`",
                f"Feature summary: `{feature_summary}`",
                f"PDF plot: `{plot_dir / 'feature_summary.pdf'}`",
                f"PNG plot: `{plot_dir / 'feature_summary.png'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "promoters_bed": promoter_bed,
        "promoters_fasta": promoter_fasta,
        "feature_summary": feature_summary,
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
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/promoter_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(run_promoter_smoke(args.r_bin, args.outdir))


if __name__ == "__main__":
    main()
