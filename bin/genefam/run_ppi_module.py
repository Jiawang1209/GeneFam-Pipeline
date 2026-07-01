#!/usr/bin/env python3
"""Run 11_ppi: AraNet-based PPI transfer tables and ggNetView plotting."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_ppi_tables import (  # noqa: E402
    EDGE_FIELDS,
    HUB_FIELDS,
    METRIC_FIELDS,
    NODE_ANNOTATION_FIELDS,
    NODE_FIELDS,
    SPECIES_PPI_ANNOTATION_FIELDS,
    build_ppi_tables,
    write_tsv,
)


STATUS_FIELDS = ["status", "edge_count", "node_count", "plot_status", "note"]


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


def write_status(row: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=STATUS_FIELDS, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerow(row)


def clean_gene_id(value: str) -> str:
    gene_id = value.strip().split()[0].split("|")[0]
    if "." in gene_id and gene_id.upper().startswith("AT"):
        gene_id = gene_id.rsplit(".", 1)[0]
    return gene_id


def family_ids_by_species(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        species_id = row.get("species_id", "").strip()
        gene_id = clean_gene_id(row.get("gene_id", ""))
        if species_id and gene_id:
            grouped[species_id].append(gene_id)
    return grouped


def manifest_path_value(row: dict[str, str], *keys: str) -> Path:
    for key in keys:
        value = row.get(key, "")
        if value:
            return Path(value)
    return Path("")


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current = ""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            if text.startswith(">"):
                current = clean_gene_id(text[1:])
                records.setdefault(current, [])
            elif current:
                records[current].append(text)
    return {key: "".join(parts) for key, parts in records.items()}


def write_family_fasta(records: dict[str, str], gene_ids: list[str], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with path.open("w", encoding="utf-8") as handle:
        for gene_id in sorted(set(gene_ids)):
            sequence = records.get(gene_id)
            if not sequence:
                continue
            handle.write(f">{gene_id}\n{sequence}\n")
            written += 1
    return written


def read_aranet(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for fields in reader:
            if len(fields) < 2:
                continue
            if fields[0].lower() in {"source", "gene1", "from"}:
                continue
            rows.append({"source": clean_gene_id(fields[0]), "target": clean_gene_id(fields[1]), "weight": fields[2] if len(fields) > 2 else "1"})
    return rows


def format_weight(value: str) -> str:
    try:
        return f"{float(value):.4f}"
    except ValueError:
        return "1.0000"


def direct_arabidopsis_edges(aranet_rows: list[dict[str, str]], family_genes: set[str], min_weight: float) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in aranet_rows:
        try:
            weight = float(row["weight"])
        except ValueError:
            weight = 1.0
        if weight < min_weight:
            continue
        source = row["source"]
        target = row["target"]
        if source not in family_genes or target not in family_genes or source == target:
            continue
        a, b = sorted([source, target])
        if (a, b) in seen:
            continue
        seen.add((a, b))
        edges.append({"source": a, "target": b, "weight": format_weight(row["weight"]), "species": "Arabidopsis_thaliana"})
    return edges


def metric_rows(metrics: dict[str, int | str]) -> list[dict[str, str]]:
    descriptions = {
        "aranet_edges_read": "AraNet reference Arabidopsis network edges read from the configured file",
        "direct_arabidopsis_edges": "Edges retained where both AraNet endpoints are Arabidopsis family members",
        "run_blast": "Whether reciprocal homology BLAST transfer was requested for non-Arabidopsis species",
    }
    return [{"metric": key, "value": str(value), "description": descriptions.get(key, "")} for key, value in metrics.items()]


def run_plot(r_bin: str, edge_path: Path, node_path: Path, plot_dir: Path, status_path: Path) -> str:
    completed = subprocess.run(
        [r_bin, "--vanilla", "--slave", "-f", str(REPO_ROOT / "scripts/plot_ppi_ggnetview_reference.R"), "--args", str(edge_path), str(node_path), str(plot_dir), str(status_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    (status_path.parent / "ppi_plot.stdout.log").write_text(completed.stdout or "", encoding="utf-8")
    (status_path.parent / "ppi_plot.stderr.log").write_text(completed.stderr or "", encoding="utf-8")
    return "ready" if completed.returncode == 0 else "failed"


def write_report(outdir: Path, edge_count: int, node_count: int, status: str, run_blast: bool) -> None:
    text = [
        "# 11_ppi Summary",
        "",
        "## Methods",
        "",
        "This module follows the Reference Step11 PPI workflow: use AraNet as the Arabidopsis reference network, prepare family peptide sets, transfer or subset network evidence through family membership/homology evidence, and use ggNetView for the primary PPI visualization.",
        "",
        "## Results",
        "",
        f"- AraNet reciprocal BLAST transfer requested: `{str(run_blast).lower()}`",
        f"- PPI edges: {edge_count}",
        f"- PPI nodes: {node_count}",
        f"- Plot status: `{status}`",
        "- ggNetView plot: `plots/ppi_ggnetview.pdf` when plotting is available.",
        "",
    ]
    (outdir / "report").mkdir(parents=True, exist_ok=True)
    (outdir / "report/ppi_summary.md").write_text("\n".join(text), encoding="utf-8")


def run_ppi_module(config_path_value: Path | None = None, outdir_override: Path | None = None, skip_plot: bool = False) -> Path:
    config = load_project_config(config_path_value)
    config_dir = config_path_value.parent if config_path_value else Path.cwd()
    project_outdir = config_path(config.get("project", {}).get("outdir", "results"), config_dir) or Path("results")
    outdir = outdir_override or (project_outdir / "11_ppi")
    for subdir in ["inputs", "tables", "plots", "report", "logs"]:
        (outdir / subdir).mkdir(parents=True, exist_ok=True)

    ppi_config = config.get("ppi", {})
    aranet_path = config_path(ppi_config.get("aranet", "data/config/AraNet.txt"), config_dir)
    family_candidates_path = config_path(ppi_config.get("family_candidates", project_outdir / "04_identification/tables/family_candidates.tsv"), config_dir)
    manifest_path = config_path(ppi_config.get("species_manifest", project_outdir / "01_preprocess/species_clean_bank_manifest.tsv"), config_dir)
    run_blast = bool(ppi_config.get("run_blast", False))
    min_weight = float(ppi_config.get("min_weight", 4))
    r_bin = str(ppi_config.get("r_bin", "/usr/local/bin/R"))

    family_candidates = read_tsv(family_candidates_path)
    manifest_rows = read_tsv(manifest_path)
    manifest_by_species = {row["species_id"]: row for row in manifest_rows}
    grouped = family_ids_by_species(family_candidates)
    for species_id, gene_ids in sorted(grouped.items()):
        manifest_row = manifest_by_species.get(species_id)
        if not manifest_row:
            continue
        records = read_fasta(manifest_path_value(manifest_row, "pep", "protein", "protein_fasta"))
        write_family_fasta(records, gene_ids, outdir / "inputs" / f"{species_id}.GF.pep.fasta")

    aranet_rows = read_aranet(aranet_path) if aranet_path and aranet_path.exists() else []
    ath_family = set(grouped.get("Arabidopsis_thaliana", []))
    edges = direct_arabidopsis_edges(aranet_rows, ath_family, min_weight)
    node_annotations = [{"node": gene_id, "species": "Arabidopsis_thaliana", "type": "Whirly", "domain": "PF08536"} for gene_id in sorted(ath_family)]
    outputs = build_ppi_tables(edges=edges, node_annotations=node_annotations, top_n=int(ppi_config.get("top_n", 20)))

    write_tsv(outputs["edges"], outdir / "tables/ppi_edges.tsv", EDGE_FIELDS)
    write_tsv(outputs["nodes"], outdir / "tables/ppi_nodes.tsv", NODE_FIELDS)
    write_tsv(outputs["node_annotation"], outdir / "tables/node_annotation.tsv", NODE_ANNOTATION_FIELDS)
    write_tsv(outputs["species_ppi_annotation"], outdir / "tables/species_ppi_annotation.tsv", SPECIES_PPI_ANNOTATION_FIELDS)
    write_tsv(outputs["hubs"], outdir / "tables/ppi_hubs.tsv", HUB_FIELDS)
    write_tsv(outputs["input_evidence"] + metric_rows({"aranet_edges_read": len(aranet_rows), "direct_arabidopsis_edges": len(edges), "run_blast": str(run_blast).lower()}), outdir / "tables/ppi_transfer_evidence.tsv", METRIC_FIELDS)
    write_tsv(outputs["network_qc"], outdir / "tables/ppi_network_qc.tsv", METRIC_FIELDS)

    plot_status = "skipped"
    if not skip_plot:
        plot_status = run_plot(r_bin, outdir / "tables/ppi_edges.tsv", outdir / "tables/ppi_nodes.tsv", outdir / "plots", outdir / "logs/ppi_ggnetview_status.tsv")
    status = "table_ready_plot_skipped" if skip_plot else f"table_ready_plot_{plot_status}"
    write_status({"status": status, "edge_count": str(len(outputs["edges"])), "node_count": str(len(outputs["nodes"])), "plot_status": plot_status, "note": "PPI tables generated from AraNet reference evidence"}, outdir / "logs/ppi_status.tsv")
    write_report(outdir, len(outputs["edges"]), len(outputs["nodes"]), plot_status, run_blast)
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--outdir", type=Path, default=None)
    parser.add_argument("--skip-plot", action="store_true")
    args = parser.parse_args()
    run_ppi_module(config_path_value=args.config, outdir_override=args.outdir, skip_plot=args.skip_plot)


if __name__ == "__main__":
    main()
