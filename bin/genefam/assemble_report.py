#!/usr/bin/env python3
"""Assemble report-index and analysis tables into a final Markdown report."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def _section_or_empty(title: str, headers: list[str], rows: list[list[str]], empty_message: str) -> list[str]:
    lines = [f"## {title}", ""]
    if rows:
        lines.extend(_markdown_table(headers, rows))
    else:
        lines.append(empty_message)
    lines.append("")
    return lines


def assemble_report(
    project_name: str,
    gene_family: str,
    report_index_rows: list[dict[str, str]],
    wgd_event_evidence: list[dict[str, str]] | None = None,
    family_event_retention: list[dict[str, str]] | None = None,
    retention_enrichment: list[dict[str, str]] | None = None,
    plot_manifest: list[dict[str, str]] | None = None,
) -> str:
    lines = [
        "# GeneFam-Pipeline Final Report",
        "",
        f"Project: {project_name}",
        f"Gene family: {gene_family}",
        "",
    ]

    lines.extend(
        _section_or_empty(
            "Output Availability",
            ["key", "status", "path", "description"],
            [
                [row["key"], row["status"], row.get("path", ""), row.get("description", "")]
                for row in report_index_rows
            ],
            "No report index rows were provided.",
        )
    )
    lines.extend(
        _section_or_empty(
            "WGD Event Evidence",
            ["wgd_layer", "event_name", "pair_count", "ks_median", "interpretation_status", "species_scope"],
            [
                [
                    row["wgd_layer"],
                    row.get("event_name", "unannotated"),
                    row.get("pair_count", ""),
                    row.get("ks_median", ""),
                    row.get("interpretation_status", ""),
                    row.get("species_scope", ""),
                ]
                for row in (wgd_event_evidence or [])
            ],
            "No WGD event evidence table was available for this run.",
        )
    )
    lines.extend(
        _section_or_empty(
            "Family Event Retention",
            ["wgd_layer", "event_name", "duplicate_type", "family_gene_count", "pair_evidence_count", "gene_ids"],
            [
                [
                    row["wgd_layer"],
                    row.get("event_name", "unannotated"),
                    row["duplicate_type"],
                    row.get("family_gene_count", ""),
                    row.get("pair_evidence_count", ""),
                    row.get("gene_ids", ""),
                ]
                for row in (family_event_retention or [])
            ],
            "No family WGD event membership summary was available for this run.",
        )
    )
    lines.extend(
        _section_or_empty(
            "Duplicate-Type Retention Enrichment",
            ["duplicate_type", "family_count", "family_total", "fold_enrichment", "p_value"],
            [
                [
                    row["duplicate_type"],
                    row.get("family_count", ""),
                    row.get("family_total", ""),
                    row.get("fold_enrichment", ""),
                    row.get("p_value", ""),
                ]
                for row in (retention_enrichment or [])
            ],
            "No duplicate-type retention enrichment table was available for this run.",
        )
    )
    lines.extend(
        _section_or_empty(
            "Plots",
            ["plot_key", "path", "description"],
            [
                [row["plot_key"], row.get("path", ""), row.get("description", "")]
                for row in (plot_manifest or [])
            ],
            "No plot manifest was available for this run.",
        )
    )
    lines.extend(
        [
            "## Interpretation Note",
            "",
            "WGD event names such as gamma, beta, alpha, and theta are configured interpretations of synteny and Ks layers. Treat anonymous WGD layers as observations and named events as metadata-backed biological labels.",
            "",
        ]
    )
    return "\n".join(lines)


def read_tsv(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_report(text: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--gene-family", required=True)
    parser.add_argument("--report-index", required=True, type=Path)
    parser.add_argument("--wgd-event-evidence", default=None, type=Path)
    parser.add_argument("--family-event-retention", default=None, type=Path)
    parser.add_argument("--retention-enrichment", default=None, type=Path)
    parser.add_argument("--plot-manifest", default=None, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_report(
        assemble_report(
            project_name=args.project_name,
            gene_family=args.gene_family,
            report_index_rows=read_tsv(args.report_index),
            wgd_event_evidence=read_tsv(args.wgd_event_evidence),
            family_event_retention=read_tsv(args.family_event_retention),
            retention_enrichment=read_tsv(args.retention_enrichment),
            plot_manifest=read_tsv(args.plot_manifest),
        ),
        args.out,
    )


if __name__ == "__main__":
    main()
