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
from bin.genefam.validate_config import load_config


FIELDNAMES = ["check", "status", "exit_code", "command", "note"]


def _bool_param(value: object) -> str:
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return "true"
        if lowered in {"false", "0", "no", "off"}:
            return "false"
    return str(bool(value)).lower()


def load_standard_params(config_path: Path) -> dict[str, str]:
    config = load_config(config_path)
    identification = config.get("identification", {}) or {}
    dev = config.get("dev", {}) or {}
    return {
        "use_hmmer": _bool_param(identification.get("use_hmmer", True)),
        "use_diamond": _bool_param(identification.get("use_diamond", True)),
        "final_rule": str(identification.get("final_rule", "intersection")),
        "mock_external_tools": _bool_param(dev.get("mock_external_tools", True)),
    }


def expected_published_outputs(standard_outdir: Path) -> list[Path]:
    return [
        standard_outdir / "tables/species_manifest.tsv",
        standard_outdir / "tables/run_config_snapshot.tsv",
        standard_outdir / "tables/family_candidates.tsv",
        standard_outdir / "tables/family_counts.tsv",
        standard_outdir / "tables/alignment_manifest.tsv",
        standard_outdir / "tables/phylogeny_manifest.tsv",
        standard_outdir / "tables/motif_summary.tsv",
        standard_outdir / "tables/chromosome_locations.tsv",
        standard_outdir / "sequences/family_members.faa",
        standard_outdir / "report/report_index.tsv",
        standard_outdir / "report/plot_manifest.tsv",
        standard_outdir / "report/final_report.md",
        standard_outdir / "plots/family_counts.pdf",
        standard_outdir / "plots/family_counts.png",
    ]


def expected_single_tool_outputs(standard_outdir: Path) -> list[Path]:
    return [
        standard_outdir / "tables/species_manifest.tsv",
        standard_outdir / "tables/family_candidates.tsv",
    ]


def build_nextflow_command(
    nextflow_bin: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: str,
    profile: str | None = None,
    use_hmmer: bool | str = True,
    use_diamond: bool | str = True,
    final_rule: str = "intersection",
    mock_external_tools: bool | str = True,
    stop_after_family_candidates: bool | str = False,
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
            "--use_hmmer",
            _bool_param(use_hmmer),
            "--use_diamond",
            _bool_param(use_diamond),
            "--final_rule",
            final_rule,
            "--mock_external_tools",
            _bool_param(mock_external_tools),
            "--standard_stop_after_family_candidates",
            _bool_param(stop_after_family_candidates),
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
    stop_after_family_candidates: bool | str = False,
) -> dict[str, str]:
    resolved_nextflow = resolve_nextflow_binary(nextflow_bin, conda_env=conda_env)
    standard_params = load_standard_params(Path(config))
    command_nextflow = resolved_nextflow or nextflow_bin
    profile = "activated" if conda_env and resolved_nextflow else None
    command = build_nextflow_command(
        nextflow_bin=command_nextflow,
        config=config,
        groups=groups,
        mock_evidence_dir=mock_evidence_dir,
        outdir=str(outdir / "standard"),
        profile=profile,
        stop_after_family_candidates=stop_after_family_candidates,
        **standard_params,
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
    standard_outdir = outdir / "standard"
    expected_outputs = (
        expected_single_tool_outputs(standard_outdir)
        if _bool_param(stop_after_family_candidates) == "true"
        else expected_published_outputs(standard_outdir)
    )
    missing_outputs = [path for path in expected_outputs if not path.exists()]
    passed = completed.returncode == 0 and not missing_outputs
    if completed.returncode == 0 and missing_outputs:
        output = "\n".join(
            [
                output,
                "Missing published outputs:",
                *[str(path) for path in missing_outputs],
            ]
        )
    return {
        "check": "nextflow_standard_identification",
        "status": "passed" if passed else "failed",
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
