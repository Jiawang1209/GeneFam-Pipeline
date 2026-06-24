#!/usr/bin/env python3
"""Run the prepared standard-to-WGD handoff example through Nextflow."""

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
from bin.genefam.run_nextflow_wgd_smoke import WGD_EVENT_ARGS, expected_published_outputs


FIELDNAMES = ["check", "status", "exit_code", "command", "note"]
EXPECTED_EVENTS = {"alpha", "beta", "gamma", "theta"}


def build_nextflow_command(
    nextflow_bin: str,
    example_dir: Path,
    events_config: str,
    outdir: Path,
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
            "configs/example.config.yaml",
            "--run_duplication_retention",
            "true",
            "--duplicates",
            str(example_dir / "duplicate_types.tsv"),
            "--family_members",
            str(example_dir / "family_candidates.tsv"),
            "--kaks_pairs",
            str(example_dir / "kaks_pairs.tsv"),
            "--events_config",
            events_config,
            "--ks_bins",
            "0.3,0.8,1.5",
            "--wgd_event_args",
            WGD_EVENT_ARGS,
            "--outdir",
            str(outdir),
        ]
    )
    return command


def _read_events(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row.get("event_name", "") for row in csv.DictReader(handle, delimiter="\t")}


def _missing_example_inputs(example_dir: Path) -> list[Path]:
    return [
        path
        for path in [
            example_dir / "family_candidates.tsv",
            example_dir / "duplicate_types.tsv",
            example_dir / "kaks_pairs.tsv",
        ]
        if not path.exists()
    ]


def run_prepared_wgd_handoff_example(
    nextflow_bin: str,
    example_dir: Path,
    events_config: str,
    outdir: Path,
    conda_env: str | None = None,
) -> dict[str, str]:
    missing_inputs = _missing_example_inputs(example_dir)
    resolved_nextflow = resolve_nextflow_binary(nextflow_bin, conda_env=conda_env)
    command_nextflow = resolved_nextflow or nextflow_bin
    profile = "activated" if conda_env and resolved_nextflow else None
    command = build_nextflow_command(command_nextflow, example_dir, events_config, outdir, profile=profile)
    if missing_inputs:
        return {
            "check": "prepared_wgd_handoff_example",
            "status": "missing_inputs",
            "exit_code": "2",
            "command": " ".join(command),
            "note": "Missing example inputs: " + ", ".join(str(path) for path in missing_inputs),
        }
    if not resolved_nextflow:
        return {
            "check": "prepared_wgd_handoff_example",
            "status": "missing_nextflow",
            "exit_code": "127",
            "command": " ".join(command),
            "note": "nextflow was not found on PATH or in the requested Conda environment; run the runtime bootstrap plan before this example can execute.",
        }
    env = os.environ.copy()
    if conda_env:
        env["PATH"] = f"{Path(resolved_nextflow).parent}:{env.get('PATH', '')}"
        env["CONDA_DEFAULT_ENV"] = conda_env
    completed = subprocess.run(command, check=False, capture_output=True, text=True, env=env)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    missing_outputs = [path for path in expected_published_outputs(outdir) if not path.exists()]
    events = _read_events(outdir / "tables/wgd_event_evidence.tsv")
    missing_events = sorted(EXPECTED_EVENTS - events)
    passed = completed.returncode == 0 and not missing_outputs and not missing_events
    note_parts = []
    if missing_outputs:
        note_parts.append("Missing published outputs: " + ", ".join(str(path) for path in missing_outputs))
    if missing_events:
        note_parts.append("Missing named WGD events: " + ", ".join(missing_events))
    if output:
        note_parts.append(output)
    return {
        "check": "prepared_wgd_handoff_example",
        "status": "passed" if passed else "failed",
        "exit_code": str(completed.returncode),
        "command": " ".join(command),
        "note": " | ".join(line.strip() for part in note_parts for line in part.splitlines() if line.strip())[:500],
    }


def _write_tsv(row: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerow(row)


def _write_markdown(row: dict[str, str], out_path: Path) -> None:
    lines = [
        "# Prepared WGD Handoff Example",
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nextflow-bin", default="nextflow")
    parser.add_argument("--conda-env", default=None)
    parser.add_argument("--example-dir", default=Path("examples/prepared_wgd_handoff"), type=Path)
    parser.add_argument("--events-config", default="configs/wgd_events.brassicaceae.yaml")
    parser.add_argument("--outdir", default=Path("results/example_prepared_wgd"), type=Path)
    args = parser.parse_args()
    row = run_prepared_wgd_handoff_example(
        args.nextflow_bin,
        args.example_dir,
        args.events_config,
        args.outdir,
        conda_env=args.conda_env,
    )
    _write_tsv(row, args.outdir / "prepared_wgd_handoff_example.tsv")
    _write_markdown(row, args.outdir / "prepared_wgd_handoff_example.md")
    sys.exit(0 if row["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
