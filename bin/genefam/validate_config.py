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


REQUIRED_SECTIONS = ("project", "runtime", "input", "species", "gene_family", "identification", "modules")


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

    runtime = config.get("runtime", {}) or {}
    if runtime.get("environment") != "GeneFamilyFlow":
        errors.append("runtime.environment must be GeneFamilyFlow")
    if runtime.get("r_bin") != "/usr/local/bin/R":
        errors.append("runtime.r_bin must be /usr/local/bin/R")

    plotting = config.get("plotting", {}) or {}
    if plotting.get("reuse_policy") not in {"adapt_not_modify"}:
        errors.append("plotting.reuse_policy must be adapt_not_modify")

    dev = config.get("dev", {}) or {}
    if dev.get("mock_external_tools") is True and not dev.get("mock_evidence_dir"):
        errors.append("dev.mock_evidence_dir is required when dev.mock_external_tools is true")

    domain_filtering = config.get("domain_filtering", {}) or {}
    min_bitscore = domain_filtering.get("hmmer_min_bitscore")
    if min_bitscore is not None and float(min_bitscore) < 0:
        errors.append("domain_filtering.hmmer_min_bitscore must be non-negative")
    min_domain_coverage = domain_filtering.get("hmmer_min_domain_coverage")
    if min_domain_coverage is not None and not 0 <= float(min_domain_coverage) <= 1:
        errors.append("domain_filtering.hmmer_min_domain_coverage must be between 0 and 1")

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
