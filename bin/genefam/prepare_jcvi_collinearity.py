#!/usr/bin/env python3
"""Prepare JCVI collinearity inputs from cleaned species manifests."""

from __future__ import annotations

import argparse
import csv
import shutil
from collections import defaultdict
from pathlib import Path


BED_FIELDS = ["seqid", "start", "end", "gene_id", "score", "strand"]
PAIR_FIELDS = ["pair_id", "query_species", "subject_species", "query_bed", "subject_bed", "query_pep", "subject_pep"]
STATUS_FIELDS = ["check", "status", "detail"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_bed(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        for row in rows:
            handle.write(
                "\t".join(
                    [
                        row["seqid"],
                        str(max(int(row["start"]) - 1, 0)),
                        row["end"],
                        row["gene_id"],
                        row["score"],
                        row["strand"],
                    ]
                )
                + "\n"
            )


def parse_attributes(value: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for item in value.split(";"):
        if not item:
            continue
        if "=" in item:
            key, raw_value = item.split("=", 1)
            attributes[key] = raw_value
    return attributes


def clean_id(value: str) -> str:
    return value.strip().split()[0].split("|", 1)[0] if value else ""


def gene_aliases(attributes: dict[str, str]) -> set[str]:
    aliases = {clean_id(attributes.get(key, "")) for key in ("ID", "Name", "gene_id", "locus", "locus_tag")}
    cleaned: set[str] = set()
    for alias in aliases:
        if not alias:
            continue
        cleaned.add(alias)
        if ".v" in alias:
            cleaned.add(alias.split(".v", 1)[0])
        if "." in alias and alias.upper().startswith("AT"):
            cleaned.add(alias.rsplit(".", 1)[0])
    return cleaned


def gene_ids_by_species(family_candidates: list[dict[str, str]]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for row in family_candidates:
        species_id = row.get("species_id", "").strip()
        gene_id = row.get("gene_id", "").strip()
        if species_id and gene_id:
            grouped[species_id].add(gene_id)
    return grouped


def extract_bed_rows(gff3: Path, species_id: str, gene_ids: set[str]) -> tuple[list[dict[str, str]], list[str]]:
    rows_by_gene: dict[str, dict[str, str]] = {}
    with Path(gff3).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            aliases = gene_aliases(parse_attributes(fields[8]))
            for gene_id in sorted(gene_ids & aliases):
                rows_by_gene[gene_id] = {
                    "seqid": fields[0],
                    "start": fields[3],
                    "end": fields[4],
                    "gene_id": gene_id,
                    "score": "0",
                    "strand": fields[6],
                }
    missing = sorted(gene_ids - set(rows_by_gene))
    return [rows_by_gene[gene_id] for gene_id in sorted(rows_by_gene)], missing


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current_id = ""
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current_id = clean_id(line[1:])
                records.setdefault(current_id, [])
            elif current_id:
                records[current_id].append(line)
    return {record_id: "".join(parts) for record_id, parts in records.items()}


def write_selected_fasta(records: dict[str, str], gene_ids: set[str], out_path: Path) -> tuple[int, list[str]]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    missing = sorted(gene_ids - set(records))
    written = 0
    with out_path.open("w", encoding="utf-8") as handle:
        for gene_id in sorted(gene_ids & set(records)):
            sequence = records[gene_id]
            handle.write(f">{gene_id}\n")
            for start in range(0, len(sequence), 60):
                handle.write(sequence[start : start + 60] + "\n")
            written += 1
    return written, missing


def species_order_from_manifest(manifest_rows: list[dict[str, str]]) -> list[str]:
    return [row["species_id"] for row in manifest_rows if row.get("species_id")]


def adjacent_pairs(species_order: list[str]) -> list[tuple[str, str]]:
    return list(zip(species_order, species_order[1:]))


def build_seqids(bed_rows_by_species: dict[str, list[dict[str, str]]], species_order: list[str]) -> list[str]:
    lines: list[str] = []
    for species_id in species_order:
        seqids = []
        seen = set()
        for row in bed_rows_by_species.get(species_id, []):
            seqid = row["seqid"]
            if seqid not in seen:
                seen.add(seqid)
                seqids.append(seqid)
        lines.append(",".join(seqids))
    return lines


def build_layout(pair_rows: list[dict[str, str]], species_order: list[str]) -> list[str]:
    lines = ["# y, xstart, xend, rotation, color, label, va, bed"]
    count = max(len(species_order), 1)
    for index, species_id in enumerate(species_order):
        y = 0.95 - index * (0.9 / max(count - 1, 1))
        va = "top" if index == 0 else ""
        lines.append(f"{y:.2f}, .15, .85, 0, #4C78A8, {species_id}, {va}, {species_id}.bed")
    lines.append("# edges")
    for index, row in enumerate(pair_rows):
        lines.append(f"e, {index}, {index + 1}, {row['pair_id']}.anchors.simple")
    return lines


def prepare_jcvi_inputs(
    *,
    family_candidates: list[dict[str, str]],
    species_manifest: list[dict[str, str]],
    outdir: Path,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    beds_dir = outdir / "beds"
    peptides_dir = outdir / "peptides"
    commands_dir = outdir / "commands"
    beds_dir.mkdir(parents=True, exist_ok=True)
    peptides_dir.mkdir(parents=True, exist_ok=True)
    commands_dir.mkdir(parents=True, exist_ok=True)

    grouped_gene_ids = gene_ids_by_species(family_candidates)
    manifest_by_species = {row["species_id"]: row for row in species_manifest}
    species_order = [species_id for species_id in species_order_from_manifest(species_manifest) if species_id in grouped_gene_ids]

    status_rows: list[dict[str, str]] = []
    bed_rows_by_species: dict[str, list[dict[str, str]]] = {}
    for species_id in species_order:
        manifest_row = manifest_by_species[species_id]
        gene_ids = grouped_gene_ids[species_id]
        bed_rows, missing_bed = extract_bed_rows(Path(manifest_row["gff3"]), species_id, gene_ids)
        bed_rows_by_species[species_id] = bed_rows
        write_bed(bed_rows, beds_dir / f"{species_id}.bed")
        write_bed(bed_rows, outdir / f"{species_id}.bed")
        records = read_fasta(Path(manifest_row["pep"]))
        written_pep, missing_pep = write_selected_fasta(records, gene_ids, peptides_dir / f"{species_id}.pep")
        write_selected_fasta(records, gene_ids, outdir / f"{species_id}.pep")
        status_rows.extend(
            [
                {
                    "check": f"{species_id}.bed_genes",
                    "status": "ok" if not missing_bed else "missing_records",
                    "detail": f"written={len(bed_rows)} missing={len(missing_bed)}",
                },
                {
                    "check": f"{species_id}.pep_genes",
                    "status": "ok" if not missing_pep else "missing_records",
                    "detail": f"written={written_pep} missing={len(missing_pep)}",
                },
            ]
        )

    pair_rows: list[dict[str, str]] = []
    command_lines: list[str] = []
    for query_species, subject_species in adjacent_pairs(species_order):
        pair_id = f"{query_species}.{subject_species}"
        pair_rows.append(
            {
                "pair_id": pair_id,
                "query_species": query_species,
                "subject_species": subject_species,
                "query_bed": f"beds/{query_species}.bed",
                "subject_bed": f"beds/{subject_species}.bed",
                "query_pep": f"peptides/{query_species}.pep",
                "subject_pep": f"peptides/{subject_species}.pep",
            }
        )
        command_lines.append(f"python -m jcvi.compara.catalog ortholog --dbtype prot --notex --no_strip_names {query_species} {subject_species}")
        command_lines.append(f"python -m jcvi.compara.synteny screen --minspan=30 --simple {pair_id}.anchors {pair_id}.anchors.simple")
    command_lines.append("python -m jcvi.graphics.karyotype seqids layout --notex --figsize=14x12 --chrstyle=roundrect")

    write_tsv(pair_rows, outdir / "jcvi_pair_manifest.tsv", PAIR_FIELDS)
    write_tsv(status_rows, outdir / "jcvi_input_status.tsv", STATUS_FIELDS)
    (commands_dir / "jcvi_commands.sh").write_text("\n".join(command_lines) + "\n", encoding="utf-8")
    (outdir / "seqids").write_text("\n".join(build_seqids(bed_rows_by_species, species_order)) + "\n", encoding="utf-8")
    (outdir / "layout").write_text("\n".join(build_layout(pair_rows, species_order)) + "\n", encoding="utf-8")
    return {
        "pair_manifest": outdir / "jcvi_pair_manifest.tsv",
        "status": outdir / "jcvi_input_status.tsv",
        "commands": commands_dir / "jcvi_commands.sh",
        "seqids": outdir / "seqids",
        "layout": outdir / "layout",
    }


def write_dependency_status(out_path: Path, jcvi_executable: str | None = None) -> None:
    status = "available" if shutil.which(jcvi_executable or "python") else "unknown"
    detail = "jcvi is executed as python -m jcvi; verify the active environment contains the jcvi Python package"
    rows = [{"check": "jcvi_python_module", "status": status, "detail": detail}]
    write_tsv(rows, out_path, STATUS_FIELDS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    prepare_jcvi_inputs(
        family_candidates=read_tsv(args.family_candidates),
        species_manifest=read_tsv(args.species_manifest),
        outdir=args.outdir,
    )


if __name__ == "__main__":
    main()
