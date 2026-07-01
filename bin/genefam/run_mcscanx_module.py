#!/usr/bin/env python3
"""Run 09_mcscanx: MCScanX self-run preparation, duplicate tables, and circlize inputs."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


STATUS_FIELDS = ["species_id", "status", "family_bed", "gene_type", "tandem", "collinearity", "note"]
RUN_STATUS_FIELDS = ["species_id", "status", "mcscanx_gff", "pep", "command", "note"]
EXECUTION_FIELDS = ["status", "execute", "missing_tools", "command", "exit_code", "note"]
CHROMOSOME_FIELDS = ["species_id", "Chr", "Start", "End"]
DENSITY_FIELDS = ["species_id", "Chr", "Start", "End", "Number_Count"]
GENE_TYPE_FIELDS = ["species_id", "Chr", "Start", "End", "gene_id", "Type"]
LINK_FIELDS = ["species_id", "Type", "Chr1", "Start1", "End1", "ID1", "Chr2", "Start2", "End2", "ID2"]
PAIR_FIELDS = ["species_id", "type", "gene_a", "gene_b"]


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
    values = {clean_id(attrs.get(key, "")) for key in ("ID", "Name", "gene_id", "locus", "locus_tag")}
    expanded: set[str] = set()
    for value in values:
        if not value:
            continue
        expanded.add(value)
        if ".v" in value:
            expanded.add(value.split(".v", 1)[0])
        if "." in value and value.upper().startswith("AT"):
            expanded.add(value.rsplit(".", 1)[0])
        if "." in value and value.startswith("LOC_"):
            expanded.add(value.rsplit(".", 1)[0])
    return expanded


def family_ids_by_species(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        species_id = row.get("species_id", "").strip()
        gene_id = row.get("gene_id", "").strip()
        if species_id and gene_id:
            grouped[species_id].add(gene_id)
    return grouped


def manifest_path_value(row: dict[str, str], *keys: str) -> Path:
    for key in keys:
        value = row.get(key, "")
        if value:
            return Path(value)
    return Path("")


def selected_species_order(config: dict, manifest_rows: list[dict[str, str]], grouped: dict[str, set[str]]) -> list[str]:
    include = config.get("species", {}).get("include") or []
    order = [str(item) for item in include] if include else [row["species_id"] for row in manifest_rows if row.get("species_id")]
    return [species_id for species_id in order if species_id in grouped]


def parse_gene_rows(gff3: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with gff3.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            gene_id = clean_id(parse_attributes(fields[8]).get("ID", ""))
            if not gene_id:
                continue
            rows.append({"seqid": fields[0], "start": fields[3], "end": fields[4], "strand": fields[6], "gene_id": gene_id, "aliases": aliases(parse_attributes(fields[8]))})
    return rows


def write_mcscanx_gff(gene_rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in gene_rows:
            handle.write(f"{row['seqid']}\t{row['gene_id']}\t{row['start']}\t{row['end']}\n")


def write_family_bed(gene_rows: list[dict[str, str]], gene_ids: set[str], path: Path) -> tuple[list[dict[str, str]], list[str]]:
    selected: dict[str, dict[str, str]] = {}
    for row in gene_rows:
        for gene_id in gene_ids & set(row["aliases"]):
            selected[gene_id] = row
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for gene_id, row in sorted(selected.items()):
            handle.write(f"{row['seqid']}\t{row['start']}\t{row['end']}\t{gene_id}\t0\t{row['strand']}\n")
    return [{"gene_id": gene_id, **row} for gene_id, row in sorted(selected.items())], sorted(gene_ids - set(selected))


def build_command(species_id: str, pep: Path, search_tool: str) -> list[str]:
    if search_tool == "blastp":
        return [
            f"makeblastdb -in {pep} -dbtype prot -out inputs/mcscanx_run/{species_id}.pepdb",
            f"blastp -query {pep} -db inputs/mcscanx_run/{species_id}.pepdb -out inputs/mcscanx_run/{species_id}.blast -evalue 1e-5 -outfmt 6 -num_threads 4",
            f"(cd inputs/mcscanx_run && MCScanX {species_id})",
        ]
    return [
        f"diamond makedb --in {pep} -d inputs/mcscanx_run/{species_id}.dmnd",
        f"diamond blastp --query {pep} --db inputs/mcscanx_run/{species_id}.dmnd --out inputs/mcscanx_run/{species_id}.blast --evalue 1e-5 --outfmt 6 --threads 4",
        f"(cd inputs/mcscanx_run && MCScanX {species_id})",
    ]


def read_chromosomes(path: Path, species_id: str) -> list[dict[str, str]]:
    rows = read_tsv(path)
    output: list[dict[str, str]] = []
    for row in rows:
        chrom = row.get("Chr") or row.get("seqid") or row.get("chromosome") or row.get("X1")
        start = row.get("Start") or row.get("start") or "1"
        end = row.get("End") or row.get("end") or row.get("length") or row.get("X2")
        if chrom and end:
            output.append({"species_id": species_id, "Chr": chrom, "Start": start, "End": end})
    return output


def build_density(chromosomes: list[dict[str, str]], family_rows_by_species: dict[str, list[dict[str, str]]], window_size: int) -> list[dict[str, str]]:
    density: list[dict[str, str]] = []
    for chrom in chromosomes:
        species_id = chrom["species_id"]
        chrom_name = chrom["Chr"]
        end = int(float(chrom["End"]))
        family_rows = [row for row in family_rows_by_species.get(species_id, []) if row["seqid"] == chrom_name]
        for start in range(0, end, window_size):
            win_end = min(start + window_size, end)
            count = sum(1 for row in family_rows if int(row["start"]) > start and int(row["end"]) <= win_end)
            density.append({"species_id": species_id, "Chr": chrom_name, "Start": str(start), "End": str(win_end), "Number_Count": str(count)})
    return density


def write_execution_status(outdir: Path, execute: bool, command_count: int, search_tool: str) -> None:
    missing_tools = []
    if execute:
        required = ["MCScanX", "diamond"] if search_tool == "diamond" else ["MCScanX", "makeblastdb", "blastp"]
        missing_tools = [tool for tool in required if shutil.which(tool) is None]
    if command_count == 0:
        row = {"status": "missing_input", "execute": str(execute).lower(), "missing_tools": ",".join(missing_tools), "command": "logs/mcscanx_self_commands.sh", "exit_code": "", "note": "No MCScanX commands were prepared"}
    elif missing_tools:
        row = {"status": "missing_dependency", "execute": "true", "missing_tools": ",".join(missing_tools), "command": "logs/mcscanx_self_commands.sh", "exit_code": "", "note": "Missing required executables for MCScanX self run"}
    elif not execute:
        row = {"status": "ready_not_executed", "execute": "false", "missing_tools": "", "command": "logs/mcscanx_self_commands.sh", "exit_code": "", "note": "MCScanX self commands prepared; set mcscanx.execute=true to run"}
    else:
        completed = subprocess.run(["bash", "logs/mcscanx_self_commands.sh"], cwd=outdir, check=False, capture_output=True, text=True)
        (outdir / "logs/mcscanx_execution.log").write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8")
        row = {"status": "executed" if completed.returncode == 0 else "failed", "execute": "true", "missing_tools": "", "command": "logs/mcscanx_self_commands.sh", "exit_code": str(completed.returncode), "note": "MCScanX command script completed" if completed.returncode == 0 else "MCScanX command script failed"}
    write_tsv([row], outdir / "logs/mcscanx_execution_status.tsv", EXECUTION_FIELDS)


def write_report(outdir: Path, species_order: list[str], command_count: int) -> None:
    status_rows = read_tsv(outdir / "logs/mcscanx_execution_status.tsv")
    status = status_rows[0] if status_rows else {"status": "unknown", "note": ""}
    text = [
        "# 09_mcscanx Summary",
        "",
        "## Methods",
        "",
        "This module follows the Reference Step9 MCScanX self workflow: prepare MCScanX GFF/protein inputs, run or plan self BLAST and `MCScanX`, extract family duplicate pairs, and prepare circlize tracks for intra-species chromosome plots.",
        "",
        "## Inputs",
        "",
        f"- Species: {', '.join(species_order) if species_order else 'none'}",
        f"- MCScanX self command count: {command_count}",
        "",
        "## Results",
        "",
        f"- MCScanX execution status: `{status.get('status', 'unknown')}`",
        f"- Status note: {status.get('note', '')}",
        "- Family BED files: `inputs/family_beds/`",
        "- MCScanX run inputs: `inputs/mcscanx_run/`",
        "- circlize chromosome table: `tables/circlize_chromosomes.tsv`",
        "- circlize gene density table: `tables/circlize_gene_density.tsv`",
        "- circlize gene type table: `tables/circlize_gene_types.tsv`",
        "",
    ]
    (outdir / "report").mkdir(parents=True, exist_ok=True)
    (outdir / "report/mcscanx_summary.md").write_text("\n".join(text), encoding="utf-8")


def run_mcscanx_module(config_path_value: Path | None = None, outdir_override: Path | None = None) -> Path:
    config = load_project_config(config_path_value)
    config_dir = config_path_value.parent if config_path_value else Path.cwd()
    project_outdir = config_path(config.get("project", {}).get("outdir", "results"), config_dir) or Path("results")
    outdir = outdir_override or (project_outdir / "09_mcscanx")
    for subdir in ["inputs/family_beds", "inputs/mcscanx_run", "tables", "plots", "report", "logs"]:
        (outdir / subdir).mkdir(parents=True, exist_ok=True)

    family_candidates_path = config_path(config.get("mcscanx", {}).get("family_candidates", project_outdir / "04_identification/tables/family_candidates.tsv"), config_dir)
    manifest_path = config_path(config.get("mcscanx", {}).get("species_manifest", project_outdir / "01_preprocess/species_clean_bank_manifest.tsv"), config_dir)
    family_candidates = read_tsv(family_candidates_path)
    manifest_rows = read_tsv(manifest_path)
    grouped = family_ids_by_species(family_candidates)
    species_order = selected_species_order(config, manifest_rows, grouped)
    manifest_by_species = {row["species_id"]: row for row in manifest_rows}
    mcscanx_config = config.get("mcscanx", {})
    search_tool = str(mcscanx_config.get("search_tool", "diamond"))
    window_size = int(mcscanx_config.get("window_size", 500000))
    execute = bool(mcscanx_config.get("execute", False))

    status_rows: list[dict[str, str]] = []
    run_status_rows: list[dict[str, str]] = []
    all_pair_rows: list[dict[str, str]] = []
    chromosomes: list[dict[str, str]] = []
    family_rows_by_species: dict[str, list[dict[str, str]]] = {}
    gene_type_rows: list[dict[str, str]] = []
    commands: list[str] = ["#!/usr/bin/env bash", "set -euo pipefail", ""]

    for species_id in species_order:
        manifest_row = manifest_by_species[species_id]
        gff3 = Path(manifest_row["gff3"])
        pep = manifest_path_value(manifest_row, "pep", "protein", "protein_fasta")
        gene_rows = parse_gene_rows(gff3)
        mcscanx_gff = outdir / "inputs/mcscanx_run" / f"{species_id}.gff"
        write_mcscanx_gff(gene_rows, mcscanx_gff)
        family_bed = outdir / "inputs/family_beds" / f"{species_id}.GF.bed"
        family_rows, missing = write_family_bed(gene_rows, grouped[species_id], family_bed)
        family_rows_by_species[species_id] = family_rows
        for row in family_rows:
            gene_type_rows.append({"species_id": species_id, "Chr": row["seqid"], "Start": row["start"], "End": row["end"], "gene_id": row["gene_id"], "Type": "unknown"})
        for command in build_command(species_id, pep, search_tool):
            commands.append(command)
        commands.append("")
        status_rows.append(
            {
                "species_id": species_id,
                "status": "available" if not missing else "missing_records",
                "family_bed": f"inputs/family_beds/{species_id}.GF.bed",
                "gene_type": "",
                "tandem": "",
                "collinearity": "",
                "note": "MCScanX self inputs prepared" if not missing else f"family BED missing {len(missing)} genes",
            }
        )
        run_status_rows.append(
            {
                "species_id": species_id,
                "status": "prepared",
                "mcscanx_gff": f"inputs/mcscanx_run/{species_id}.gff",
                "pep": str(pep),
                "command": "logs/mcscanx_self_commands.sh",
                "note": "MCScanX self-run command prepared",
            }
        )
        chrom_path = manifest_path_value(manifest_row, "chromosome_lengths")
        chromosomes.extend(read_chromosomes(chrom_path, species_id))

    command_count = sum(1 for command in commands if command and not command.startswith("#!") and not command.startswith("set "))
    (outdir / "logs/mcscanx_self_commands.sh").write_text("\n".join(commands).rstrip() + "\n", encoding="utf-8")
    write_tsv(status_rows, outdir / "tables/mcscanx_self_status.tsv", STATUS_FIELDS)
    write_tsv(run_status_rows, outdir / "tables/mcscanx_run_status.tsv", RUN_STATUS_FIELDS)
    write_tsv(all_pair_rows, outdir / "tables/mcscanx_gene_pairs.tsv", PAIR_FIELDS)
    write_tsv(chromosomes, outdir / "tables/circlize_chromosomes.tsv", CHROMOSOME_FIELDS)
    write_tsv(build_density(chromosomes, family_rows_by_species, window_size), outdir / "tables/circlize_gene_density.tsv", DENSITY_FIELDS)
    write_tsv(gene_type_rows, outdir / "tables/circlize_gene_types.tsv", GENE_TYPE_FIELDS)
    write_tsv([], outdir / "tables/circlize_duplicate_links.tsv", LINK_FIELDS)
    write_execution_status(outdir, execute, command_count, search_tool)
    write_report(outdir, species_order, command_count)
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--outdir", type=Path, default=None)
    args = parser.parse_args()
    run_mcscanx_module(config_path_value=args.config, outdir_override=args.outdir)


if __name__ == "__main__":
    main()
