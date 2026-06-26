#!/usr/bin/env python3
"""Run or diagnose Nextflow container-profile smoke paths."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.run_nextflow_smoke import build_nextflow_command, resolve_nextflow_binary


FIELDNAMES = ["check", "profile", "status", "exit_code", "command", "note"]
CONTAINER_PROFILES = {"docker": "docker", "apptainer": "apptainer"}


def runtime_command_for_profile(profile: str) -> str:
    if profile not in CONTAINER_PROFILES:
        raise ValueError(f"unsupported container profile: {profile}")
    return CONTAINER_PROFILES[profile]


def build_container_smoke_command(
    nextflow_bin: str,
    profile: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: str,
) -> list[str]:
    return build_nextflow_command(
        nextflow_bin=nextflow_bin,
        config=config,
        groups=groups,
        mock_evidence_dir=mock_evidence_dir,
        outdir=outdir,
        profile=profile,
    )


def _note(output: str) -> str:
    return " | ".join(line.strip() for line in output.splitlines() if line.strip())[:500]


def _missing_runtime_note(profile: str, runtime_command: str) -> str:
    return (
        f"{runtime_command} was not found; install or expose {runtime_command} before verifying the {profile} Nextflow "
        "profile. Next step: run `bash results/readiness/runtime_bootstrap.sh`, then rerun "
        f"`python bin/genefam/run_container_profile_smoke.py --profile {profile} --conda-env GeneFamilyFlow "
        f"--outdir results/container_profile_smoke/{profile}`. Expected diagnostic output: "
        f"`results/container_profile_smoke/{profile}/container_profile_smoke.md`."
    )


def run_container_profile_smoke(
    profile: str,
    nextflow_bin: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: str | Path,
    conda_env: str | None = None,
    which: Callable[[str], str | None] = shutil.which,
    path_exists: Callable[[str], bool] = lambda path: Path(path).exists(),
) -> dict[str, str]:
    runtime_command = runtime_command_for_profile(profile)
    profile_outdir = Path(outdir) / "mock_mvp"
    command = build_container_smoke_command(
        nextflow_bin=nextflow_bin,
        profile=profile,
        config=config,
        groups=groups,
        mock_evidence_dir=mock_evidence_dir,
        outdir=str(profile_outdir),
    )
    if not which(runtime_command):
        return {
            "check": f"{profile}_profile_smoke",
            "profile": profile,
            "status": "missing_runtime",
            "exit_code": "127",
            "command": " ".join(command),
            "note": _missing_runtime_note(profile, runtime_command),
        }

    resolved_nextflow = resolve_nextflow_binary(
        nextflow_bin,
        conda_env=conda_env,
        which=which,
        path_exists=path_exists,
    )
    if not resolved_nextflow:
        return {
            "check": f"{profile}_profile_smoke",
            "profile": profile,
            "status": "missing_nextflow",
            "exit_code": "127",
            "command": " ".join(command),
            "note": "nextflow was not found on PATH or in the requested Conda environment.",
        }

    command = build_container_smoke_command(
        nextflow_bin=resolved_nextflow,
        profile=profile,
        config=config,
        groups=groups,
        mock_evidence_dir=mock_evidence_dir,
        outdir=str(profile_outdir),
    )
    env = os.environ.copy()
    if conda_env:
        env["PATH"] = f"{Path(resolved_nextflow).parent}:{env.get('PATH', '')}"
        env["CONDA_DEFAULT_ENV"] = conda_env
    completed = subprocess.run(command, check=False, capture_output=True, text=True, env=env)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return {
        "check": f"{profile}_profile_smoke",
        "profile": profile,
        "status": "passed" if completed.returncode == 0 else "failed",
        "exit_code": str(completed.returncode),
        "command": " ".join(command),
        "note": _note(output),
    }


def write_tsv(row: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerow(row)


def write_markdown(row: dict[str, str], out_path: Path) -> None:
    lines = [
        "# Container Profile Smoke",
        "",
        f"Profile: {row['profile']}",
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
    parser.add_argument("--profile", choices=sorted(CONTAINER_PROFILES), required=True)
    parser.add_argument("--nextflow-bin", default="nextflow")
    parser.add_argument("--conda-env", default=None)
    parser.add_argument("--config", default="configs/example.config.yaml")
    parser.add_argument("--groups", default="configs/species_groups.yaml")
    parser.add_argument("--mock-evidence-dir", default="tests/fixtures/mock_evidence")
    parser.add_argument("--outdir", default=Path("results/container_profile_smoke"), type=Path)
    args = parser.parse_args()
    row = run_container_profile_smoke(
        profile=args.profile,
        nextflow_bin=args.nextflow_bin,
        config=args.config,
        groups=args.groups,
        mock_evidence_dir=args.mock_evidence_dir,
        outdir=args.outdir,
        conda_env=args.conda_env,
    )
    write_tsv(row, args.outdir / "container_profile_smoke.tsv")
    write_markdown(row, args.outdir / "container_profile_smoke.md")
    print(row["note"])
    sys.exit(0 if row["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
