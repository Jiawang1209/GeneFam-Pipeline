#!/usr/bin/env python3
"""Parse MCScanX .collinearity output into syntenic gene pairs."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FIELDNAMES = [
    "block_id",
    "block_score",
    "block_evalue",
    "block_pair_count",
    "gene_a",
    "gene_b",
    "pair_evalue",
]
HEADER_RE = re.compile(
    r"## Alignment (?P<block_id>\S+): score=(?P<score>\S+) e_value=(?P<evalue>\S+) N=(?P<pair_count>\S+)"
)
PAIR_RE = re.compile(r"\s*\S+-\s*\S+:\s+(?P<gene_a>\S+)\s+(?P<gene_b>\S+)\s+(?P<pair_evalue>\S+)")


def parse_collinearity(path: Path) -> list[dict[str, str]]:
    current_block: dict[str, str] | None = None
    rows: list[dict[str, str]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            header = HEADER_RE.search(line)
            if header:
                current_block = {
                    "block_id": header.group("block_id"),
                    "block_score": header.group("score"),
                    "block_evalue": header.group("evalue"),
                    "block_pair_count": header.group("pair_count"),
                }
                continue
            pair = PAIR_RE.match(line)
            if pair and current_block:
                rows.append(
                    {
                        **current_block,
                        "gene_a": pair.group("gene_a"),
                        "gene_b": pair.group("gene_b"),
                        "pair_evalue": pair.group("pair_evalue"),
                    }
                )
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collinearity", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(parse_collinearity(args.collinearity), args.out)


if __name__ == "__main__":
    main()
