#!/usr/bin/env python3
"""Run a duplicate-type Ka/Ks table and plot smoke."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_duplicate_type_kaks import build_duplicate_type_kaks, read_tsv


def run_duplicate_type_kaks_smoke(*, duplicates: Path, kaks_pairs: Path, r_bin: str, outdir: Path) -> dict[str, Path]:
    tables_dir = outdir / "tables"
    plots_dir = outdir / "plots"
    summary = outdir / "duplicate_type_kaks_smoke.md"
    outputs = build_duplicate_type_kaks(duplicates=duplicates, kaks_pairs=kaks_pairs, outdir=tables_dir)
    completed = subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            str(REPO_ROOT / "scripts/plot_duplicate_type_kaks.R"),
            "--args",
            str(outputs["pair_table"]),
            str(outputs["summary_table"]),
            str(plots_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
        raise RuntimeError(f"duplicate-type Ka/Ks plotting failed with {r_bin}: {output}")
    pair_count = len(read_tsv(kaks_pairs))
    grouped_count = len(read_tsv(outputs["pair_table"]))
    summary.write_text(
        "\n".join(
            [
                "# Duplicate-Type Ka/Ks Smoke",
                "",
                f"Duplicate types: `{duplicates}`",
                f"Ka/Ks pairs: `{kaks_pairs}`",
                f"Input pairs: {pair_count}",
                f"Grouped pair rows: {grouped_count}",
                f"Pair table: `{outputs['pair_table']}`",
                f"Summary table: `{outputs['summary_table']}`",
                f"Skipped pairs: `{outputs['skipped_pairs']}`",
                f"PDF plot: `{plots_dir / 'duplicate_type_kaks.pdf'}`",
                f"PNG plot: `{plots_dir / 'duplicate_type_kaks.png'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "duplicate_type_kaks": outputs["pair_table"],
        "duplicate_type_kaks_summary": outputs["summary_table"],
        "duplicate_type_kaks_skipped": outputs["skipped_pairs"],
        "duplicate_type_kaks_pdf": plots_dir / "duplicate_type_kaks.pdf",
        "duplicate_type_kaks_png": plots_dir / "duplicate_type_kaks.png",
        "summary": summary,
    }


def _print_outputs(outputs: dict[str, Path]) -> None:
    print("output\tpath")
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duplicates", required=True, type=Path)
    parser.add_argument("--kaks-pairs", required=True, type=Path)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/duplicate_type_kaks_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(
        run_duplicate_type_kaks_smoke(
            duplicates=args.duplicates,
            kaks_pairs=args.kaks_pairs,
            r_bin=args.r_bin,
            outdir=args.outdir,
        )
    )


if __name__ == "__main__":
    main()
