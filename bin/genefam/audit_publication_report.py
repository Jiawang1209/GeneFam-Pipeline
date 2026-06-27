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
PLACEHOLDER_TOKENS = ("todo", "tbd", "placeholder")
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
METHOD_SUMMARY_REQUIRED_TERMS = [
    "HMMER",
    "DIAMOND",
    "MCScanX",
    "Ka/Ks",
    "gamma",
    "beta",
    "alpha",
    "theta",
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


def _output_path_mismatches(
    plot_rows: list[dict[str, str]],
    interpretation_rows: dict[str, dict[str, str]],
) -> list[str]:
    mismatches: list[str] = []
    for row in plot_rows:
        plot_key = row.get("plot_key", "").strip()
        if not plot_key or plot_key not in interpretation_rows:
            continue
        manifest_path = row.get("path", "").strip()
        interpretation_path = interpretation_rows[plot_key].get("output_path", "").strip()
        if manifest_path != interpretation_path:
            mismatches.append(f"{plot_key}:manifest={manifest_path}:interpretation={interpretation_path}")
    return mismatches


def _unregistered_interpretation_keys(
    plot_keys: list[str],
    interpretation_rows: dict[str, dict[str, str]],
) -> list[str]:
    registered = set(plot_keys)
    return sorted(key for key in interpretation_rows if key not in registered)


def _missing_detail_fields(rows: list[dict[str, str]]) -> list[str]:
    missing: list[str] = []
    for row in rows:
        figure_key = row.get("figure_key", "").strip() or "unknown"
        for field in REQUIRED_INTERPRETATION_FIELDS:
            value = row.get(field, "").strip()
            if not value:
                missing.append(f"{figure_key}:{field}")
            elif any(token in value.lower() for token in PLACEHOLDER_TOKENS):
                missing.append(f"{figure_key}:{field}:placeholder_text")
            elif field == "result_reading_status" and not value.startswith("figure-specific close reading"):
                missing.append(f"{figure_key}:{field}:not_figure_specific")
    return missing


def _placeholder_text_issues(text: str, source: str) -> list[str]:
    lowered = text.lower()
    return [f"{source}:{token}" for token in PLACEHOLDER_TOKENS if token in lowered]


def _report_contains(report_text: str, needle: str) -> bool:
    return needle in report_text


def _markdown_section(report_text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = report_text.find(marker)
    if start < 0:
        return ""
    next_heading = report_text.find("\n## ", start + len(marker))
    if next_heading < 0:
        return report_text[start:]
    return report_text[start:next_heading]


def _methods_summary_issues(report_text: str) -> list[str]:
    section = _markdown_section(report_text, "Methods Summary")
    if not section:
        return ["missing_section:Methods Summary"]

    issues = [f"missing_term:{term}" for term in METHOD_SUMMARY_REQUIRED_TERMS if term not in section]
    if "### Software Versions" not in report_text:
        issues.append("missing_linked_section:Software Versions")
    return issues


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


def _non_detected_version_warning_issues(
    report_text: str,
    version_rows: list[dict[str, str]],
) -> list[str]:
    issues: list[str] = []
    for row in version_rows:
        component = row.get("component", "").strip()
        version = row.get("version", "").strip()
        status = row.get("status", "").strip()
        source = row.get("source", "").strip()
        if not component or not version:
            continue
        if status == "detected" and version != "version_not_detected":
            continue
        missing_tokens = [
            token
            for token in [component, version, status, source]
            if token and not _report_contains(report_text, token)
        ]
        if missing_tokens:
            issues.append(f"software_version_warning:{component}:{version}:{status or 'missing_status'}")
    return issues


def _versioned_components(software_rows: list[dict[str, str]]) -> set[str]:
    return {
        row.get("component", "").strip()
        for row in software_rows
        if row.get("component", "").strip()
        and row.get("version", "").strip()
        and row.get("status", "").strip() not in {"", "missing"}
    }


def _version_kinds(version_rows: list[dict[str, str]]) -> set[str]:
    return {row.get("kind", "").strip() for row in version_rows if row.get("kind", "").strip()}


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


def _traceability_matrix_issues(report_text: str, detail_rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    if "## Figure Traceability Matrix" not in report_text:
        issues.append("missing_section:Figure Traceability Matrix")
    header = "| figure_key | plot_path | interpretation_status | qc_tables | method_and_software | reproducibility |"
    if header not in report_text:
        issues.append("missing_header:figure_traceability")
    for row in detail_rows:
        figure_key = row.get("figure_key", "").strip() or "unknown"
        expected = (
            f"| {figure_key} | {row.get('output_path', '').strip()} | "
            f"{row.get('result_reading_status', '').strip()} | "
            f"{row.get('qc_tables', '').strip()} | "
            f"{row.get('method_and_software', '').strip()} | "
            f"{row.get('reproducibility', '').strip()} |"
        )
        if expected not in report_text:
            issues.append(f"{figure_key}:traceability_row")
    return issues


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
    unregistered_interpretations = _unregistered_interpretation_keys(plot_keys, interpretation_rows)
    output_path_mismatches = _output_path_mismatches(plots, interpretation_rows)

    detail_rows = [interpretation_rows[key] for key in plot_keys if key in interpretation_rows]
    missing_details = _missing_detail_fields(detail_rows)
    missing_method_component_versions = _missing_method_component_versions(detail_rows, software)
    methods_summary_issues = _methods_summary_issues(report_text)
    traceability_matrix_issues = _traceability_matrix_issues(report_text, detail_rows)
    final_report_placeholder_issues = _placeholder_text_issues(report_text, "final_report")

    version_rows = [
        row
        for row in software
        if row.get("component", "").strip()
        and row.get("version", "").strip()
        and row.get("status", "").strip() not in {"", "missing"}
    ]
    required_version_kinds = {"command", "R_package"}
    version_kinds = _version_kinds(version_rows)
    missing_version_kinds = sorted(required_version_kinds - version_kinds)
    non_detected_version_warning_issues = _non_detected_version_warning_issues(report_text, version_rows)

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
            "figure_interpretation_scope",
            not unregistered_interpretations and bool(plot_keys),
            f"{plot_manifest}; {figure_interpretations}",
            "all figure interpretation rows correspond to registered plot_manifest figures"
            if not unregistered_interpretations and plot_keys
            else "unregistered interpretation rows: "
            + ", ".join(unregistered_interpretations or ["no plots registered"]),
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
            "figure_output_paths_match_manifest",
            not output_path_mismatches and bool(detail_rows),
            f"{plot_manifest}; {figure_interpretations}",
            "all figure interpretation output_path values match plot_manifest paths"
            if not output_path_mismatches and detail_rows
            else "figure output_path mismatches: " + ", ".join(output_path_mismatches or ["no interpretation rows"]),
        ),
        _row(
            "software_versions_present",
            bool(version_rows) and not missing_version_kinds,
            str(software_versions),
            f"detected version rows={len(version_rows)}; kinds={','.join(sorted(version_kinds))}"
            if version_rows and not missing_version_kinds
            else "missing required software version categories: "
            + ", ".join(missing_version_kinds or ["no detected software version rows"]),
        ),
        _row(
            "software_version_detection_warnings_visible",
            not non_detected_version_warning_issues,
            f"{software_versions}; {final_report}",
            "all non-detected software version statuses are visible in the final report"
            if not non_detected_version_warning_issues
            else "non-detected software version statuses missing from final report: "
            + ", ".join(non_detected_version_warning_issues),
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
            "final_report_methods_summary",
            not methods_summary_issues,
            str(final_report),
            "final report Methods Summary names core search, synteny, Ka/Ks, WGD event-label, and software-version context"
            if not methods_summary_issues
            else "missing or incomplete final report Methods Summary: " + ", ".join(methods_summary_issues),
        ),
        _row(
            "final_report_embeds_publication_sections",
            not missing_report_sections,
            str(final_report),
            "final report includes software versions and complete per-figure interpretation sections"
            if not missing_report_sections
            else "missing report sections/details: " + ", ".join(missing_report_sections),
        ),
        _row(
            "final_report_figure_traceability",
            not traceability_matrix_issues and bool(detail_rows),
            str(final_report),
            "final report Figure Traceability Matrix links every interpreted plot to status, QC tables, method/software, and reproducibility"
            if not traceability_matrix_issues and detail_rows
            else "missing figure traceability matrix evidence: "
            + ", ".join(traceability_matrix_issues or ["no interpretation rows"]),
        ),
        _row(
            "final_report_placeholder_text",
            not final_report_placeholder_issues,
            str(final_report),
            "final report has no TODO/TBD/placeholder text"
            if not final_report_placeholder_issues
            else "final report contains placeholder text: " + ", ".join(final_report_placeholder_issues),
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
