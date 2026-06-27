#!/usr/bin/env python3
"""Generate TAIR-domain reference peptides from YAML config and a clean species manifest."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

try:
    from bin.genefam.build_reference_from_tair_domains import select_reference_records, write_fasta, write_ids
except ModuleNotFoundError:  # pragma: no cover - supports direct script execution
    from build_reference_from_tair_domains import select_reference_records, write_fasta, write_ids


REFERENCE_MANIFEST_FIELDS = ["hmm_id", "reference_peptides", "ids", "missing_ids"]


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


def write_reference_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REFERENCE_MANIFEST_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def first_hmm_id(config: dict[str, Any]) -> str:
    profiles = (config.get("gene_family", {}) or {}).get("hmm_profiles", []) or []
    if not profiles:
        raise ValueError("gene_family.hmm_profiles is required for automatic reference generation")
    hmm_id = str(profiles[0].get("id", "")).strip()
    if not hmm_id:
        raise ValueError("gene_family.hmm_profiles[0].id is required for automatic reference generation")
    return hmm_id


def reference_species_pep(rows: list[dict[str, str]], species_id: str) -> Path:
    for row in rows:
        if row.get("species_id") == species_id:
            if not row.get("pep"):
                raise ValueError(f"Reference species has no peptide FASTA in clean manifest: {species_id}")
            return Path(row["pep"])
    raise ValueError(f"Reference species not found in clean manifest: {species_id}")


def resolve_path(value: str, base_dir: Path | None) -> Path:
    path = Path(value)
    if path.is_absolute() or base_dir is None:
        return path
    return base_dir / path


def build_reference_from_config(
    config: dict[str, Any],
    clean_manifest_rows: list[dict[str, str]],
    outdir: Path,
    base_dir: Path | None = None,
) -> list[dict[str, str]]:
    reference_config = config.get("reference_generation", {}) or {}
    if reference_config.get("enabled") is False:
        return []
    if reference_config.get("source") != "tair_all_domains":
        raise ValueError("reference_generation.source must be tair_all_domains")
    hmm_id = first_hmm_id(config)
    domains = resolve_path(str(reference_config.get("domain_annotation", "")), base_dir)
    if not domains:
        raise ValueError("reference_generation.domain_annotation is required")
    reference_species = str(reference_config.get("reference_species", "Arabidopsis_thaliana"))
    peptides = reference_species_pep(clean_manifest_rows, reference_species)

    outdir.mkdir(parents=True, exist_ok=True)
    reference_fasta = outdir / f"{hmm_id}.reference.pep.fa"
    ids_out = outdir / f"{hmm_id}.TAIR.ID"
    missing_out = outdir / f"{hmm_id}.missing_ids.txt"
    reference_ids, records, missing = select_reference_records(domains, peptides, [hmm_id])
    write_fasta(records, reference_fasta)
    write_ids(reference_ids, ids_out)
    write_ids(missing, missing_out)
    return [
        {
            "hmm_id": hmm_id,
            "reference_peptides": str(reference_fasta),
            "ids": str(ids_out),
            "missing_ids": str(missing_out),
        }
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--base-dir", default=None, type=Path)
    args = parser.parse_args()

    rows = build_reference_from_config(load_yaml(args.config), read_tsv(args.species_manifest), args.outdir, args.base_dir)
    write_reference_manifest(rows, args.outdir / "reference_generation.tsv")
    print(f"Generated {len(rows)} reference peptide set(s) in {args.outdir}")


if __name__ == "__main__":
    main()
