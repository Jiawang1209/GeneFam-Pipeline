from pathlib import Path

from bin.genefam.validate_config import load_config, validate_config


def test_advanced_modules_example_config_passes_dependency_validation():
    config = load_config(Path("configs/advanced_modules.example.yaml"))

    assert validate_config(config) == []


def test_advanced_modules_example_enables_required_inputs_for_optional_modules():
    config = load_config(Path("configs/advanced_modules.example.yaml"))

    assert config["input"]["required"]["cds"] is True
    assert config["input"]["required"]["gff3"] is True
    assert config["expression"]["matrix"] == "data/expression/family_expression.tsv"
    assert config["modules"]["kaks"] is True
    assert config["modules"]["chromosome_location"] is True
    assert config["modules"]["expression"] is True
    assert config["modules"]["synteny"] is True
    assert config["modules"]["duplication_retention"] is True
