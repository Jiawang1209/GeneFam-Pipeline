#!/usr/bin/env python3
"""Summarize family WGD event membership by event and duplicate type."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


FIELDNAMES = [
    "wgd_layer",
    "event_name",
    "duplicate_type",
    "family_gene_count",
    "pair_evidence_count",
    "gene_ids",
]


def summarize_family_event_retention(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str], dict[str, object]] = defaultdict(lambda: {"genes": set(), "pairs": 0})
    for row in rows:
        key = (row["wgd_layer"], row.get("event_name", "unannotated") or "unannotated", row["duplicate_type"])
        grouped[key]["genes"].add(row["gene_id"])  # type: ignore[union-attr]
        grouped[key]["pairs"] = int(grouped[key]["pairs"]) + 1

    summary_rows: list[dict[str, str]] = []
    for wgd_layer, event_name, duplicate_type in sorted(grouped):
        genes = sorted(grouped[(wgd_layer, event_name, duplicate_type)]["genes"])  # type: ignore[arg-type]
        pair_count = grouped[(wgd_layer, event_name, duplicate_type)]["pairs"]
        summary_rows.append(
            {
                "wgd_layer": wgd_layer,
                "event_name": event_name,
                "duplicate_type": duplicate_type,
                "family_gene_count": str(len(genes)),
                "pair_evidence_count": str(pair_count),
                "gene_ids": ",".join(genes),
            }
        )
    return summary_rows


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
    parser.add_argument("--family-wgd-events", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(summarize_family_event_retention(read_tsv(args.family_wgd_events)), args.out)


if __name__ == "__main__":
    main()
