from bin.genefam.validate_config import validate_config


def test_validate_config_accepts_minimal_valid_config():
    errors = validate_config(
        {
            "project": {},
            "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
            "input": {"mode": "auto"},
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
            "input": {"mode": "auto"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "ambiguous"},
            "plotting": {"reuse_policy": "adapt_not_modify"},
            "modules": {},
        }
    )

    assert "identification.final_rule must be intersection, union, or hmmer_only" in errors


def test_validate_config_reports_wrong_runtime():
    errors = validate_config(
        {
            "project": {},
            "runtime": {"environment": "base", "r_bin": "/usr/bin/R"},
            "input": {"mode": "auto"},
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
            "input": {"mode": "auto"},
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
            "input": {"mode": "auto"},
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
