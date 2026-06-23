#!/usr/bin/env python3
"""Build a YAML-driven run plan table from a GeneFam-Pipeline config."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.validate_config import load_config


FIELDNAMES = ["section", "key", "value"]


def _stringify(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value)


def build_run_plan(config: dict[str, Any]) -> list[dict[str, str]]:
    project = config.get("project", {}) or {}
    runtime = config.get("runtime", {}) or {}
    run = config.get("run", {}) or {}
    species = config.get("species", {}) or {}
    dev = config.get("dev", {}) or {}
    modules = config.get("modules", {}) or {}

    rows = [
        {"section": "project", "key": "name", "value": _stringify(project.get("name"))},
        {"section": "project", "key": "outdir", "value": _stringify(project.get("outdir"))},
        {"section": "runtime", "key": "environment", "value": _stringify(runtime.get("environment"))},
        {"section": "runtime", "key": "r_bin", "value": _stringify(runtime.get("r_bin"))},
        {"section": "species", "key": "species_group", "value": _stringify(run.get("species_group"))},
        {"section": "species", "key": "include", "value": _stringify(species.get("include", []))},
        {"section": "species", "key": "exclude", "value": _stringify(species.get("exclude", []))},
        {"section": "dev", "key": "mock_external_tools", "value": _stringify(dev.get("mock_external_tools", False))},
    ]
    for module_name in sorted(modules):
        rows.append(
            {
                "section": "module",
                "key": module_name,
                "value": "enabled" if modules[module_name] else "disabled",
            }
        )
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(build_run_plan(load_config(args.config)), args.out)


if __name__ == "__main__":
    main()
