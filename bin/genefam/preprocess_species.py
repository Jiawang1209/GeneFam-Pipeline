#!/usr/bin/env python3
"""Clean species-bank peptide/CDS FASTA files and select representative transcripts."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


MANIFEST_FIELDS = ["species_id", "pep", "gff3", "cds", "genome"]
TRANSCRIPT_FIELDS = ["species_id", "raw_transcript_id", "clean_transcript_id", "gene_id", "source"]
REPRESENTATIVE_FIELDS = [
    "species_id",
    "gene_id",
    "selected_transcript_id",
    "pep_length",
    "cds_length",
    "rule",
]
WARNING_FIELDS = ["species_id", "gene_id", "transcript_id", "warning"]


def read_fasta_records(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    current_id: str | None = None
    current_sequence: list[str] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current_id is not None:
                    records.append((current_id, "".join(current_sequence)))
                current_id = line[1:]
                current_sequence = []
            elif current_id is None:
                raise ValueError(f"Sequence found before first FASTA header in {path}")
            else:
                current_sequence.append(line)
    if current_id is not None:
        records.append((current_id, "".join(current_sequence)))
    return records


def write_fasta(records: list[tuple[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record_id, sequence in records:
            handle.write(f">{record_id}\n{sequence}\n")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], fields: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def clean_header_id(raw_id: str) -> str:
    parts = raw_id.split()
    if not parts:
        return ""
    return parts[0].split("|", 1)[0]


def parse_fasta_header_attributes(raw_id: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for token in raw_id.split()[1:]:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        attributes[key] = value
    return attributes


def _parse_gff3_attributes(value: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for item in value.split(";"):
        if not item:
            continue
        if "=" in item:
            key, raw_value = item.split("=", 1)
        elif " " in item:
            key, raw_value = item.split(" ", 1)
        else:
            continue
        attributes[key.strip()] = raw_value.strip().strip('"')
    return attributes


def parse_gff3_transcript_gene_map(path: Path | str | None) -> dict[str, str]:
    if not path:
        return {}
    gff3 = Path(path)
    if not gff3.exists():
        return {}

    gene_ids: set[str] = set()
    transcript_to_gene: dict[str, str] = {}
    child_to_parent: dict[str, str] = {}
    transcript_features = {"mrna", "transcript", "rna"}
    with gff3.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            feature_type = parts[2].casefold()
            attributes = _parse_gff3_attributes(parts[8])
            feature_id = clean_header_id(attributes.get("ID", ""))
            feature_name = clean_header_id(attributes.get("Name", ""))
            parent = clean_header_id(attributes.get("Parent", ""))
            gene_id = clean_header_id(attributes.get("gene_id", ""))
            transcript_id = clean_header_id(attributes.get("transcript_id", ""))

            if feature_type == "gene" and feature_id:
                gene_ids.add(feature_id)
            if feature_type in transcript_features:
                tx_id = transcript_id or feature_id
                tx_gene = gene_id or parent
                if tx_id and tx_gene:
                    transcript_to_gene[tx_id] = tx_gene
                for alias_key in ("Name", "Alias", "protein_id", "polypeptide", "Derives_from"):
                    for alias in attributes.get(alias_key, "").split(","):
                        clean_alias = clean_header_id(alias)
                        if clean_alias and tx_gene:
                            transcript_to_gene[clean_alias] = tx_gene
                if feature_name and tx_gene:
                    transcript_to_gene[feature_name] = tx_gene
            elif parent and transcript_id:
                child_to_parent[transcript_id] = parent

    for child, parent in child_to_parent.items():
        if child not in transcript_to_gene and parent in transcript_to_gene:
            transcript_to_gene[child] = transcript_to_gene[parent]
        elif child not in transcript_to_gene and parent in gene_ids:
            transcript_to_gene[child] = parent
    return transcript_to_gene


def fallback_gene_id(clean_transcript_id: str) -> tuple[str, str]:
    patterns = [
        (r"^(?P<gene>.+?)\.\d+[A-Za-z]*$", "auto_suffix"),
        (r"^(?P<gene>.+?)\.t\d+$", "auto_suffix"),
        (r"^(?P<gene>.+?)-R[A-Za-z]+$", "auto_suffix"),
        (r"^(?P<gene>.+?)_T\d+$", "auto_suffix"),
        (r"^(?P<gene>.+?)\.p\d+$", "auto_suffix"),
    ]
    for pattern, source in patterns:
        match = re.match(pattern, clean_transcript_id, flags=re.IGNORECASE)
        if match:
            return match.group("gene"), source
    return clean_transcript_id, "self"


def infer_gene_id(raw_transcript_id: str, transcript_gene_map: dict[str, str]) -> tuple[str, str, str]:
    attributes = parse_fasta_header_attributes(raw_transcript_id)
    clean_transcript_id = clean_header_id(attributes.get("transcript", "")) or clean_header_id(raw_transcript_id)
    if attributes.get("locus"):
        return clean_transcript_id, clean_header_id(attributes["locus"]), "fasta_locus"
    if clean_transcript_id in transcript_gene_map:
        return clean_transcript_id, transcript_gene_map[clean_transcript_id], "gff3"
    if f"{clean_transcript_id}.v1.1" in transcript_gene_map:
        return clean_transcript_id, transcript_gene_map[f"{clean_transcript_id}.v1.1"], "gff3"
    gene_id, source = fallback_gene_id(clean_transcript_id)
    return clean_transcript_id, gene_id, source


def _strip_terminal_stop(sequence: str) -> str:
    return sequence[:-1] if sequence.endswith("*") else sequence


def _record_aliases(record_id: str) -> set[str]:
    clean_id = clean_header_id(record_id)
    gene_id, _source = fallback_gene_id(clean_id)
    attributes = parse_fasta_header_attributes(record_id)
    aliases = {record_id, clean_id, gene_id}
    for key in ("transcript", "polypeptide", "locus", "ID"):
        if attributes.get(key):
            aliases.add(clean_header_id(attributes[key]))
    return aliases


def clean_sequence_records(
    species_id: str,
    pep_records: list[tuple[str, str]],
    cds_records: list[tuple[str, str]],
    transcript_gene_map: dict[str, str],
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    transcript_rows: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    pep_by_gene: dict[str, list[dict[str, str | int]]] = defaultdict(list)

    for raw_id, sequence in pep_records:
        clean_transcript_id, gene_id, source = infer_gene_id(raw_id, transcript_gene_map)
        clean_sequence = _strip_terminal_stop(sequence)
        transcript_rows.append(
            {
                "species_id": species_id,
                "raw_transcript_id": raw_id,
                "clean_transcript_id": clean_transcript_id,
                "gene_id": gene_id,
                "source": source,
            }
        )
        pep_by_gene[gene_id].append(
            {
                "raw_id": raw_id,
                "clean_transcript_id": clean_transcript_id,
                "sequence": clean_sequence,
                "pep_length": len(clean_sequence),
            }
        )

    cds_by_alias: dict[str, tuple[str, str]] = {}
    for raw_id, sequence in cds_records:
        for alias in _record_aliases(raw_id):
            cds_by_alias[alias] = (raw_id, sequence)

    cleaned_pep: list[tuple[str, str]] = []
    cleaned_cds: list[tuple[str, str]] = []
    representative_rows: list[dict[str, str]] = []
    for gene_id in sorted(pep_by_gene):
        candidates = sorted(
            pep_by_gene[gene_id],
            key=lambda row: (-int(row["pep_length"]), str(row["clean_transcript_id"])),
        )
        selected = candidates[0]
        selected_transcript = str(selected["clean_transcript_id"])
        pep_sequence = str(selected["sequence"])
        cleaned_pep.append((gene_id, pep_sequence))

        cds_length = ""
        cds_match = cds_by_alias.get(str(selected["raw_id"])) or cds_by_alias.get(selected_transcript) or cds_by_alias.get(gene_id)
        if cds_match:
            _cds_raw_id, cds_sequence = cds_match
            cds_length = str(len(cds_sequence))
            cleaned_cds.append((gene_id, cds_sequence))
        elif cds_records:
            warnings.append(
                {
                    "species_id": species_id,
                    "gene_id": gene_id,
                    "transcript_id": selected_transcript,
                    "warning": "selected peptide transcript has no matching CDS record",
                }
            )

        representative_rows.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "selected_transcript_id": selected_transcript,
                "pep_length": str(len(pep_sequence)),
                "cds_length": cds_length,
                "rule": "longest_pep",
            }
        )
    return cleaned_pep, cleaned_cds, transcript_rows, representative_rows, warnings


def preprocess_manifest(manifest_rows: list[dict[str, str]], outdir: Path) -> list[dict[str, str]]:
    clean_rows: list[dict[str, str]] = []
    all_transcript_rows: list[dict[str, str]] = []
    all_representative_rows: list[dict[str, str]] = []
    all_warning_rows: list[dict[str, str]] = []
    for row in manifest_rows:
        species_id = row["species_id"]
        species_outdir = outdir / "species_bank_clean" / species_id
        pep_path = Path(row.get("pep", ""))
        cds_path = Path(row.get("cds", "")) if row.get("cds") else None
        gff3_path = Path(row.get("gff3", "")) if row.get("gff3") else None

        transcript_gene_map = parse_gff3_transcript_gene_map(gff3_path)
        cds_records = read_fasta_records(cds_path) if cds_path else []
        cleaned_pep, cleaned_cds, transcript_rows, representative_rows, warnings = clean_sequence_records(
            species_id=species_id,
            pep_records=read_fasta_records(pep_path),
            cds_records=cds_records,
            transcript_gene_map=transcript_gene_map,
        )

        clean_pep_path = species_outdir / f"{species_id}.pep.clean.fa"
        clean_cds_path = species_outdir / f"{species_id}.cds.clean.fa"
        write_fasta(cleaned_pep, clean_pep_path)
        if cds_path:
            write_fasta(cleaned_cds, clean_cds_path)
        write_tsv(transcript_rows, TRANSCRIPT_FIELDS, species_outdir / "transcript_gene_map.tsv")
        write_tsv(representative_rows, REPRESENTATIVE_FIELDS, species_outdir / "representative_transcripts.tsv")
        write_tsv(warnings, WARNING_FIELDS, species_outdir / "preprocess_warnings.tsv")
        all_transcript_rows.extend(transcript_rows)
        all_representative_rows.extend(representative_rows)
        all_warning_rows.extend(warnings)

        clean_row = dict(row)
        clean_row["pep"] = str(clean_pep_path.resolve())
        if cds_path:
            clean_row["cds"] = str(clean_cds_path.resolve())
        clean_rows.append(clean_row)
    write_tsv(all_transcript_rows, TRANSCRIPT_FIELDS, outdir / "all_transcript_gene_map.tsv")
    write_tsv(all_representative_rows, REPRESENTATIVE_FIELDS, outdir / "all_representative_transcripts.tsv")
    write_tsv(all_warning_rows, WARNING_FIELDS, outdir / "all_preprocess_warnings.tsv")
    return clean_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()

    manifest_rows = read_tsv(args.species_manifest)
    args.outdir.mkdir(parents=True, exist_ok=True)
    write_tsv(manifest_rows, MANIFEST_FIELDS, args.outdir / "species_manifest.raw.tsv")
    clean_rows = preprocess_manifest(manifest_rows, args.outdir)
    write_tsv(clean_rows, MANIFEST_FIELDS, args.outdir / "species_manifest.clean.tsv")
    print(f"Preprocessed {len(clean_rows)} species into {args.outdir}")


if __name__ == "__main__":
    main()
