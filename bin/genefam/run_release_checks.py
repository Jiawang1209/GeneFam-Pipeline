#!/usr/bin/env python3
"""Run repository release checks and write TSV/Markdown summaries."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.audit_objective_completion import (
    build_objective_audit,
    read_tsv,
    write_markdown as write_objective_markdown,
    write_tsv as write_objective_tsv,
)


FIELDNAMES = ["check", "required", "status", "exit_code", "command", "note"]


@dataclass(frozen=True)
class CheckSpec:
    name: str
    command: list[str]
    required: bool = True


def default_checks() -> list[CheckSpec]:
    python = sys.executable
    return [
        CheckSpec("pytest", [python, "-m", "pytest", "tests", "-q"]),
        CheckSpec("validate example config", [python, "bin/genefam/validate_config.py", "configs/example.config.yaml"]),
        CheckSpec(
            "validate advanced config",
            [python, "bin/genefam/validate_config.py", "configs/advanced_modules.example.yaml"],
        ),
        CheckSpec(
            "mock MVP",
            [
                python,
                "bin/genefam/run_mock_mvp.py",
                "--config",
                "configs/example.config.yaml",
                "--groups",
                "configs/species_groups.yaml",
                "--mock-evidence-dir",
                "tests/fixtures/mock_evidence",
                "--outdir",
                "results/mock_mvp",
            ],
        ),
        CheckSpec(
            "standard branch smoke",
            [
                python,
                "bin/genefam/run_standard_smoke.py",
                "--config",
                "configs/example.config.yaml",
                "--groups",
                "configs/species_groups.yaml",
                "--mock-evidence-dir",
                "tests/fixtures/mock_evidence",
                "--outdir",
                "results/standard_smoke",
            ],
        ),
        CheckSpec(
            "WGD event smoke",
            [
                python,
                "bin/genefam/run_wgd_smoke.py",
                "--events-config",
                "configs/wgd_events.brassicaceae.yaml",
                "--outdir",
                "results/wgd_smoke",
            ],
        ),
        CheckSpec(
            "Nextflow mock MVP smoke",
            [
                python,
                "bin/genefam/run_nextflow_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/nextflow_smoke",
            ],
        ),
        CheckSpec(
            "Nextflow standard branch smoke",
            [
                python,
                "bin/genefam/run_nextflow_standard_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/nextflow_standard_smoke",
            ],
        ),
        CheckSpec(
            "Nextflow WGD event smoke",
            [
                python,
                "bin/genefam/run_nextflow_wgd_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/nextflow_wgd_smoke",
            ],
        ),
        CheckSpec(
            "prepared WGD handoff example",
            [
                python,
                "bin/genefam/run_prepared_wgd_handoff_example.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--example-dir",
                "examples/prepared_wgd_handoff",
                "--outdir",
                "results/example_prepared_wgd",
            ],
        ),
        CheckSpec(
            "quickstart handoff",
            [
                python,
                "bin/genefam/run_quickstart.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/quickstart",
            ],
        ),
        CheckSpec(
            "readiness audit",
            [
                python,
                "bin/genefam/audit_readiness.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--out",
                "results/readiness/command_readiness.tsv",
            ],
        ),
        CheckSpec(
            "runtime bootstrap plan",
            [
                python,
                "bin/genefam/plan_runtime_bootstrap.py",
                "--readiness",
                "results/readiness/command_readiness.tsv",
                "--outdir",
                "results/readiness",
            ],
        ),
    ]


def quick_checks() -> list[CheckSpec]:
    return [CheckSpec("python self check", [sys.executable, "-c", "print('ok')"])]


def _subprocess_runner(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return completed.returncode, output


def _note(output: str) -> str:
    return " | ".join(line.strip() for line in output.splitlines() if line.strip())[:500]


def run_checks(
    checks: list[CheckSpec],
    runner: Callable[[list[str]], tuple[int, str]] = _subprocess_runner,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for check in checks:
        exit_code, output = runner(check.command)
        rows.append(
            {
                "check": check.name,
                "required": "true" if check.required else "false",
                "status": "passed" if exit_code == 0 else "failed",
                "exit_code": str(exit_code),
                "command": " ".join(check.command),
                "note": _note(output),
            }
        )
    return rows


def summarize_checks(rows: list[dict[str, str]]) -> dict[str, int | bool]:
    passed = sum(1 for row in rows if row["status"] == "passed")
    failed = sum(1 for row in rows if row["status"] == "failed")
    required_failed = any(row["required"] == "true" and row["status"] == "failed" for row in rows)
    return {"passed": passed, "failed": failed, "release_ready": not required_failed}


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    summary = summarize_checks(rows)
    lines = [
        "# GeneFam-Pipeline Release Checks",
        "",
        f"Passed: {summary['passed']}",
        f"Failed: {summary['failed']}",
        f"Release ready: {str(summary['release_ready']).lower()}",
        "",
        "| check | required | status | exit_code | command | note |",
        "|---|---|---|---:|---|---|",
    ]
    for row in rows:
        escaped = {key: _markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {check} | {required} | {status} | {exit_code} | `{command}` | {note} |".format(**escaped)
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_objective_audit(
    rows: list[dict[str, str]],
    readiness_path: Path = Path("results/readiness/command_readiness.tsv"),
    outdir: Path = Path("results/objective_audit"),
) -> bool:
    if not readiness_path.exists():
        return False
    objective_rows = build_objective_audit(rows, read_tsv(readiness_path))
    write_objective_tsv(objective_rows, outdir / "objective_audit.tsv")
    write_objective_markdown(objective_rows, outdir / "objective_audit.md")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default="results/release_checks", type=Path)
    parser.add_argument("--quick-self-check", action="store_true")
    args = parser.parse_args()
    checks = quick_checks() if args.quick_self_check else default_checks()
    rows = run_checks(checks)
    write_tsv(rows, args.outdir / "release_checks.tsv")
    write_markdown(rows, args.outdir / "release_checks.md")
    if not args.quick_self_check:
        write_objective_audit(rows)
    sys.exit(0 if summarize_checks(rows)["release_ready"] else 1)


if __name__ == "__main__":
    main()
