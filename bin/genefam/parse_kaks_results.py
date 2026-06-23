#!/usr/bin/env python3
"""Parse KaKs_Calculator-style output into normalized pair rows."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["gene_a", "gene_b", "ka", "ks", "ka_ks", "p_value", "selection_category"]


def _selection_category(ka_ks: str) -> str:
    ratio = float(ka_ks)
    if ratio < 1:
        return "purifying"
    if ratio > 1:
        return "positive"
    return "neutral"


def _split_pair(sequence: str) -> tuple[str, str]:
    for separator in ("|", ",", "\t", "-"):
        if separator in sequence:
            left, right = sequence.split(separator, 1)
            return left, right
    raise ValueError(f"Could not split Ka/Ks sequence pair: {sequence}")


def parse_kaks_table(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            gene_a, gene_b = _split_pair(row["Sequence"])
            ka_ks = row.get("Ka/Ks") or row.get("Ka_Ks") or row.get("ka_ks") or ""
            if not ka_ks:
                raise ValueError("Ka/Ks column is required")
            rows.append(
                {
                    "gene_a": gene_a,
                    "gene_b": gene_b,
                    "ka": row.get("Ka", row.get("ka", "")),
                    "ks": row.get("Ks", row.get("ks", "")),
                    "ka_ks": ka_ks,
                    "p_value": row.get("P-Value(Fisher)", row.get("p_value", "")),
                    "selection_category": _selection_category(ka_ks),
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
    parser.add_argument("--kaks", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(parse_kaks_table(args.kaks), args.out)


if __name__ == "__main__":
    main()
