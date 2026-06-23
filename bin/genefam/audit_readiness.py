#!/usr/bin/env python3
"""Audit command availability for running GeneFam-Pipeline end to end."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from pathlib import Path
from typing import Callable


FIELDNAMES = ["command", "status", "path"]
DEFAULT_COMMANDS = [
    "nextflow",
    "conda",
    "/usr/local/bin/R",
    "docker",
    "apptainer",
    "hmmsearch",
    "diamond",
    "mafft",
    "iqtree2",
    "meme",
]


def audit_commands(
    required_commands: list[str],
    which: Callable[[str], str | None] = shutil.which,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for command in required_commands:
        path = which(command) or ""
        rows.append({"command": command, "status": "available" if path else "missing", "path": path})
    return rows


def summarize_status(rows: list[dict[str, str]]) -> dict[str, int | bool]:
    available = sum(1 for row in rows if row["status"] == "available")
    missing = sum(1 for row in rows if row["status"] == "missing")
    return {"available": available, "missing": missing, "ready": missing == 0}


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", action="append", default=[], help="Command or absolute binary path to check")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    commands = args.command or DEFAULT_COMMANDS
    rows = audit_commands(commands)
    write_tsv(rows, args.out)
    summary = summarize_status(rows)
    sys.exit(0 if summary["ready"] else 1)


if __name__ == "__main__":
    main()
