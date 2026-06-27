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
    assert config["domain_annotation"]["tair_all_domains"] == "data/domain_annotations/all.domains.txt"
    assert config["reference_generation"] == {
        "source": "tair_all_domains",
        "species_id": "Arabidopsis_thaliana",
        "peptides": "data/species_bank/Arabidopsis_thaliana/Arabidopsis_thaliana.pep.fa",
        "all_domains": "data/domain_annotations/all.domains.txt",
        "domain_terms": ["PF00657"],
        "output": "data/reference/GDSL_reference.pep.fa",
        "ids_output": "data/reference/GDSL_reference.ids.txt",
        "missing_ids_output": "data/reference/GDSL_reference.missing_ids.txt",
    }
    assert config["modules"]["phylogeny"] is True
    assert config["modules"]["promoter_cis"] is False
    assert config["modules"]["ppi"] is False
    assert config["modules"]["synteny"] is False
    assert config["modules"]["kaks"] is False
    assert config["modules"]["duplication_retention"] is False
