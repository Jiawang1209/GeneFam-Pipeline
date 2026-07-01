#!/usr/bin/env python3
"""Run 08_jcvi: Reference-style JCVI collinearity preparation and optional execution."""

from __future__ import annotations

import argparse
import csv
import shlex
import subprocess
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


PAIR_FIELDS = ["pair_id", "query_species", "subject_species", "query_bed", "subject_bed", "query_pep", "subject_pep"]
STATUS_FIELDS = ["check", "status", "detail"]
COMMAND_STATUS_FIELDS = ["command_index", "command", "status", "exit_code", "note"]
RUN_STATUS_FIELDS = ["status", "command_count", "succeeded_count", "failed_count", "note"]


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


def read_tsv(path: Path) -> list[dict[str, str]]:
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
    attributes: dict[str, str] = {}
    for item in value.split(";"):
        if "=" not in item:
            continue
        key, raw = item.split("=", 1)
        attributes[key] = raw
    return attributes


def gene_aliases(attributes: dict[str, str]) -> set[str]:
    raw_aliases = {clean_id(attributes.get(key, "")) for key in ("ID", "Name", "gene_id", "locus", "locus_tag")}
    aliases: set[str] = set()
    for alias in raw_aliases:
        if not alias:
            continue
        aliases.add(alias)
        if ".v" in alias:
            aliases.add(alias.split(".v", 1)[0])
        if "." in alias and alias.upper().startswith("AT"):
            aliases.add(alias.rsplit(".", 1)[0])
        if "." in alias and alias.startswith("LOC_"):
            aliases.add(alias.rsplit(".", 1)[0])
    return aliases


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current_id = ""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            if text.startswith(">"):
                current_id = clean_id(text[1:])
                records.setdefault(current_id, [])
            elif current_id:
                records[current_id].append(text)
    return {record_id: "".join(parts) for record_id, parts in records.items()}


def write_fasta(records: dict[str, str], gene_ids: set[str], path: Path) -> tuple[int, list[str]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    missing = sorted(gene_ids - set(records))
    written = 0
    with path.open("w", encoding="utf-8") as handle:
        for gene_id in sorted(gene_ids & set(records)):
            handle.write(f">{gene_id}\n")
            sequence = records[gene_id]
            for start in range(0, len(sequence), 60):
                handle.write(sequence[start : start + 60] + "\n")
            written += 1
    return written, missing


def family_ids_by_species(rows: list[dict[str, str]]) -> dict[str, set[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        species_id = row.get("species_id", "").strip()
        gene_id = row.get("gene_id", "").strip()
        if species_id and gene_id:
            grouped[species_id].add(gene_id)
    return grouped


def extract_bed_rows(gff3: Path, gene_ids: set[str]) -> tuple[list[dict[str, str]], list[str]]:
    by_gene: dict[str, dict[str, str]] = {}
    with gff3.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            aliases = gene_aliases(parse_attributes(fields[8]))
            for gene_id in sorted(gene_ids & aliases):
                by_gene[gene_id] = {
                    "seqid": fields[0],
                    "start": str(max(int(fields[3]) - 1, 0)),
                    "end": fields[4],
                    "gene_id": gene_id,
                    "score": "0",
                    "strand": fields[6],
                }
    return [by_gene[gene_id] for gene_id in sorted(by_gene)], sorted(gene_ids - set(by_gene))


def write_bed(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write("\t".join([row["seqid"], row["start"], row["end"], row["gene_id"], row["score"], row["strand"]]) + "\n")


def selected_species_order(config: dict, manifest_rows: list[dict[str, str]], grouped_ids: dict[str, set[str]]) -> list[str]:
    include = config.get("species", {}).get("include") or []
    if include:
        base_order = [str(species_id) for species_id in include]
    else:
        base_order = [row["species_id"] for row in manifest_rows if row.get("species_id")]
    return [species_id for species_id in base_order if species_id in grouped_ids]


def manifest_path_value(row: dict[str, str], *keys: str) -> Path:
    for key in keys:
        value = row.get(key, "")
        if value:
            return Path(value)
    return Path("")


def adjacent_pairs(species_order: list[str], configured_pairs: list | None = None) -> list[tuple[str, str]]:
    if configured_pairs:
        pairs: list[tuple[str, str]] = []
        for item in configured_pairs:
            if isinstance(item, dict):
                query = item.get("query") or item.get("query_species") or item.get("a")
                subject = item.get("subject") or item.get("subject_species") or item.get("b")
                if query and subject:
                    pairs.append((str(query), str(subject)))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                pairs.append((str(item[0]), str(item[1])))
        if pairs:
            return pairs
    return list(zip(species_order, species_order[1:]))


def build_seqids(bed_rows_by_species: dict[str, list[dict[str, str]]], species_order: list[str]) -> list[str]:
    lines: list[str] = []
    for species_id in species_order:
        seen: set[str] = set()
        seqids: list[str] = []
        for row in bed_rows_by_species.get(species_id, []):
            if row["seqid"] not in seen:
                seen.add(row["seqid"])
                seqids.append(row["seqid"])
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


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


def jcvi_importable(python_bin: str) -> bool:
    completed = subprocess.run(
        [python_bin, "-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('jcvi') else 1)"],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def write_run_status(path: Path, status: str, command_count: int, succeeded: int, failed: int, note: str) -> None:
    write_tsv(
        [{"status": status, "command_count": str(command_count), "succeeded_count": str(succeeded), "failed_count": str(failed), "note": note}],
        path,
        RUN_STATUS_FIELDS,
    )


def maybe_run_commands(commands: list[str], *, outdir: Path, python_bin: str, run: bool) -> None:
    command_rows: list[dict[str, str]] = []
    command_status = outdir / "logs/jcvi_command_status.tsv"
    run_status = outdir / "logs/jcvi_run_status.tsv"
    if not run:
        for index, command in enumerate(commands, start=1):
            command_rows.append({"command_index": str(index), "command": command, "status": "planned", "exit_code": "", "note": "run disabled"})
        write_tsv(command_rows, command_status, COMMAND_STATUS_FIELDS)
        write_run_status(run_status, "planned", len(commands), 0, 0, "JCVI commands were prepared but not executed")
        return

    if not jcvi_importable(python_bin):
        for index, command in enumerate(commands, start=1):
            command_rows.append({"command_index": str(index), "command": command, "status": "not_run", "exit_code": "", "note": "missing_dependency"})
        write_tsv(command_rows, command_status, COMMAND_STATUS_FIELDS)
        write_run_status(run_status, "missing_dependency", len(commands), 0, 0, f"JCVI Python module is not importable with {python_bin}")
        return

    succeeded = 0
    failed = 0
    for index, command in enumerate(commands, start=1):
        rewritten = command.replace("python -m jcvi.", f"{python_bin} -m jcvi.")
        completed = subprocess.run(rewritten, shell=True, cwd=outdir / "inputs", check=False, capture_output=True, text=True)
        if completed.returncode == 0:
            status = "available"
            note = "ok"
            succeeded += 1
        else:
            status = "failed"
            note = (completed.stderr or completed.stdout or f"exit {completed.returncode}").strip().replace("\n", " ")[:500]
            failed += 1
        command_rows.append({"command_index": str(index), "command": rewritten, "status": status, "exit_code": str(completed.returncode), "note": note})
    write_tsv(command_rows, command_status, COMMAND_STATUS_FIELDS)
    overall = "available" if succeeded and failed == 0 else "partial" if succeeded else "failed"
    write_run_status(run_status, overall, len(commands), succeeded, failed, "ok" if failed == 0 else "Some JCVI commands failed")


def write_report(outdir: Path, species_order: list[str], pair_rows: list[dict[str, str]], commands: list[str], run_status_path: Path) -> None:
    run_status = read_tsv(run_status_path)[0] if run_status_path.exists() else {"status": "unknown", "note": ""}
    pair_names = ", ".join(row["pair_id"] for row in pair_rows) if pair_rows else "none"
    text = [
        "# 08_jcvi Summary",
        "",
        "## Methods",
        "",
        "This module follows the Reference Step8 JCVI collinearity workflow: prepare per-species BED and peptide files, run `jcvi.compara.catalog ortholog`, screen anchors with `jcvi.compara.synteny screen`, and render karyotype with `jcvi.graphics.karyotype` when JCVI is available.",
        "",
        "## Inputs",
        "",
        f"- Species: {', '.join(species_order) if species_order else 'none'}",
        f"- Pair chain: {pair_names}",
        "",
        "## Commands",
        "",
    ]
    text.extend(f"- `{command}`" for command in commands)
    text.extend(
        [
            "",
            "## Results",
            "",
            f"- JCVI run status: `{run_status.get('status', 'unknown')}`",
            f"- Status note: {run_status.get('note', '')}",
            "- Pair manifest: `tables/jcvi_pair_manifest.tsv`",
            "- Input QC: `tables/jcvi_input_status.tsv`",
            "- Commands: `logs/jcvi_commands.sh`",
            "- Ka/Ks: not calculated in this module unless a prepared Ka/Ks table is provided; downstream Ka/Ks integration will read anchor-derived gene pairs when available.",
            "",
        ]
    )
    (outdir / "report").mkdir(parents=True, exist_ok=True)
    (outdir / "report/jcvi_summary.md").write_text("\n".join(text), encoding="utf-8")


def run_jcvi_module(config_path_value: Path | None = None, outdir_override: Path | None = None) -> Path:
    config = load_project_config(config_path_value)
    config_dir = config_path_value.parent if config_path_value else Path.cwd()
    project_outdir = config_path(config.get("project", {}).get("outdir", "results"), config_dir) or Path("results")
    outdir = outdir_override or (project_outdir / "08_jcvi")
    for subdir in ["inputs/beds", "inputs/peptides", "tables", "plots", "report", "logs"]:
        (outdir / subdir).mkdir(parents=True, exist_ok=True)

    family_candidates_path = config_path(
        config.get("jcvi", {}).get("family_candidates", project_outdir / "04_identification/tables/family_candidates.tsv"),
        config_dir,
    )
    manifest_path = config_path(
        config.get("jcvi", {}).get("species_manifest", project_outdir / "01_preprocess/species_clean_bank_manifest.tsv"),
        config_dir,
    )
    if family_candidates_path is None or not family_candidates_path.exists():
        raise FileNotFoundError(f"Missing family candidates: {family_candidates_path}")
    if manifest_path is None or not manifest_path.exists():
        raise FileNotFoundError(f"Missing species manifest: {manifest_path}")

    family_candidates = read_tsv(family_candidates_path)
    manifest_rows = read_tsv(manifest_path)
    manifest_by_species = {row["species_id"]: row for row in manifest_rows}
    grouped_ids = family_ids_by_species(family_candidates)
    species_order = selected_species_order(config, manifest_rows, grouped_ids)

    input_status: list[dict[str, str]] = []
    bed_rows_by_species: dict[str, list[dict[str, str]]] = {}
    for species_id in species_order:
        manifest_row = manifest_by_species.get(species_id, {})
        gene_ids = grouped_ids[species_id]
        gff3 = Path(manifest_row.get("gff3", ""))
        pep = manifest_path_value(manifest_row, "pep", "protein", "protein_fasta")
        bed_rows, missing_bed = extract_bed_rows(gff3, gene_ids)
        bed_rows_by_species[species_id] = bed_rows
        write_bed(bed_rows, outdir / "inputs/beds" / f"{species_id}.bed")
        records = read_fasta(pep)
        written_pep, missing_pep = write_fasta(records, gene_ids, outdir / "inputs/peptides" / f"{species_id}.pep")
        input_status.extend(
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

    jcvi_config = config.get("jcvi", {})
    minspan = int(jcvi_config.get("minspan", 30))
    figsize = str(jcvi_config.get("figsize", "14x12"))
    chrstyle = str(jcvi_config.get("chrstyle", "roundrect"))
    pair_rows: list[dict[str, str]] = []
    commands: list[str] = []
    for query, subject in adjacent_pairs(species_order, jcvi_config.get("pairs")):
        pair_id = f"{query}.{subject}"
        pair_rows.append(
            {
                "pair_id": pair_id,
                "query_species": query,
                "subject_species": subject,
                "query_bed": f"inputs/beds/{query}.bed",
                "subject_bed": f"inputs/beds/{subject}.bed",
                "query_pep": f"inputs/peptides/{query}.pep",
                "subject_pep": f"inputs/peptides/{subject}.pep",
            }
        )
        commands.append(shell_join(["python", "-m", "jcvi.compara.catalog", "ortholog", "--dbtype", "prot", "--notex", "--no_strip_names", query, subject]))
        commands.append(shell_join(["python", "-m", "jcvi.compara.synteny", "screen", f"--minspan={minspan}", "--simple", f"{pair_id}.anchors", f"{pair_id}.anchors.simple"]))
    commands.append(shell_join(["python", "-m", "jcvi.graphics.karyotype", "seqids", "layout", "--notex", f"--figsize={figsize}", f"--chrstyle={chrstyle}"]))

    write_tsv(pair_rows, outdir / "tables/jcvi_pair_manifest.tsv", PAIR_FIELDS)
    write_tsv(input_status, outdir / "tables/jcvi_input_status.tsv", STATUS_FIELDS)
    (outdir / "inputs/seqids").write_text("\n".join(build_seqids(bed_rows_by_species, species_order)) + "\n", encoding="utf-8")
    (outdir / "inputs/layout").write_text("\n".join(build_layout(pair_rows, species_order)) + "\n", encoding="utf-8")
    (outdir / "logs/jcvi_commands.sh").write_text("#!/usr/bin/env bash\nset -euo pipefail\ncd inputs\n" + "\n".join(commands) + "\n", encoding="utf-8")
    maybe_run_commands(commands, outdir=outdir, python_bin=str(jcvi_config.get("python_bin", "python")), run=bool(jcvi_config.get("run", False)))
    write_report(outdir, species_order, pair_rows, commands, outdir / "logs/jcvi_run_status.tsv")
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--outdir", type=Path, default=None)
    args = parser.parse_args()
    run_jcvi_module(config_path_value=args.config, outdir_override=args.outdir)


if __name__ == "__main__":
    main()
