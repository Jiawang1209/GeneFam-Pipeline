#!/usr/bin/env python3
"""Run a small normalized HMMER domain-filter smoke check."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.filter_hmmer_domains import filter_domains, read_tsv, write_tsv


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_domain_filter_smoke(
    input_path: Path,
    outdir: Path,
    max_evalue: float,
    min_bitscore: float,
    min_domain_coverage: float,
) -> dict[str, Path]:
    outputs = {
        "filtered_domains": outdir / "tables/filtered_domains.tsv",
        "summary": outdir / "domain_filter_smoke.md",
    }
    rows = read_tsv(input_path)
    filtered = filter_domains(
        rows,
        max_evalue=max_evalue,
        min_bitscore=min_bitscore,
        min_domain_coverage=min_domain_coverage,
    )
    write_tsv(filtered, outputs["filtered_domains"])
    outputs["summary"].parent.mkdir(parents=True, exist_ok=True)
    outputs["summary"].write_text(
        "\n".join(
            [
                "# Domain Filter Smoke",
                "",
                f"Input: `{input_path}`",
                f"Input domains: {len(rows)}",
                f"Filtered domains: {len(filtered)}",
                f"Thresholds: max_evalue={max_evalue}, min_bitscore={min_bitscore}, min_domain_coverage={min_domain_coverage}",
                f"Output: `{outputs['filtered_domains']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--max-evalue", required=True, type=float)
    parser.add_argument("--min-bitscore", required=True, type=float)
    parser.add_argument("--min-domain-coverage", required=True, type=float)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(
        run_domain_filter_smoke(
            input_path=args.input,
            outdir=args.outdir,
            max_evalue=args.max_evalue,
            min_bitscore=args.min_bitscore,
            min_domain_coverage=args.min_domain_coverage,
        )
    )


if __name__ == "__main__":
    main()
