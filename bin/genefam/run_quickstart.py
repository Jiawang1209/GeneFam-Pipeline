#!/usr/bin/env python3
"""Run the shortest verified local GeneFam-Pipeline handoff."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.run_prepared_wgd_handoff_example import run_prepared_wgd_handoff_example
from bin.genefam.run_standard_smoke import run_standard_smoke


FIELDNAMES = ["step", "status", "path", "note"]


def _status_from_path(path: Path) -> str:
    return "passed" if path.exists() else "failed"


def run_quickstart(
    config: Path,
    groups: Path,
    mock_evidence_dir: Path,
    example_dir: Path,
    events_config: str,
    conda_env: str,
    outdir: Path,
    skip_wgd: bool = False,
    standard_runner: Callable[..., dict[str, Path]] = run_standard_smoke,
    wgd_runner: Callable[..., dict[str, str]] = run_prepared_wgd_handoff_example,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    standard_outdir = outdir / "standard_smoke"
    standard_outputs = standard_runner(config, groups, mock_evidence_dir, standard_outdir)
    standard_report = standard_outputs["standard_final_report"]
    rows.append(
        {
            "step": "standard_branch_smoke",
            "status": _status_from_path(standard_report),
            "path": str(standard_report),
            "note": "family candidates and standard report generated",
        }
    )
    if skip_wgd:
        return rows

    wgd_outdir = outdir / "example_prepared_wgd"
    wgd_row = wgd_runner(
        "nextflow",
        example_dir,
        events_config,
        wgd_outdir,
        conda_env=conda_env,
    )
    wgd_report = wgd_outdir / "report/final_report.md"
    rows.append(
        {
            "step": "prepared_wgd_handoff",
            "status": "passed" if wgd_row.get("status") == "passed" and wgd_report.exists() else "failed",
            "path": str(wgd_report),
            "note": "alpha beta gamma theta evidence generated"
            if wgd_row.get("status") == "passed"
            else wgd_row.get("note", ""),
        }
    )
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    lines = [
        "# GeneFam-Pipeline Quickstart Summary",
        "",
        "| step | status | path | note |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| {step} | {status} | `{path}` | {note} |".format(**row))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=Path("configs/example.config.yaml"), type=Path)
    parser.add_argument("--groups", default=Path("configs/species_groups.yaml"), type=Path)
    parser.add_argument("--mock-evidence-dir", default=Path("tests/fixtures/mock_evidence"), type=Path)
    parser.add_argument("--example-dir", default=Path("examples/prepared_wgd_handoff"), type=Path)
    parser.add_argument("--events-config", default="configs/wgd_events.brassicaceae.yaml")
    parser.add_argument("--conda-env", default="GeneFamilyFlow")
    parser.add_argument("--outdir", default=Path("results/quickstart"), type=Path)
    parser.add_argument("--skip-wgd", action="store_true")
    args = parser.parse_args()
    rows = run_quickstart(
        config=args.config,
        groups=args.groups,
        mock_evidence_dir=args.mock_evidence_dir,
        example_dir=args.example_dir,
        events_config=args.events_config,
        conda_env=args.conda_env,
        outdir=args.outdir,
        skip_wgd=args.skip_wgd,
    )
    write_tsv(rows, args.outdir / "quickstart_summary.tsv")
    write_markdown(rows, args.outdir / "quickstart_summary.md")
    failed = any(row["status"] != "passed" for row in rows)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
