#!/usr/bin/env python3
"""Run or diagnose the Nextflow mock-MVP smoke path."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path


FIELDNAMES = ["check", "status", "exit_code", "command", "note"]


def build_nextflow_command(
    nextflow_bin: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: str,
) -> list[str]:
    return [
        nextflow_bin,
        "run",
        "workflows/main.nf",
        "-c",
        "workflows/nextflow.config",
        "--config",
        config,
        "--groups",
        groups,
        "--mock_mvp",
        "true",
        "--mock_evidence_dir",
        mock_evidence_dir,
        "--outdir",
        outdir,
    ]


def _write_tsv(row: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerow(row)


def _write_markdown(row: dict[str, str], out_path: Path) -> None:
    lines = [
        "# Nextflow Mock MVP Smoke",
        "",
        f"Status: {row['status']}",
        f"Exit code: {row['exit_code']}",
        "",
        "```bash",
        row["command"],
        "```",
        "",
        row["note"],
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def run_nextflow_smoke(
    nextflow_bin: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: Path,
) -> dict[str, str]:
    resolved_nextflow = shutil.which(nextflow_bin) if "/" not in nextflow_bin else nextflow_bin
    command = build_nextflow_command(
        nextflow_bin=nextflow_bin,
        config=config,
        groups=groups,
        mock_evidence_dir=mock_evidence_dir,
        outdir=str(outdir / "mock_mvp"),
    )
    if not resolved_nextflow or not Path(resolved_nextflow).exists():
        return {
            "check": "nextflow_mock_mvp",
            "status": "missing_nextflow",
            "exit_code": "127",
            "command": " ".join(command),
            "note": "nextflow was not found on PATH; run the runtime bootstrap plan before this smoke can execute.",
        }
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return {
        "check": "nextflow_mock_mvp",
        "status": "passed" if completed.returncode == 0 else "failed",
        "exit_code": str(completed.returncode),
        "command": " ".join(command),
        "note": " | ".join(line.strip() for line in output.splitlines() if line.strip())[:500],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nextflow-bin", default="nextflow")
    parser.add_argument("--config", default="configs/example.config.yaml")
    parser.add_argument("--groups", default="configs/species_groups.yaml")
    parser.add_argument("--mock-evidence-dir", default="tests/fixtures/mock_evidence")
    parser.add_argument("--outdir", default=Path("results/nextflow_smoke"), type=Path)
    args = parser.parse_args()
    row = run_nextflow_smoke(args.nextflow_bin, args.config, args.groups, args.mock_evidence_dir, args.outdir)
    _write_tsv(row, args.outdir / "nextflow_smoke.tsv")
    _write_markdown(row, args.outdir / "nextflow_smoke.md")
    sys.exit(0 if row["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
