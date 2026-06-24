#!/usr/bin/env python3
"""Run or diagnose the Nextflow WGD/named-event smoke path."""

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
WGD_EVENT_ARGS = "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta"


def expected_published_outputs(wgd_outdir: Path) -> list[Path]:
    return [
        wgd_outdir / "tables/normalized_duplicate_types.tsv",
        wgd_outdir / "tables/family_duplicate_classification.tsv",
        wgd_outdir / "tables/wgd_layers.tsv",
        wgd_outdir / "tables/wgd_event_evidence.tsv",
        wgd_outdir / "tables/family_wgd_event_membership.tsv",
        wgd_outdir / "tables/family_event_retention_summary.tsv",
        wgd_outdir / "tables/retention_enrichment.tsv",
        wgd_outdir / "report/report_index.tsv",
        wgd_outdir / "report/final_report.md",
    ]


def write_tsv(rows: list[dict[str, str]], fieldnames: list[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_smoke_inputs(inputs_dir: Path) -> dict[str, Path]:
    family_members = [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT_ALPHA1"},
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT_ALPHA2"},
        {"species_id": "Brassica_rapa", "gene_id": "BR_BETA1"},
        {"species_id": "Brassica_rapa", "gene_id": "BR_BETA2"},
        {"species_id": "Brassica_rapa", "gene_id": "BR_THETA1"},
        {"species_id": "Brassica_rapa", "gene_id": "BR_THETA2"},
        {"species_id": "Vitis_vinifera", "gene_id": "VV_GAMMA1"},
        {"species_id": "Vitis_vinifera", "gene_id": "VV_GAMMA2"},
    ]
    duplicates = [{"gene_id": row["gene_id"], "duplicate_type": "wgd"} for row in family_members]
    duplicates.extend(
        [
            {"gene_id": "BG_TANDEM1", "duplicate_type": "tandem"},
            {"gene_id": "BG_TANDEM2", "duplicate_type": "tandem"},
            {"gene_id": "BG_DISPERSED1", "duplicate_type": "dispersed"},
            {"gene_id": "BG_SINGLETON1", "duplicate_type": "singleton"},
        ]
    )
    kaks_pairs = [
        {"gene_a": "AT_ALPHA1", "gene_b": "AT_ALPHA2", "ks": "0.12"},
        {"gene_a": "BR_BETA1", "gene_b": "BR_BETA2", "ks": "0.55"},
        {"gene_a": "VV_GAMMA1", "gene_b": "VV_GAMMA2", "ks": "1.20"},
        {"gene_a": "BR_THETA1", "gene_b": "BR_THETA2", "ks": "1.80"},
    ]
    paths = {
        "family_members": inputs_dir / "family_members.tsv",
        "duplicates": inputs_dir / "duplicates.tsv",
        "kaks_pairs": inputs_dir / "kaks_pairs.tsv",
    }
    write_tsv(family_members, ["species_id", "gene_id"], paths["family_members"])
    write_tsv(duplicates, ["gene_id", "duplicate_type"], paths["duplicates"])
    write_tsv(kaks_pairs, ["gene_a", "gene_b", "ks"], paths["kaks_pairs"])
    return paths


def build_nextflow_command(
    nextflow_bin: str,
    duplicates: str,
    family_members: str,
    kaks_pairs: str,
    events_config: str,
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
            "configs/example.config.yaml",
            "--run_duplication_retention",
            "true",
            "--duplicates",
            duplicates,
            "--family_members",
            family_members,
            "--kaks_pairs",
            kaks_pairs,
            "--events_config",
            events_config,
            "--ks_bins",
            "0.3,0.8,1.5",
            "--wgd_event_args",
            WGD_EVENT_ARGS,
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
        "# Nextflow WGD Event Smoke",
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


def run_nextflow_wgd_smoke(
    nextflow_bin: str,
    events_config: str,
    outdir: Path,
    conda_env: str | None = None,
) -> dict[str, str]:
    inputs = write_smoke_inputs(outdir / "inputs")
    resolved_nextflow = resolve_nextflow_binary(nextflow_bin, conda_env=conda_env)
    command_nextflow = resolved_nextflow or nextflow_bin
    profile = "activated" if conda_env and resolved_nextflow else None
    command = build_nextflow_command(
        nextflow_bin=command_nextflow,
        duplicates=str(inputs["duplicates"]),
        family_members=str(inputs["family_members"]),
        kaks_pairs=str(inputs["kaks_pairs"]),
        events_config=events_config,
        outdir=str(outdir / "wgd"),
        profile=profile,
    )
    if not resolved_nextflow:
        return {
            "check": "nextflow_wgd_events",
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
    missing_outputs = [path for path in expected_published_outputs(outdir / "wgd") if not path.exists()]
    passed = completed.returncode == 0 and not missing_outputs
    if completed.returncode == 0 and missing_outputs:
        output = "\n".join(["Missing published outputs:", *[str(path) for path in missing_outputs], output])
    return {
        "check": "nextflow_wgd_events",
        "status": "passed" if passed else "failed",
        "exit_code": str(completed.returncode),
        "command": " ".join(command),
        "note": " | ".join(line.strip() for line in output.splitlines() if line.strip())[:500],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nextflow-bin", default="nextflow")
    parser.add_argument("--conda-env", default=None)
    parser.add_argument("--events-config", default="configs/wgd_events.brassicaceae.yaml")
    parser.add_argument("--outdir", default=Path("results/nextflow_wgd_smoke"), type=Path)
    args = parser.parse_args()
    row = run_nextflow_wgd_smoke(
        args.nextflow_bin,
        args.events_config,
        args.outdir,
        conda_env=args.conda_env,
    )
    _write_tsv(row, args.outdir / "nextflow_wgd_smoke.tsv")
    _write_markdown(row, args.outdir / "nextflow_wgd_smoke.md")
    sys.exit(0 if row["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
