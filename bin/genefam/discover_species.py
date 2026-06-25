#!/usr/bin/env python3
"""Discover species inputs from a folder-per-species bank."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only on minimal installs
    yaml = None


FILE_TYPES = ("pep", "gff3", "cds", "genome")
MANIFEST_FIELDNAMES = ("species_id", *FILE_TYPES)


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read YAML configuration files")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping: {path}")
    return data


def _normalize_include(include: str | list[str] | tuple[str, ...] | None) -> str | set[str]:
    if include is None or include == "all":
        return "all"
    if isinstance(include, str):
        return {include}
    return set(include)


def _filter_manifest_rows(
    rows: list[dict[str, str]],
    include: str | list[str] | tuple[str, ...] | None,
    exclude: list[str] | tuple[str, ...] | None,
    required: dict[str, bool],
) -> list[dict[str, str]]:
    include_set = _normalize_include(include)
    exclude_set = set(exclude or [])
    filtered: list[dict[str, str]] = []

    for source_row in rows:
        species_id = source_row.get("species_id", "")
        if not species_id:
            raise ValueError("Species manifest contains a row without species_id")
        if include_set != "all" and species_id not in include_set:
            continue
        if species_id in exclude_set:
            continue
        row = {field: source_row.get(field, "") for field in MANIFEST_FIELDNAMES}
        for file_type in FILE_TYPES:
            if required.get(file_type, False) and not row[file_type]:
                raise ValueError(f"Missing required {file_type} file for species {species_id}")
        filtered.append(row)

    if include_set != "all":
        discovered = {row["species_id"] for row in filtered}
        missing = sorted(include_set - discovered - exclude_set)
        if missing:
            raise ValueError(f"Requested species not found: {', '.join(missing)}")

    return filtered


def load_species_manifest(
    manifest: Path,
    include: str | list[str] | tuple[str, ...] | None,
    exclude: list[str] | tuple[str, ...] | None,
    required: dict[str, bool],
    base_dir: Path | None = None,
) -> list[dict[str, str]]:
    """Read and filter a prebuilt species manifest."""

    manifest = Path(manifest)
    if base_dir and not manifest.is_absolute():
        manifest = Path(base_dir) / manifest
    if not manifest.exists():
        raise ValueError(f"Species manifest does not exist: {manifest}")

    with manifest.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing_columns = [field for field in MANIFEST_FIELDNAMES if field not in (reader.fieldnames or [])]
        if missing_columns:
            raise ValueError(f"Species manifest is missing required columns: {', '.join(missing_columns)}")
        rows = list(reader)
    return _filter_manifest_rows(rows, include=include, exclude=exclude, required=required)


def _match_one(species_dir: Path, file_type: str, patterns: dict[str, list[str]]) -> str:
    matches: list[Path] = []
    for pattern in patterns.get(file_type, []):
        matches.extend(species_dir.glob(pattern))
    unique_matches = sorted(set(path for path in matches if path.is_file()))
    if len(unique_matches) > 1:
        names = ", ".join(path.name for path in unique_matches)
        raise ValueError(f"Multiple {file_type} files found in {species_dir}: {names}")
    if not unique_matches:
        return ""
    return str(unique_matches[0])


def discover_species(
    root: Path,
    include: str | list[str] | tuple[str, ...] | None,
    exclude: list[str] | tuple[str, ...] | None,
    patterns: dict[str, list[str]],
    required: dict[str, bool],
    base_dir: Path | None = None,
) -> list[dict[str, str]]:
    """Return sorted species manifest rows discovered under root."""

    root = Path(root)
    if base_dir and not root.is_absolute():
        root = Path(base_dir) / root
    if not root.exists():
        raise ValueError(f"Species bank root does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Species bank root is not a directory: {root}")

    include_set = _normalize_include(include)
    exclude_set = set(exclude or [])
    rows: list[dict[str, str]] = []

    for species_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        species_id = species_dir.name
        if include_set != "all" and species_id not in include_set:
            continue
        if species_id in exclude_set:
            continue

        row = {"species_id": species_id}
        for file_type in FILE_TYPES:
            row[file_type] = _match_one(species_dir, file_type, patterns)
            if required.get(file_type, False) and not row[file_type]:
                raise ValueError(f"Missing required {file_type} file for species {species_id}")
        rows.append(row)

    return _filter_manifest_rows(rows, include=include, exclude=exclude, required=required)


def _select_species(config: dict[str, Any], groups: dict[str, Any]) -> tuple[str | list[str], list[str]]:
    species_config = config.get("species", {})
    include: str | list[str] = species_config.get("include", "all")
    exclude: list[str] = species_config.get("exclude", []) or []

    group_name = (config.get("run", {}) or {}).get("species_group")
    if group_name:
        group_map = (groups.get("species_groups", {}) or {})
        if group_name not in group_map:
            raise ValueError(f"species_group '{group_name}' is not defined")
        include = group_map[group_name]

    return include, exclude


def write_manifest(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["species_id", *FILE_TYPES], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--groups", default=None, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--base-dir", default=None, type=Path)
    args = parser.parse_args()

    config = _load_yaml(args.config)
    groups = _load_yaml(args.groups) if args.groups and args.groups.exists() else {}
    include, exclude = _select_species(config, groups)
    input_config = config.get("input", {})
    input_mode = input_config.get("mode", "auto")
    if input_mode == "manifest":
        rows = load_species_manifest(
            manifest=Path(input_config["manifest"]),
            include=include,
            exclude=exclude,
            required=input_config.get("required", {}),
            base_dir=args.base_dir,
        )
    else:
        rows = discover_species(
            root=Path(input_config["root"]),
            include=include,
            exclude=exclude,
            patterns=input_config.get("patterns", {}),
            required=input_config.get("required", {}),
            base_dir=args.base_dir,
        )
    write_manifest(rows, args.out)


if __name__ == "__main__":
    main()
