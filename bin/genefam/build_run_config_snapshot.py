#!/usr/bin/env python3
"""Write a stable key/value snapshot for a GeneFam standard run."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


FIELDNAMES = ["key", "value"]


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read GeneFam configuration")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _read_species_ids(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [row["species_id"] for row in csv.DictReader(handle, delimiter="\t")]


def _stringify(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    return str(value)


def build_snapshot(config: dict, species_ids: list[str], source_config: str, species_manifest: str) -> list[dict[str, str]]:
    project = config.get("project", {}) or {}
    runtime = config.get("runtime", {}) or {}
    input_config = config.get("input", {}) or {}
    species = config.get("species", {}) or {}
    run = config.get("run", {}) or {}
    gene_family = config.get("gene_family", {}) or {}
    identification = config.get("identification", {}) or {}
    modules = config.get("modules", {}) or {}
    dev = config.get("dev", {}) or {}

    rows = [
        ("source_config", source_config),
        ("species_manifest", species_manifest),
        ("project.name", project.get("name", "")),
        ("runtime.environment", runtime.get("environment", "")),
        ("runtime.r_bin", runtime.get("r_bin", "")),
        ("input.mode", input_config.get("mode", "")),
        ("input.root", input_config.get("root", "")),
        ("input.manifest", input_config.get("manifest", "")),
        ("run.species_group", run.get("species_group", "")),
        ("species.include", species.get("include", [])),
        ("species.exclude", species.get("exclude", [])),
        ("selected_species", species_ids),
        ("selected_species_count", len(species_ids)),
        ("gene_family.name", gene_family.get("name", "")),
        ("gene_family.hmm_profiles", [profile.get("id", "") for profile in gene_family.get("hmm_profiles", [])]),
        ("gene_family.reference_peptides", gene_family.get("reference_peptides", "")),
        ("identification.use_hmmer", identification.get("use_hmmer", "")),
        ("identification.use_diamond", identification.get("use_diamond", "")),
        ("identification.final_rule", identification.get("final_rule", "")),
        ("identification.hmm_evalue", identification.get("hmm_evalue", "")),
        ("identification.diamond_evalue", identification.get("diamond_evalue", "")),
        ("dev.mock_external_tools", dev.get("mock_external_tools", "")),
        ("modules.enabled", [key for key, enabled in modules.items() if enabled]),
    ]
    return [{"key": key, "value": _stringify(value)} for key, value in rows]


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(
        build_snapshot(
            _load_yaml(args.config),
            _read_species_ids(args.species_manifest),
            source_config=str(args.config),
            species_manifest=str(args.species_manifest),
        ),
        args.out,
    )


if __name__ == "__main__":
    main()
