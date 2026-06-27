#!/usr/bin/env python3
"""Audit delivery-bundle manifest paths."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["check", "status", "evidence", "note"]
REQUIRED_COLUMNS = ["section", "item", "status", "path", "note"]
PATH_REQUIRED_STATUSES = {"available", "blocked"}
VIRTUAL_PATH_PREFIXES = ("GeneFamilyFlow:",)
REQUIRED_ITEMS = [
    ("status", "release_checks"),
    ("status", "release_ready"),
    ("status", "r_runtime_health"),
    ("status", "objective_audit"),
    ("status", "final_stage_blocker"),
    ("status", "figure_gallery"),
    ("status", "delivery_bundle_figure_gallery_smoke"),
    ("status", "publication_report_audit"),
    ("status", "standard_report_index_audit"),
    ("status", "wgd_publication_report_audit"),
    ("status", "wgd_report_index_audit"),
    ("standard", "mock_mvp"),
    ("nextflow", "nextflow_mock_mvp_smoke"),
    ("nextflow", "nextflow_single_tool_smoke"),
    ("wgd", "event_evidence"),
    ("governance", "reference_gitignore"),
    ("runtime_recovery", "local_acceptance"),
    ("docs", "history"),
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


def _resolve_path(manifest: Path, indexed_path: str) -> Path:
    path = Path(indexed_path)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return manifest.parent / path


def _required_column_issues(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return ["delivery_manifest:no_rows"]
    columns = set(rows[0])
    return [f"{column}:missing_column" for column in REQUIRED_COLUMNS if column not in columns]


def _is_virtual_path(path: str) -> bool:
    return path.startswith(VIRTUAL_PATH_PREFIXES)


def _path_issues(manifest: Path, rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        status = row.get("status", "").strip()
        if status not in PATH_REQUIRED_STATUSES:
            continue
        indexed_path = row.get("path", "").strip()
        item = row.get("item", "").strip() or f"row_{row_number}"
        if not indexed_path:
            issues.append(f"{item}:path:missing_path")
            continue
        if _is_virtual_path(indexed_path):
            continue
        resolved = _resolve_path(manifest, indexed_path)
        if not resolved.exists():
            issues.append(f"{item}:path:missing_file:{indexed_path}")
            continue
        if resolved.is_file() and resolved.stat().st_size <= 0:
            issues.append(f"{item}:path:empty_file:{indexed_path}")
    return issues


def _required_item_issues(rows: list[dict[str, str]]) -> list[str]:
    seen = {
        (row.get("section", "").strip(), row.get("item", "").strip())
        for row in rows
        if row.get("section", "").strip() and row.get("item", "").strip()
    }
    return [f"{section}:{item}:missing_item" for section, item in REQUIRED_ITEMS if (section, item) not in seen]


def audit_delivery_manifest(delivery_manifest: Path) -> list[dict[str, str]]:
    rows = read_tsv(delivery_manifest)
    column_issues = _required_column_issues(rows)
    path_issues = _path_issues(delivery_manifest, rows) if not column_issues else []
    item_issues = _required_item_issues(rows) if not column_issues else []
    return [
        _row(
            "delivery_manifest_required_columns",
            not column_issues,
            str(delivery_manifest),
            "delivery manifest includes required columns"
            if not column_issues
            else "missing required delivery manifest columns: " + ", ".join(column_issues),
        ),
        _row(
            "delivery_manifest_paths_exist",
            not path_issues,
            str(delivery_manifest),
            "delivery manifest available/blocked filesystem targets exist"
            if not path_issues
            else "missing, empty, or unresolved delivery manifest targets: " + ", ".join(path_issues),
        ),
        _row(
            "delivery_manifest_required_items",
            not item_issues,
            str(delivery_manifest),
            "delivery manifest includes required handoff items"
            if not item_issues
            else "missing required delivery manifest handoff items: " + ", ".join(item_issues),
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
        "# Delivery Manifest Audit",
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
    parser.add_argument("--delivery-manifest", required=True, type=Path)
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    rows = audit_delivery_manifest(args.delivery_manifest)
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)
    raise SystemExit(0 if summarize_audit(rows)["complete"] else 1)


if __name__ == "__main__":
    main()
