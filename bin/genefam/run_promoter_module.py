#!/usr/bin/env python3
"""Run 10_promoter: promoter extraction, PlantCARE submission files, and cis-element status."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


PROMOTER_FIELDS = ["species_id", "gene_id", "seqid", "start", "end", "strand", "length", "clipped"]
STATUS_FIELDS = ["status", "promoter_count", "cis_input", "note"]
SPLIT_FIELDS = ["part", "path", "record_count"]


def load_project_config(path: Path | None) -> dict:
    if path is None:
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML is required to read project.yaml")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Project config must be a mapping: {path}")
    return data


def config_path(value: str | Path | None, config_dir: Path) -> Path | None:
    if value is None or value == "":
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return config_dir / path


def read_tsv(path: Path | None) -> list[dict[str, str]]:
    if path is None or not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def clean_id(value: str) -> str:
    return value.strip().split()[0].split("|", 1)[0] if value else ""


def parse_attributes(value: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for item in value.split(";"):
        if "=" not in item:
            continue
        key, raw = item.split("=", 1)
        attrs[key] = raw
    return attrs


def aliases(attrs: dict[str, str]) -> set[str]:
    raw = {clean_id(attrs.get(key, "")) for key in ("ID", "Name", "gene_id", "locus", "locus_tag")}
    out: set[str] = set()
    for value in raw:
        if not value:
            continue
        out.add(value)
        if ".v" in value:
            out.add(value.split(".v", 1)[0])
        if "." in value and value.upper().startswith("AT"):
            out.add(value.rsplit(".", 1)[0])
        if "." in value and value.startswith("LOC_"):
            out.add(value.rsplit(".", 1)[0])
    return out


def family_ids_by_species(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        species_id = row.get("species_id", "").strip()
        gene_id = row.get("gene_id", "").strip()
        if species_id and gene_id:
            grouped[species_id].add(gene_id)
    return grouped


def selected_species_order(config: dict, manifest_rows: list[dict[str, str]], grouped: dict[str, set[str]]) -> list[str]:
    include = config.get("species", {}).get("include") or []
    order = [str(item) for item in include] if include else [row["species_id"] for row in manifest_rows if row.get("species_id")]
    return [species_id for species_id in order if species_id in grouped]


def manifest_path_value(row: dict[str, str], *keys: str) -> Path:
    for key in keys:
        value = row.get(key, "")
        if value:
            return Path(value)
    return Path("")


def read_genome(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current = ""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            if text.startswith(">"):
                current = clean_id(text[1:])
                records.setdefault(current, [])
            elif current:
                records[current].append(text.upper())
    return {key: "".join(parts) for key, parts in records.items()}


def reverse_complement(sequence: str) -> str:
    table = str.maketrans("ACGTRYKMSWBDHVNacgtrykmswbdhvn", "TGCAYRMKSWVHDBNtgcayrmkswvhdbn")
    return sequence.translate(table)[::-1]


def gene_rows(gff3: Path, gene_ids: set[str]) -> list[dict[str, str]]:
    selected: dict[str, dict[str, str]] = {}
    with gff3.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            row_aliases = aliases(parse_attributes(fields[8]))
            for gene_id in sorted(gene_ids & row_aliases):
                selected[gene_id] = {"gene_id": gene_id, "seqid": fields[0], "start": int(fields[3]), "end": int(fields[4]), "strand": fields[6]}
    return [selected[gene_id] for gene_id in sorted(selected)]


def promoter_interval(row: dict[str, str], upstream_bp: int, chrom_length: int) -> tuple[int, int, bool]:
    if row["strand"] == "-":
        start = int(row["end"])
        end = min(int(row["end"]) + upstream_bp, chrom_length)
        return start, end, end - start < upstream_bp
    start = max(int(row["start"]) - upstream_bp - 1, 0)
    end = int(row["start"]) - 1
    return start, end, start == 0 and end - start < upstream_bp


def wrap_sequence(sequence: str) -> str:
    return "\n".join(sequence[index : index + 60] for index in range(0, len(sequence), 60))


def split_fasta(records: list[tuple[str, str]], outdir: Path, family_name: str, records_per_file: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not records:
        return rows
    records_per_file = max(records_per_file, 1)
    for part_index, start in enumerate(range(0, len(records), records_per_file), start=1):
        part_records = records[start : start + records_per_file]
        part_path = outdir / f"{family_name}_promoters.part{part_index:03d}.fa"
        with part_path.open("w", encoding="utf-8") as handle:
            for header, sequence in part_records:
                handle.write(f">{header}\n{wrap_sequence(sequence)}\n")
        rows.append({"part": f"{part_index:03d}", "path": str(part_path), "record_count": str(len(part_records))})
    return rows


def write_report(outdir: Path, promoter_count: int, cis_status: str, split_count: int) -> None:
    text = [
        "# 10_promoter Summary",
        "",
        "## Methods",
        "",
        "This module follows the Reference Step10 promoter workflow: extract upstream promoter regions from genome FASTA and GFF3 coordinates, prepare PlantCARE submission FASTA files, and integrate cis-element tables when available.",
        "",
        "## Results",
        "",
        f"- Promoter sequences: {promoter_count}",
        f"- PlantCARE submission parts: {split_count}",
        f"- Cis-element status: `{cis_status}`",
        "- Promoter BED: `tables/promoters.bed`",
        "- Promoter FASTA: `sequences/promoters.fa`",
        "- PlantCARE files: `plantcare_submission/`",
        "",
    ]
    (outdir / "report").mkdir(parents=True, exist_ok=True)
    (outdir / "report/promoter_summary.md").write_text("\n".join(text), encoding="utf-8")


def run_promoter_module(config_path_value: Path | None = None, outdir_override: Path | None = None) -> Path:
    config = load_project_config(config_path_value)
    config_dir = config_path_value.parent if config_path_value else Path.cwd()
    project_outdir = config_path(config.get("project", {}).get("outdir", "results"), config_dir) or Path("results")
    outdir = outdir_override or (project_outdir / "10_promoter")
    for subdir in ["inputs", "tables", "sequences", "plantcare_submission", "plots", "report", "logs"]:
        (outdir / subdir).mkdir(parents=True, exist_ok=True)

    promoter_config = config.get("promoter", {})
    family_name = str(promoter_config.get("family_name", config.get("project", {}).get("name", "GeneFamily"))).replace("_2026", "")
    upstream_bp = int(promoter_config.get("upstream_bp", 2000))
    split_records = int(promoter_config.get("split_records", 100))
    cis_input = config_path(promoter_config.get("cis_elements"), config_dir)
    family_candidates_path = config_path(promoter_config.get("family_candidates", project_outdir / "04_identification/tables/family_candidates.tsv"), config_dir)
    manifest_path = config_path(promoter_config.get("species_manifest", project_outdir / "01_preprocess/species_clean_bank_manifest.tsv"), config_dir)
    family_candidates = read_tsv(family_candidates_path)
    manifest_rows = read_tsv(manifest_path)
    grouped = family_ids_by_species(family_candidates)
    species_order = selected_species_order(config, manifest_rows, grouped)
    manifest_by_species = {row["species_id"]: row for row in manifest_rows}

    promoter_rows: list[dict[str, str]] = []
    fasta_records: list[tuple[str, str]] = []
    for species_id in species_order:
        manifest_row = manifest_by_species[species_id]
        genome = read_genome(manifest_path_value(manifest_row, "genome"))
        genes = gene_rows(manifest_path_value(manifest_row, "gff3"), grouped[species_id])
        for gene in genes:
            chrom_seq = genome.get(gene["seqid"], "")
            if not chrom_seq:
                continue
            start, end, clipped = promoter_interval(gene, upstream_bp, len(chrom_seq))
            if end <= start:
                sequence = ""
            else:
                sequence = chrom_seq[start:end]
            if gene["strand"] == "-":
                sequence = reverse_complement(sequence)
            promoter_rows.append(
                {
                    "species_id": species_id,
                    "gene_id": gene["gene_id"],
                    "seqid": gene["seqid"],
                    "start": str(start),
                    "end": str(end),
                    "strand": gene["strand"],
                    "length": str(len(sequence)),
                    "clipped": str(clipped).lower(),
                }
            )
            fasta_records.append((f"{species_id}|{gene['gene_id']}", sequence))

    write_tsv(promoter_rows, outdir / "tables/promoters.bed", PROMOTER_FIELDS)
    (outdir / "inputs/original.ID.clean.out").write_text("\n".join(row["gene_id"] for row in promoter_rows) + "\n", encoding="utf-8")
    with (outdir / "sequences/promoters.fa").open("w", encoding="utf-8") as handle:
        for header, sequence in fasta_records:
            handle.write(f">{header}\n{wrap_sequence(sequence)}\n")
    split_rows = split_fasta(fasta_records, outdir / "plantcare_submission", family_name, split_records)
    write_tsv(split_rows, outdir / "plantcare_submission/plantcare_submission_manifest.tsv", SPLIT_FIELDS)

    if cis_input and cis_input.exists():
        cis_status = "available"
        note = "Cis-element input is available; Reference heatmap plotting can be run from normalized tables"
    else:
        cis_status = "missing_input"
        note = "PlantCARE cis-element table was not provided; promoter extraction completed"
    write_tsv([{"status": cis_status, "promoter_count": str(len(promoter_rows)), "cis_input": str(cis_input or ""), "note": note}], outdir / "logs/promoter_cis_status.tsv", STATUS_FIELDS)
    write_report(outdir, len(promoter_rows), cis_status, len(split_rows))
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--outdir", type=Path, default=None)
    args = parser.parse_args()
    run_promoter_module(config_path_value=args.config, outdir_override=args.outdir)


if __name__ == "__main__":
    main()
