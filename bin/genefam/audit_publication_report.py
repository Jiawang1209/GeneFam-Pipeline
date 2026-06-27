#!/usr/bin/env python3
"""Audit that publication-style report figures are closed by interpretation evidence."""

from __future__ import annotations

import argparse
import csv
import re
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
INSTRUCTIONAL_READING_PREFIXES = ("inspect ", "review ", "validate ", "check ")
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


def _resolve_indexed_path(index_path: Path, indexed_path: str) -> Path:
    value = indexed_path.split("#", 1)[0].strip()
    path = Path(value)
    if path.is_absolute():
        return path
    candidates = [Path.cwd() / path, index_path.parent / path, index_path.parent.parent / path]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _plot_variant_targets(plot_manifest: Path, plot_row: dict[str, str]) -> list[tuple[str, Path]]:
    plot_path = plot_row.get("path", "").strip()
    if not plot_path:
        return []
    resolved = _resolve_plot_path(plot_manifest, plot_path)
    suffix = resolved.suffix.lower().lstrip(".")
    targets = [(suffix or "plot", resolved)]
    if suffix == "pdf":
        targets.append(("png", resolved.with_suffix(".png")))
    return targets


def _report_index_plot_variant_issues(
    plot_manifest: Path,
    plot_rows: list[dict[str, str]],
    report_index: Path | None,
) -> list[str]:
    if report_index is None:
        return []
    index_rows = read_tsv(report_index)
    available_paths = {
        _resolve_indexed_path(report_index, row.get("path", "")).resolve()
        for row in index_rows
        if row.get("status", "").strip() == "available" and row.get("path", "").strip()
    }
    issues: list[str] = []
    for row in plot_rows:
        plot_key = row.get("plot_key", "").strip() or "unknown"
        for variant, expected in _plot_variant_targets(plot_manifest, row):
            expected_resolved = expected.resolve()
            if expected_resolved not in available_paths:
                issues.append(f"{plot_key}:{variant}:missing_report_index_row:{expected}")
                continue
            if not expected.exists():
                issues.append(f"{plot_key}:{variant}:missing_file:{expected}")
                continue
            if expected.stat().st_size <= 0:
                issues.append(f"{plot_key}:{variant}:empty_file:{expected}")
                continue
            format_issue = _plot_format_issue(plot_key, str(expected), expected)
            if format_issue:
                issues.append(f"{plot_key}:{variant}:{format_issue.split(':', 1)[1]}")
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


def _instructional_reading_issues(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row in rows:
        figure_key = row.get("figure_key", "").strip() or "unknown"
        for field in [
            "key_observations",
            "biological_interpretation",
            "qc_warnings",
            "result_reading_status",
        ]:
            value = row.get(field, "").strip().lower()
            if value.startswith(INSTRUCTIONAL_READING_PREFIXES) or any(
                f"; {prefix}" in value for prefix in INSTRUCTIONAL_READING_PREFIXES
            ):
                issues.append(f"{figure_key}:{field}:instructional_text")
    return issues


def _qc_specificity_issues(rows: list[dict[str, str]]) -> list[str]:
    by_warning: dict[str, list[str]] = {}
    for row in rows:
        figure_key = row.get("figure_key", "").strip() or "unknown"
        warning = " ".join(row.get("qc_warnings", "").strip().lower().split())
        if not warning:
            continue
        by_warning.setdefault(warning, []).append(figure_key)
    return [
        "reused_qc_warning:" + ",".join(figure_keys)
        for figure_keys in by_warning.values()
        if len(figure_keys) > 1
    ]


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


def _markdown_table_values(section: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {"key", "---"}:
            continue
        values[cells[0]] = cells[1]
    return values


def _final_report_identity_values(report_text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in report_text.splitlines():
        if line.startswith("Project:"):
            values["Project"] = line.split(":", 1)[1].strip()
        elif line.startswith("Gene family:"):
            values["Gene family"] = line.split(":", 1)[1].strip()
    return values


def _report_identity_issues(report_text: str) -> list[str]:
    run_config = _markdown_table_values(_markdown_section(report_text, "Run Configuration Snapshot"))
    report_identity = _final_report_identity_values(report_text)
    expected_fields = {
        "project.name": "Project",
        "gene_family.name": "Gene family",
    }
    issues: list[str] = []
    for config_key, report_key in expected_fields.items():
        expected = run_config.get(config_key, "").strip()
        if not expected:
            continue
        actual = report_identity.get(report_key, "").strip()
        if actual != expected:
            issues.append(f"report_identity:{config_key}:expected={expected}:actual={actual or 'missing'}")
    return issues


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


def _detected_version_parse_issues(version_rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row in version_rows:
        component = row.get("component", "").strip() or "unknown"
        version = row.get("version", "").strip()
        status = row.get("status", "").strip()
        if status == "detected" and not re.search(r"\d", version):
            issues.append(f"detected_version_without_numeric_value:{component}:{version or 'missing_version'}")
    return issues


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
    section = _markdown_section(report_text, "Figure Traceability Matrix")
    if not section:
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
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 6 or cells[0] in {"figure_key", "---"}:
            continue
        if cells[2] == "interpretation_not_provided" or cells[3:] == ["not provided", "not provided", "not provided"]:
            issues.append(f"uninterpreted_traceability_row:{cells[0]}")
    return issues


def _figure_preview_path(output_path: str) -> str:
    value = output_path.split("#", 1)[0].strip()
    if not value:
        return ""
    path = Path(value).with_suffix(".png")
    if not path.is_absolute() and path.parts and path.parts[0] == "plots":
        return str(Path("..") / path)
    return str(path)


def _final_report_plot_preview_issues(report_text: str, detail_rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row in detail_rows:
        figure_key = row.get("figure_key", "").strip() or "unknown"
        title = row.get("title", "").strip()
        preview_path = _figure_preview_path(row.get("output_path", ""))
        if not preview_path:
            issues.append(f"{figure_key}:missing_preview_path")
            continue
        expected = f"![{figure_key}: {title}]({preview_path})"
        if expected not in report_text:
            issues.append(f"{figure_key}:missing_preview:{preview_path}")
    return issues


def audit_publication_report(
    plot_manifest: Path,
    figure_interpretations: Path,
    software_versions: Path,
    final_report: Path,
    report_index: Path | None = None,
) -> list[dict[str, str]]:
    plots = read_tsv(plot_manifest)
    interpretations = read_tsv(figure_interpretations)
    software = read_tsv(software_versions)
    report_text = final_report.read_text(encoding="utf-8") if final_report.exists() else ""

    plot_keys = _plot_keys(plots)
    plot_file_issues = _plot_file_issues(plot_manifest, plots)
    plot_format_issues = _plot_format_issues(plot_manifest, plots)
    report_index_plot_variant_issues = _report_index_plot_variant_issues(plot_manifest, plots, report_index)
    interpretation_rows = _interpretation_by_key(interpretations)
    missing_interpretations = [key for key in plot_keys if key not in interpretation_rows]
    unregistered_interpretations = _unregistered_interpretation_keys(plot_keys, interpretation_rows)
    output_path_mismatches = _output_path_mismatches(plots, interpretation_rows)

    detail_rows = [interpretation_rows[key] for key in plot_keys if key in interpretation_rows]
    missing_details = _missing_detail_fields(detail_rows)
    instructional_reading_issues = _instructional_reading_issues(detail_rows)
    qc_specificity_issues = _qc_specificity_issues(detail_rows)
    missing_method_component_versions = _missing_method_component_versions(detail_rows, software)
    methods_summary_issues = _methods_summary_issues(report_text)
    traceability_matrix_issues = _traceability_matrix_issues(report_text, detail_rows)
    final_report_plot_preview_issues = _final_report_plot_preview_issues(report_text, detail_rows)
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
    detected_version_parse_issues = _detected_version_parse_issues(version_rows)
    non_detected_version_warning_issues = _non_detected_version_warning_issues(report_text, version_rows)

    missing_report_sections: list[str] = []
    for section in ["### Software Versions", "## Figure Result Interpretations"]:
        if not _report_contains(report_text, section):
            missing_report_sections.append(section)
    missing_report_sections.extend(_report_identity_issues(report_text))
    missing_report_sections.extend(_missing_software_versions_in_report(report_text, version_rows))
    for key in plot_keys:
        if not _report_contains(report_text, f"### {key}:"):
            missing_report_sections.append(f"figure:{key}")
    for row in detail_rows:
        for field in REPORT_EMBEDDED_INTERPRETATION_FIELDS:
            value = row.get(field, "").strip()
            if value and not _report_contains(report_text, value):
                missing_report_sections.append(f"{row.get('figure_key', 'unknown')}:{field}")

    rows = [
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
    ]
    if report_index is not None:
        rows.append(
            _row(
                "report_index_plot_variants",
                not report_index_plot_variant_issues and bool(plot_keys),
                f"{plot_manifest}; {report_index}",
                "report index exposes valid PDF/PNG plot variants for every registered plot"
                if not report_index_plot_variant_issues and plot_keys
                else "missing, empty, or invalid report-index plot variants: "
                + ", ".join(report_index_plot_variant_issues or ["no plots registered"]),
            )
        )
    rows.extend([
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
            "figure_interpretation_close_reading_voice",
            not instructional_reading_issues and bool(detail_rows),
            str(figure_interpretations),
            "figure interpretation narrative fields are result statements, not instructions"
            if not instructional_reading_issues and detail_rows
            else "instructional interpretation text: "
            + ", ".join(instructional_reading_issues or ["no interpretation rows"]),
        ),
        _row(
            "figure_interpretation_qc_specificity",
            not qc_specificity_issues and bool(detail_rows),
            str(figure_interpretations),
            "figure interpretation QC warnings are figure-specific and not reused across plots"
            if not qc_specificity_issues and detail_rows
            else "generic or reused QC warnings: " + ", ".join(qc_specificity_issues or ["no interpretation rows"]),
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
            "software_detected_versions_parseable",
            not detected_version_parse_issues,
            str(software_versions),
            "all detected software version values contain a numeric version token"
            if not detected_version_parse_issues
            else "detected software version rows lack numeric version values: "
            + ", ".join(detected_version_parse_issues),
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
            "final_report_plot_previews",
            not final_report_plot_preview_issues and bool(detail_rows),
            str(final_report),
            "final report embeds PNG previews for every interpreted plot"
            if not final_report_plot_preview_issues and detail_rows
            else "missing final report plot previews: "
            + ", ".join(final_report_plot_preview_issues or ["no interpretation rows"]),
        ),
        _row(
            "final_report_placeholder_text",
            not final_report_placeholder_issues,
            str(final_report),
            "final report has no TODO/TBD/placeholder text"
            if not final_report_placeholder_issues
            else "final report contains placeholder text: " + ", ".join(final_report_placeholder_issues),
        ),
    ])
    return rows


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
    parser.add_argument("--report-index", type=Path)
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    rows = audit_publication_report(
        plot_manifest=args.plot_manifest,
        figure_interpretations=args.figure_interpretations,
        software_versions=args.software_versions,
        final_report=args.final_report,
        report_index=args.report_index,
    )
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)
    raise SystemExit(0 if summarize_audit(rows)["complete"] else 1)


if __name__ == "__main__":
    main()
