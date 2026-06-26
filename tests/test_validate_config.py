import subprocess
import sys
from pathlib import Path

from bin.genefam.validate_config import validate_config


def test_validate_config_accepts_minimal_valid_config():
    errors = validate_config(
        {
            "project": {},
            "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
            "input": {"mode": "auto", "root": "tests/fixtures/species_bank"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "intersection"},
            "plotting": {"reuse_policy": "adapt_not_modify"},
            "modules": {},
        }
    )

    assert errors == []


def test_validate_config_reports_invalid_final_rule():
    errors = validate_config(
        {
            "project": {},
            "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
            "input": {"mode": "auto", "root": "tests/fixtures/species_bank"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "ambiguous"},
            "plotting": {"reuse_policy": "adapt_not_modify"},
            "modules": {},
        }
    )

    assert "identification.final_rule must be intersection, union, or hmmer_only" in errors


def test_validate_config_reports_auto_mode_without_species_bank_root():
    config = _valid_base_config()
    config["input"].pop("root", None)
    config["input"]["mode"] = "auto"

    errors = validate_config(config)

    assert "input.root is required when input.mode is auto" in errors


def test_validate_config_reports_manifest_mode_without_manifest_path():
    config = _valid_base_config()
    config["input"].pop("root", None)
    config["input"]["mode"] = "manifest"

    errors = validate_config(config)

    assert "input.manifest is required when input.mode is manifest" in errors


def test_validate_config_reports_identification_without_any_enabled_search_tool():
    config = _valid_base_config()
    config["identification"]["use_hmmer"] = False
    config["identification"]["use_diamond"] = False

    errors = validate_config(config)

    assert "identification requires at least one enabled search tool: use_hmmer or use_diamond" in errors


def test_validate_config_reports_wrong_runtime():
    errors = validate_config(
        {
            "project": {},
            "runtime": {"environment": "base", "r_bin": "/usr/bin/R"},
            "input": {"mode": "auto", "root": "tests/fixtures/species_bank"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "intersection"},
            "plotting": {"reuse_policy": "adapt_not_modify"},
            "modules": {},
        }
    )

    assert "runtime.environment must be GeneFamilyFlow" in errors
    assert "runtime.r_bin must be /usr/local/bin/R" in errors


def test_validate_config_reports_wrong_plotting_reuse_policy():
    errors = validate_config(
        {
            "project": {},
            "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
            "input": {"mode": "auto", "root": "tests/fixtures/species_bank"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "intersection"},
            "plotting": {"reuse_policy": "directly_modify_reference"},
            "modules": {},
        }
    )

    assert "plotting.reuse_policy must be adapt_not_modify" in errors


def test_validate_config_accepts_mock_mode_with_evidence_dir():
    errors = validate_config(
        {
            "project": {},
            "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
            "input": {"mode": "auto", "root": "tests/fixtures/species_bank"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "intersection"},
            "plotting": {"reuse_policy": "adapt_not_modify"},
            "dev": {"mock_external_tools": True, "mock_evidence_dir": "tests/fixtures/mock_evidence"},
            "modules": {},
        }
    )

    assert errors == []


def test_validate_config_reports_mock_mode_without_evidence_dir():
    errors = validate_config(
        {
            "project": {},
            "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
            "input": {"mode": "auto"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "intersection"},
            "plotting": {"reuse_policy": "adapt_not_modify"},
            "dev": {"mock_external_tools": True},
            "modules": {},
        }
    )

    assert "dev.mock_evidence_dir is required when dev.mock_external_tools is true" in errors


def test_validate_config_reports_fixture_inputs_in_non_mock_identification():
    config = _valid_base_config()
    config["input"]["root"] = "data/species_bank"
    config["dev"] = {"mock_external_tools": False}
    config["gene_family"] = {
        "hmm_profiles": [{"id": "PF00657", "path": "tests/fixtures/hmmer_profiles/PF00657.demo.hmm"}],
        "reference_peptides": "tests/fixtures/reference/GDSL_reference.pep.fa",
    }
    config["identification"]["use_hmmer"] = True
    config["identification"]["use_diamond"] = True

    errors = validate_config(config)

    assert "gene_family.hmm_profiles must not use tests/fixtures paths when dev.mock_external_tools is false" in errors
    assert "gene_family.reference_peptides must not use tests/fixtures paths when dev.mock_external_tools is false" in errors


def test_validate_config_check_paths_reports_missing_runtime_inputs(tmp_path):
    config = _valid_base_config()
    config["input"]["root"] = "missing_species_bank"
    config["dev"] = {"mock_external_tools": False}
    config["gene_family"] = {
        "hmm_profiles": [{"id": "PF00657", "path": "data/hmm_profiles/PF00657.hmm"}],
        "reference_peptides": "data/reference/GDSL_reference.pep.fa",
    }
    config["identification"]["use_hmmer"] = True
    config["identification"]["use_diamond"] = True
    config["modules"]["expression"] = True
    config["expression"] = {"matrix": "data/expression/family_expression.tsv"}

    errors = validate_config(config, check_paths=True, base_dir=tmp_path)

    assert "input.root path does not exist: missing_species_bank" in errors
    assert "gene_family.hmm_profiles path does not exist: data/hmm_profiles/PF00657.hmm" in errors
    assert "gene_family.reference_peptides path does not exist: data/reference/GDSL_reference.pep.fa" in errors
    assert "expression.matrix path does not exist: data/expression/family_expression.tsv" in errors


def test_validate_config_reports_promoter_cis_requires_annotation_table_and_missing_path(tmp_path):
    config = _valid_base_config()
    config["input"]["root"] = "tests/fixtures/species_bank"
    config["modules"]["promoter_cis"] = True

    errors = validate_config(config)

    assert "modules.promoter_cis requires promoter.cis_elements" in errors

    config["promoter"] = {"cis_elements": "data/promoter/plantcare.tsv"}
    errors = validate_config(config, check_paths=True, base_dir=tmp_path)

    assert "promoter.cis_elements path does not exist: data/promoter/plantcare.tsv" in errors


def test_validate_config_cli_check_paths_accepts_fixture_configs():
    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/validate_config.py",
            "configs/example.config.yaml",
            "--check-paths",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "Configuration OK"


def test_validate_config_cli_check_paths_resolves_against_base_dir(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text(
        "project: {}\n"
        "runtime:\n"
        "  environment: GeneFamilyFlow\n"
        "  r_bin: /usr/local/bin/R\n"
        "input:\n"
        "  mode: auto\n"
        "  root: species_bank\n"
        "species: {}\n"
        "gene_family: {}\n"
        "identification:\n"
        "  final_rule: intersection\n"
        "plotting:\n"
        "  reuse_policy: adapt_not_modify\n"
        "modules: {}\n",
        encoding="utf-8",
    )
    (tmp_path / "species_bank").mkdir()

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/validate_config.py",
            str(config),
            "--check-paths",
            "--base-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "Configuration OK"


def test_validate_config_reports_invalid_domain_filtering_thresholds():
    errors = validate_config(
        {
            "project": {},
            "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
            "input": {"mode": "auto"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "intersection"},
            "domain_filtering": {"hmmer_min_bitscore": -1, "hmmer_min_domain_coverage": 1.5},
            "plotting": {"reuse_policy": "adapt_not_modify"},
            "modules": {},
        }
    )

    assert "domain_filtering.hmmer_min_bitscore must be non-negative" in errors
    assert "domain_filtering.hmmer_min_domain_coverage must be between 0 and 1" in errors


def _valid_base_config():
    return {
        "project": {},
        "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
        "input": {"mode": "auto", "required": {"pep": True, "gff3": True, "cds": False, "genome": False}},
        "species": {},
        "gene_family": {},
        "identification": {"final_rule": "intersection"},
        "plotting": {"reuse_policy": "adapt_not_modify"},
        "modules": {
            "identification": True,
            "family_summary": True,
            "phylogeny": False,
            "motif": False,
            "synteny": False,
            "duplication_retention": False,
            "kaks": False,
            "chromosome_location": False,
            "expression": False,
            "report": True,
        },
    }


def test_validate_config_reports_kaks_requires_cds_inputs():
    config = _valid_base_config()
    config["modules"]["kaks"] = True

    errors = validate_config(config)

    assert "modules.kaks requires input.required.cds: true" in errors


def test_validate_config_reports_identification_modules_require_pep_inputs():
    config = _valid_base_config()
    config["input"]["required"]["pep"] = False
    config["modules"]["identification"] = True
    config["modules"]["domain_filtering"] = True
    config["modules"]["phylogeny"] = True
    config["modules"]["motif"] = True

    errors = validate_config(config)

    assert "modules.identification requires input.required.pep: true" in errors
    assert "modules.domain_filtering requires input.required.pep: true" in errors
    assert "modules.phylogeny requires input.required.pep: true" in errors
    assert "modules.motif requires input.required.pep: true" in errors


def test_validate_config_reports_synteny_requires_pep_and_gff3_inputs():
    config = _valid_base_config()
    config["input"]["required"]["pep"] = False
    config["input"]["required"]["gff3"] = False
    config["modules"]["synteny"] = True

    errors = validate_config(config)

    assert "modules.synteny requires input.required.pep: true" in errors
    assert "modules.synteny requires input.required.gff3: true" in errors


def test_validate_config_reports_chromosome_location_requires_gff3_inputs():
    config = _valid_base_config()
    config["input"]["required"]["gff3"] = False
    config["modules"]["chromosome_location"] = True

    errors = validate_config(config)

    assert "modules.chromosome_location requires input.required.gff3: true" in errors


def test_validate_config_reports_expression_requires_matrix_path():
    config = _valid_base_config()
    config["modules"]["expression"] = True

    errors = validate_config(config)

    assert "modules.expression requires expression.matrix" in errors


def test_validate_config_checks_expression_metadata_path_when_provided():
    config = _valid_base_config()
    config["modules"]["expression"] = True
    config["expression"] = {"matrix": "tests/fixtures/expression/family_expression.tsv", "metadata": "missing.tsv"}

    errors = validate_config(config, check_paths=True)

    assert "expression.metadata path does not exist: missing.tsv" in errors


def test_validate_config_reports_ppi_requires_edge_table_and_missing_paths():
    config = _valid_base_config()
    config["modules"]["ppi"] = True
    errors = validate_config(config)

    assert "modules.ppi requires ppi.edges" in errors

    config["ppi"] = {"edges": "data/ppi/edges.tsv", "nodes": "data/ppi/nodes.tsv"}
    errors = validate_config(config, check_paths=True)

    assert "ppi.edges path does not exist: data/ppi/edges.tsv" in errors
    assert "ppi.nodes path does not exist: data/ppi/nodes.tsv" in errors


def test_validate_config_reports_phylogeny_and_motif_require_family_summary():
    config = _valid_base_config()
    config["modules"]["family_summary"] = False
    config["modules"]["phylogeny"] = True
    config["modules"]["motif"] = True

    errors = validate_config(config)

    assert "modules.phylogeny requires modules.family_summary: true" in errors
    assert "modules.motif requires modules.family_summary: true" in errors


def test_validate_config_reports_duplication_retention_requires_synteny_and_kaks():
    config = _valid_base_config()
    config["modules"]["duplication_retention"] = True

    errors = validate_config(config)

    assert "modules.duplication_retention requires modules.synteny: true" in errors
    assert "modules.duplication_retention requires modules.kaks: true" in errors


def test_validate_config_reports_named_wgd_events_without_event_map():
    config = _valid_base_config()
    config["input"]["root"] = "tests/fixtures/species_bank"
    config["wgd_events"] = {"named_event_annotation": True, "event_map": None}

    errors = validate_config(config)

    assert "wgd_events.event_map is required when wgd_events.named_event_annotation is true" in errors


def test_validate_config_reports_named_wgd_events_without_duplication_retention_module():
    config = _valid_base_config()
    config["input"]["root"] = "tests/fixtures/species_bank"
    config["wgd_events"] = {
        "named_event_annotation": True,
        "event_map": "configs/wgd_events.brassicaceae.yaml",
    }
    config["modules"]["duplication_retention"] = False

    errors = validate_config(config)

    assert "wgd_events.named_event_annotation requires modules.duplication_retention: true" in errors


def test_validate_config_check_paths_rejects_duplicate_wgd_event_names(tmp_path):
    event_map = tmp_path / "duplicate_events.yaml"
    event_map.write_text(
        "\n".join(
            [
                "wgd_events:",
                "  - name: alpha",
                "    scope: Arabidopsis_Brassicaceae",
                "    evidence: literature",
                "    expected_relative_age: recent",
                "  - name: alpha",
                "    scope: duplicate_scope",
                "    evidence: literature",
                "    expected_relative_age: duplicate",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    config = _valid_base_config()
    config["input"]["root"] = "species_bank"
    config["wgd_events"] = {"named_event_annotation": True, "event_map": "duplicate_events.yaml"}
    (tmp_path / "species_bank").mkdir()

    errors = validate_config(config, check_paths=True, base_dir=tmp_path)

    assert "wgd_events.event_map is invalid: Duplicate WGD event name: alpha" in errors
