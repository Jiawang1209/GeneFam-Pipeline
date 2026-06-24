#!/usr/bin/env python3
"""Run a small MEME motif parser smoke check."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.parse_meme_motifs import parse_meme_text, write_tsv


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_motif_smoke(meme_txt: Path, family_name: str, outdir: Path) -> dict[str, Path]:
    outputs = {
        "motif_summary": outdir / "tables/motif_summary.tsv",
        "summary": outdir / "motif_smoke.md",
    }
    rows = parse_meme_text(meme_txt, family_name=family_name)
    write_tsv(rows, outputs["motif_summary"])
    motif_names = ", ".join(row["motif_name"] for row in rows) if rows else "none"
    outputs["summary"].parent.mkdir(parents=True, exist_ok=True)
    outputs["summary"].write_text(
        "\n".join(
            [
                "# Motif Parser Smoke",
                "",
                f"Input: `{meme_txt}`",
                f"Family: `{family_name}`",
                f"Parsed motifs: {len(rows)}",
                f"Motifs: {motif_names}",
                f"Output: `{outputs['motif_summary']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meme-txt", required=True, type=Path)
    parser.add_argument("--family-name", required=True)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(run_motif_smoke(args.meme_txt, args.family_name, args.outdir))


if __name__ == "__main__":
    main()
