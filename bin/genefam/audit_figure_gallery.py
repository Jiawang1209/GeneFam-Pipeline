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
    "plot_png_path",
    "plot_description",
    "figure_interpretations",
    "software_versions",
    "final_report",
    "traceability_matrix",
]
LINK_COLUMNS = [
    "plot_path",
    "plot_png_path",
    "figure_interpretations",
    "software_versions",
    "final_report",
    "traceability_matrix",
]
MARKDOWN_LINK_LABELS = {
    "plot_path": "PDF",
    "plot_png_path": "PNG",
    "figure_interpretations": "close reading",
    "software_versions": "versions",
    "final_report": "final report",
    "traceability_matrix": "traceability",
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
    html_anchor = anchor.lstrip("#")
    html_id_re = re.compile(rf"""<a\s+[^>]*(?:id|name)=["']{re.escape(html_anchor)}["']""")
    return any(
        (line.lstrip().startswith("#") and _markdown_heading_slug(line) == anchor)
        or html_id_re.search(line)
        for line in lines
    )


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
            if column in {"plot_path", "plot_png_path"}:
                format_issue = _plot_format_issue(plot_key, column, indexed_path, resolved)
                if format_issue:
                    issues.append(format_issue)
                    continue
            anchor = _anchor_from_path(indexed_path)
            if anchor and not _markdown_has_anchor(resolved, anchor):
                issues.append(f"{plot_key}:{column}:missing_anchor:{anchor}")
    return issues


def _traceability_target_issues(gallery: Path, rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        plot_key = row.get("plot_key", "").strip() or f"row_{row_number}"
        final_report = row.get("final_report", "").strip()
        traceability = row.get("traceability_matrix", "").strip()
        if not final_report or not traceability:
            continue
        resolved_final = _resolve_path(gallery, final_report)
        resolved_traceability = _resolve_path(gallery, traceability)
        if (
            resolved_final != resolved_traceability
            or _anchor_from_path(traceability) != "#figure-traceability-matrix"
        ):
            issues.append(f"{plot_key}:traceability_matrix:not_final_report_anchor")
    return issues


def _per_figure_interpretation_target_issues(rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        plot_key = row.get("plot_key", "").strip() or f"row_{row_number}"
        interpretation_target = row.get("figure_interpretations", "").strip()
        anchor = _anchor_from_path(interpretation_target)
        if not anchor:
            issues.append(f"{plot_key}:figure_interpretations:missing_per_figure_anchor")
            continue
        if plot_key.lower() not in anchor.lower():
            issues.append(f"{plot_key}:figure_interpretations:anchor_not_plot_specific:{anchor}")
    return issues


def _markdown_link_issues(figure_gallery: Path, rows: list[dict[str, str]]) -> list[str]:
    markdown_path = figure_gallery.with_suffix(".md")
    if not markdown_path.exists():
        return [f"{markdown_path}:missing_markdown"]
    text = markdown_path.read_text(encoding="utf-8")
    issues: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        plot_key = row.get("plot_key", "").strip() or f"row_{row_number}"
        for column, label in MARKDOWN_LINK_LABELS.items():
            target = row.get(column, "").strip()
            if not target:
                issues.append(f"{plot_key}:{column}:missing_target")
                continue
            expected = f"[{label}]({target})"
            if expected not in text:
                issues.append(f"{plot_key}:{column}:missing_markdown_link")
    return issues


def _plot_format_issue(plot_key: str, column: str, indexed_path: str, resolved: Path) -> str | None:
    suffix = resolved.suffix.lower()
    try:
        header = resolved.read_bytes()[:256]
    except OSError:
        return f"{plot_key}:{column}:unreadable:{indexed_path}"
    if suffix == ".pdf" and not header.startswith(b"%PDF"):
        return f"{plot_key}:{column}:invalid_pdf:{indexed_path}"
    if suffix == ".png" and not header.startswith(b"\x89PNG\r\n\x1a\n"):
        return f"{plot_key}:{column}:invalid_png:{indexed_path}"
    if suffix == ".svg":
        stripped = header.lstrip()
        if not (stripped.startswith(b"<svg") or stripped.startswith(b"<?xml")):
            return f"{plot_key}:{column}:invalid_svg:{indexed_path}"
    return None


def _manifest_expected_plot_path(plot_manifest: Path, manifest_path: str) -> str:
    path = Path(manifest_path)
    if path.is_absolute():
        return str(path.resolve())
    return str((plot_manifest.parent.parent / path).resolve())


def _manifest_coverage_issues(
    rows: list[dict[str, str]],
    plot_manifests: dict[str, Path],
) -> list[str]:
    if not plot_manifests:
        return []
    gallery_by_key = {
        (row.get("branch", "").strip(), row.get("plot_key", "").strip()): row
        for row in rows
        if row.get("branch", "").strip() and row.get("plot_key", "").strip()
    }
    issues: list[str] = []
    for branch, plot_manifest in plot_manifests.items():
        manifest_rows = read_tsv(plot_manifest)
        if not manifest_rows:
            issues.append(f"{branch}:plot_manifest:no_rows")
            continue
        for manifest_row in manifest_rows:
            plot_key = manifest_row.get("plot_key", "").strip()
            if not plot_key:
                issues.append(f"{branch}:plot_manifest:missing_plot_key")
                continue
            gallery_row = gallery_by_key.get((branch, plot_key))
            if gallery_row is None:
                issues.append(f"{branch}:{plot_key}:missing_gallery_row")
                continue
            manifest_plot = _manifest_expected_plot_path(plot_manifest, manifest_row.get("path", "").strip())
            gallery_plot = str(_resolve_path(plot_manifest, gallery_row.get("plot_path", "").strip()).resolve())
            if Path(gallery_plot) != Path(manifest_plot):
                issues.append(f"{branch}:{plot_key}:plot_path_mismatch:{gallery_row.get('plot_path', '')}")
    return issues


def audit_figure_gallery(
    figure_gallery: Path,
    plot_manifests: dict[str, Path] | None = None,
) -> list[dict[str, str]]:
    rows = read_tsv(figure_gallery)
    column_issues = _required_column_issues(rows)
    link_issues = _linked_file_issues(figure_gallery, rows) if not column_issues else []
    traceability_target_issues = _traceability_target_issues(figure_gallery, rows) if not column_issues else []
    per_figure_interpretation_target_issues = (
        _per_figure_interpretation_target_issues(rows) if not column_issues else []
    )
    markdown_link_issues = _markdown_link_issues(figure_gallery, rows) if not column_issues else []
    coverage_issues = (
        _manifest_coverage_issues(rows, plot_manifests or {}) if not column_issues else []
    )
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
            "figure gallery linked PDF/PNG plot, interpretation, version, report, and traceability targets exist with valid plot file signatures"
            if not link_issues
            else "missing, empty, or unresolved figure gallery targets: " + ", ".join(link_issues),
        ),
        _row(
            "figure_gallery_traceability_targets",
            not traceability_target_issues,
            str(figure_gallery),
            "figure gallery traceability_matrix values point to final_report.md#figure-traceability-matrix"
            if not traceability_target_issues
            else "invalid figure gallery traceability targets: " + ", ".join(traceability_target_issues),
        ),
        _row(
            "figure_gallery_per_figure_interpretation_targets",
            not per_figure_interpretation_target_issues,
            str(figure_gallery),
            "figure gallery interpretation links point to per-figure close-reading anchors"
            if not per_figure_interpretation_target_issues
            else "missing or non-specific figure interpretation anchors: "
            + ", ".join(per_figure_interpretation_target_issues),
        ),
        _row(
            "figure_gallery_markdown_links",
            not markdown_link_issues,
            str(figure_gallery.with_suffix(".md")),
            "figure gallery Markdown exposes clickable PDF, PNG, close-reading, version, final-report, and traceability links"
            if not markdown_link_issues
            else "missing clickable figure gallery Markdown links: " + ", ".join(markdown_link_issues),
        ),
        _row(
            "figure_gallery_manifest_coverage",
            not coverage_issues,
            "; ".join(f"{branch}={path}" for branch, path in sorted((plot_manifests or {}).items()))
            if plot_manifests
            else str(figure_gallery),
            "figure gallery covers all registered standard/WGD plot_manifest rows"
            if not coverage_issues
            else "missing or mismatched plot_manifest gallery rows: " + ", ".join(coverage_issues),
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
    parser.add_argument(
        "--plot-manifest",
        action="append",
        default=[],
        metavar="BRANCH=PATH",
        help="optional branch=plot_manifest.tsv coverage source; repeat for standard and WGD",
    )
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    plot_manifests = {}
    for item in args.plot_manifest:
        if "=" not in item:
            raise SystemExit(f"--plot-manifest must be BRANCH=PATH, got: {item}")
        branch, path = item.split("=", 1)
        plot_manifests[branch] = Path(path)
    rows = audit_figure_gallery(args.figure_gallery, plot_manifests=plot_manifests)
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)
    raise SystemExit(0 if summarize_audit(rows)["complete"] else 1)


if __name__ == "__main__":
    main()
