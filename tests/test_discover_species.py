from pathlib import Path

import pytest

from bin.genefam.discover_species import discover_species, load_species_manifest, species_rows_from_config


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


def test_load_species_manifest_filters_include_and_exclude(tmp_path):
    manifest = tmp_path / "species_manifest.tsv"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        "Arabidopsis_thaliana\tath.pep.fa\tath.gff3\tath.cds.fa\tath.genome.fa\n"
        "Brassica_rapa\tbra.pep.fa\tbra.gff3\tbra.cds.fa\tbra.genome.fa\n"
        "Camelina_sativa\tcam.pep.fa\tcam.gff3\tcam.cds.fa\tcam.genome.fa\n",
        encoding="utf-8",
    )

    rows = load_species_manifest(
        manifest,
        include=["Arabidopsis_thaliana", "Brassica_rapa"],
        exclude=["Brassica_rapa"],
        required=REQUIRED,
    )

    assert rows == [
        {
            "species_id": "Arabidopsis_thaliana",
            "pep": "ath.pep.fa",
            "gff3": "ath.gff3",
            "cds": "ath.cds.fa",
            "genome": "ath.genome.fa",
        }
    ]


def test_load_species_manifest_reports_missing_requested_species(tmp_path):
    manifest = tmp_path / "species_manifest.tsv"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\nArabidopsis_thaliana\tath.pep.fa\tath.gff3\t\t\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Requested species not found: Brassica_rapa"):
        load_species_manifest(
            manifest,
            include=["Brassica_rapa"],
            exclude=[],
            required=REQUIRED,
        )


def test_species_rows_from_config_uses_manifest_mode():
    rows = species_rows_from_config(
        {
            "input": {
                "mode": "manifest",
                "manifest": "tests/fixtures/species_manifest.tsv",
                "required": REQUIRED,
            },
            "species": {"include": ["Arabidopsis_thaliana"], "exclude": []},
        },
        groups={},
    )

    assert rows == [
        {
            "species_id": "Arabidopsis_thaliana",
            "pep": "tests/fixtures/species_bank/Arabidopsis_thaliana/Arabidopsis_thaliana.pep.fa",
            "gff3": "tests/fixtures/species_bank/Arabidopsis_thaliana/Arabidopsis_thaliana.gff3",
            "cds": "",
            "genome": "",
        }
    ]
