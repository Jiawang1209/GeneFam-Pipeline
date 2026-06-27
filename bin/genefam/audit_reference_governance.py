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
            "status": "gitignore_reference",
            "count": "1" if summary["gitignore_reference"] else "0",
            "paths": "Reference/" if summary["gitignore_reference"] else "missing Reference/ ignore rule",
        },
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
    ignored = bool(summary["gitignore_reference"])
    lines = [
        "# Reference Governance Audit",
        "",
        f"Reference/ ignored: {'yes' if ignored else 'no'}",
        f"Tracked changes: {len(tracked)}",
        f"Untracked reference files: {len(untracked)}",
        "",
        "Tracked Reference/ changes are release-blocking. Reference/ must also be ignored so paper PDFs, source data, and plotting templates are not accidentally staged.",
        "",
    ]
    if not ignored:
        lines.extend(
            [
                "Add `Reference/` to `.gitignore` before treating the repository as release-ready.",
                "",
            ]
        )
    lines.extend(["## Tracked Changes", ""])
    lines.extend(f"- `{path}`" for path in tracked)
    if not tracked:
        lines.append("- none")
    lines.extend(["", "## Untracked Reference Files", ""])
    lines.extend(f"- `{path}`" for path in untracked)
    if not untracked:
        lines.append("- none")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def reference_is_ignored(gitignore_path: Path) -> bool:
    if not gitignore_path.exists():
        return False
    patterns = {
        line.strip()
        for line in gitignore_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    return bool({"Reference/", "/Reference/", "Reference/**", "/Reference/**"} & patterns)


def run_audit(lines: list[str], outdir: Path, gitignore_path: Path = Path(".gitignore")) -> int:
    summary = summarize_status(lines)
    summary["gitignore_reference"] = ["Reference/"] if reference_is_ignored(gitignore_path) else []
    write_tsv(rows_from_summary(summary), outdir / "reference_governance.tsv")
    write_markdown(summary, outdir / "reference_governance.md")
    return 1 if summary["tracked_changes"] or not summary["gitignore_reference"] else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--status-line",
        action="append",
        default=None,
        help="Porcelain status line for tests; when omitted, git status is used.",
    )
    parser.add_argument("--gitignore-path", default=Path(".gitignore"), type=Path)
    parser.add_argument("--outdir", default=Path("results/reference_governance"), type=Path)
    args = parser.parse_args()

    lines = args.status_line if args.status_line is not None else git_reference_status()
    sys.exit(run_audit(lines, args.outdir, args.gitignore_path))


if __name__ == "__main__":
    main()
