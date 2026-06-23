#!/usr/bin/env python3
"""Extract family member peptide sequences using candidate and species manifest tables."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current_id: str | None = None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current_id = line[1:].split()[0]
                records[current_id] = []
            elif current_id is None:
                raise ValueError(f"Sequence found before first FASTA header in {path}")
            else:
                records[current_id].append(line)
    return {record_id: "".join(parts) for record_id, parts in records.items()}


def extract_family_sequences(
    family_rows: list[dict[str, str]],
    manifest_rows: list[dict[str, str]],
) -> list[tuple[str, str]]:
    pep_by_species = {row["species_id"]: Path(row["pep"]) for row in manifest_rows}
    fasta_cache: dict[str, dict[str, str]] = {}
    records: list[tuple[str, str]] = []
    for row in family_rows:
        species_id = row["species_id"]
        gene_id = row["gene_id"]
        if species_id not in pep_by_species:
            raise ValueError(f"Missing species in manifest: {species_id}")
        if species_id not in fasta_cache:
            fasta_cache[species_id] = _read_fasta(pep_by_species[species_id])
        if gene_id not in fasta_cache[species_id]:
            raise ValueError(f"Missing sequence ID for {species_id}: {gene_id}")
        records.append((f"{species_id}|{gene_id}", fasta_cache[species_id][gene_id]))
    return records


def write_fasta(records: list[tuple[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for record_id, sequence in records:
            handle.write(f">{record_id}\n{sequence}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_fasta(
        extract_family_sequences(read_tsv(args.family_candidates), read_tsv(args.species_manifest)),
        args.out,
    )


if __name__ == "__main__":
    main()
