#!/usr/bin/env python3
"""Audit that tracked Reference/ files were not changed by development work."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path


FIELDNAMES = ["status", "count", "paths"]


def git_reference_status() -> list[str]:
    completed = subprocess.run(
        ["git", "status", "--porcelain", "--", "Reference"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or "git status failed")
    return [line for line in completed.stdout.splitlines() if line.strip()]


def summarize_status(lines: list[str]) -> dict[str, list[str]]:
    summary = {"tracked_changes": [], "untracked": []}
    for line in lines:
        status = line[:2]
        path = line[3:].strip()
        if status == "??":
            summary["untracked"].append(path)
        else:
            summary["tracked_changes"].append(path)
    return summary


def rows_from_summary(summary: dict[str, list[str]]) -> list[dict[str, str]]:
    return [
        {
            "status": "tracked_changes",
            "count": str(len(summary["tracked_changes"])),
            "paths": "; ".join(summary["tracked_changes"]),
        },
        {
            "status": "untracked",
            "count": str(len(summary["untracked"])),
            "paths": "; ".join(summary["untracked"]),
        },
    ]


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, list[str]], out_path: Path) -> None:
    tracked = summary["tracked_changes"]
    untracked = summary["untracked"]
    lines = [
        "# Reference Governance Audit",
        "",
        f"Tracked changes: {len(tracked)}",
        f"Untracked reference files: {len(untracked)}",
        "",
        "Tracked Reference/ changes are release-blocking. Untracked Reference/ source material is reported but allowed.",
        "",
        "## Tracked Changes",
        "",
    ]
    lines.extend(f"- `{path}`" for path in tracked)
    if not tracked:
        lines.append("- none")
    lines.extend(["", "## Untracked Reference Files", ""])
    lines.extend(f"- `{path}`" for path in untracked)
    if not untracked:
        lines.append("- none")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_audit(lines: list[str], outdir: Path) -> int:
    summary = summarize_status(lines)
    write_tsv(rows_from_summary(summary), outdir / "reference_governance.tsv")
    write_markdown(summary, outdir / "reference_governance.md")
    return 1 if summary["tracked_changes"] else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--status-line",
        action="append",
        default=None,
        help="Porcelain status line for tests; when omitted, git status is used.",
    )
    parser.add_argument("--outdir", default=Path("results/reference_governance"), type=Path)
    args = parser.parse_args()

    lines = args.status_line if args.status_line is not None else git_reference_status()
    sys.exit(run_audit(lines, args.outdir))


if __name__ == "__main__":
    main()
