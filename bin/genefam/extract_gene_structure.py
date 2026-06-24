#!/usr/bin/env python3
"""Summarize family member gene structure from GFF3 annotations."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = [
    "species_id",
    "gene_id",
    "gene_length",
    "transcript_count",
    "exon_count",
    "cds_count",
    "exon_total_length",
    "cds_total_length",
]
TRANSCRIPT_TYPES = {"mRNA", "transcript"}


def _parse_attributes(value: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for part in value.split(";"):
        if not part or "=" not in part:
            continue
        key, raw_value = part.split("=", 1)
        attributes[key] = raw_value
    return attributes


def _feature_length(start: str, end: str) -> int:
    return int(end) - int(start) + 1


def _parent_ids(attributes: dict[str, str]) -> list[str]:
    return [part for part in attributes.get("Parent", "").split(",") if part]


def extract_structure(gff3_path: Path, species_id: str, gene_ids: set[str]) -> list[dict[str, str]]:
    gene_rows: dict[str, dict[str, int]] = {}
    transcript_to_gene: dict[str, str] = {}
    transcript_ids_by_gene: dict[str, set[str]] = {gene_id: set() for gene_id in gene_ids}

    with Path(gff3_path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9:
                continue
            feature_type = fields[2]
            attributes = _parse_attributes(fields[8])
            feature_id = attributes.get("ID") or attributes.get("gene_id") or attributes.get("Name")
            parents = _parent_ids(attributes)

            if feature_type == "gene":
                gene_id = feature_id
                if gene_id in gene_ids:
                    gene_rows[gene_id] = {
                        "gene_length": _feature_length(fields[3], fields[4]),
                        "exon_count": 0,
                        "cds_count": 0,
                        "exon_total_length": 0,
                        "cds_total_length": 0,
                    }
                continue

            if feature_type in TRANSCRIPT_TYPES and feature_id:
                for parent in parents:
                    if parent in gene_ids:
                        transcript_to_gene[feature_id] = parent
                        transcript_ids_by_gene[parent].add(feature_id)
                continue

            if feature_type not in {"exon", "CDS"}:
                continue

            target_genes = {
                transcript_to_gene.get(parent, parent)
                for parent in parents
                if transcript_to_gene.get(parent, parent) in gene_ids
            }
            for gene_id in target_genes:
                gene_rows.setdefault(
                    gene_id,
                    {
                        "gene_length": 0,
                        "exon_count": 0,
                        "cds_count": 0,
                        "exon_total_length": 0,
                        "cds_total_length": 0,
                    },
                )
                if feature_type == "exon":
                    gene_rows[gene_id]["exon_count"] += 1
                    gene_rows[gene_id]["exon_total_length"] += _feature_length(fields[3], fields[4])
                else:
                    gene_rows[gene_id]["cds_count"] += 1
                    gene_rows[gene_id]["cds_total_length"] += _feature_length(fields[3], fields[4])

    missing = sorted(gene_ids - set(gene_rows))
    if missing:
        raise ValueError(f"Missing GFF3 gene IDs: {', '.join(missing)}")

    rows: list[dict[str, str]] = []
    for gene_id in sorted(gene_rows):
        summary = gene_rows[gene_id]
        rows.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "gene_length": str(summary["gene_length"]),
                "transcript_count": str(len(transcript_ids_by_gene.get(gene_id, set()))),
                "exon_count": str(summary["exon_count"]),
                "cds_count": str(summary["cds_count"]),
                "exon_total_length": str(summary["exon_total_length"]),
                "cds_total_length": str(summary["cds_total_length"]),
            }
        )
    return rows


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _gene_ids_by_species(family_candidates: list[dict[str, str]]) -> dict[str, set[str]]:
    gene_ids: dict[str, set[str]] = {}
    for row in family_candidates:
        species_id = row.get("species_id", "")
        gene_id = row.get("gene_id", "")
        if species_id and gene_id:
            gene_ids.setdefault(species_id, set()).add(gene_id)
    return gene_ids


def summarize_structure(
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
        rows.extend(extract_structure(Path(gff3), species_id, gene_ids))
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(summarize_structure(read_tsv(args.family_candidates), read_tsv(args.species_manifest)), args.out)


if __name__ == "__main__":
    main()
