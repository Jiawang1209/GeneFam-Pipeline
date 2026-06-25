#!/usr/bin/env python3
"""Extract promoter intervals and FASTA sequences for family members."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


BED_FIELDNAMES = [
    "species_id",
    "gene_id",
    "seqid",
    "strand",
    "gene_start",
    "gene_end",
    "promoter_start",
    "promoter_end",
    "promoter_length",
    "boundary_clipped",
]
COMPLEMENT = str.maketrans("ACGTNacgtn", "TGCANtgcan")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current_id = ""
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current_id = line[1:].split()[0]
                records[current_id] = []
                continue
            if not current_id:
                raise ValueError(f"FASTA sequence before header in {path}")
            records[current_id].append(line)
    return {record_id: "".join(parts) for record_id, parts in records.items()}


def _parse_attributes(value: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for part in value.split(";"):
        if not part or "=" not in part:
            continue
        key, raw_value = part.split("=", 1)
        attributes[key] = raw_value
    return attributes


def _read_gene_rows(gff3: Path, gene_ids: set[str]) -> dict[str, dict[str, str]]:
    genes: dict[str, dict[str, str]] = {}
    with Path(gff3).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            attributes = _parse_attributes(fields[8])
            gene_id = attributes.get("ID") or attributes.get("gene_id") or attributes.get("Name")
            if gene_id in gene_ids:
                genes[gene_id] = {
                    "seqid": fields[0],
                    "start": fields[3],
                    "end": fields[4],
                    "strand": fields[6],
                }
    missing = sorted(gene_ids - set(genes))
    if missing:
        raise ValueError(f"Missing GFF3 gene IDs: {', '.join(missing)}")
    return genes


def _reverse_complement(sequence: str) -> str:
    return sequence.translate(COMPLEMENT)[::-1].upper()


def _gene_ids_by_species(family_rows: list[dict[str, str]]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = {}
    for row in family_rows:
        species_id = row.get("species_id", "")
        gene_id = row.get("gene_id", "")
        if species_id and gene_id:
            grouped.setdefault(species_id, set()).add(gene_id)
    return grouped


def _promoter_bounds(
    gene_start: int,
    gene_end: int,
    strand: str,
    sequence_length: int,
    upstream_bp: int,
    downstream_bp: int,
) -> tuple[int, int, bool]:
    if strand == "-":
        raw_start = gene_end - downstream_bp + 1
        raw_end = gene_end + upstream_bp
    else:
        raw_start = gene_start - upstream_bp
        raw_end = gene_start + downstream_bp - 1
    start = max(1, raw_start)
    end = min(sequence_length, raw_end)
    return start, end, start != raw_start or end != raw_end


def extract_promoters(
    family_rows: list[dict[str, str]],
    species_manifest: list[dict[str, str]],
    upstream_bp: int,
    downstream_bp: int = 0,
) -> tuple[list[dict[str, str]], list[tuple[str, str]]]:
    manifest_by_species = {row["species_id"]: row for row in species_manifest}
    bed_rows: list[dict[str, str]] = []
    fasta_records: list[tuple[str, str]] = []
    for species_id, gene_ids in sorted(_gene_ids_by_species(family_rows).items()):
        manifest_row = manifest_by_species.get(species_id)
        if not manifest_row:
            raise ValueError(f"Missing species manifest row for {species_id}")
        gff3 = manifest_row.get("gff3", "")
        genome = manifest_row.get("genome", "")
        if not gff3:
            raise ValueError(f"Missing GFF3 path for {species_id}")
        if not genome:
            raise ValueError(f"Missing genome path for {species_id}")
        genes = _read_gene_rows(Path(gff3), gene_ids)
        genome_records = read_fasta(Path(genome))
        for gene_id in sorted(genes):
            gene = genes[gene_id]
            seqid = gene["seqid"]
            sequence = genome_records.get(seqid)
            if sequence is None:
                raise ValueError(f"Missing genome sequence {seqid} for {species_id}")
            gene_start = int(gene["start"])
            gene_end = int(gene["end"])
            strand = gene["strand"]
            promoter_start, promoter_end, clipped = _promoter_bounds(
                gene_start,
                gene_end,
                strand,
                len(sequence),
                upstream_bp,
                downstream_bp,
            )
            promoter = sequence[promoter_start - 1 : promoter_end].upper()
            if strand == "-":
                promoter = _reverse_complement(promoter)
            bed_rows.append(
                {
                    "species_id": species_id,
                    "gene_id": gene_id,
                    "seqid": seqid,
                    "strand": strand,
                    "gene_start": str(gene_start),
                    "gene_end": str(gene_end),
                    "promoter_start": str(promoter_start),
                    "promoter_end": str(promoter_end),
                    "promoter_length": str(max(0, promoter_end - promoter_start + 1)),
                    "boundary_clipped": str(clipped).lower(),
                }
            )
            fasta_records.append((f"{species_id}|{gene_id}|{seqid}:{promoter_start}-{promoter_end}({strand})", promoter))
    return bed_rows, fasta_records


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BED_FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_fasta(records: list[tuple[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for record_id, sequence in records:
        lines.append(f">{record_id}")
        lines.extend(sequence[index : index + 80] for index in range(0, len(sequence), 80))
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--upstream-bp", required=True, type=int)
    parser.add_argument("--downstream-bp", default=0, type=int)
    parser.add_argument("--out-bed", required=True, type=Path)
    parser.add_argument("--out-fasta", required=True, type=Path)
    args = parser.parse_args()
    bed_rows, fasta_records = extract_promoters(
        read_tsv(args.family_candidates),
        read_tsv(args.species_manifest),
        upstream_bp=args.upstream_bp,
        downstream_bp=args.downstream_bp,
    )
    write_tsv(bed_rows, args.out_bed)
    write_fasta(fasta_records, args.out_fasta)


if __name__ == "__main__":
    main()
