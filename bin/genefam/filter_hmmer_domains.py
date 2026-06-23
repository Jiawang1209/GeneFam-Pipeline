#!/usr/bin/env python3
"""Filter normalized HMMER domain evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.parse_hmmer_domtbl import FIELDNAMES


def filter_domains(
    rows: list[dict[str, str]],
    max_evalue: float,
    min_bitscore: float,
    min_domain_coverage: float,
) -> list[dict[str, str]]:
    filtered: list[dict[str, str]] = []
    for row in rows:
        if float(row["evalue"]) > max_evalue:
            continue
        if float(row["bitscore"]) < min_bitscore:
            continue
        if float(row.get("domain_coverage", "0")) < min_domain_coverage:
            continue
        filtered.append(row)
    return filtered


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--max-evalue", required=True, type=float)
    parser.add_argument("--min-bitscore", required=True, type=float)
    parser.add_argument("--min-domain-coverage", required=True, type=float)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(
        filter_domains(
            read_tsv(args.input),
            max_evalue=args.max_evalue,
            min_bitscore=args.min_bitscore,
            min_domain_coverage=args.min_domain_coverage,
        ),
        args.out,
    )


if __name__ == "__main__":
    main()
