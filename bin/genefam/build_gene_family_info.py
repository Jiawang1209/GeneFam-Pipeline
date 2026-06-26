#!/usr/bin/env python3
"""Build copy-number and protein-property tables for gene family information plots."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


COPY_FIELDS = [
    "species_id",
    "member_count",
    "hmmer_count",
    "diamond_count",
    "intersection_count",
    "copy_number_class",
    "copy_number_rank",
    "percent_of_max",
]
SUMMARY_FIELDS = ["copy_number_class", "species_count", "mean_member_count", "max_member_count"]
SPECIES_ORDER_FIELDS = ["species_id", "member_count", "copy_number_class", "copy_number_rank", "plot_order"]
EXPANSION_FIELDS = [
    "species_id",
    "member_count",
    "median_member_count",
    "fold_change_vs_median",
    "expansion_status",
    "copy_number_class",
]
PANGENOME_FIELDS = [
    "total_species",
    "present_species",
    "absent_species",
    "presence_fraction",
    "pangenome_presence_class",
    "max_member_count",
    "median_present_member_count",
]
PROTEIN_FIELDS = [
    "species_id",
    "gene_id",
    "protein_length",
    "molecular_weight_kda",
    "isoelectric_point",
    "gravy",
]

AA_WEIGHTS = {
    "A": 89.09,
    "R": 174.20,
    "N": 132.12,
    "D": 133.10,
    "C": 121.15,
    "Q": 146.15,
    "E": 147.13,
    "G": 75.07,
    "H": 155.16,
    "I": 131.17,
    "L": 131.17,
    "K": 146.19,
    "M": 149.21,
    "F": 165.19,
    "P": 115.13,
    "S": 105.09,
    "T": 119.12,
    "W": 204.23,
    "Y": 181.19,
    "V": 117.15,
}
KD_SCALE = {
    "A": 1.8,
    "R": -4.5,
    "N": -3.5,
    "D": -3.5,
    "C": 2.5,
    "Q": -3.5,
    "E": -3.5,
    "G": -0.4,
    "H": -3.2,
    "I": 4.5,
    "L": 3.8,
    "K": -3.9,
    "M": 1.9,
    "F": 2.8,
    "P": -1.6,
    "S": -0.8,
    "T": -0.7,
    "W": -0.9,
    "Y": -1.3,
    "V": 4.2,
}


@dataclass(frozen=True)
class GeneFamilyInfoTables:
    copy_number: list[dict[str, str]]
    copy_number_summary: list[dict[str, str]]
    species_order: list[dict[str, str]]
    copy_number_expansion: list[dict[str, str]]
    pangenome_summary: list[dict[str, str]]
    protein_properties: list[dict[str, str]]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_fasta(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    header = ""
    sequence_parts: list[str] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header:
                    records.append((header, "".join(sequence_parts)))
                header = line[1:].split()[0]
                sequence_parts = []
            else:
                sequence_parts.append(line)
    if header:
        records.append((header, "".join(sequence_parts)))
    return records


def _copy_class(member_count: int) -> str:
    if member_count <= 0:
        return "absent"
    if member_count == 1:
        return "single_copy"
    if member_count <= 5:
        return "multi_copy"
    return "high_copy"


def _mean(values: list[int]) -> str:
    if not values:
        return "0.0000"
    return f"{sum(values) / len(values):.4f}"


def _copy_number_rows(family_counts: list[dict[str, str]]) -> list[dict[str, str]]:
    counts = [(row.get("species_id", ""), int(float(row.get("member_count", "0") or 0)), row) for row in family_counts]
    max_count = max([count for _, count, _ in counts] or [0])
    sorted_counts = sorted(counts, key=lambda item: (-item[1], item[0]))
    rank_by_species = {species_id: rank for rank, (species_id, _, _) in enumerate(sorted_counts, start=1)}
    rows: list[dict[str, str]] = []
    for species_id, member_count, source in sorted(counts, key=lambda item: item[0]):
        percent = 0 if max_count == 0 else member_count / max_count * 100
        rows.append(
            {
                "species_id": species_id,
                "member_count": str(member_count),
                "hmmer_count": str(source.get("hmmer_count", "0") or "0"),
                "diamond_count": str(source.get("diamond_count", "0") or "0"),
                "intersection_count": str(source.get("intersection_count", "0") or "0"),
                "copy_number_class": _copy_class(member_count),
                "copy_number_rank": str(rank_by_species[species_id]),
                "percent_of_max": f"{percent:.4f}",
            }
        )
    return rows


def _copy_number_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[int]] = {}
    for row in rows:
        grouped.setdefault(row["copy_number_class"], []).append(int(row["member_count"]))
    return [
        {
            "copy_number_class": class_name,
            "species_count": str(len(values)),
            "mean_member_count": _mean(values),
            "max_member_count": str(max(values) if values else 0),
        }
        for class_name, values in sorted(grouped.items())
    ]


def _species_order(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    ordered = sorted(rows, key=lambda row: (int(row["copy_number_rank"]), row["species_id"]))
    return [
        {
            "species_id": row["species_id"],
            "member_count": row["member_count"],
            "copy_number_class": row["copy_number_class"],
            "copy_number_rank": row["copy_number_rank"],
            "plot_order": str(index),
        }
        for index, row in enumerate(ordered, start=1)
    ]


def _expansion_status(member_count: int, median_count: float) -> str:
    if member_count <= 0:
        return "absent"
    if median_count <= 0:
        return "baseline"
    fold_change = member_count / median_count
    if fold_change >= 2:
        return "expanded"
    if fold_change <= 0.5:
        return "contracted"
    return "baseline"


def _copy_number_expansion(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    counts = [int(row["member_count"]) for row in rows if int(row["member_count"]) > 0]
    median_count = statistics.median(counts) if counts else 0
    ordered = sorted(rows, key=lambda row: (int(row["copy_number_rank"]), row["species_id"]))
    expansion_rows: list[dict[str, str]] = []
    for row in ordered:
        member_count = int(row["member_count"])
        fold_change = 0 if median_count <= 0 else member_count / median_count
        expansion_rows.append(
            {
                "species_id": row["species_id"],
                "member_count": row["member_count"],
                "median_member_count": f"{median_count:.4f}",
                "fold_change_vs_median": f"{fold_change:.4f}",
                "expansion_status": _expansion_status(member_count, median_count),
                "copy_number_class": row["copy_number_class"],
            }
        )
    return expansion_rows


def _pangenome_presence_class(presence_fraction: float) -> str:
    if presence_fraction >= 1:
        return "core"
    if presence_fraction >= 0.95:
        return "soft_core"
    if presence_fraction > 0:
        return "dispensable"
    return "absent"


def _pangenome_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    counts = [int(row["member_count"]) for row in rows]
    present_counts = [count for count in counts if count > 0]
    total_species = len(counts)
    present_species = len(present_counts)
    absent_species = total_species - present_species
    presence_fraction = 0 if total_species == 0 else present_species / total_species
    median_present = statistics.median(present_counts) if present_counts else 0
    return [
        {
            "total_species": str(total_species),
            "present_species": str(present_species),
            "absent_species": str(absent_species),
            "presence_fraction": f"{presence_fraction:.4f}",
            "pangenome_presence_class": _pangenome_presence_class(presence_fraction),
            "max_member_count": str(max(counts) if counts else 0),
            "median_present_member_count": f"{median_present:.4f}",
        }
    ]


def _split_fasta_header(header: str) -> tuple[str, str]:
    parts = header.split("|")
    if len(parts) >= 2:
        return parts[0], parts[1]
    return "", header


def _molecular_weight_kda(sequence: str) -> float:
    residues = [aa for aa in sequence.upper() if aa in AA_WEIGHTS]
    if not residues:
        return 0.0
    # Sum free amino-acid masses and subtract water for peptide bonds.
    return (sum(AA_WEIGHTS[aa] for aa in residues) - 18.015 * max(0, len(residues) - 1)) / 1000


def _gravy(sequence: str) -> float:
    values = [KD_SCALE[aa] for aa in sequence.upper() if aa in KD_SCALE]
    if not values:
        return 0.0
    return sum(values) / len(values)


def _charge_at_ph(sequence: str, ph: float) -> float:
    counts = Counter(sequence.upper())
    positive = (
        counts["K"] * (10**10.54 / (10**10.54 + 10**ph))
        + counts["R"] * (10**12.48 / (10**12.48 + 10**ph))
        + counts["H"] * (10**6.04 / (10**6.04 + 10**ph))
        + (10**9.69 / (10**9.69 + 10**ph))
    )
    negative = (
        counts["D"] * (10**ph / (10**3.90 + 10**ph))
        + counts["E"] * (10**ph / (10**4.07 + 10**ph))
        + counts["C"] * (10**ph / (10**8.18 + 10**ph))
        + counts["Y"] * (10**ph / (10**10.46 + 10**ph))
        + (10**ph / (10**2.34 + 10**ph))
    )
    return positive - negative


def _isoelectric_point(sequence: str) -> float:
    if not sequence:
        return 0.0
    low = 0.0
    high = 14.0
    for _ in range(40):
        mid = (low + high) / 2
        if _charge_at_ph(sequence, mid) > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def _protein_property_rows(fasta_records: list[tuple[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for header, sequence in fasta_records:
        species_id, gene_id = _split_fasta_header(header)
        clean_sequence = "".join(aa for aa in sequence.upper() if aa.isalpha())
        rows.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "protein_length": str(len(clean_sequence)),
                "molecular_weight_kda": f"{_molecular_weight_kda(clean_sequence):.4f}",
                "isoelectric_point": f"{_isoelectric_point(clean_sequence):.4f}",
                "gravy": f"{_gravy(clean_sequence):.4f}",
            }
        )
    return rows


def build_gene_family_info_tables(
    family_counts: list[dict[str, str]], fasta_records: list[tuple[str, str]] | None = None
) -> GeneFamilyInfoTables:
    copy_number = _copy_number_rows(family_counts)
    return GeneFamilyInfoTables(
        copy_number=copy_number,
        copy_number_summary=_copy_number_summary(copy_number),
        species_order=_species_order(copy_number),
        copy_number_expansion=_copy_number_expansion(copy_number),
        pangenome_summary=_pangenome_summary(copy_number),
        protein_properties=_protein_property_rows(fasta_records or []),
    )


def _write_tsv(rows: list[dict[str, str]], fieldnames: list[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_tables(tables: GeneFamilyInfoTables, outdir: Path) -> dict[str, Path]:
    outputs = {
        "gene_family_copy_number": outdir / "gene_family_copy_number.tsv",
        "gene_family_copy_number_summary": outdir / "gene_family_copy_number_summary.tsv",
        "gene_family_species_order": outdir / "gene_family_species_order.tsv",
        "gene_family_copy_number_expansion": outdir / "gene_family_copy_number_expansion.tsv",
        "gene_family_pangenome_summary": outdir / "gene_family_pangenome_summary.tsv",
        "gene_family_protein_properties": outdir / "gene_family_protein_properties.tsv",
    }
    _write_tsv(tables.copy_number, COPY_FIELDS, outputs["gene_family_copy_number"])
    _write_tsv(tables.copy_number_summary, SUMMARY_FIELDS, outputs["gene_family_copy_number_summary"])
    _write_tsv(tables.species_order, SPECIES_ORDER_FIELDS, outputs["gene_family_species_order"])
    _write_tsv(tables.copy_number_expansion, EXPANSION_FIELDS, outputs["gene_family_copy_number_expansion"])
    _write_tsv(tables.pangenome_summary, PANGENOME_FIELDS, outputs["gene_family_pangenome_summary"])
    _write_tsv(tables.protein_properties, PROTEIN_FIELDS, outputs["gene_family_protein_properties"])
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-counts", required=True, type=Path)
    parser.add_argument("--family-members-faa", default=None, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    fasta_records = read_fasta(args.family_members_faa) if args.family_members_faa else []
    tables = build_gene_family_info_tables(read_tsv(args.family_counts), fasta_records)
    write_tables(tables, args.outdir)


if __name__ == "__main__":
    main()
