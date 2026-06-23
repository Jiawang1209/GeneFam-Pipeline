#!/usr/bin/env python3
"""Extract chromosome coordinates for selected genes from GFF3."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["species_id", "gene_id", "seqid", "start", "end", "strand"]


def _parse_attributes(value: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for part in value.split(";"):
        if not part:
            continue
        if "=" not in part:
            continue
        key, raw_value = part.split("=", 1)
        attributes[key] = raw_value
    return attributes


def extract_locations(gff3_path: Path, species_id: str, gene_ids: set[str]) -> list[dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    with Path(gff3_path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            attributes = _parse_attributes(fields[8])
            gene_id = attributes.get("ID") or attributes.get("gene_id") or attributes.get("Name")
            if not gene_id or gene_id not in gene_ids:
                continue
            found[gene_id] = {
                "species_id": species_id,
                "gene_id": gene_id,
                "seqid": fields[0],
                "start": fields[3],
                "end": fields[4],
                "strand": fields[6],
            }

    missing = sorted(gene_ids - set(found))
    if missing:
        raise ValueError(f"Missing GFF3 gene IDs: {', '.join(missing)}")
    return [found[gene_id] for gene_id in sorted(found)]


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gff3", required=True, type=Path)
    parser.add_argument("--species-id", required=True)
    parser.add_argument("--ids", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    gene_ids = {line.strip() for line in args.ids.read_text(encoding="utf-8").splitlines() if line.strip()}
    write_tsv(extract_locations(args.gff3, args.species_id, gene_ids), args.out)


if __name__ == "__main__":
    main()
