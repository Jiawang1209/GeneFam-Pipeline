#!/usr/bin/env python3
"""Run or diagnose the Nextflow WGD/named-event smoke path."""

from __future__ import annotations

import argparse
import csv
import os
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.run_nextflow_smoke import resolve_nextflow_binary


FIELDNAMES = ["check", "status", "exit_code", "command", "note"]
WGD_EVENT_ARGS = "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta"


def format_command(command: list[str]) -> str:
    return shlex.join(command)


def expected_published_outputs(wgd_outdir: Path, raw_handoff: bool = False) -> list[Path]:
    outputs = [
        wgd_outdir / "tables/wgd_run_config_snapshot.tsv",
        wgd_outdir / "tables/normalized_duplicate_types.tsv",
        wgd_outdir / "tables/family_duplicate_classification.tsv",
        wgd_outdir / "tables/wgd_layers.tsv",
        wgd_outdir / "tables/wgd_event_evidence.tsv",
        wgd_outdir / "tables/family_wgd_event_membership.tsv",
        wgd_outdir / "tables/family_event_retention_summary.tsv",
        wgd_outdir / "tables/retention_enrichment.tsv",
        wgd_outdir / "plots/ks_distribution.pdf",
        wgd_outdir / "plots/ks_distribution.png",
        wgd_outdir / "tables/pangenome_kaks.tsv",
        wgd_outdir / "tables/pangenome_kaks_summary.tsv",
        wgd_outdir / "tables/pangenome_kaks_skipped.tsv",
        wgd_outdir / "plots/pangenome_kaks.pdf",
        wgd_outdir / "plots/pangenome_kaks.png",
        wgd_outdir / "report/report_index.tsv",
        wgd_outdir / "report/plot_manifest.tsv",
        wgd_outdir / "report/software_versions.tsv",
        wgd_outdir / "report/figure_interpretations.tsv",
        wgd_outdir / "report/figure_interpretations.md",
        wgd_outdir / "report/final_report.md",
    ]
    if raw_handoff:
        outputs.extend(
            [
                wgd_outdir / "mcscanx_kaks_handoff/tables/syntenic_pairs.tsv",
                wgd_outdir / "mcscanx_kaks_handoff/tables/duplicate_types.tsv",
                wgd_outdir / "mcscanx_kaks_handoff/tables/normalized_kaks.tsv",
                wgd_outdir / "mcscanx_kaks_handoff/tables/kaks_pairs.tsv",
                wgd_outdir / "mcscanx_kaks_handoff/tables/kaks_pair_manifest.tsv",
                wgd_outdir / "mcscanx_kaks_handoff/mcscanx_kaks_handoff.md",
            ]
        )
    return outputs


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
        "pangenome_classes": inputs_dir / "pangenome_classes.tsv",
    }
    write_tsv(family_members, ["species_id", "gene_id"], paths["family_members"])
    write_tsv(duplicates, ["gene_id", "duplicate_type"], paths["duplicates"])
    write_tsv(kaks_pairs, ["gene_a", "gene_b", "ks"], paths["kaks_pairs"])
    write_tsv(
        [
            {"gene_id": "AT_ALPHA1", "pangenome_class": "core"},
            {"gene_id": "AT_ALPHA2", "pangenome_class": "core"},
            {"gene_id": "BR_BETA1", "pangenome_class": "dispensable"},
            {"gene_id": "BR_BETA2", "pangenome_class": "dispensable"},
            {"gene_id": "VV_GAMMA1", "pangenome_class": "core"},
            {"gene_id": "VV_GAMMA2", "pangenome_class": "core"},
            {"gene_id": "BR_THETA1", "pangenome_class": "rare"},
            {"gene_id": "BR_THETA2", "pangenome_class": "rare"},
        ],
        ["gene_id", "pangenome_class"],
        paths["pangenome_classes"],
    )
    return paths


def write_raw_handoff_smoke_inputs(inputs_dir: Path) -> dict[str, Path]:
    family_members = [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010"},
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01020"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA010001"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA010002"},
    ]
    paths = {"family_members": inputs_dir / "family_members.tsv"}
    write_tsv(family_members, ["species_id", "gene_id"], paths["family_members"])
    return paths


def build_nextflow_command(
    nextflow_bin: str,
    family_members: str,
    events_config: str,
    outdir: str,
    duplicates: str | None = None,
    kaks_pairs: str | None = None,
    mcscanx_collinearity: str | None = None,
    kaks_results: str | None = None,
    pangenome_classes: str | None = None,
    mcscanx_cds_a: str | None = None,
    mcscanx_cds_b: str | None = None,
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
        ]
    )
    if mcscanx_collinearity and kaks_results:
        command.extend(
            [
                "--family_members",
                family_members,
                "--mcscanx_collinearity",
                mcscanx_collinearity,
                "--kaks_results",
                kaks_results,
            ]
        )
        if mcscanx_cds_a and mcscanx_cds_b:
            command.extend(["--mcscanx_cds_a", mcscanx_cds_a, "--mcscanx_cds_b", mcscanx_cds_b])
    elif duplicates and kaks_pairs:
        command.extend(
            [
                "--duplicates",
                duplicates,
                "--family_members",
                family_members,
                "--kaks_pairs",
                kaks_pairs,
            ]
        )
    else:
        raise ValueError("Provide either duplicates/kaks_pairs or mcscanx_collinearity/kaks_results")
    if pangenome_classes:
        command.extend(["--pangenome_classes", pangenome_classes])
    command.extend(
        [
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
    mode: str = "prepared",
) -> dict[str, str]:
    if mode == "raw-mcscanx-kaks":
        inputs = write_raw_handoff_smoke_inputs(outdir / "inputs")
    else:
        inputs = write_smoke_inputs(outdir / "inputs")
    resolved_nextflow = resolve_nextflow_binary(nextflow_bin, conda_env=conda_env)
    command_nextflow = resolved_nextflow or nextflow_bin
    profile = "activated" if conda_env and resolved_nextflow else None
    if mode == "raw-mcscanx-kaks":
        command = build_nextflow_command(
            nextflow_bin=command_nextflow,
            family_members=str(inputs["family_members"]),
            mcscanx_collinearity="tests/fixtures/mcscanx/sample.collinearity",
            kaks_results="tests/fixtures/kaks/kaks_calculator.tsv",
            events_config=events_config,
            outdir=str(outdir / "wgd"),
            profile=profile,
        )
    else:
        command = build_nextflow_command(
            nextflow_bin=command_nextflow,
            duplicates=str(inputs["duplicates"]),
            family_members=str(inputs["family_members"]),
            kaks_pairs=str(inputs["kaks_pairs"]),
            pangenome_classes=str(inputs["pangenome_classes"]),
            events_config=events_config,
            outdir=str(outdir / "wgd"),
            profile=profile,
        )
    if not resolved_nextflow:
        return {
            "check": "nextflow_wgd_events",
            "status": "missing_nextflow",
            "exit_code": "127",
            "command": format_command(command),
            "note": "nextflow was not found on PATH or in the requested Conda environment; run the runtime bootstrap plan before this smoke can execute.",
        }
    env = os.environ.copy()
    if conda_env:
        env["PATH"] = f"{Path(resolved_nextflow).parent}:{env.get('PATH', '')}"
        env["CONDA_DEFAULT_ENV"] = conda_env
    completed = subprocess.run(command, check=False, capture_output=True, text=True, env=env)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    missing_outputs = [
        path for path in expected_published_outputs(outdir / "wgd", raw_handoff=mode == "raw-mcscanx-kaks") if not path.exists()
    ]
    passed = completed.returncode == 0 and not missing_outputs
    if completed.returncode == 0 and missing_outputs:
        output = "\n".join(["Missing published outputs:", *[str(path) for path in missing_outputs], output])
    return {
        "check": "nextflow_wgd_events",
        "status": "passed" if passed else "failed",
        "exit_code": str(completed.returncode),
        "command": format_command(command),
        "note": " | ".join(line.strip() for line in output.splitlines() if line.strip())[:500],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nextflow-bin", default="nextflow")
    parser.add_argument("--conda-env", default=None)
    parser.add_argument("--events-config", default="configs/wgd_events.brassicaceae.yaml")
    parser.add_argument("--outdir", default=Path("results/nextflow_wgd_smoke"), type=Path)
    parser.add_argument("--mode", choices=["prepared", "raw-mcscanx-kaks"], default="prepared")
    args = parser.parse_args()
    row = run_nextflow_wgd_smoke(
        args.nextflow_bin,
        args.events_config,
        args.outdir,
        conda_env=args.conda_env,
        mode=args.mode,
    )
    _write_tsv(row, args.outdir / "nextflow_wgd_smoke.tsv")
    _write_markdown(row, args.outdir / "nextflow_wgd_smoke.md")
    sys.exit(0 if row["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
