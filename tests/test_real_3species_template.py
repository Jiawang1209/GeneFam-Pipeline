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
    assert config["input"]["required"]["genome"] is True
    assert config["preprocess"] == {"enabled": True, "outdir": "results/01_preprocess"}
    assert config["reference_generation"] == {
        "enabled": True,
        "source": "tair_all_domains",
        "domain_annotation": "data/domain_annotations/all.domains.txt",
        "reference_species": "Arabidopsis_thaliana",
    }
    assert "reference_peptides" not in config["gene_family"]
    assert config["modules"]["phylogeny"] is True
    assert config["modules"]["promoter_cis"] is True
    assert config["modules"]["ppi"] is True
    assert config["modules"]["synteny"] is True
    assert config["modules"]["kaks"] is True
    assert config["modules"]["duplication_retention"] is True
    assert config["modules"]["expression"] is True
    assert config["promoter"]["cis_elements"] is None
    assert config["promoter"]["element_descriptions"] == "data/config/cir_element.desc.20240509.xlsx"
    assert config["mcscanx"]["self_dir"] is None
    assert config["mcscanx"]["execute_self"] is True
    assert config["mcscanx"]["search_tool"] == "diamond"
    assert config["identification"]["two_pass_hmmer"] is False
    assert config["ppi"]["edges"] == "data/config/AraNet.txt"
    assert config["ppi"]["reference_species"] == "Arabidopsis_thaliana"
