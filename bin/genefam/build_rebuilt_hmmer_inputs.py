#!/usr/bin/env python3
"""Prepare first-pass HMMER hits for a Reference-style rebuilt HMM search."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


INPUT_FIELDS = ["species_id", "pep", "hmm_id", "hmm_profile"]
STATUS_FIELDS = ["status", "hit_count", "species_count", "note"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    current_id: str | None = None
    current_sequence: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current_id is not None:
                    records[current_id] = "".join(current_sequence)
                current_id = line[1:].split()[0]
                current_sequence = []
            elif current_id is not None:
                current_sequence.append(line)
    if current_id is not None:
        records[current_id] = "".join(current_sequence)
    return records


def write_fasta(records: list[tuple[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record_id, sequence in records:
            handle.write(f">{record_id}\n{sequence}\n")


def _first_pass_hits(hmmer_tables: list[Path]) -> dict[str, set[str]]:
    hits: dict[str, set[str]] = {}
    for table in hmmer_tables:
        for row in read_tsv(table):
            species_id = row.get("species_id", "").strip()
            gene_id = row.get("gene_id", "").strip()
            if species_id and gene_id:
                hits.setdefault(species_id, set()).add(gene_id)
    return hits


def build_rebuilt_hmmer_inputs(
    *,
    hmmer_tables: list[Path],
    species_manifest: Path,
    family_name: str,
    outdir: Path,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "hits_fasta": outdir / "first_pass_hits.faa",
        "inputs": outdir / "rebuilt_hmmer_inputs.tsv",
        "status": outdir / "rebuilt_hmmer_status.tsv",
    }
    rebuilt_hmm = (outdir / f"{family_name}.rebuilt.hmm").resolve()
    hits_by_species = _first_pass_hits(hmmer_tables)

    hit_records: list[tuple[str, str]] = []
    input_rows: list[dict[str, str]] = []
    for species in read_tsv(species_manifest):
        species_id = species.get("species_id", "").strip()
        pep_path = Path(species.get("pep", ""))
        if species_id:
            input_rows.append(
                {
                    "species_id": species_id,
                    "pep": str(pep_path),
                    "hmm_id": f"{family_name}_rebuilt",
                    "hmm_profile": str(rebuilt_hmm),
                }
            )
        if not species_id or not pep_path.exists():
            continue
        peptides = read_fasta(pep_path)
        for gene_id in sorted(hits_by_species.get(species_id, set())):
            sequence = peptides.get(gene_id)
            if sequence:
                hit_records.append((f"{species_id}|{gene_id}", sequence))

    write_fasta(hit_records, outputs["hits_fasta"])
    write_tsv(input_rows, outputs["inputs"], INPUT_FIELDS)
    if hit_records:
        status = {
            "status": "available",
            "hit_count": str(len(hit_records)),
            "species_count": str(len({record_id.split("|", 1)[0] for record_id, _seq in hit_records})),
            "note": "First-pass HMMER hits extracted for HMM rebuild",
        }
    else:
        status = {
            "status": "missing_input",
            "hit_count": "0",
            "species_count": "0",
            "note": "No first-pass HMMER hits could be matched to cleaned peptide FASTA records",
        }
    write_tsv([status], outputs["status"], STATUS_FIELDS)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hmmer-table", action="append", default=[], type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--family-name", required=True)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    build_rebuilt_hmmer_inputs(
        hmmer_tables=args.hmmer_table,
        species_manifest=args.species_manifest,
        family_name=args.family_name,
        outdir=args.outdir,
    )


if __name__ == "__main__":
    main()
