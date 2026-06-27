#!/usr/bin/env python3
"""Build reference peptide FASTA from TAIR all.domains.txt annotations."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from bin.genefam.extract_sequences import write_fasta
except ModuleNotFoundError:  # pragma: no cover - supports direct script execution
    from extract_sequences import write_fasta


def read_tair_domains(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line:
                continue
            rows.append(line.split("\t"))
    return rows


def tair_gene_id(protein_id: str) -> str:
    return protein_id.split(".", 1)[0]


def find_domain_protein_ids(rows: list[list[str]], terms: list[str]) -> list[str]:
    normalized_terms = [term.casefold() for term in terms if term.strip()]
    if not normalized_terms:
        raise ValueError("At least one domain search term is required")
    protein_ids: set[str] = set()
    for row in rows:
        if not row:
            continue
        protein_id = row[0].strip()
        searchable_text = "\t".join(row[2:]).casefold()
        if protein_id and any(term in searchable_text for term in normalized_terms):
            protein_ids.add(tair_gene_id(protein_id))
    return sorted(protein_ids)


def read_peptide_fasta_records(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    current_id: str | None = None
    current_sequence: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current_id is not None:
                    records.append((current_id, "".join(current_sequence)))
                current_id = line[1:].split()[0]
                current_sequence = []
            elif current_id is None:
                raise ValueError(f"Sequence found before first FASTA header in {path}")
            else:
                current_sequence.append(line)
    if current_id is not None:
        records.append((current_id, "".join(current_sequence)))
    return records


def read_peptide_fasta_aliases(path: Path) -> dict[str, str]:
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

    aliases: dict[str, str] = {}
    for record_id, sequence_parts in records.items():
        sequence = "".join(sequence_parts)
        record_before_pipe = record_id.split("|", 1)[0]
        for alias in {record_id, record_before_pipe, tair_gene_id(record_before_pipe)}:
            if alias in aliases and aliases[alias] != sequence:
                raise ValueError(f"Duplicate FASTA alias with conflicting sequences: {alias}")
            aliases[alias] = sequence
    return aliases


def select_reference_records(
    domains: Path,
    peptides: Path,
    terms: list[str],
) -> tuple[list[str], list[tuple[str, str]], list[str]]:
    protein_ids = find_domain_protein_ids(read_tair_domains(domains), terms)
    if not protein_ids:
        raise ValueError(f"No TAIR domain records matched terms: {', '.join(terms)}")
    protein_id_set = set(protein_ids)
    selected: list[tuple[str, str]] = []
    matched_gene_ids: set[str] = set()
    for record_id, sequence in read_peptide_fasta_records(peptides):
        record_before_pipe = record_id.split("|", 1)[0]
        gene_id = tair_gene_id(record_before_pipe)
        if gene_id in protein_id_set:
            selected.append((record_id, sequence))
            matched_gene_ids.add(gene_id)
    missing = sorted(protein_id_set - matched_gene_ids)
    return protein_ids, selected, missing


def extract_reference_records(
    domains: Path,
    peptides: Path,
    terms: list[str],
    allow_missing: bool = False,
) -> list[tuple[str, str]]:
    _protein_ids, selected, missing = select_reference_records(domains, peptides, terms)
    if missing:
        if allow_missing:
            return selected
        raise ValueError(f"Missing sequence IDs: {', '.join(missing)}")
    return selected


def write_ids(ids: list[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(f"{protein_id}\n" for protein_id in ids), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domains", required=True, type=Path, help="TAIR all.domains.txt file")
    parser.add_argument("--peptides", required=True, type=Path, help="Arabidopsis peptide FASTA")
    parser.add_argument("--terms", required=True, nargs="+", help="Domain terms such as PF00657 or GDSL_lipase")
    parser.add_argument("--out", required=True, type=Path, help="Output reference peptide FASTA")
    parser.add_argument("--ids-out", default=None, type=Path, help="Optional output protein ID list")
    parser.add_argument("--allow-missing", action="store_true", help="Write matched records even if some TAIR IDs are absent from the peptide FASTA")
    parser.add_argument("--missing-out", default=None, type=Path, help="Optional output missing gene ID list")
    args = parser.parse_args()

    reference_ids, records, missing = select_reference_records(args.domains, args.peptides, args.terms)
    if missing and not args.allow_missing:
        raise ValueError(f"Missing sequence IDs: {', '.join(missing)}")
    write_fasta(records, args.out)
    if args.ids_out:
        write_ids(reference_ids, args.ids_out)
    if args.missing_out:
        write_ids(missing, args.missing_out)
    print(f"Extracted {len(records)} reference peptide records to {args.out}")
    if missing:
        print(f"Missing {len(missing)} TAIR gene IDs from peptide FASTA")


if __name__ == "__main__":
    main()
