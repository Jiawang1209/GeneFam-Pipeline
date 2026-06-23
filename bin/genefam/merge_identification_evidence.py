#!/usr/bin/env python3
"""Merge HMMER and DIAMOND evidence into final candidate rows."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = [
    "species_id",
    "gene_id",
    "evidence_sources",
    "hmmer_evalue",
    "diamond_evalue",
    "best_reference_hit",
]


def _key(row: dict[str, str]) -> tuple[str, str]:
    return row["species_id"], row["gene_id"]


def merge_evidence(
    hmmer_rows: list[dict[str, str]],
    diamond_rows: list[dict[str, str]],
    final_rule: str,
) -> list[dict[str, str]]:
    if final_rule not in {"intersection", "union", "hmmer_only"}:
        raise ValueError("final_rule must be intersection, union, or hmmer_only")

    hmmer_by_key = {_key(row): row for row in hmmer_rows}
    diamond_by_key = {_key(row): row for row in diamond_rows}

    if final_rule == "intersection":
        keys = sorted(set(hmmer_by_key) & set(diamond_by_key))
    elif final_rule == "hmmer_only":
        keys = sorted(hmmer_by_key)
    else:
        keys = sorted(set(hmmer_by_key) | set(diamond_by_key))

    merged: list[dict[str, str]] = []
    for species_id, gene_id in keys:
        hmmer = hmmer_by_key.get((species_id, gene_id))
        diamond = diamond_by_key.get((species_id, gene_id))
        sources = []
        if diamond:
            sources.append("diamond")
        if hmmer:
            sources.append("hmmer")
        merged.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "evidence_sources": ",".join(sources),
                "hmmer_evalue": hmmer.get("evalue", "") if hmmer else "",
                "diamond_evalue": diamond.get("evalue", "") if diamond else "",
                "best_reference_hit": diamond.get("reference_hit", "") if diamond else "",
            }
        )
    return merged


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path or str(path) == "-":
        return []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hmmer", required=True, type=Path)
    parser.add_argument("--diamond", required=False, type=Path)
    parser.add_argument("--final-rule", required=True, choices=["intersection", "union", "hmmer_only"])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(merge_evidence(read_tsv(args.hmmer), read_tsv(args.diamond), args.final_rule), args.out)


if __name__ == "__main__":
    main()
