#!/usr/bin/env python3
"""Collect software and R-package versions for report methods sections."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path
from typing import Callable


FIELDNAMES = ["component", "kind", "version", "status", "source"]
DEFAULT_TOOL_COMMANDS = {
    "Nextflow": ["nextflow", "-version"],
    "HMMER": ["hmmsearch", "-h"],
    "DIAMOND": ["diamond", "--version"],
    "MAFFT": ["mafft", "--version"],
    "FastTree": ["FastTree", "-help"],
    "IQ-TREE": [["iqtree2", "--version"], ["iqtree", "--version"]],
    "MEME": ["meme", "-version"],
    "MCScanX": ["MCScanX"],
    "KaKs_Calculator": ["KaKs_Calculator", "-h"],
    "R": ["/usr/local/bin/R", "--version"],
}
DEFAULT_R_PACKAGES = ["ggplot2", "pheatmap", "circlize", "ggtree", "treeio", "ggNetView"]


def _run_command(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    return completed.returncode, "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()


def _detect_r_package(package: str, r_bin: str) -> str | None:
    expr = f'cat(as.character(utils::packageVersion("{package}")))'
    completed = subprocess.run([r_bin, "--vanilla", "--slave", "-e", expr], check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None


def _first_version_line(output: str) -> str:
    candidates = [line.strip() for line in output.splitlines() if line.strip()]
    version_like_words = ("version", "v", "release", "build")
    for line in candidates:
        normalized = line.lower()
        if re.search(r"\d+(?:\.\d+)+", line) and any(word in normalized for word in version_like_words):
            return line[:160]
    for line in candidates:
        if re.search(r"\d+(?:\.\d+)+", line):
            return line[:160]
    for line in output.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:160]
    return "version_not_detected"


def _command_options(command: list[str] | list[list[str]]) -> list[list[str]]:
    if command and isinstance(command[0], list):
        return command  # type: ignore[return-value]
    return [command]  # type: ignore[list-item]


def _run_first_available_command(
    command_options: list[list[str]],
    command_runner: Callable[[list[str]], tuple[int, str]],
) -> tuple[list[str], int, str]:
    last_command = command_options[-1]
    for command in command_options:
        try:
            exit_code, output = command_runner(command)
        except FileNotFoundError:
            exit_code, output = 127, ""
        if exit_code == 0 and output.strip():
            return command, exit_code, output
        last_command = command
    return last_command, exit_code, output


def collect_versions(
    *,
    command_runner: Callable[[list[str]], tuple[int, str]] | None = None,
    r_package_runner: Callable[[str], str | None] | None = None,
    tool_commands: dict[str, list[str] | list[list[str]]] | None = None,
    r_packages: list[str] | None = None,
) -> list[dict[str, str]]:
    command_runner = command_runner or _run_command
    tool_commands = DEFAULT_TOOL_COMMANDS if tool_commands is None else tool_commands
    r_packages = DEFAULT_R_PACKAGES if r_packages is None else r_packages
    rows: list[dict[str, str]] = []

    for component, command in tool_commands.items():
        used_command, exit_code, output = _run_first_available_command(_command_options(command), command_runner)
        detected = exit_code == 0 and bool(output.strip())
        rows.append(
            {
                "component": component,
                "kind": "command",
                "version": _first_version_line(output) if detected else "version_not_detected",
                "status": "detected" if detected else "version_not_detected",
                "source": " ".join(used_command),
            }
        )

    if r_package_runner is None:
        r_package_runner = lambda package: _detect_r_package(package, "/usr/local/bin/R")
    for package in r_packages:
        version = r_package_runner(package)
        rows.append(
            {
                "component": package,
                "kind": "R_package",
                "version": version or "version_not_detected",
                "status": "detected" if version else "version_not_detected",
                "source": f'packageVersion("{package}")',
            }
        )
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    args = parser.parse_args()

    rows = collect_versions(r_package_runner=lambda package: _detect_r_package(package, args.r_bin))
    write_tsv(rows, args.out)


if __name__ == "__main__":
    main()
