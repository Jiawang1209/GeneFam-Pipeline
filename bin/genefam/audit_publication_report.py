#!/usr/bin/env python3
"""Audit that publication-style report figures are closed by interpretation evidence."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["check", "status", "evidence", "note"]
REQUIRED_INTERPRETATION_FIELDS = [
    "qc_tables",
    "method_and_software",
    "reproducibility",
    "result_reading_status",
    "output_path",
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
    interpretation_rows = _interpretation_by_key(interpretations)
    missing_interpretations = [key for key in plot_keys if key not in interpretation_rows]

    detail_rows = [interpretation_rows[key] for key in plot_keys if key in interpretation_rows]
    missing_details = _missing_detail_fields(detail_rows)

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
        for field in ["qc_tables", "method_and_software", "reproducibility", "result_reading_status"]:
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
            "all figure interpretation rows include QC tables, method/software, reproducibility, status, and output path"
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
            "final_report_embeds_publication_sections",
            not missing_report_sections,
            str(final_report),
            "final report includes software versions and per-figure interpretation sections"
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
