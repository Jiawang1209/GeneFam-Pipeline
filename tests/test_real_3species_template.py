from pathlib import Path

from bin.genefam.validate_config import load_config, validate_config


def test_real_three_species_template_is_a_valid_non_mock_config():
    config_path = Path("configs/real_3species.template.yaml")

    config = load_config(config_path)
    errors = validate_config(config, check_paths=False)

    assert errors == []
    assert config["project"]["outdir"] == "results/My_3species_GDSL"
    assert config["input"]["root"] == "data/species_bank"
    assert config["species"]["include"] == [
        "Arabidopsis_thaliana",
        "Brassica_rapa",
        "Capsella_rubella",
    ]
    assert config["dev"]["mock_external_tools"] is False
    assert config["input"]["required"]["cds"] is True
    assert config["preprocess"] == {"enabled": True, "outdir": "results/00_preprocess"}
    assert config["reference_generation"] == {
        "enabled": True,
        "source": "tair_all_domains",
        "domain_annotation": "data/domain_annotations/all.domains.txt",
        "reference_species": "Arabidopsis_thaliana",
    }
    assert "reference_peptides" not in config["gene_family"]
    assert config["modules"]["phylogeny"] is True
    assert config["modules"]["promoter_cis"] is False
    assert config["modules"]["ppi"] is False
    assert config["modules"]["synteny"] is False
    assert config["modules"]["kaks"] is False
    assert config["modules"]["duplication_retention"] is False
