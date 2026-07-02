import csv
from pathlib import Path

from bin.genefam.fetch_timetree_species_tree import validate_downloaded_tree


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_validate_downloaded_tree_reports_missing_species(tmp_path):
    species = ["Arabidopsis thaliana", "Triticum aestivum", "Zea mays"]
    tree = tmp_path / "species_tree.nwk"
    tree.write_text("(Arabidopsis_thaliana:1,Zea_mays:1);\n", encoding="utf-8")
    validation = tmp_path / "timetree_species_validation.tsv"

    status, note = validate_downloaded_tree(species, tree, validation)

    assert status == "available_with_missing_taxa"
    assert note == "Downloaded Newick tree is missing 1 of 3 submitted species: Triticum aestivum"
    assert read_tsv(validation) == [
        {"latin_name": "Arabidopsis thaliana", "newick_label": "Arabidopsis_thaliana", "status": "found"},
        {"latin_name": "Triticum aestivum", "newick_label": "Triticum_aestivum", "status": "missing"},
        {"latin_name": "Zea mays", "newick_label": "Zea_mays", "status": "found"},
    ]


def test_validate_downloaded_tree_reports_complete_tree(tmp_path):
    species = ["Arabidopsis thaliana", "Zea mays"]
    tree = tmp_path / "species_tree.nwk"
    tree.write_text("(Arabidopsis_thaliana:1,Zea_mays:1);\n", encoding="utf-8")
    validation = tmp_path / "timetree_species_validation.tsv"

    status, note = validate_downloaded_tree(species, tree, validation)

    assert status == "available"
    assert note == "Downloaded Newick species tree from TimeTree with all submitted species represented."
