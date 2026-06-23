#!/usr/bin/env python3
"""Validate the minimal GeneFam-Pipeline YAML contract."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


REQUIRED_SECTIONS = ("project", "input", "species", "gene_family", "identification", "modules")


def load_config(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read YAML configuration files")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Configuration must be a YAML mapping")
    return data


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    input_mode = (config.get("input", {}) or {}).get("mode")
    if input_mode not in {"auto", "manifest"}:
        errors.append("input.mode must be 'auto' or 'manifest'")

    final_rule = (config.get("identification", {}) or {}).get("final_rule")
    if final_rule not in {"intersection", "union", "hmmer_only"}:
        errors.append("identification.final_rule must be intersection, union, or hmmer_only")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    errors = validate_config(load_config(args.config))
    if errors:
        raise SystemExit("\n".join(errors))
    print("Configuration OK")


if __name__ == "__main__":
    main()
