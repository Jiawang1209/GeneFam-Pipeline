#!/usr/bin/env python3
"""Run JCVI collinearity commands when the jcvi Python package is available."""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


STATUS_FIELDS = ["status", "command_count", "succeeded_count", "failed_count", "note"]
COMMAND_FIELDS = ["command_index", "command", "status", "exit_code", "note"]


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_status(out_path: Path, status: str, command_count: int, succeeded_count: int, failed_count: int, note: str) -> None:
    write_tsv(
        [
            {
                "status": status,
                "command_count": str(command_count),
                "succeeded_count": str(succeeded_count),
                "failed_count": str(failed_count),
                "note": note,
            }
        ],
        out_path,
        STATUS_FIELDS,
    )


def read_commands(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]


def jcvi_importable(executable: str) -> bool:
    try:
        completed = subprocess.run(
            [executable, "-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('jcvi') else 1)"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False
    return completed.returncode == 0


def run_jcvi_collinearity(
    *,
    jcvi_dir: Path,
    executable: str = "python",
    run: bool = True,
) -> dict[str, Path]:
    jcvi_dir = Path(jcvi_dir)
    outputs = {
        "status": jcvi_dir / "jcvi_run_status.tsv",
        "commands": jcvi_dir / "jcvi_command_status.tsv",
    }
    commands = read_commands(jcvi_dir / "commands" / "jcvi_commands.sh")
    if not commands:
        write_tsv([], outputs["commands"], COMMAND_FIELDS)
        _write_status(outputs["status"], "missing_input", 0, 0, 0, "commands/jcvi_commands.sh not found")
        return outputs

    if not jcvi_importable(executable):
        rows = [
            {
                "command_index": str(index),
                "command": command,
                "status": "not_run",
                "exit_code": "",
                "note": "missing_dependency",
            }
            for index, command in enumerate(commands, start=1)
        ]
        write_tsv(rows, outputs["commands"], COMMAND_FIELDS)
        _write_status(outputs["status"], "missing_dependency", len(commands), 0, 0, f"JCVI Python module is not importable with {executable}")
        return outputs

    succeeded = 0
    failed = 0
    rows: list[dict[str, str]] = []
    for index, command in enumerate(commands, start=1):
        if not run:
            rows.append({"command_index": str(index), "command": command, "status": "planned", "exit_code": "", "note": "run disabled"})
            continue
        rewritten = command.replace("python -m jcvi.", f"{executable} -m jcvi.")
        completed = subprocess.run(rewritten, shell=True, cwd=jcvi_dir, check=False, capture_output=True, text=True)
        if completed.returncode == 0:
            status = "available"
            note = "ok"
            succeeded += 1
        else:
            status = "failed"
            note = (completed.stderr or completed.stdout or f"exit {completed.returncode}").strip().replace("\n", " ")[:500]
            failed += 1
        rows.append({"command_index": str(index), "command": rewritten, "status": status, "exit_code": str(completed.returncode), "note": note})

    write_tsv(rows, outputs["commands"], COMMAND_FIELDS)
    overall = "available" if succeeded and failed == 0 else "partial" if succeeded else "failed"
    _write_status(outputs["status"], overall, len(commands), succeeded, failed, "ok" if failed == 0 else "Some JCVI commands failed")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jcvi-dir", required=True, type=Path)
    parser.add_argument("--python-bin", default="python")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    run_jcvi_collinearity(jcvi_dir=args.jcvi_dir, executable=args.python_bin, run=not args.plan_only)


if __name__ == "__main__":
    main()
