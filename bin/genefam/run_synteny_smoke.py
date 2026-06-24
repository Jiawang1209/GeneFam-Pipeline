#!/usr/bin/env python3
"""Run a small MCScanX collinearity parser smoke check."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.parse_mcscanx_collinearity import parse_collinearity, write_tsv


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_synteny_smoke(collinearity: Path, outdir: Path) -> dict[str, Path]:
    outputs = {
        "syntenic_pairs": outdir / "tables/syntenic_pairs.tsv",
        "summary": outdir / "synteny_smoke.md",
    }
    rows = parse_collinearity(collinearity)
    write_tsv(rows, outputs["syntenic_pairs"])
    outputs["summary"].parent.mkdir(parents=True, exist_ok=True)
    outputs["summary"].write_text(
        "\n".join(
            [
                "# Synteny Parser Smoke",
                "",
                f"Input: `{collinearity}`",
                f"Parsed syntenic pairs: {len(rows)}",
                f"Output: `{outputs['syntenic_pairs']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collinearity", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(run_synteny_smoke(args.collinearity, args.outdir))


if __name__ == "__main__":
    main()
