#!/usr/bin/env python3
"""Run 05_genefamily_info from final family members and clean GFF3 files."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

try:
    import openpyxl
except ImportError:  # pragma: no cover
    openpyxl = None

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_gene_family_info import build_gene_family_info_tables, read_fasta, write_tables
from bin.genefam.preprocess_species import clean_header_id, fallback_gene_id


GENE_INFO_FIELDS = [
    "Species",
    "ID",
    "Chr",
    "Start",
    "End",
    "Strand",
    "Length",
    "MW_kDa",
    "hydrophobicity",
    "pI",
]
GENE_INFO_STAT_FIELDS = [
    "Species",
    "count",
    "mean_length",
    "min_length",
    "max_length",
    "mean_MW_kDa",
    "min_MW_kDa",
    "max_MW_kDa",
    "mean_hydrophobicity",
    "min_hydrophobicity",
    "max_hydrophobicity",
    "mean_pI",
    "min_pI",
    "max_pI",
]
BED_FIELDS = ["Chr", "Start", "End", "ID", "Info", "Strand", "Species"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], fieldnames: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(rows: list[dict[str, str]], fieldnames: list[str], path: Path) -> None:
    if openpyxl is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(fieldnames)
    for row in rows:
        sheet.append([row.get(field, "") for field in fieldnames])
    workbook.save(path)


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


def resolve_args(args: argparse.Namespace) -> dict:
    config = load_project_config(args.config)
    config_dir = args.config.parent if args.config else Path.cwd()
    project_config = config.get("project", {}) or {}
    database_config = config.get("database", {}) or {}
    module_config = config.get("genefamily_info", {}) or {}
    project_outdir = config_path(project_config.get("outdir"), config_dir) or Path("results")
    clean_bank = args.clean_bank or config_path(database_config.get("species_clean_bank"), config_dir)
    if clean_bank is None:
        clean_bank = project_outdir / "01_preprocess/species_clean_bank"
    members_fasta = args.members_fasta or config_path(module_config.get("members_fasta"), config_dir) or project_outdir / "04_identification/fasta/identify.ID.fa"
    should_plot = args.plot or bool(module_config.get("plot", False))
    if args.skip_plot:
        should_plot = False
    return {
        "clean_bank": clean_bank,
        "members_fasta": members_fasta,
        "outdir": args.outdir or config_path(module_config.get("outdir"), config_dir) or project_outdir / "05_genefamily_info",
        "r_bin": args.r_bin or module_config.get("r_bin", "/usr/local/bin/R"),
        "plot": should_plot,
    }


def parse_gff3_attributes(value: str) -> dict[str, str]:
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


def gene_aliases(gene_id: str, name: str = "") -> set[str]:
    aliases: set[str] = set()
    for value in [gene_id, name]:
        clean = clean_header_id(value)
        if not clean:
            continue
        aliases.add(clean)
        fallback, _source = fallback_gene_id(clean)
        aliases.add(fallback)
    return aliases


def parse_gene_bed(species_id: str, gff3: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with gff3.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9 or parts[2].casefold() != "gene":
                continue
            attributes = parse_gff3_attributes(parts[8])
            gene_id = clean_header_id(attributes.get("ID", ""))
            if not gene_id:
                continue
            rows.append(
                {
                    "Chr": parts[0],
                    "Start": parts[3],
                    "End": parts[4],
                    "ID": gene_id,
                    "Info": attributes.get("Name", gene_id),
                    "Strand": parts[6],
                    "Species": species_id,
                }
            )
    return rows


def discover_clean_gff3(clean_bank: Path) -> dict[str, Path]:
    if not clean_bank.exists():
        raise ValueError(f"Clean bank does not exist: {clean_bank}")
    rows: dict[str, Path] = {}
    for species_dir in sorted(path for path in clean_bank.iterdir() if path.is_dir()):
        matches = sorted((species_dir / "clean").glob("*.gff3"))
        if matches:
            rows[species_dir.name] = matches[0]
    if not rows:
        raise ValueError(f"No clean GFF3 files found in {clean_bank}")
    return rows


def protein_property_map(fasta_records: list[tuple[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    tables = build_gene_family_info_tables([], fasta_records)
    return {(row["species_id"], row["gene_id"]): row for row in tables.protein_properties}


def family_counts_from_records(clean_bank: Path, fasta_records: list[tuple[str, str]]) -> list[dict[str, str]]:
    counts: dict[str, int] = defaultdict(int)
    for header, _sequence in fasta_records:
        species_id, _sep, _gene_id = header.partition("|")
        if species_id:
            counts[species_id] += 1
    species_ids = sorted(path.name for path in clean_bank.iterdir() if path.is_dir())
    return [
        {
            "species_id": species_id,
            "member_count": str(counts.get(species_id, 0)),
            "hmmer_count": "",
            "diamond_count": "",
            "intersection_count": "",
        }
        for species_id in species_ids
    ]


def build_gene_information(members_fasta: Path, clean_bank: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[tuple[str, str]]]:
    fasta_records = read_fasta(members_fasta)
    properties = protein_property_map(fasta_records)
    gff_paths = discover_clean_gff3(clean_bank)
    all_bed: list[dict[str, str]] = []
    bed_by_alias: dict[tuple[str, str], dict[str, str]] = {}
    for species_id, gff3 in gff_paths.items():
        for row in parse_gene_bed(species_id, gff3):
            all_bed.append(row)
            for alias in gene_aliases(row["ID"], row["Info"]):
                bed_by_alias[(species_id, alias)] = row

    info_rows: list[dict[str, str]] = []
    for header, _sequence in fasta_records:
        species_id, sep, gene_id = header.partition("|")
        if not sep:
            species_id = ""
            gene_id = header
        bed = bed_by_alias.get((species_id, gene_id), {})
        prop = properties.get((species_id, gene_id), {})
        info_rows.append(
            {
                "Species": species_id,
                "ID": gene_id,
                "Chr": bed.get("Chr", ""),
                "Start": bed.get("Start", ""),
                "End": bed.get("End", ""),
                "Strand": bed.get("Strand", ""),
                "Length": prop.get("protein_length", ""),
                "MW_kDa": prop.get("molecular_weight_kda", ""),
                "hydrophobicity": prop.get("gravy", ""),
                "pI": prop.get("isoelectric_point", ""),
            }
        )
    return info_rows, summarize_gene_information(info_rows), all_bed, fasta_records


def _float_values(rows: list[dict[str, str]], field: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        try:
            values.append(float(row.get(field, "")))
        except ValueError:
            continue
    return values


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def summarize_gene_information(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["Species"]].append(row)
    summaries: list[dict[str, str]] = []
    for species_id, species_rows in sorted(grouped.items()):
        summary = {"Species": species_id, "count": str(len(species_rows))}
        for source_field, prefix in [
            ("Length", "length"),
            ("MW_kDa", "MW_kDa"),
            ("hydrophobicity", "hydrophobicity"),
            ("pI", "pI"),
        ]:
            values = _float_values(species_rows, source_field)
            summary[f"mean_{prefix}"] = _fmt(sum(values) / len(values)) if values else ""
            summary[f"min_{prefix}"] = _fmt(min(values)) if values else ""
            summary[f"max_{prefix}"] = _fmt(max(values)) if values else ""
        summaries.append(summary)
    return summaries


def run_plot(r_bin: str, outdir: Path, tables_dir: Path) -> None:
    script = REPO_ROOT / "scripts/plot_gene_family_info.R"
    subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            str(script),
            "--args",
            str(tables_dir / "gene_family_copy_number.tsv"),
            str(tables_dir / "gene_family_copy_number_summary.tsv"),
            str(tables_dir / "gene_family_protein_properties.tsv"),
            str(tables_dir / "gene_family_species_order.tsv"),
            str(tables_dir / "gene_family_copy_number_expansion.tsv"),
            str(tables_dir / "gene_family_pangenome_summary.tsv"),
            str(outdir / "plots"),
        ],
        check=True,
    )


def run_module(**kwargs) -> Path:
    outdir: Path = kwargs["outdir"]
    tables_dir = outdir / "tables"
    info_rows, stat_rows, bed_rows, fasta_records = build_gene_information(kwargs["members_fasta"], kwargs["clean_bank"])
    write_tsv(info_rows, GENE_INFO_FIELDS, tables_dir / "Gene_Information.tsv")
    write_tsv(stat_rows, GENE_INFO_STAT_FIELDS, tables_dir / "Gene_Information_stat.tsv")
    write_tsv(bed_rows, BED_FIELDS, tables_dir / "all_species_gene.bed")
    legacy_bed = tables_dir / "species_10.bed"
    if legacy_bed.exists():
        legacy_bed.unlink()
    write_xlsx(info_rows, GENE_INFO_FIELDS, tables_dir / "Gene_Information.xlsx")
    write_xlsx(stat_rows, GENE_INFO_STAT_FIELDS, tables_dir / "Gene_Information_stat.xlsx")

    family_counts = family_counts_from_records(kwargs["clean_bank"], fasta_records)
    family_tables = build_gene_family_info_tables(family_counts, fasta_records)
    write_tables(family_tables, tables_dir)
    if kwargs["plot"]:
        run_plot(kwargs["r_bin"], outdir, tables_dir)
    report = [
        "# 05_genefamily_info Summary",
        "",
        f"- Family members: {len(info_rows)}",
        f"- Species with members: {sum(1 for row in stat_rows if int(row['count']) > 0)}",
        f"- GFF gene BED rows: {len(bed_rows)}",
        f"- Plot generated: {str(bool(kwargs['plot'])).lower()}",
    ]
    (outdir / "report").mkdir(parents=True, exist_ok=True)
    (outdir / "report/genefamily_info_summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None, type=Path)
    parser.add_argument("--clean-bank", default=None, type=Path)
    parser.add_argument("--members-fasta", default=None, type=Path)
    parser.add_argument("--outdir", default=None, type=Path)
    parser.add_argument("--r-bin", default=None)
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--skip-plot", action="store_true")
    args = parser.parse_args()
    try:
        outdir = run_module(**resolve_args(args))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"05_genefamily_info completed at {outdir.resolve()}")


if __name__ == "__main__":
    main()
