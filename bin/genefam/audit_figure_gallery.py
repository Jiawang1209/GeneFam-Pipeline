#!/usr/bin/env python3
"""Audit the delivery-bundle global figure gallery links."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FIELDNAMES = ["check", "status", "evidence", "note"]
REQUIRED_COLUMNS = [
    "branch",
    "plot_key",
    "plot_path",
    "plot_description",
    "figure_interpretations",
    "software_versions",
    "final_report",
    "traceability_matrix",
]
LINK_COLUMNS = [
    "plot_path",
    "figure_interpretations",
    "software_versions",
    "final_report",
    "traceability_matrix",
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


def _anchor_from_path(path: str) -> str:
    if "#" not in path:
        return ""
    return "#" + path.split("#", 1)[1]


def _path_without_anchor(path: str) -> str:
    return path.split("#", 1)[0]


def _resolve_path(gallery: Path, indexed_path: str) -> Path:
    path = Path(_path_without_anchor(indexed_path))
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return gallery.parent / path


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


def _required_column_issues(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return ["figure_gallery:no_rows"]
    columns = set(rows[0])
    return [f"{column}:missing_column" for column in REQUIRED_COLUMNS if column not in columns]


def _linked_file_issues(gallery: Path, rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        plot_key = row.get("plot_key", "").strip() or f"row_{row_number}"
        for column in LINK_COLUMNS:
            indexed_path = row.get(column, "").strip()
            if not indexed_path:
                issues.append(f"{plot_key}:{column}:missing_path")
                continue
            resolved = _resolve_path(gallery, indexed_path)
            if not resolved.exists():
                issues.append(f"{plot_key}:{column}:missing_file:{indexed_path}")
                continue
            if resolved.stat().st_size <= 0:
                issues.append(f"{plot_key}:{column}:empty_file:{indexed_path}")
                continue
            anchor = _anchor_from_path(indexed_path)
            if anchor and not _markdown_has_anchor(resolved, anchor):
                issues.append(f"{plot_key}:{column}:missing_anchor:{anchor}")
    return issues


def audit_figure_gallery(figure_gallery: Path) -> list[dict[str, str]]:
    rows = read_tsv(figure_gallery)
    column_issues = _required_column_issues(rows)
    link_issues = _linked_file_issues(figure_gallery, rows) if not column_issues else []
    return [
        _row(
            "figure_gallery_required_columns",
            not column_issues,
            str(figure_gallery),
            "figure gallery includes required navigation columns"
            if not column_issues
            else "missing required figure gallery columns: " + ", ".join(column_issues),
        ),
        _row(
            "figure_gallery_linked_files_exist",
            not link_issues,
            str(figure_gallery),
            "figure gallery linked plot, interpretation, version, report, and traceability targets exist"
            if not link_issues
            else "missing, empty, or unresolved figure gallery targets: " + ", ".join(link_issues),
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
        "# Figure Gallery Audit",
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
    parser.add_argument("--figure-gallery", required=True, type=Path)
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    rows = audit_figure_gallery(args.figure_gallery)
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)
    raise SystemExit(0 if summarize_audit(rows)["complete"] else 1)


if __name__ == "__main__":
    main()
