#!/usr/bin/env python3
"""Run focused Nextflow standard smokes for HMMER-only and DIAMOND-only routing."""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.run_nextflow_standard_smoke import run_nextflow_standard_smoke
from bin.genefam.validate_config import load_config


FIELDNAMES = ["check", "status", "exit_code", "command", "note"]


@dataclass(frozen=True)
class SingleToolConfig:
    name: str
    config_path: Path


def _write_yaml(data: dict, out_path: Path) -> None:
    if yaml is None:
        raise RuntimeError("PyYAML is required to write single-tool smoke configs")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _single_tool_config(base_config: dict, case_name: str, use_hmmer: bool, use_diamond: bool, final_rule: str) -> dict:
    config = dict(base_config)
    config["project"] = dict((base_config.get("project", {}) or {}))
    config["project"]["name"] = f"{config['project'].get('name', 'GeneFam')}_{case_name}"
    config["identification"] = dict((base_config.get("identification", {}) or {}))
    config["identification"]["use_hmmer"] = use_hmmer
    config["identification"]["use_diamond"] = use_diamond
    config["identification"]["final_rule"] = final_rule
    config["dev"] = dict((base_config.get("dev", {}) or {}))
    config["dev"]["mock_external_tools"] = False
    return config


def build_single_tool_configs(base_config_path: str | Path, outdir: Path) -> list[SingleToolConfig]:
    base_config = load_config(Path(base_config_path))
    config_dir = outdir / "configs"
    cases = [
        ("hmmer_only", True, False, "hmmer_only"),
        ("diamond_only", False, True, "union"),
    ]
    written: list[SingleToolConfig] = []
    for case_name, use_hmmer, use_diamond, final_rule in cases:
        out_path = config_dir / f"{case_name}.config.yaml"
        _write_yaml(_single_tool_config(base_config, case_name, use_hmmer, use_diamond, final_rule), out_path)
        written.append(SingleToolConfig(case_name, out_path))
    return written


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    lines = ["# Nextflow Standard Single-Tool Smoke", ""]
    for row in rows:
        lines.extend(
            [
                f"## {row['check']}",
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
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def run_nextflow_single_tool_smoke(
    nextflow_bin: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: Path,
    conda_env: str | None = None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for case in build_single_tool_configs(config, outdir):
        row = run_nextflow_standard_smoke(
            nextflow_bin=nextflow_bin,
            config=str(case.config_path),
            groups=groups,
            mock_evidence_dir=mock_evidence_dir,
            outdir=outdir / case.name,
            conda_env=conda_env,
            stop_after_family_candidates=True,
        )
        row["check"] = f"nextflow_standard_{case.name}"
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nextflow-bin", default="nextflow")
    parser.add_argument("--conda-env", default=None)
    parser.add_argument("--config", default="configs/example.config.yaml")
    parser.add_argument("--groups", default="configs/species_groups.yaml")
    parser.add_argument("--mock-evidence-dir", default="tests/fixtures/mock_evidence")
    parser.add_argument("--outdir", default=Path("results/nextflow_single_tool_smoke"), type=Path)
    args = parser.parse_args()
    rows = run_nextflow_single_tool_smoke(
        args.nextflow_bin,
        args.config,
        args.groups,
        args.mock_evidence_dir,
        args.outdir,
        conda_env=args.conda_env,
    )
    write_tsv(rows, args.outdir / "nextflow_single_tool_smoke.tsv")
    write_markdown(rows, args.outdir / "nextflow_single_tool_smoke.md")
    sys.exit(0 if all(row["status"] == "passed" for row in rows) else 1)


if __name__ == "__main__":
    main()
