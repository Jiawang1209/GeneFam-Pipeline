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
