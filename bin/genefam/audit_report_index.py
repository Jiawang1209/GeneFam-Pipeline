#!/usr/bin/env python3
"""Audit that report indexes expose the core report deliverables."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FIELDNAMES = ["check", "status", "evidence", "note"]
REQUIRED_ARTIFACT_KEYS = {
    "standard": [
        "plot_manifest",
        "software_versions",
        "figure_interpretations",
        "figure_interpretations_md",
        "final_report",
        "figure_traceability_matrix",
    ],
    "wgd": [
        "plot_manifest",
        "software_versions",
        "figure_interpretations",
        "figure_interpretations_md",
        "final_report",
        "figure_traceability_matrix",
    ],
}


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


def _rows_by_key(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("key", "").strip(): row for row in rows if row.get("key", "").strip()}


def _required_artifact_issues(rows: list[dict[str, str]], profile: str) -> list[str]:
    indexed = _rows_by_key(rows)
    issues: list[str] = []
    for key in REQUIRED_ARTIFACT_KEYS[profile]:
        row = indexed.get(key)
        if row is None:
            issues.append(f"{key}:missing_row")
            continue
        if row.get("status", "").strip() != "available":
            issues.append(f"{key}:status={row.get('status', '').strip() or 'missing'}")
        if not row.get("path", "").strip():
            issues.append(f"{key}:missing_path")
    return issues


def _resolve_indexed_path(report_index: Path, indexed_path: str) -> Path:
    path = Path(indexed_path.split("#", 1)[0])
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return report_index.parent / path


def _anchor_from_indexed_path(indexed_path: str) -> str:
    if "#" not in indexed_path:
        return ""
    return "#" + indexed_path.split("#", 1)[1]


def _markdown_heading_slug(heading: str) -> str:
    text = re.sub(r"^#+\s*", "", heading.strip()).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return f"#{text}"


def _markdown_has_anchor(path: Path, anchor: str) -> bool:
    if not anchor:
        return True
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return False
    return any(line.lstrip().startswith("#") and _markdown_heading_slug(line) == anchor for line in lines)


def _artifact_file_issues(report_index: Path, rows: list[dict[str, str]], profile: str) -> list[str]:
    indexed = _rows_by_key(rows)
    issues: list[str] = []
    for key in REQUIRED_ARTIFACT_KEYS[profile]:
        row = indexed.get(key)
        if row is None:
            continue
        indexed_path = row.get("path", "").strip()
        if not indexed_path:
            continue
        resolved = _resolve_indexed_path(report_index, indexed_path)
        if not resolved.exists():
            issues.append(f"{key}:missing_file:{indexed_path}")
        elif resolved.stat().st_size <= 0:
            issues.append(f"{key}:empty_file:{indexed_path}")
        else:
            anchor = _anchor_from_indexed_path(indexed_path)
            if anchor and not _markdown_has_anchor(resolved, anchor):
                issues.append(f"{key}:missing_anchor:{anchor}")
    return issues


def _available_path_issues(report_index: Path, rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        if row.get("status", "").strip() != "available":
            continue
        key = row.get("key", "").strip() or f"row_{row_number}"
        indexed_path = row.get("path", "").strip()
        if not indexed_path:
            issues.append(f"{key}:missing_path")
            continue
        resolved = _resolve_indexed_path(report_index, indexed_path)
        if not resolved.exists():
            issues.append(f"{key}:missing_file:{indexed_path}")
            continue
        if resolved.is_file() and resolved.stat().st_size <= 0:
            issues.append(f"{key}:empty_file:{indexed_path}")
            continue
        anchor = _anchor_from_indexed_path(indexed_path)
        if anchor and not _markdown_has_anchor(resolved, anchor):
            issues.append(f"{key}:missing_anchor:{anchor}")
    return issues


def audit_report_index(report_index: Path, profile: str) -> list[dict[str, str]]:
    rows = read_tsv(report_index)
    required_issues = _required_artifact_issues(rows, profile)
    file_issues = _artifact_file_issues(report_index, rows, profile)
    available_path_issues = _available_path_issues(report_index, rows)
    return [
        _row(
            "report_index_required_artifacts",
            not required_issues,
            str(report_index),
            f"{profile} report index includes required report artifacts"
            if not required_issues
            else "missing or unavailable required report artifacts: " + ", ".join(required_issues),
        ),
        _row(
            "report_index_artifact_files_exist",
            not file_issues,
            str(report_index),
            f"{profile} report index artifact paths exist and are non-empty"
            if not file_issues
            else "missing or empty indexed report artifacts: " + ", ".join(file_issues or required_issues),
        ),
        _row(
            "report_index_available_paths_exist",
            not available_path_issues,
            str(report_index),
            f"{profile} report index available paths exist and are non-empty"
            if not available_path_issues
            else "missing, empty, or unresolved available report-index paths: "
            + ", ".join(available_path_issues),
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
        "# Report Index Audit",
        "",
        f"Passed: {summary['passed']}",
        f"Failed: {summary['failed']}",
        f"Complete: {str(summary['complete']).lower()}",
        "",
        "| check | status | evidence | note |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_markdown_cell(row[field]) for field in FIELDNAMES) + " |")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-index", required=True, type=Path)
    parser.add_argument("--profile", choices=sorted(REQUIRED_ARTIFACT_KEYS), required=True)
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    rows = audit_report_index(args.report_index, args.profile)
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)
    raise SystemExit(0 if summarize_audit(rows)["complete"] else 1)


if __name__ == "__main__":
    main()
