#!/usr/bin/env python3
"""Run or diagnose the Nextflow standard identification smoke path."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.run_nextflow_smoke import resolve_nextflow_binary


FIELDNAMES = ["check", "status", "exit_code", "command", "note"]


def build_nextflow_command(
    nextflow_bin: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: str,
    profile: str | None = None,
) -> list[str]:
    command = [
        nextflow_bin,
        "run",
        "workflows/main.nf",
        "-c",
        "workflows/nextflow.config",
    ]
    if profile:
        command.extend(["-profile", profile])
    command.extend(
        [
            "--config",
            config,
            "--groups",
            groups,
            "--run_identification",
            "true",
            "--mock_external_tools",
            "true",
            "--mock_evidence_dir",
            mock_evidence_dir,
            "--outdir",
            outdir,
        ]
    )
    return command


def _write_tsv(row: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerow(row)


def _write_markdown(row: dict[str, str], out_path: Path) -> None:
    lines = [
        "# Nextflow Standard Branch Smoke",
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


def run_nextflow_standard_smoke(
    nextflow_bin: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: Path,
    conda_env: str | None = None,
) -> dict[str, str]:
    resolved_nextflow = resolve_nextflow_binary(nextflow_bin, conda_env=conda_env)
    command_nextflow = resolved_nextflow or nextflow_bin
    profile = "activated" if conda_env and resolved_nextflow else None
    command = build_nextflow_command(
        nextflow_bin=command_nextflow,
        config=config,
        groups=groups,
        mock_evidence_dir=mock_evidence_dir,
        outdir=str(outdir / "standard"),
        profile=profile,
    )
    if not resolved_nextflow:
        return {
            "check": "nextflow_standard_identification",
            "status": "missing_nextflow",
            "exit_code": "127",
            "command": " ".join(command),
            "note": "nextflow was not found on PATH or in the requested Conda environment; run the runtime bootstrap plan before this smoke can execute.",
        }
    env = os.environ.copy()
    if conda_env:
        env["PATH"] = f"{Path(resolved_nextflow).parent}:{env.get('PATH', '')}"
        env["CONDA_DEFAULT_ENV"] = conda_env
    completed = subprocess.run(command, check=False, capture_output=True, text=True, env=env)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return {
        "check": "nextflow_standard_identification",
        "status": "passed" if completed.returncode == 0 else "failed",
        "exit_code": str(completed.returncode),
        "command": " ".join(command),
        "note": " | ".join(line.strip() for line in output.splitlines() if line.strip())[:500],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nextflow-bin", default="nextflow")
    parser.add_argument("--conda-env", default=None)
    parser.add_argument("--config", default="configs/example.config.yaml")
    parser.add_argument("--groups", default="configs/species_groups.yaml")
    parser.add_argument("--mock-evidence-dir", default="tests/fixtures/mock_evidence")
    parser.add_argument("--outdir", default=Path("results/nextflow_standard_smoke"), type=Path)
    args = parser.parse_args()
    row = run_nextflow_standard_smoke(
        args.nextflow_bin,
        args.config,
        args.groups,
        args.mock_evidence_dir,
        args.outdir,
        conda_env=args.conda_env,
    )
    _write_tsv(row, args.outdir / "nextflow_standard_smoke.tsv")
    _write_markdown(row, args.outdir / "nextflow_standard_smoke.md")
    sys.exit(0 if row["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
