from pathlib import Path

import pytest

from bin.genefam.discover_species import discover_species


PATTERNS = {
    "pep": ["*.pep.fa"],
    "gff3": ["*.gff3"],
    "cds": ["*.cds.fa"],
    "genome": ["*.genome.fa"],
}

REQUIRED = {"pep": True, "gff3": True, "cds": False, "genome": False}


def test_discover_species_filters_include_list():
    rows = discover_species(
        root=Path("tests/fixtures/species_bank"),
        include=["Arabidopsis_thaliana"],
        exclude=[],
        patterns=PATTERNS,
        required=REQUIRED,
    )

    assert [row["species_id"] for row in rows] == ["Arabidopsis_thaliana"]
    assert rows[0]["pep"].endswith("Arabidopsis_thaliana.pep.fa")
    assert rows[0]["gff3"].endswith("Arabidopsis_thaliana.gff3")
    assert rows[0]["cds"] == ""
    assert rows[0]["genome"] == ""


def test_discover_species_supports_all_with_exclude():
    rows = discover_species(
        root=Path("tests/fixtures/species_bank"),
        include="all",
        exclude=["Brassica_rapa"],
        patterns=PATTERNS,
        required=REQUIRED,
    )

    assert [row["species_id"] for row in rows] == ["Arabidopsis_thaliana"]


def test_discover_species_resolves_relative_root_against_base_dir(tmp_path):
    species_dir = tmp_path / "species_bank" / "Demo_species"
    species_dir.mkdir(parents=True)
    (species_dir / "Demo_species.pep.fa").write_text(">gene1\nMSSS\n", encoding="utf-8")
    (species_dir / "Demo_species.gff3").write_text("##gff-version 3\n", encoding="utf-8")

    rows = discover_species(
        root=Path("species_bank"),
        include="all",
        exclude=[],
        patterns=PATTERNS,
        required=REQUIRED,
        base_dir=tmp_path,
    )

    assert rows[0]["pep"] == str(species_dir / "Demo_species.pep.fa")
    assert rows[0]["gff3"] == str(species_dir / "Demo_species.gff3")


def test_discover_species_fails_for_missing_required_file(tmp_path):
    species_dir = tmp_path / "Missing_gff"
    species_dir.mkdir()
    (species_dir / "Missing_gff.pep.fa").write_text(">gene1\nMSSS\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required gff3"):
        discover_species(
            root=tmp_path,
            include="all",
            exclude=[],
            patterns=PATTERNS,
            required=REQUIRED,
        )
