#!/usr/bin/env python3
"""Extract chromosome coordinates for selected genes from GFF3."""

from __future__ import annotations

import argparse
import csv
import re
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


def _clean_attr_id(value: str) -> str:
    return value.split()[0].split("|", 1)[0] if value else ""


def _strip_common_gene_version(value: str) -> str:
    stripped = re.sub(r"\.v\d+(?:\.\d+)*$", "", value, flags=re.IGNORECASE)
    if stripped != value:
        return stripped
    return re.sub(r"\.\d+$", "", value)


def _gene_aliases(attributes: dict[str, str]) -> set[str]:
    aliases: set[str] = set()
    for key in ("ID", "Name", "gene_id", "locus", "locus_tag"):
        alias = _clean_attr_id(attributes.get(key, ""))
        if alias:
            aliases.add(alias)
            aliases.add(_strip_common_gene_version(alias))
    return {alias for alias in aliases if alias}


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
            for gene_id in sorted(gene_ids & _gene_aliases(attributes)):
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _gene_ids_by_species(family_candidates: list[dict[str, str]]) -> dict[str, set[str]]:
    gene_ids: dict[str, set[str]] = {}
    for row in family_candidates:
        species_id = row.get("species_id", "")
        gene_id = row.get("gene_id", "")
        if not species_id or not gene_id:
            continue
        gene_ids.setdefault(species_id, set()).add(gene_id)
    return gene_ids


def extract_locations_for_manifest(
    family_candidates: list[dict[str, str]],
    species_manifest: list[dict[str, str]],
) -> list[dict[str, str]]:
    manifest_by_species = {row["species_id"]: row for row in species_manifest}
    rows: list[dict[str, str]] = []
    for species_id, gene_ids in sorted(_gene_ids_by_species(family_candidates).items()):
        manifest_row = manifest_by_species.get(species_id)
        if not manifest_row:
            raise ValueError(f"Missing species manifest row for {species_id}")
        gff3 = manifest_row.get("gff3", "")
        if not gff3:
            raise ValueError(f"Missing GFF3 path for {species_id}")
        rows.extend(extract_locations(Path(gff3), species_id, gene_ids))
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", type=Path)
    parser.add_argument("--species-manifest", type=Path)
    parser.add_argument("--gff3", type=Path)
    parser.add_argument("--species-id")
    parser.add_argument("--ids", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.family_candidates and args.species_manifest:
        rows = extract_locations_for_manifest(read_tsv(args.family_candidates), read_tsv(args.species_manifest))
    elif args.gff3 and args.species_id and args.ids:
        gene_ids = {line.strip() for line in args.ids.read_text(encoding="utf-8").splitlines() if line.strip()}
        rows = extract_locations(args.gff3, args.species_id, gene_ids)
    else:
        raise SystemExit(
            "Provide either --family-candidates with --species-manifest or --gff3 with --species-id and --ids"
        )
    write_tsv(rows, args.out)


if __name__ == "__main__":
    main()
