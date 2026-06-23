from bin.genefam.validate_config import validate_config


def test_validate_config_accepts_minimal_valid_config():
    errors = validate_config(
        {
            "project": {},
            "input": {"mode": "auto"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "intersection"},
            "modules": {},
        }
    )

    assert errors == []


def test_validate_config_reports_invalid_final_rule():
    errors = validate_config(
        {
            "project": {},
            "input": {"mode": "auto"},
            "species": {},
            "gene_family": {},
            "identification": {"final_rule": "ambiguous"},
            "modules": {},
        }
    )

    assert "identification.final_rule must be intersection, union, or hmmer_only" in errors
