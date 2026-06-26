#!/usr/bin/env python3
"""Check ggNetView availability for PPI visualization."""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


FIELDNAMES = ["check", "status", "package", "version", "note"]


def detect_ggnetview(r_bin: str, force_missing: bool = False) -> dict[str, str]:
    if force_missing:
        return {
            "check": "ppi_ggnetview",
            "status": "missing_dependency",
            "package": "ggNetView",
            "version": "version_not_detected",
            "note": "Forced missing dependency check for deterministic smoke testing.",
        }
    expr = 'cat(as.character(utils::packageVersion("ggNetView")))'
    completed = subprocess.run([r_bin, "--vanilla", "--slave", "-e", expr], check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        return {
            "check": "ppi_ggnetview",
            "status": "missing_dependency",
            "package": "ggNetView",
            "version": "version_not_detected",
            "note": "ggNetView is not available; PPI plotting should be reported as skipped until installed.",
        }
    return {
        "check": "ppi_ggnetview",
        "status": "ready",
        "package": "ggNetView",
        "version": completed.stdout.strip() or "version_not_detected",
        "note": "ggNetView is available for PPI network visualization.",
    }


def write_tsv(row: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerow(row)


def write_markdown(row: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "\n".join(
            [
                "# ggNetView PPI Smoke",
                "",
                f"Status: {row['status']}",
                f"Package: {row['package']}",
                f"Version: {row['version']}",
                "",
                row["note"],
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/ppi_ggnetview_smoke"), type=Path)
    parser.add_argument("--force-missing", action="store_true")
    args = parser.parse_args()
    row = detect_ggnetview(args.r_bin, force_missing=args.force_missing)
    write_tsv(row, args.outdir / "ppi_ggnetview_smoke.tsv")
    write_markdown(row, args.outdir / "ppi_ggnetview_smoke.md")
    print(f"status\t{row['status']}")


if __name__ == "__main__":
    main()
