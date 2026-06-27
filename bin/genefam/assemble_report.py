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


def _available_rows(report_index_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in report_index_rows if row.get("status") == "available"]


def _named_wgd_events(wgd_event_evidence: list[dict[str, str]]) -> list[str]:
    names = {
        row.get("event_name", "")
        for row in wgd_event_evidence
        if row.get("event_name") and row.get("event_name") != "unannotated"
    }
    return sorted(names)


def _report_figure_rows(
    report_index_rows: list[dict[str, str]], plot_manifest: list[dict[str, str]]
) -> list[list[str]]:
    return [[row["plot_key"], row.get("path", ""), row.get("description", "")] for row in plot_manifest]


def _figure_traceability_rows(
    figure_rows: list[list[str]], figure_interpretations: list[dict[str, str]]
) -> list[list[str]]:
    interpretations_by_key = {row.get("figure_key", ""): row for row in figure_interpretations}
    rows: list[list[str]] = []
    for figure_key, plot_path, _description in figure_rows:
        interpretation = interpretations_by_key.get(figure_key, {})
        rows.append(
            [
                figure_key,
                plot_path,
                interpretation.get("result_reading_status", "interpretation_not_provided"),
                interpretation.get("qc_tables", "not provided"),
                interpretation.get("method_and_software", "not provided"),
                interpretation.get("reproducibility", "not provided"),
            ]
        )
    return rows


def _figure_preview_path(output_path: str) -> str:
    value = output_path.split("#", 1)[0].strip()
    if not value:
        return ""
    path = Path(value).with_suffix(".png")
    if not path.is_absolute() and path.parts and path.parts[0] == "plots":
        return str(Path("..") / path)
    return str(path)


def assemble_report(
    project_name: str,
    gene_family: str,
    report_index_rows: list[dict[str, str]],
    run_config_snapshot: list[dict[str, str]] | None = None,
    wgd_event_evidence: list[dict[str, str]] | None = None,
    family_event_retention: list[dict[str, str]] | None = None,
    retention_enrichment: list[dict[str, str]] | None = None,
    plot_manifest: list[dict[str, str]] | None = None,
    software_versions: list[dict[str, str]] | None = None,
    figure_interpretations: list[dict[str, str]] | None = None,
) -> str:
    available_outputs = _available_rows(report_index_rows)
    named_events = _named_wgd_events(wgd_event_evidence or [])
    figure_rows = _report_figure_rows(report_index_rows, plot_manifest or [])
    lines = [
        "# GeneFam-Pipeline Final Report",
        "",
        f"Project: {project_name}",
        f"Gene family: {gene_family}",
        "",
        "## Executive Summary",
        "",
        f"- Available outputs: {len(available_outputs)}",
        f"- Registered plots: {len(figure_rows)}",
        f"- Named WGD events with evidence: {len(named_events)}",
        f"- Named event labels: {', '.join(named_events) if named_events else 'none'}",
        "",
        "## Methods Summary",
        "",
        "Family members are identified from genome-scale protein evidence, with HMMER/DIAMOND-style search outputs filtered into family candidate tables. Alignment, phylogeny, motif, chromosome, promoter, expression, MCScanX synteny, and Ka/Ks evidence can then be integrated into the same report package. WGD labels such as gamma, beta, alpha, and theta are assigned from configured Ks-supported layers rather than treated as raw tool output.",
        "",
        "### Software Versions",
        "",
    ]
    if software_versions:
        lines.extend(
            _markdown_table(
                ["component", "kind", "version", "status", "source"],
                [
                    [
                        row.get("component", ""),
                        row.get("kind", ""),
                        row.get("version", "version_not_detected"),
                        row.get("status", "version_not_detected"),
                        row.get("source", ""),
                    ]
                    for row in software_versions
                ],
            )
        )
    else:
        lines.append("No software version table was provided; method versions should be treated as `version_not_detected`.")
    lines.extend(
        [
            "",
        "## Results Package Inventory",
        "",
        "### Available Tables",
        "",
        ]
    )
    table_rows = [
        [row["key"], row.get("path", ""), row.get("description", "")]
        for row in available_outputs
        if not row.get("path", "").lower().endswith((".pdf", ".png", ".svg"))
    ]
    if table_rows:
        lines.extend(_markdown_table(["key", "path", "description"], table_rows))
    else:
        lines.append("No available table outputs were registered.")
    lines.extend(["", "### Figures", ""])
    if figure_rows:
        lines.extend(_markdown_table(["plot_key", "path", "description"], figure_rows))
    else:
        lines.append("No figure outputs were registered.")
    lines.append("")

    lines.extend(
        _section_or_empty(
            "Run Configuration Snapshot",
            ["key", "value"],
            [[row["key"], row.get("value", "")] for row in (run_config_snapshot or [])],
            "No run configuration snapshot was available for this run.",
        )
    )
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
            [
                "wgd_layer",
                "event_name",
                "pair_count",
                "ks_median",
                "interpretation_status",
                "evidence_source",
                "species_scope",
                "expected_relative_age",
            ],
            [
                [
                    row["wgd_layer"],
                    row.get("event_name", "unannotated"),
                    row.get("pair_count", ""),
                    row.get("ks_median", ""),
                    row.get("interpretation_status", ""),
                    row.get("evidence_source", ""),
                    row.get("species_scope", ""),
                    row.get("expected_relative_age", ""),
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
        _section_or_empty(
            "Figure Traceability Matrix",
            ["figure_key", "plot_path", "interpretation_status", "qc_tables", "method_and_software", "reproducibility"],
            _figure_traceability_rows(figure_rows, figure_interpretations or []),
            "No figure traceability rows were available for this run.",
        )
    )
    lines.extend(["## Figure Result Interpretations", ""])
    if figure_interpretations:
        for row in figure_interpretations:
            figure_key = row.get("figure_key", "")
            title = row.get("title", "")
            preview_path = _figure_preview_path(row.get("output_path", ""))
            lines.extend(
                [
                    f"### {figure_key}: {title}",
                    "",
                    f"![{figure_key}: {title}]({preview_path})" if preview_path else "",
                    "",
                    f"- Input data: {row.get('input_data', '')}",
                    f"- What the figure shows: {row.get('what_figure_shows', '')}",
                    f"- Key observations: {row.get('key_observations', '')}",
                    f"- Biological interpretation: {row.get('biological_interpretation', '')}",
                    f"- QC warnings / limitations: {row.get('qc_warnings', '')}",
                    f"- QC tables: {row.get('qc_tables', 'not provided')}",
                    f"- Method/software: {row.get('method_and_software', 'not provided')}",
                    f"- Reproducibility: {row.get('reproducibility', 'not provided')}",
                    f"- Result reading status: {row.get('result_reading_status', 'not provided')}",
                    f"- Output path: `{row.get('output_path', '')}`",
                    "",
                ]
            )
    else:
        lines.extend(
            [
                "No structured figure interpretations were provided. Interpret plotted results only after reviewing the input tables and QC warnings.",
                "",
            ]
        )
    lines.extend(
        [
            "## Reproducibility Note",
            "",
            "This report is designed to be regenerated from the GeneFamilyFlow runtime. R visualizations use `/usr/local/bin/R` in the local development environment, and containerized execution can be layered on after the analysis workflow is stable.",
            "",
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
    parser.add_argument("--run-config-snapshot", default=None, type=Path)
    parser.add_argument("--wgd-event-evidence", default=None, type=Path)
    parser.add_argument("--family-event-retention", default=None, type=Path)
    parser.add_argument("--retention-enrichment", default=None, type=Path)
    parser.add_argument("--plot-manifest", default=None, type=Path)
    parser.add_argument("--software-versions", default=None, type=Path)
    parser.add_argument("--figure-interpretations", default=None, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_report(
        assemble_report(
            project_name=args.project_name,
            gene_family=args.gene_family,
            report_index_rows=read_tsv(args.report_index),
            run_config_snapshot=read_tsv(args.run_config_snapshot),
            wgd_event_evidence=read_tsv(args.wgd_event_evidence),
            family_event_retention=read_tsv(args.family_event_retention),
            retention_enrichment=read_tsv(args.retention_enrichment),
            plot_manifest=read_tsv(args.plot_manifest),
            software_versions=read_tsv(args.software_versions),
            figure_interpretations=read_tsv(args.figure_interpretations),
        ),
        args.out,
    )


if __name__ == "__main__":
    main()
