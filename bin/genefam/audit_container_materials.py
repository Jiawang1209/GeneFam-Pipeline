#!/usr/bin/env python3
"""Audit static container reproducibility materials before runtime smoke tests."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import yaml


FIELDNAMES = ["check", "status", "note"]


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _row(check: str, condition: bool, note: str) -> dict[str, str]:
    return {"check": check, "status": "passed" if condition else "failed", "note": note}


def _missing(text: str, required: list[str]) -> list[str]:
    return [item for item in required if item not in text]


def _hmm_profile_reference_paths(config_paths: list[Path]) -> list[str]:
    reference_paths: list[str] = []
    for config_path in config_paths:
        if not config_path.exists():
            reference_paths.append(f"{config_path}: missing config")
            continue
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        profiles = ((config.get("gene_family") or {}).get("hmm_profiles") or [])
        for profile in profiles:
            profile_path = str((profile or {}).get("path", ""))
            if profile_path.startswith("Reference/") or profile_path == "Reference":
                reference_paths.append(f"{config_path}: {profile_path}")
    return reference_paths


def audit_container_materials(
    dockerfile: Path,
    linux_env: Path,
    nextflow_config: Path,
    dockerignore: Path,
    example_configs: list[Path] | None = None,
) -> list[dict[str, str]]:
    docker_text = _read(dockerfile)
    env_text = _read(linux_env)
    config_text = _read(nextflow_config)
    dockerignore_text = _read(dockerignore)
    if example_configs is None:
        example_configs = [
            Path("configs/example.config.yaml"),
            Path("configs/manifest.example.yaml"),
            Path("configs/advanced_modules.example.yaml"),
        ]

    docker_env_required = [
        "GeneFamilyFlow.linux-64.conda.yaml",
        "micromamba create -y -f",
        "CONDA_DEFAULT_ENV=GeneFamilyFlow",
        "/opt/conda/envs/GeneFamilyFlow/bin",
    ]
    docker_r_required = [
        "ln -sf /opt/conda/envs/GeneFamilyFlow/bin/R /usr/local/bin/R",
    ]
    linux_toolchain_required = [
        "name: GeneFamilyFlow",
        "nextflow",
        "hmmer",
        "diamond",
        "mafft",
        "iqtree",
        "meme",
        "mcscanx",
        "jcvi",
        "kaks_calculator",
        "r-base",
        "quarto",
    ]
    profile_required = [
        "profiles",
        "docker {",
        "apptainer {",
        "docker.enabled = true",
        "apptainer.enabled = true",
        "process.container = params.container_image",
        "process.container = params.apptainer_image",
        "process.conda = null",
    ]
    image_param_required = [
        'params.container_image = "genefam-pipeline:latest"',
        'params.apptainer_image = "genefam-pipeline_latest.sif"',
    ]
    dockerignore_required = [
        ".git",
        ".nextflow*",
        "work/",
        "results/",
        "__pycache__/",
        ".pytest_cache/",
        "Reference/",
    ]

    checks = [
        (
            "dockerfile_genefamilyflow_env",
            docker_text,
            docker_env_required,
            "Dockerfile creates and exposes the GeneFamilyFlow linux-64 Conda environment.",
        ),
        (
            "dockerfile_usr_local_r",
            docker_text,
            docker_r_required,
            "Dockerfile links GeneFamilyFlow R to /usr/local/bin/R.",
        ),
        (
            "linux_env_full_toolchain",
            env_text,
            linux_toolchain_required,
            "Linux Conda environment includes Nextflow, core search/alignment/tree tools, MCScanX/JCVI, Ka/Ks, R, and Quarto.",
        ),
        (
            "nextflow_container_profiles",
            config_text,
            profile_required,
            "Nextflow docker and apptainer profiles disable Conda and use container images.",
        ),
        (
            "container_image_params",
            config_text,
            image_param_required,
            "Nextflow container image names are parameterized for Docker and Apptainer.",
        ),
        (
            "dockerignore_build_context",
            dockerignore_text,
            dockerignore_required,
            ".dockerignore excludes VCS metadata, Nextflow/cache outputs, generated results, Python caches, and Reference source material from container build context.",
        ),
    ]

    rows: list[dict[str, str]] = []
    for check, text, required, success_note in checks:
        missing = _missing(text, required)
        rows.append(
            _row(
                check,
                not missing,
                success_note if not missing else "Missing required snippets: " + ", ".join(missing),
            )
        )
    reference_hmm_paths = _hmm_profile_reference_paths(example_configs)
    rows.append(
        _row(
            "example_config_hmm_profiles_container_safe",
            not reference_hmm_paths,
            "Example HMM profile paths use files that are available in the container build context."
            if not reference_hmm_paths
            else "Reference-backed HMM paths are excluded from the container build context: "
            + "; ".join(reference_hmm_paths),
        )
    )
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    passed = sum(1 for row in rows if row["status"] == "passed")
    failed = sum(1 for row in rows if row["status"] != "passed")
    lines = [
        "# Container Materials Audit",
        "",
        f"Passed: {passed}",
        f"Failed: {failed}",
        "",
        "| check | status | note |",
        "|---|---|---|",
    ]
    for row in rows:
        note = row["note"].replace("|", "\\|")
        lines.append(f"| {row['check']} | {row['status']} | {note} |")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dockerfile", default=Path("Dockerfile"), type=Path)
    parser.add_argument("--linux-env", default=Path("envs/GeneFamilyFlow.linux-64.conda.yaml"), type=Path)
    parser.add_argument("--nextflow-config", default=Path("workflows/nextflow.config"), type=Path)
    parser.add_argument("--dockerignore", default=Path(".dockerignore"), type=Path)
    parser.add_argument(
        "--example-config",
        action="append",
        dest="example_configs",
        type=Path,
        help="Example YAML config to audit for container-safe HMM profile paths. Can be repeated.",
    )
    parser.add_argument("--outdir", default=Path("results/container_materials"), type=Path)
    args = parser.parse_args()

    rows = audit_container_materials(
        dockerfile=args.dockerfile,
        linux_env=args.linux_env,
        nextflow_config=args.nextflow_config,
        dockerignore=args.dockerignore,
        example_configs=args.example_configs,
    )
    write_tsv(rows, args.outdir / "container_materials.tsv")
    write_markdown(rows, args.outdir / "container_materials.md")
    sys.exit(0 if all(row["status"] == "passed" for row in rows) else 1)


if __name__ == "__main__":
    main()
