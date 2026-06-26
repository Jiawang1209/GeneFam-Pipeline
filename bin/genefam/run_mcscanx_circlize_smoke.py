#!/usr/bin/env python3
"""Run MCScanX-to-circlize visualization smoke."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_circlize_inputs import (
    CHROMOSOME_FIELDNAMES,
    DENSITY_FIELDNAMES,
    DUPLICATE_TRACK_FIELDNAMES,
    LINK_FIELDNAMES,
    SKIPPED_FIELDNAMES,
    build_circlize_inputs,
    read_tsv,
    write_tsv,
)


def _write_smoke_inputs(input_dir: Path) -> tuple[Path, Path]:
    input_dir.mkdir(parents=True, exist_ok=True)
    locations = input_dir / "chromosome_locations.tsv"
    pairs = input_dir / "syntenic_pairs.tsv"
    locations.write_text(
        "\n".join(
            [
                "species_id\tgene_id\tseqid\tstart\tend\tstrand",
                "Arabidopsis_thaliana\tAT1G01010\tChr1\t100\t500\t+",
                "Arabidopsis_thaliana\tAT1G01020\tChr1\t800\t1100\t+",
                "Brassica_rapa\tBraA010001\tA01\t200\t900\t-",
                "Brassica_rapa\tBraA010002\tA01\t1300\t1700\t+",
                "",
            ]
        ),
        encoding="utf-8",
    )
    pairs.write_text(
        "\n".join(
            [
                "block_id\tblock_score\tblock_evalue\tblock_pair_count\tgene_a\tgene_b\tpair_evalue",
                "0\t123.4\t1e-20\t2\tAT1G01010\tBraA010001\t1e-50",
                "0\t123.4\t1e-20\t2\tAT1G01020\tBraA010002\t2e-40",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return locations, pairs


def run_mcscanx_circlize_smoke(
    chromosome_locations: Path | None,
    syntenic_pairs: Path | None,
    r_bin: str,
    outdir: Path,
) -> dict[str, Path]:
    input_dir = outdir / "inputs"
    if chromosome_locations is None or syntenic_pairs is None:
        chromosome_locations, syntenic_pairs = _write_smoke_inputs(input_dir)

    table_dir = outdir / "tables"
    plot_dir = outdir / "plots"
    chromosomes, links, skipped, density, duplicate_tracks = build_circlize_inputs(
        read_tsv(chromosome_locations),
        read_tsv(syntenic_pairs),
        density_window_size=1_000_000,
        include_tracks=True,
    )
    chromosome_tsv = table_dir / "circlize_chromosomes.tsv"
    link_tsv = table_dir / "circlize_links.tsv"
    skipped_tsv = table_dir / "circlize_skipped_links.tsv"
    density_tsv = table_dir / "circlize_link_density.tsv"
    duplicate_tracks_tsv = table_dir / "circlize_duplicate_type_tracks.tsv"
    write_tsv(chromosomes, chromosome_tsv, CHROMOSOME_FIELDNAMES)
    write_tsv(links, link_tsv, LINK_FIELDNAMES)
    write_tsv(skipped, skipped_tsv, SKIPPED_FIELDNAMES)
    write_tsv(density, density_tsv, DENSITY_FIELDNAMES)
    write_tsv(duplicate_tracks, duplicate_tracks_tsv, DUPLICATE_TRACK_FIELDNAMES)

    subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            "scripts/plot_mcscanx_circlize.R",
            "--args",
            str(chromosome_tsv),
            str(link_tsv),
            str(density_tsv),
            str(duplicate_tracks_tsv),
            str(plot_dir),
        ],
        check=True,
    )

    summary_md = outdir / "mcscanx_circlize_smoke.md"
    summary_md.write_text(
        "\n".join(
            [
                "# MCScanX Circlize Smoke",
                "",
                f"Chromosomes: {len(chromosomes)}",
                f"Links: {len(links)}",
                f"Density windows: {len(density)}",
                f"Duplicate-type track rows: {len(duplicate_tracks)}",
                f"Skipped links: {len(skipped)}",
                f"Chromosome table: `{chromosome_tsv}`",
                f"Link table: `{link_tsv}`",
                f"Density table: `{density_tsv}`",
                f"Duplicate-type track table: `{duplicate_tracks_tsv}`",
                f"Skipped table: `{skipped_tsv}`",
                f"PDF plot: `{plot_dir / 'mcscanx_circlize.pdf'}`",
                f"PNG plot: `{plot_dir / 'mcscanx_circlize.png'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "circlize_chromosomes": chromosome_tsv,
        "circlize_links": link_tsv,
        "circlize_link_density": density_tsv,
        "circlize_duplicate_type_tracks": duplicate_tracks_tsv,
        "circlize_skipped_links": skipped_tsv,
        "circlize_pdf": plot_dir / "mcscanx_circlize.pdf",
        "circlize_png": plot_dir / "mcscanx_circlize.png",
        "summary": summary_md,
    }


def _print_outputs(outputs: dict[str, Path]) -> None:
    print("output\tpath")
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromosome-locations", default=None, type=Path)
    parser.add_argument("--syntenic-pairs", default=None, type=Path)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/mcscanx_circlize_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(
        run_mcscanx_circlize_smoke(
            chromosome_locations=args.chromosome_locations,
            syntenic_pairs=args.syntenic_pairs,
            r_bin=args.r_bin,
            outdir=args.outdir,
        )
    )


if __name__ == "__main__":
    main()
