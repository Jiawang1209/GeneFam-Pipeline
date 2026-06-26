#!/usr/bin/env python3
"""Audit command availability for running GeneFam-Pipeline end to end."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable


FIELDNAMES = ["command", "status", "path", "requirement"]
DEFAULT_COMMANDS = [
    "nextflow",
    "conda",
    "/usr/local/bin/R",
    "docker",
    "apptainer",
    "hmmsearch",
    "diamond",
    "mafft",
    "FastTree",
    "iqtree2",
    "meme",
]
OPTIONAL_COMMANDS = {"docker", "apptainer"}
CONDA_SCOPED_COMMANDS = {"nextflow", "hmmsearch", "diamond", "mafft", "FastTree", "fasttree", "iqtree2", "iqtree", "meme"}
COMMAND_ALIASES = {"iqtree2": ["iqtree"]}


def conda_which(env_name: str, command: str) -> str:
    if "/" in command or command not in CONDA_SCOPED_COMMANDS or not shutil.which("conda"):
        return ""
    completed = subprocess.run(
        [
            "conda",
            "run",
            "-n",
            env_name,
            "python",
            "-c",
            "import shutil, sys; print(shutil.which(sys.argv[1]) or '')",
            command,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip().splitlines()[-1] if completed.stdout.strip() else ""


def audit_commands(
    required_commands: list[str],
    which: Callable[[str], str | None] = shutil.which,
    conda_env: str | None = None,
    conda_which: Callable[[str, str], str | None] | None = None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    conda_lookup = conda_which or globals()["conda_which"]
    for command in required_commands:
        requirement = "optional" if command in OPTIONAL_COMMANDS else "required"
        candidates = [command, *COMMAND_ALIASES.get(command, [])]
        path = ""
        for candidate in candidates:
            path = which(candidate) or ""
            if path:
                break
        if path:
            rows.append({"command": command, "status": "available", "path": path, "requirement": requirement})
            continue
        conda_path = ""
        if conda_env:
            for candidate in candidates:
                conda_path = conda_lookup(conda_env, candidate) or ""
                if conda_path:
                    break
        if conda_path:
            rows.append(
                {
                    "command": command,
                    "status": "available_in_conda",
                    "path": f"{conda_env}:{conda_path}",
                    "requirement": requirement,
                }
            )
            continue
        rows.append({"command": command, "status": "missing", "path": "", "requirement": requirement})
    return rows


def summarize_status(rows: list[dict[str, str]]) -> dict[str, int | bool]:
    available = sum(1 for row in rows if row["status"].startswith("available"))
    missing = sum(1 for row in rows if row["status"] == "missing")
    missing_required = sum(
        1 for row in rows if row["status"] == "missing" and row.get("requirement", "required") == "required"
    )
    missing_optional = sum(
        1 for row in rows if row["status"] == "missing" and row.get("requirement", "required") == "optional"
    )
    return {
        "available": available,
        "missing": missing,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "ready": missing_required == 0,
    }


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", action="append", default=[], help="Command or absolute binary path to check")
    parser.add_argument("--conda-env", default=None, help="Optional Conda environment to inspect when PATH misses")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    commands = args.command or DEFAULT_COMMANDS
    rows = audit_commands(commands, conda_env=args.conda_env)
    write_tsv(rows, args.out)
    summary = summarize_status(rows)
    sys.exit(0 if summary["ready"] else 1)


if __name__ == "__main__":
    main()
