#!/usr/bin/env python3
"""Audit that publication-style report figures are closed by interpretation evidence."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["check", "status", "evidence", "note"]
REQUIRED_INTERPRETATION_FIELDS = [
    "input_data",
    "what_figure_shows",
    "key_observations",
    "biological_interpretation",
    "qc_warnings",
    "qc_tables",
    "method_and_software",
    "reproducibility",
    "result_reading_status",
    "output_path",
]
REPORT_EMBEDDED_INTERPRETATION_FIELDS = REQUIRED_INTERPRETATION_FIELDS
VERSIONED_METHOD_COMPONENTS = [
    "Nextflow",
    "HMMER",
    "DIAMOND",
    "MAFFT",
    "FastTree",
    "IQ-TREE",
    "MEME",
    "MCScanX",
    "KaKs_Calculator",
    "R",
    "ggplot2",
    "pheatmap",
    "circlize",
    "ggtree",
    "treeio",
    "ggNetView",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _row(check: str, passed: bool, evidence: str, note: str) -> dict[str, str]:
    return {
        "check": check,
        "status": "passed" if passed else "failed",
        "evidence": evidence,
        "note": note,
    }


def _plot_keys(rows: list[dict[str, str]]) -> list[str]:
    return [row.get("plot_key", "").strip() for row in rows if row.get("plot_key", "").strip()]


def _plot_base_dir(plot_manifest: Path) -> Path:
    if plot_manifest.parent.name == "report":
        return plot_manifest.parent.parent
    return plot_manifest.parent


def _resolve_plot_path(plot_manifest: Path, plot_path: str) -> Path:
    path = Path(plot_path)
    if path.is_absolute():
        return path
    return _plot_base_dir(plot_manifest) / path


def _plot_file_issues(plot_manifest: Path, rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row in rows:
        plot_key = row.get("plot_key", "").strip() or "unknown"
        plot_path = row.get("path", "").strip()
        if not plot_path:
            issues.append(f"{plot_key}:missing_path")
            continue
        resolved = _resolve_plot_path(plot_manifest, plot_path)
        if not resolved.exists():
            issues.append(f"{plot_key}:missing:{plot_path}")
        elif resolved.stat().st_size <= 0:
            issues.append(f"{plot_key}:empty:{plot_path}")
    return issues


def _plot_format_issue(plot_key: str, plot_path: str, resolved: Path) -> str | None:
    suffix = resolved.suffix.lower()
    try:
        header = resolved.read_bytes()[:256]
    except OSError:
        return f"{plot_key}:unreadable:{plot_path}"
    if suffix == ".pdf" and not header.startswith(b"%PDF"):
        return f"{plot_key}:invalid_pdf:{plot_path}"
    if suffix == ".png" and not header.startswith(b"\x89PNG\r\n\x1a\n"):
        return f"{plot_key}:invalid_png:{plot_path}"
    if suffix == ".svg":
        stripped = header.lstrip()
        if not (stripped.startswith(b"<svg") or stripped.startswith(b"<?xml")):
            return f"{plot_key}:invalid_svg:{plot_path}"
    return None


def _plot_format_issues(plot_manifest: Path, rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row in rows:
        plot_key = row.get("plot_key", "").strip() or "unknown"
        plot_path = row.get("path", "").strip()
        if not plot_path:
            continue
        resolved = _resolve_plot_path(plot_manifest, plot_path)
        if not resolved.exists() or resolved.stat().st_size <= 0:
            continue
        issue = _plot_format_issue(plot_key, plot_path, resolved)
        if issue:
            issues.append(issue)
    return issues


def _interpretation_by_key(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("figure_key", "").strip(): row for row in rows if row.get("figure_key", "").strip()}


def _missing_detail_fields(rows: list[dict[str, str]]) -> list[str]:
    missing: list[str] = []
    for row in rows:
        figure_key = row.get("figure_key", "").strip() or "unknown"
        for field in REQUIRED_INTERPRETATION_FIELDS:
            value = row.get(field, "").strip()
            if not value:
                missing.append(f"{figure_key}:{field}")
            elif field == "result_reading_status" and not value.startswith("figure-specific close reading"):
                missing.append(f"{figure_key}:{field}:not_figure_specific")
    return missing


def _report_contains(report_text: str, needle: str) -> bool:
    return needle in report_text


def _missing_software_versions_in_report(
    report_text: str,
    version_rows: list[dict[str, str]],
) -> list[str]:
    missing: list[str] = []
    for row in version_rows:
        component = row.get("component", "").strip()
        version = row.get("version", "").strip()
        if component and version and (
            not _report_contains(report_text, component)
            or not _report_contains(report_text, version)
        ):
            missing.append(f"software_version:{component}:{version}")
    return missing


def _versioned_components(software_rows: list[dict[str, str]]) -> set[str]:
    return {
        row.get("component", "").strip()
        for row in software_rows
        if row.get("component", "").strip()
        and row.get("version", "").strip()
        and row.get("status", "").strip() not in {"", "missing"}
    }


def _method_components(method_text: str) -> list[str]:
    normalized = method_text.replace("/usr/local/bin/R", " R ")
    components: list[str] = []
    for component in VERSIONED_METHOD_COMPONENTS:
        if component == "R":
            if " R " in f" {normalized} ":
                components.append(component)
            continue
        if component in normalized:
            components.append(component)
    return components


def _missing_method_component_versions(
    detail_rows: list[dict[str, str]],
    software_rows: list[dict[str, str]],
) -> list[str]:
    available = _versioned_components(software_rows)
    missing: list[str] = []
    for row in detail_rows:
        figure_key = row.get("figure_key", "").strip() or "unknown"
        method_text = row.get("method_and_software", "")
        for component in _method_components(method_text):
            if component not in available:
                missing.append(f"{figure_key}:{component}")
    return missing


def audit_publication_report(
    plot_manifest: Path,
    figure_interpretations: Path,
    software_versions: Path,
    final_report: Path,
) -> list[dict[str, str]]:
    plots = read_tsv(plot_manifest)
    interpretations = read_tsv(figure_interpretations)
    software = read_tsv(software_versions)
    report_text = final_report.read_text(encoding="utf-8") if final_report.exists() else ""

    plot_keys = _plot_keys(plots)
    plot_file_issues = _plot_file_issues(plot_manifest, plots)
    plot_format_issues = _plot_format_issues(plot_manifest, plots)
    interpretation_rows = _interpretation_by_key(interpretations)
    missing_interpretations = [key for key in plot_keys if key not in interpretation_rows]

    detail_rows = [interpretation_rows[key] for key in plot_keys if key in interpretation_rows]
    missing_details = _missing_detail_fields(detail_rows)
    missing_method_component_versions = _missing_method_component_versions(detail_rows, software)

    version_rows = [
        row
        for row in software
        if row.get("component", "").strip()
        and row.get("version", "").strip()
        and row.get("status", "").strip() not in {"", "missing"}
    ]

    missing_report_sections: list[str] = []
    for section in ["### Software Versions", "## Figure Result Interpretations"]:
        if not _report_contains(report_text, section):
            missing_report_sections.append(section)
    missing_report_sections.extend(_missing_software_versions_in_report(report_text, version_rows))
    for key in plot_keys:
        if not _report_contains(report_text, f"### {key}:"):
            missing_report_sections.append(f"figure:{key}")
    for row in detail_rows:
        for field in REPORT_EMBEDDED_INTERPRETATION_FIELDS:
            value = row.get(field, "").strip()
            if value and not _report_contains(report_text, value):
                missing_report_sections.append(f"{row.get('figure_key', 'unknown')}:{field}")

    return [
        _row(
            "plot_files_exist",
            not plot_file_issues and bool(plot_keys),
            str(plot_manifest),
            "all plot_manifest paths exist and are non-empty"
            if not plot_file_issues and plot_keys
            else "missing or empty plot files: " + ", ".join(plot_file_issues or ["no plots registered"]),
        ),
        _row(
            "plot_file_format_valid",
            not plot_format_issues and bool(plot_keys),
            str(plot_manifest),
            "all plot_manifest PDF, PNG, and SVG files have valid file signatures"
            if not plot_format_issues and plot_keys
            else "invalid plot file formats: " + ", ".join(plot_format_issues or ["no plots registered"]),
        ),
        _row(
            "figure_interpretation_coverage",
            not missing_interpretations and bool(plot_keys),
            f"{plot_manifest}; {figure_interpretations}",
            "all plot_manifest figures have interpretation rows"
            if not missing_interpretations and plot_keys
            else "missing interpretation rows: " + ", ".join(missing_interpretations or ["no plots registered"]),
        ),
        _row(
            "figure_interpretation_detail",
            not missing_details and bool(detail_rows),
            str(figure_interpretations),
            "all figure interpretation rows include close-reading text, QC tables, method/software, reproducibility, status, and output path"
            if not missing_details and detail_rows
            else "missing required interpretation details: " + ", ".join(missing_details or ["no interpretation rows"]),
        ),
        _row(
            "software_versions_present",
            bool(version_rows),
            str(software_versions),
            f"detected version rows={len(version_rows)}" if version_rows else "no detected software version rows",
        ),
        _row(
            "figure_method_software_versions",
            not missing_method_component_versions and bool(detail_rows),
            f"{figure_interpretations}; {software_versions}",
            "every versioned method/software component named by figure interpretations has a software_versions row"
            if not missing_method_component_versions and detail_rows
            else "missing method/software version rows: "
            + ", ".join(missing_method_component_versions or ["no interpretation rows"]),
        ),
        _row(
            "final_report_embeds_publication_sections",
            not missing_report_sections,
            str(final_report),
            "final report includes software versions and complete per-figure interpretation sections"
            if not missing_report_sections
            else "missing report sections/details: " + ", ".join(missing_report_sections),
        ),
    ]


def summarize_audit(rows: list[dict[str, str]]) -> dict[str, int | bool]:
    passed = sum(1 for row in rows if row["status"] == "passed")
    failed = sum(1 for row in rows if row["status"] == "failed")
    return {"passed": passed, "failed": failed, "complete": failed == 0}


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    summary = summarize_audit(rows)
    lines = [
        "# Publication Report Audit",
        "",
        f"Passed: {summary['passed']}",
        f"Failed: {summary['failed']}",
        f"Complete: {str(summary['complete']).lower()}",
        "",
        "| check | status | evidence | note |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(_markdown_cell(row[field]) for field in FIELDNAMES)
            + " |"
        )
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-manifest", required=True, type=Path)
    parser.add_argument("--figure-interpretations", required=True, type=Path)
    parser.add_argument("--software-versions", required=True, type=Path)
    parser.add_argument("--final-report", required=True, type=Path)
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    rows = audit_publication_report(
        plot_manifest=args.plot_manifest,
        figure_interpretations=args.figure_interpretations,
        software_versions=args.software_versions,
        final_report=args.final_report,
    )
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)
    raise SystemExit(0 if summarize_audit(rows)["complete"] else 1)


if __name__ == "__main__":
    main()
