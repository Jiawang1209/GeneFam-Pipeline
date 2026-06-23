#!/usr/bin/env python3
"""Build HMMER and DIAMOND input tables from config and species manifest."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


HMMER_FIELDNAMES = ["species_id", "pep", "hmm_id", "hmm_profile"]
DIAMOND_FIELDNAMES = ["species_id", "pep", "reference_peptides"]


def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read YAML configuration files")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping: {path}")
    return data


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build_hmmer_inputs(manifest_rows: list[dict[str, str]], config: dict[str, Any]) -> list[dict[str, str]]:
    profiles = (config.get("gene_family", {}) or {}).get("hmm_profiles", []) or []
    rows: list[dict[str, str]] = []
    for species in manifest_rows:
        for profile in profiles:
            rows.append(
                {
                    "species_id": species["species_id"],
                    "pep": species["pep"],
                    "hmm_id": str(profile["id"]),
                    "hmm_profile": str(profile["path"]),
                }
            )
    return rows


def build_diamond_inputs(manifest_rows: list[dict[str, str]], config: dict[str, Any]) -> list[dict[str, str]]:
    reference_peptides = (config.get("gene_family", {}) or {}).get("reference_peptides")
    if not reference_peptides:
        return []
    return [
        {
            "species_id": species["species_id"],
            "pep": species["pep"],
            "reference_peptides": str(reference_peptides),
        }
        for species in manifest_rows
    ]


def write_tsv(rows: list[dict[str, str]], fieldnames: list[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    config = load_yaml(args.config)
    manifest_rows = read_tsv(args.species_manifest)
    write_tsv(build_hmmer_inputs(manifest_rows, config), HMMER_FIELDNAMES, args.outdir / "hmmer_inputs.tsv")
    write_tsv(build_diamond_inputs(manifest_rows, config), DIAMOND_FIELDNAMES, args.outdir / "diamond_inputs.tsv")


if __name__ == "__main__":
    main()
