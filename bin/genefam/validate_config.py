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

    input_config = config.get("input", {}) or {}
    input_mode = input_config.get("mode")
    if input_mode not in {"auto", "manifest"}:
        errors.append("input.mode must be 'auto' or 'manifest'")
    if input_mode == "auto" and not input_config.get("root"):
        errors.append("input.root is required when input.mode is auto")
    if input_mode == "manifest" and not input_config.get("manifest"):
        errors.append("input.manifest is required when input.mode is manifest")

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

    gene_family = config.get("gene_family", {}) or {}
    identification = config.get("identification", {}) or {}
    if dev.get("mock_external_tools") is False:
        if identification.get("use_hmmer", True) is not False:
            fixture_profiles = [
                str(profile.get("path", ""))
                for profile in gene_family.get("hmm_profiles", []) or []
                if str(profile.get("path", "")).startswith("tests/fixtures/")
            ]
            if fixture_profiles:
                errors.append(
                    "gene_family.hmm_profiles must not use tests/fixtures paths when dev.mock_external_tools is false"
                )
        if identification.get("use_diamond", True) is not False:
            reference_peptides = str(gene_family.get("reference_peptides", ""))
            if reference_peptides.startswith("tests/fixtures/"):
                errors.append(
                    "gene_family.reference_peptides must not use tests/fixtures paths when dev.mock_external_tools is false"
                )

    domain_filtering = config.get("domain_filtering", {}) or {}
    min_bitscore = domain_filtering.get("hmmer_min_bitscore")
    if min_bitscore is not None and float(min_bitscore) < 0:
        errors.append("domain_filtering.hmmer_min_bitscore must be non-negative")
    min_domain_coverage = domain_filtering.get("hmmer_min_domain_coverage")
    if min_domain_coverage is not None and not 0 <= float(min_domain_coverage) <= 1:
        errors.append("domain_filtering.hmmer_min_domain_coverage must be between 0 and 1")

    final_rule = identification.get("final_rule")
    if final_rule not in {"intersection", "union", "hmmer_only"}:
        errors.append("identification.final_rule must be intersection, union, or hmmer_only")

    modules = config.get("modules", {}) or {}
    if modules.get("identification") is True:
        if identification.get("use_hmmer", True) is False and identification.get("use_diamond", True) is False:
            errors.append("identification requires at least one enabled search tool: use_hmmer or use_diamond")

    input_required = (config.get("input", {}) or {}).get("required", {}) or {}
    expression = config.get("expression", {}) or {}

    pep_dependent_modules = ("identification", "domain_filtering", "phylogeny", "motif")
    for module_name in pep_dependent_modules:
        if modules.get(module_name) is True and input_required.get("pep") is not True:
            errors.append(f"modules.{module_name} requires input.required.pep: true")
    if modules.get("synteny") is True:
        if input_required.get("pep") is not True:
            errors.append("modules.synteny requires input.required.pep: true")
        if input_required.get("gff3") is not True:
            errors.append("modules.synteny requires input.required.gff3: true")
    if modules.get("kaks") is True and input_required.get("cds") is not True:
        errors.append("modules.kaks requires input.required.cds: true")
    if modules.get("chromosome_location") is True and input_required.get("gff3") is not True:
        errors.append("modules.chromosome_location requires input.required.gff3: true")
    if modules.get("expression") is True and not expression.get("matrix"):
        errors.append("modules.expression requires expression.matrix")

    if modules.get("phylogeny") is True and modules.get("family_summary") is not True:
        errors.append("modules.phylogeny requires modules.family_summary: true")
    if modules.get("motif") is True and modules.get("family_summary") is not True:
        errors.append("modules.motif requires modules.family_summary: true")
    if modules.get("duplication_retention") is True:
        if modules.get("synteny") is not True:
            errors.append("modules.duplication_retention requires modules.synteny: true")
        if modules.get("kaks") is not True:
            errors.append("modules.duplication_retention requires modules.kaks: true")

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
