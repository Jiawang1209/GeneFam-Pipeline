#!/usr/bin/env python3
"""Validate the minimal GeneFam-Pipeline YAML contract."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

try:
    from bin.genefam.build_wgd_event_evidence import load_event_metadata
except ModuleNotFoundError:  # pragma: no cover - supports direct script execution
    from build_wgd_event_evidence import load_event_metadata

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


REQUIRED_SECTIONS = ("project", "runtime", "input", "species", "gene_family", "identification", "modules")
MANIFEST_FIELDNAMES = ("species_id", "pep", "gff3", "cds", "genome")


def load_config(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read YAML configuration files")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Configuration must be a YAML mapping")
    return data


def _path_exists(value: str, base_dir: Path) -> bool:
    path = Path(value)
    if path.is_absolute():
        return path.exists()
    return (base_dir / path).exists()


def _resolve_path(value: str, base_dir: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return base_dir / path


def _normalize_include(include: str | list[str]) -> set[str] | None:
    if include == "all":
        return None
    if isinstance(include, str):
        return {include}
    return set(include)


def _validate_species_manifest_paths(
    manifest: Path,
    input_required: dict[str, bool],
    base_dir: Path,
    include: str | list[str],
    exclude: list[str],
) -> list[str]:
    errors: list[str] = []
    try:
        with manifest.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            missing_columns = [field for field in MANIFEST_FIELDNAMES if field not in (reader.fieldnames or [])]
            if missing_columns:
                return [
                    "input.manifest is invalid: Species manifest is missing required columns: "
                    + ", ".join(missing_columns)
                ]
            rows = list(reader)
    except OSError as exc:
        return [f"input.manifest is invalid: {exc}"]

    include_set = _normalize_include(include)
    exclude_set = set(exclude or [])
    discovered_species: set[str] = set()
    for row in rows:
        species_id = row.get("species_id", "").strip() or "unknown"
        discovered_species.add(species_id)
        if include_set is not None and species_id not in include_set:
            continue
        if species_id in exclude_set:
            continue
        for file_type in ("pep", "gff3", "cds", "genome"):
            value = row.get(file_type, "").strip()
            if input_required.get(file_type, False) and not value:
                errors.append(f"input.manifest missing required {file_type} path for species {species_id}")
                continue
            if value and not _resolve_path(value, base_dir).exists():
                errors.append(f"input.manifest {file_type} path does not exist for species {species_id}: {value}")
    if include_set is not None:
        missing = sorted(include_set - discovered_species - exclude_set)
        if missing:
            errors.append(f"input.manifest requested species not found: {', '.join(missing)}")
    return errors


def _validate_auto_species_bank_paths(
    root: Path,
    patterns: dict[str, list[str]],
    input_required: dict[str, bool],
    include: str | list[str],
    exclude: list[str],
) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return errors
    include_set = _normalize_include(include)
    exclude_set = set(exclude or [])
    discovered_species: set[str] = set()
    for species_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        species_id = species_dir.name
        discovered_species.add(species_id)
        if include_set is not None and species_id not in include_set:
            continue
        if species_id in exclude_set:
            continue
        for file_type in ("pep", "gff3", "cds", "genome"):
            matches = []
            for pattern in patterns.get(file_type, []):
                matches.extend(species_dir.glob(pattern))
            unique_matches = sorted(set(path for path in matches if path.is_file()))
            if input_required.get(file_type, False) and not unique_matches:
                errors.append(f"input.root missing required {file_type} file for species {species_id}")
            if len(unique_matches) > 1:
                names = ", ".join(path.name for path in unique_matches)
                errors.append(f"input.root multiple {file_type} files for species {species_id}: {names}")
    if include_set is not None:
        missing = sorted(include_set - discovered_species - exclude_set)
        if missing:
            errors.append(f"input.root requested species not found: {', '.join(missing)}")
    return errors


def validate_config(config: dict[str, Any], check_paths: bool = False, base_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    base_dir = Path(".") if base_dir is None else base_dir
    for section in REQUIRED_SECTIONS:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    input_config = config.get("input", {}) or {}
    species_config = config.get("species", {}) or {}
    include = species_config.get("include", "all")
    exclude = species_config.get("exclude", []) or []
    input_mode = input_config.get("mode")
    if input_mode not in {"auto", "manifest"}:
        errors.append("input.mode must be 'auto' or 'manifest'")
    if input_mode == "auto" and not input_config.get("root"):
        errors.append("input.root is required when input.mode is auto")
    if input_mode == "manifest" and not input_config.get("manifest"):
        errors.append("input.manifest is required when input.mode is manifest")
    input_required = input_config.get("required", {}) or {}
    if check_paths:
        if input_mode == "auto" and input_config.get("root"):
            root_path = _resolve_path(str(input_config["root"]), base_dir)
            if not root_path.exists():
                errors.append(f"input.root path does not exist: {input_config['root']}")
            else:
                errors.extend(
                    _validate_auto_species_bank_paths(
                        root_path,
                        input_config.get("patterns", {}) or {},
                        input_required,
                        include,
                        exclude,
                    )
                )
        if (
            input_mode == "manifest"
            and input_config.get("manifest")
        ):
            manifest_path = _resolve_path(str(input_config["manifest"]), base_dir)
            if not manifest_path.exists():
                errors.append(f"input.manifest path does not exist: {input_config['manifest']}")
            else:
                errors.extend(_validate_species_manifest_paths(manifest_path, input_required, base_dir, include, exclude))

    runtime = config.get("runtime", {}) or {}
    if runtime.get("environment") != "GeneFamilyFlow":
        errors.append("runtime.environment must be GeneFamilyFlow")
    if runtime.get("r_bin") != "/usr/local/bin/R":
        errors.append("runtime.r_bin must be /usr/local/bin/R")

    plotting = config.get("plotting", {}) or {}
    if plotting.get("reuse_policy") not in {"adapt_not_modify"}:
        errors.append("plotting.reuse_policy must be adapt_not_modify")
    if (
        check_paths
        and plotting.get("gene_family_species_order")
        and not _path_exists(str(plotting["gene_family_species_order"]), base_dir)
    ):
        errors.append(f"plotting.gene_family_species_order path does not exist: {plotting['gene_family_species_order']}")
    if (
        check_paths
        and plotting.get("syntenic_pairs")
        and not _path_exists(str(plotting["syntenic_pairs"]), base_dir)
    ):
        errors.append(f"plotting.syntenic_pairs path does not exist: {plotting['syntenic_pairs']}")

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
    if check_paths:
        if identification.get("use_hmmer", True) is not False:
            for profile in gene_family.get("hmm_profiles", []) or []:
                profile_path = str(profile.get("path", ""))
                if profile_path and not _path_exists(profile_path, base_dir):
                    errors.append(f"gene_family.hmm_profiles path does not exist: {profile_path}")
        if identification.get("use_diamond", True) is not False:
            reference_peptides = str(gene_family.get("reference_peptides", ""))
            if reference_peptides and not _path_exists(reference_peptides, base_dir):
                errors.append(f"gene_family.reference_peptides path does not exist: {reference_peptides}")

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

    expression = config.get("expression", {}) or {}
    promoter = config.get("promoter", {}) or {}
    ppi = config.get("ppi", {}) or {}

    pep_dependent_modules = ("identification", "domain_filtering", "family_summary", "phylogeny", "motif")
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
    if check_paths and expression.get("matrix") and not _path_exists(str(expression["matrix"]), base_dir):
        errors.append(f"expression.matrix path does not exist: {expression['matrix']}")
    if check_paths and expression.get("metadata") and not _path_exists(str(expression["metadata"]), base_dir):
        errors.append(f"expression.metadata path does not exist: {expression['metadata']}")
    if modules.get("promoter_cis") is True and not promoter.get("cis_elements"):
        errors.append("modules.promoter_cis requires promoter.cis_elements")
    if modules.get("promoter_cis") is True:
        if input_required.get("gff3") is not True:
            errors.append("modules.promoter_cis requires input.required.gff3: true")
        if input_required.get("genome") is not True:
            errors.append("modules.promoter_cis requires input.required.genome: true")
    if check_paths and promoter.get("cis_elements") and not _path_exists(str(promoter["cis_elements"]), base_dir):
        errors.append(f"promoter.cis_elements path does not exist: {promoter['cis_elements']}")
    if modules.get("ppi") is True and not ppi.get("edges"):
        errors.append("modules.ppi requires ppi.edges")
    if check_paths and ppi.get("edges") and not _path_exists(str(ppi["edges"]), base_dir):
        errors.append(f"ppi.edges path does not exist: {ppi['edges']}")
    if check_paths and ppi.get("nodes") and not _path_exists(str(ppi["nodes"]), base_dir):
        errors.append(f"ppi.nodes path does not exist: {ppi['nodes']}")

    if modules.get("domain_filtering") is True and modules.get("identification") is not True:
        errors.append("modules.domain_filtering requires modules.identification: true")
    if modules.get("family_summary") is True and modules.get("domain_filtering") is not True:
        errors.append("modules.family_summary requires modules.domain_filtering: true")
    if modules.get("phylogeny") is True and modules.get("family_summary") is not True:
        errors.append("modules.phylogeny requires modules.family_summary: true")
    if modules.get("motif") is True and modules.get("family_summary") is not True:
        errors.append("modules.motif requires modules.family_summary: true")
    if modules.get("expression") is True and modules.get("family_summary") is not True:
        errors.append("modules.expression requires modules.family_summary: true")
    if modules.get("duplication_retention") is True:
        if modules.get("synteny") is not True:
            errors.append("modules.duplication_retention requires modules.synteny: true")
        if modules.get("kaks") is not True:
            errors.append("modules.duplication_retention requires modules.kaks: true")

    wgd_events = config.get("wgd_events", {}) or {}
    if wgd_events.get("named_event_annotation") is True:
        if modules.get("duplication_retention") is not True:
            errors.append("wgd_events.named_event_annotation requires modules.duplication_retention: true")
        event_map = wgd_events.get("event_map")
        if not event_map:
            errors.append("wgd_events.event_map is required when wgd_events.named_event_annotation is true")
        elif check_paths:
            event_map_path = Path(str(event_map))
            resolved_event_map = event_map_path if event_map_path.is_absolute() else base_dir / event_map_path
            if not resolved_event_map.exists():
                errors.append(f"wgd_events.event_map path does not exist: {event_map}")
            else:
                try:
                    load_event_metadata(resolved_event_map)
                except Exception as exc:
                    errors.append(f"wgd_events.event_map is invalid: {exc}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument(
        "--check-paths",
        action="store_true",
        help="Also require configured runtime input paths to exist relative to the current working directory.",
    )
    parser.add_argument(
        "--base-dir",
        default=Path("."),
        type=Path,
        help="Base directory for resolving relative runtime paths when --check-paths is set.",
    )
    args = parser.parse_args()
    errors = validate_config(load_config(args.config), check_paths=args.check_paths, base_dir=args.base_dir)
    if errors:
        raise SystemExit("\n".join(errors))
    print("Configuration OK")


if __name__ == "__main__":
    main()
