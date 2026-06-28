#!/usr/bin/env python3
"""Check and optionally execute prepared MCScanX self-run commands."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from pathlib import Path


STATUS_FIELDS = ["status", "execute", "missing_tools", "command", "exit_code", "note"]
REQUIRED_TOOLS = ("MCScanX",)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=STATUS_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def required_tools_for_command(command_text: str) -> list[str]:
    tools = ["MCScanX"]
    if "diamond " in command_text:
        tools.insert(0, "diamond")
    if "makeblastdb" in command_text:
        tools.insert(0, "makeblastdb")
    if "blastp" in command_text and "diamond blastp" not in command_text:
        insert_at = 1 if "makeblastdb" in tools else 0
        tools.insert(insert_at, "blastp")
    deduplicated = []
    for tool in tools:
        if tool not in deduplicated:
            deduplicated.append(tool)
    return deduplicated


def missing_required_tools(command_text: str) -> list[str]:
    return [tool for tool in required_tools_for_command(command_text) if shutil.which(tool) is None]


def run_mcscanx_self(*, prepared_dir: Path, execute: bool = False) -> Path:
    prepared_dir = Path(prepared_dir)
    command_rel = Path("commands") / "mcscanx_self_commands.sh"
    command_path = prepared_dir / command_rel
    status_path = prepared_dir / "mcscanx_execution_status.tsv"
    log_path = prepared_dir / "mcscanx_execution.log"

    if not command_path.exists():
        missing_tools = [tool for tool in REQUIRED_TOOLS if shutil.which(tool) is None]
        write_tsv(
            [
                {
                    "status": "missing_input",
                    "execute": str(execute).lower(),
                    "missing_tools": ",".join(missing_tools),
                    "command": str(command_rel),
                    "exit_code": "",
                    "note": "MCScanX command script was not prepared",
                }
            ],
            status_path,
        )
        return status_path

    command_text = command_path.read_text(encoding="utf-8")
    missing_tools = missing_required_tools(command_text)
    if missing_tools:
        write_tsv(
            [
                {
                    "status": "missing_dependency",
                    "execute": str(execute).lower(),
                    "missing_tools": ",".join(missing_tools),
                    "command": str(command_rel),
                    "exit_code": "",
                    "note": "Missing required executables for MCScanX self run",
                }
            ],
            status_path,
        )
        return status_path

    if not execute:
        write_tsv(
            [
                {
                    "status": "ready_not_executed",
                    "execute": "false",
                    "missing_tools": "",
                    "command": str(command_rel),
                    "exit_code": "",
                    "note": "MCScanX dependencies are available; set mcscanx_execute_self=true to execute self BLAST and MCScanX",
                }
            ],
            status_path,
        )
        return status_path

    completed = subprocess.run(
        ["bash", str(command_rel)],
        cwd=prepared_dir,
        check=False,
        text=True,
        capture_output=True,
    )
    log_path.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8")
    status = "executed" if completed.returncode == 0 else "failed"
    note = "MCScanX self command script executed successfully" if completed.returncode == 0 else "MCScanX self command script failed"
    write_tsv(
        [
            {
                "status": status,
                "execute": "true",
                "missing_tools": "",
                "command": str(command_rel),
                "exit_code": str(completed.returncode),
                "note": note,
            }
        ],
        status_path,
    )
    return status_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared-dir", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    run_mcscanx_self(prepared_dir=args.prepared_dir, execute=args.execute)


if __name__ == "__main__":
    main()
