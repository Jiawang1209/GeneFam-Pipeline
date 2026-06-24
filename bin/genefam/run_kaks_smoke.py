#!/usr/bin/env python3
"""Run a small Ka/Ks parser smoke check."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.parse_kaks_results import parse_kaks_table, write_tsv


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_kaks_smoke(kaks: Path, outdir: Path) -> dict[str, Path]:
    outputs = {
        "normalized_kaks": outdir / "tables/normalized_kaks.tsv",
        "summary": outdir / "kaks_smoke.md",
    }
    rows = parse_kaks_table(kaks)
    write_tsv(rows, outputs["normalized_kaks"])
    counts = Counter(row["selection_category"] for row in rows)
    outputs["summary"].parent.mkdir(parents=True, exist_ok=True)
    outputs["summary"].write_text(
        "\n".join(
            [
                "# Ka/Ks Parser Smoke",
                "",
                f"Input: `{kaks}`",
                f"Input pairs: {len(rows)}",
                f"purifying: {counts.get('purifying', 0)}",
                f"neutral: {counts.get('neutral', 0)}",
                f"positive: {counts.get('positive', 0)}",
                f"Output: `{outputs['normalized_kaks']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kaks", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(run_kaks_smoke(args.kaks, args.outdir))


if __name__ == "__main__":
    main()
