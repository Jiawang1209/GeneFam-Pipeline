#!/usr/bin/env python3
"""Build structured figure-reading notes for completion reports."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = [
    "figure_key",
    "title",
    "input_data",
    "what_figure_shows",
    "key_observations",
    "biological_interpretation",
    "qc_warnings",
    "output_path",
]


TEMPLATES = {
    "family": (
        "Family copy number and member count overview",
        "Family member count table",
        "Per-species gene family member counts and copy-number differences.",
        "Inspect the highest and lowest member counts and whether related species share similar copy-number patterns.",
        "Species with larger counts may indicate lineage-specific expansion or contraction relative to the sampled set.",
    ),
    "mcscanx": (
        "MCScanX syntenic relationship overview",
        "MCScanX syntenic pair table and chromosome coordinates",
        "syntenic block links among family members and their chromosome positions.",
        "Inspect dense link clusters, skipped links, and chromosome-specific concentration of duplicated genes.",
        "Conserved syntenic block structure supports segmental/WGD-derived relationships when paired with Ks evidence.",
    ),
    "kaks": (
        "Ka/Ks and Ks distribution overview",
        "Normalized Ka/Ks pair table",
        "Ks distribution, Ka/Ks ratios, and WGD layer support for duplicated gene pairs.",
        "Inspect Ks peaks, ratios above or below 1, and whether configured WGD layers are well separated.",
        "Ks-supported layers provide observational evidence; gamma/beta/alpha/theta labels remain configured interpretations.",
    ),
    "expression": (
        "Expression heatmap",
        "Family expression matrix and sample metadata",
        "Expression variation among family members across tissues, treatments, or time points.",
        "Inspect co-expression clusters, treatment-specific responses, and low-expression genes.",
        "Clustered expression patterns can suggest functional divergence or conserved regulatory responses.",
    ),
    "promoter": (
        "Promoter cis-element summary",
        "Promoter BED/FASTA and cis-element annotation table",
        "Promoter lengths and cis-element category abundance across genes or species.",
        "Inspect enriched stress, hormone, light, and development-related element classes.",
        "Cis-element differences suggest candidate regulatory divergence that should be validated experimentally.",
    ),
    "ppi": (
        "PPI network generated with ggNetView",
        "PPI edge table and node annotation table",
        "Protein interaction network structure, node groups, and edge weights.",
        "Inspect hub genes, dense modules, isolated nodes, and whether hubs overlap key family members.",
        "Hub genes may represent candidate regulatory or functional interaction centers.",
    ),
    "feature": (
        "Feature summary overview",
        "Domain, motif, gene-structure, synteny, and promoter summary tables",
        "Aggregated feature counts and distributions for large gene families.",
        "Inspect outlier genes, dominant feature categories, and modules with missing evidence.",
        "Feature summaries help prioritize interpretable subsets when full per-gene figures are too dense.",
    ),
}


def _template_key(plot_key: str, path: str) -> str:
    value = f"{plot_key} {path}".lower()
    for key in ["mcscanx", "kaks", "expression", "promoter", "ppi", "feature", "family"]:
        if key in value or (key == "kaks" and "ks_" in value):
            return key
    return "feature"


def _qc_warning(path: str) -> str:
    if "smoke" in path or "fixtures" in path or "demo" in path:
        return "This figure is generated from smoke/demo data; do not treat it as a biological conclusion."
    return "Review input completeness, skipped rows, and module QC tables before biological interpretation."


def build_figure_interpretations(plots: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for plot in plots:
        key = plot.get("plot_key") or plot.get("key") or Path(plot.get("path", "")).stem
        path = plot.get("path", "")
        template = TEMPLATES[_template_key(key, path)]
        rows.append(
            {
                "figure_key": key,
                "title": template[0],
                "input_data": template[1],
                "what_figure_shows": template[2],
                "key_observations": template[3],
                "biological_interpretation": template[4],
                "qc_warnings": _qc_warning(path),
                "output_path": path,
            }
        )
    return rows


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    lines = ["# Figure Result Interpretations", ""]
    for row in rows:
        lines.extend(
            [
                f"## {row['figure_key']}: {row['title']}",
                "",
                f"- Input data: {row['input_data']}",
                f"- What the figure shows: {row['what_figure_shows']}",
                f"- Key observations: {row['key_observations']}",
                f"- Biological interpretation: {row['biological_interpretation']}",
                f"- QC warnings / limitations: {row['qc_warnings']}",
                f"- Output path: `{row['output_path']}`",
                "",
            ]
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-manifest", required=True, type=Path)
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    rows = build_figure_interpretations(read_tsv(args.plot_manifest))
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)


if __name__ == "__main__":
    main()
