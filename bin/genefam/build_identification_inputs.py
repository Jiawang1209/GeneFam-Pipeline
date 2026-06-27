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


def _rebase_path(value: str, base_dir: Path | None) -> str:
    if not value or not base_dir:
        return value
    path = Path(value)
    if path.is_absolute():
        return value
    return str(Path(base_dir) / path)


def resolve_input_paths(
    manifest_rows: list[dict[str, str]],
    config: dict[str, Any],
    base_dir: Path | None,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    resolved_manifest = []
    for row in manifest_rows:
        resolved = dict(row)
        for key in ("pep", "gff3", "cds", "genome"):
            resolved[key] = _rebase_path(resolved.get(key, ""), base_dir)
        resolved_manifest.append(resolved)

    resolved_config = dict(config)
    gene_family = dict((config.get("gene_family", {}) or {}))
    gene_family["hmm_profiles"] = [
        {**profile, "path": _rebase_path(str(profile.get("path", "")), base_dir)}
        for profile in gene_family.get("hmm_profiles", []) or []
    ]
    if gene_family.get("reference_peptides"):
        gene_family["reference_peptides"] = _rebase_path(str(gene_family["reference_peptides"]), base_dir)
    resolved_config["gene_family"] = gene_family
    return resolved_manifest, resolved_config


def build_hmmer_inputs(manifest_rows: list[dict[str, str]], config: dict[str, Any]) -> list[dict[str, str]]:
    if (config.get("identification", {}) or {}).get("use_hmmer", True) is False:
        return []
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


def build_diamond_inputs(
    manifest_rows: list[dict[str, str]],
    config: dict[str, Any],
    reference_peptides_override: str | None = None,
) -> list[dict[str, str]]:
    if (config.get("identification", {}) or {}).get("use_diamond", True) is False:
        return []
    reference_peptides = reference_peptides_override or (config.get("gene_family", {}) or {}).get("reference_peptides")
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
    parser.add_argument("--base-dir", default=None, type=Path)
    parser.add_argument("--reference-peptides", default=None, help="Generated reference peptide FASTA overriding YAML gene_family.reference_peptides")
    args = parser.parse_args()
    config = load_yaml(args.config)
    manifest_rows = read_tsv(args.species_manifest)
    manifest_rows, config = resolve_input_paths(manifest_rows, config, args.base_dir)
    write_tsv(build_hmmer_inputs(manifest_rows, config), HMMER_FIELDNAMES, args.outdir / "hmmer_inputs.tsv")
    reference_peptides_override = str(Path(args.reference_peptides).resolve()) if args.reference_peptides else None
    write_tsv(
        build_diamond_inputs(manifest_rows, config, reference_peptides_override=reference_peptides_override),
        DIAMOND_FIELDNAMES,
        args.outdir / "diamond_inputs.tsv",
    )


if __name__ == "__main__":
    main()
