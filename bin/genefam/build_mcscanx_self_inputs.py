#!/usr/bin/env python3
"""Prepare Reference Step9 MCScanX self-duplication inputs and status tables."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


BED_FIELDS = ["seqid", "start", "end", "gene_id", "score", "strand"]
STATUS_FIELDS = ["species_id", "status", "family_bed", "gene_type", "tandem", "collinearity", "note"]
PAIR_FIELDS = ["species_id", "type", "gene_a", "gene_b"]
ID_FIELDS = ["species_id", "gene_id"]
RUN_STATUS_FIELDS = ["species_id", "status", "mcscanx_gff", "pep", "command", "note"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def parse_attributes(value: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for item in value.split(";"):
        if "=" not in item:
            continue
        key, raw = item.split("=", 1)
        attrs[key] = raw
    return attrs


def clean_id(value: str) -> str:
    return value.strip().split()[0].split("|", 1)[0] if value else ""


def aliases(attrs: dict[str, str]) -> set[str]:
    values = {clean_id(attrs.get(key, "")) for key in ("ID", "Name", "gene_id", "locus", "locus_tag")}
    expanded = set()
    for value in values:
        if not value:
            continue
        expanded.add(value)
        if ".v" in value:
            expanded.add(value.split(".v", 1)[0])
        if value.upper().startswith("AT") and "." in value:
            expanded.add(value.rsplit(".", 1)[0])
    return expanded


def family_gene_ids(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        species_id = row.get("species_id", "").strip()
        gene_id = row.get("gene_id", "").strip()
        if species_id and gene_id:
            grouped[species_id].add(gene_id)
    return grouped


def extract_family_bed(gff3: Path, gene_ids: set[str]) -> tuple[list[dict[str, str]], list[str]]:
    found: dict[str, dict[str, str]] = {}
    with Path(gff3).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            for gene_id in sorted(gene_ids & aliases(parse_attributes(fields[8]))):
                found[gene_id] = {
                    "seqid": fields[0],
                    "start": fields[3],
                    "end": fields[4],
                    "gene_id": gene_id,
                    "score": "0",
                    "strand": fields[6],
                }
    return [found[gene_id] for gene_id in sorted(found)], sorted(gene_ids - set(found))


def extract_mcscanx_gff_rows(gff3: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with Path(gff3).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            gene_id = clean_id(parse_attributes(fields[8]).get("ID", ""))
            if not gene_id:
                continue
            rows.append({"gene_id": gene_id, "seqid": fields[0], "start": fields[3], "end": fields[4]})
    return rows


def write_mcscanx_gff(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(f"{row['seqid']}\t{row['gene_id']}\t{row['start']}\t{row['end']}\n")


def build_mcscanx_self_command(species_id: str, pep: str, mcscanx_gff: str, search_tool: str = "diamond") -> list[str]:
    if search_tool == "diamond":
        return [
            f"diamond makedb --in {pep} -d mcscanx_run/{species_id}.dmnd",
            (
                f"diamond blastp --query {pep} --db mcscanx_run/{species_id}.dmnd "
                f"--out mcscanx_run/{species_id}.blast --evalue 1e-5 --outfmt 6 --threads 4"
            ),
            f"(cd mcscanx_run && MCScanX {species_id})",
        ]
    return [
        f"makeblastdb -in {pep} -dbtype prot -out mcscanx_run/{species_id}.pepdb",
        (
            f"blastp -query {pep} -db mcscanx_run/{species_id}.pepdb "
            f"-out mcscanx_run/{species_id}.blast -evalue 1e-5 -outfmt 6 -num_threads 4"
        ),
        f"(cd mcscanx_run && MCScanX {species_id})",
    ]


def _candidate_paths(root: Path, species_id: str, suffixes: list[str]) -> list[Path]:
    candidates = []
    for suffix in suffixes:
        candidates.extend([root / f"{species_id}{suffix}", root / species_id / f"{species_id}{suffix}"])
    return candidates


def find_first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def find_mcscanx_inputs(root: Path | None, species_id: str) -> tuple[Path | None, Path | None, Path | None]:
    if root is None:
        return None, None, None
    gene_type = find_first_existing(_candidate_paths(root, species_id, [".gene_type", ".gene_type.tsv"]))
    tandem = find_first_existing(_candidate_paths(root, species_id, [".tandem2", ".tandem", ".tandem.tsv"]))
    collinearity = find_first_existing(_candidate_paths(root, species_id, [".collinearity2", ".collinearity", ".collinearity.tsv"]))
    return gene_type, tandem, collinearity


def read_pairs(path: Path | None, pair_type: str, family_ids: set[str]) -> list[dict[str, str]]:
    if path is None:
        return []
    rows = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.strip().replace(",", "\t").split()
            if len(fields) < 2:
                continue
            if any(field.endswith(":") for field in fields):
                colon_index = next(index for index, field in enumerate(fields) if field.endswith(":"))
                if len(fields) <= colon_index + 2:
                    continue
                gene_a, gene_b = clean_id(fields[colon_index + 1]), clean_id(fields[colon_index + 2])
            else:
                gene_a, gene_b = clean_id(fields[0]), clean_id(fields[1])
            if gene_a in family_ids or gene_b in family_ids:
                rows.append({"type": pair_type, "gene_a": gene_a, "gene_b": gene_b})
    return rows


def build_mcscanx_self_inputs(
    *,
    family_candidates: list[dict[str, str]],
    species_manifest: list[dict[str, str]],
    outdir: Path,
    mcscanx_self_dir: Path | None = None,
    search_tool: str = "diamond",
) -> dict[str, Path]:
    if search_tool not in {"diamond", "blastp"}:
        raise ValueError("search_tool must be 'diamond' or 'blastp'")
    outdir.mkdir(parents=True, exist_ok=True)
    family_bed_dir = outdir / "family_beds"
    pairs_dir = outdir / "species_pairs"
    mcscanx_run_dir = outdir / "mcscanx_run"
    commands_dir = outdir / "commands"
    family_bed_dir.mkdir(parents=True, exist_ok=True)
    pairs_dir.mkdir(parents=True, exist_ok=True)
    mcscanx_run_dir.mkdir(parents=True, exist_ok=True)
    commands_dir.mkdir(parents=True, exist_ok=True)

    grouped = family_gene_ids(family_candidates)
    manifest_by_species = {row["species_id"]: row for row in species_manifest}
    status_rows: list[dict[str, str]] = []
    run_status_rows: list[dict[str, str]] = []
    command_lines: list[str] = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    all_pair_rows: list[dict[str, str]] = []
    all_id_rows: list[dict[str, str]] = []

    for species_id in sorted(grouped):
        manifest_row = manifest_by_species.get(species_id)
        if not manifest_row:
            continue
        pep_path = manifest_row.get("pep", "")
        run_gff_path = mcscanx_run_dir / f"{species_id}.gff"
        write_mcscanx_gff(extract_mcscanx_gff_rows(Path(manifest_row["gff3"])), run_gff_path)
        if pep_path:
            command_lines.extend(build_mcscanx_self_command(species_id, pep_path, str(run_gff_path.relative_to(outdir)), search_tool=search_tool))
            command_lines.append("")
            run_status_rows.append(
                {
                    "species_id": species_id,
                    "status": "prepared",
                    "mcscanx_gff": str(run_gff_path.relative_to(outdir)),
                    "pep": pep_path,
                    "command": "commands/mcscanx_self_commands.sh",
                    "note": "MCScanX self-run inputs prepared; execute command script when blastp and MCScanX are available",
                }
            )
        else:
            run_status_rows.append(
                {
                    "species_id": species_id,
                    "status": "missing_input",
                    "mcscanx_gff": str(run_gff_path.relative_to(outdir)),
                    "pep": "",
                    "command": "commands/mcscanx_self_commands.sh",
                    "note": "Missing peptide FASTA for MCScanX self run",
                }
            )
        bed_rows, missing_bed = extract_family_bed(Path(manifest_row["gff3"]), grouped[species_id])
        bed_path = family_bed_dir / f"{species_id}.GF.bed"
        write_tsv(bed_rows, bed_path, BED_FIELDS)

        gene_type, tandem, collinearity = find_mcscanx_inputs(mcscanx_self_dir, species_id)
        pair_rows = []
        pair_rows.extend(read_pairs(tandem, "tandem", grouped[species_id]))
        pair_rows.extend(read_pairs(collinearity, "WGD", grouped[species_id]))
        species_pair_rows = [{"species_id": species_id, **row} for row in pair_rows]
        pair_path = pairs_dir / f"{species_id}.gene_pairs.csv"
        id_path = pairs_dir / f"{species_id}.gene_pairs.ID.csv"
        write_tsv(species_pair_rows, pair_path, PAIR_FIELDS)
        pair_ids = sorted({row["gene_a"] for row in pair_rows} | {row["gene_b"] for row in pair_rows})
        id_rows = [{"species_id": species_id, "gene_id": gene_id} for gene_id in pair_ids]
        write_tsv(id_rows, id_path, ID_FIELDS)
        all_pair_rows.extend(species_pair_rows)
        all_id_rows.extend(id_rows)

        has_inputs = bool(tandem or collinearity or pair_rows)
        status = "available" if has_inputs else "missing_input"
        note = "ok" if has_inputs else "MCScanX self .tandem/.collinearity outputs are required"
        if missing_bed:
            status = "missing_records"
            note = f"family BED missing {len(missing_bed)} genes"
        status_rows.append(
            {
                "species_id": species_id,
                "status": status,
                "family_bed": str(bed_path.relative_to(outdir)),
                "gene_type": str(gene_type.relative_to(mcscanx_self_dir)) if gene_type and mcscanx_self_dir else "",
                "tandem": str(tandem.relative_to(mcscanx_self_dir)) if tandem and mcscanx_self_dir else "",
                "collinearity": str(collinearity.relative_to(mcscanx_self_dir)) if collinearity and mcscanx_self_dir else "",
                "note": note,
            }
        )

    write_tsv(status_rows, outdir / "mcscanx_self_status.tsv", STATUS_FIELDS)
    write_tsv(run_status_rows, outdir / "mcscanx_run_status.tsv", RUN_STATUS_FIELDS)
    (commands_dir / "mcscanx_self_commands.sh").write_text("\n".join(command_lines).rstrip() + "\n", encoding="utf-8")
    write_tsv(all_pair_rows, outdir / "mcscanx_gene_pairs.tsv", PAIR_FIELDS)
    write_tsv(all_id_rows, outdir / "mcscanx_gene_pair_ids.tsv", ID_FIELDS)
    return {
        "status": outdir / "mcscanx_self_status.tsv",
        "run_status": outdir / "mcscanx_run_status.tsv",
        "pairs": outdir / "mcscanx_gene_pairs.tsv",
        "ids": outdir / "mcscanx_gene_pair_ids.tsv",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--mcscanx-self-dir", default=None, type=Path)
    parser.add_argument("--search-tool", choices=["diamond", "blastp"], default="diamond")
    args = parser.parse_args()
    build_mcscanx_self_inputs(
        family_candidates=read_tsv(args.family_candidates),
        species_manifest=read_tsv(args.species_manifest),
        outdir=args.outdir,
        mcscanx_self_dir=args.mcscanx_self_dir,
        search_tool=args.search_tool,
    )


if __name__ == "__main__":
    main()
