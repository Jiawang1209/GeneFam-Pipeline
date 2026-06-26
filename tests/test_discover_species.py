from pathlib import Path
import subprocess
import sys

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
    assert rows[0]["genome"].endswith("Arabidopsis_thaliana.genome.fa")


def test_example_species_bank_exposes_genome_paths_for_promoter_extraction():
    rows = discover_species(
        root=Path("tests/fixtures/species_bank"),
        include=["Arabidopsis_thaliana", "Brassica_rapa"],
        exclude=[],
        patterns=PATTERNS,
        required={**REQUIRED, "genome": True},
    )

    genomes = {row["species_id"]: row["genome"] for row in rows}

    assert genomes["Arabidopsis_thaliana"].endswith("Arabidopsis_thaliana.genome.fa")
    assert genomes["Brassica_rapa"].endswith("Brassica_rapa.genome.fa")


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


def test_load_species_manifest_resolves_relative_file_paths_against_base_dir(tmp_path):
    manifest = tmp_path / "manifests" / "species_manifest.tsv"
    manifest.parent.mkdir()
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        "Demo_species\tdata/demo.pep.fa\tdata/demo.gff3\tdata/demo.cds.fa\t\n",
        encoding="utf-8",
    )

    rows = load_species_manifest(
        Path("manifests/species_manifest.tsv"),
        include="all",
        exclude=[],
        required=REQUIRED,
        base_dir=tmp_path,
    )

    assert rows == [
        {
            "species_id": "Demo_species",
            "pep": str(tmp_path / "data/demo.pep.fa"),
            "gff3": str(tmp_path / "data/demo.gff3"),
            "cds": str(tmp_path / "data/demo.cds.fa"),
            "genome": "",
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


def test_discover_species_cli_base_dir_resolves_manifest_file_paths_for_nextflow_workdirs(tmp_path):
    manifest = tmp_path / "species_manifest.tsv"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        "Demo_species\tdata/demo.pep.fa\tdata/demo.gff3\t\t\n",
        encoding="utf-8",
    )
    config = tmp_path / "config.yaml"
    config.write_text(
        "\n".join(
            [
                "input:",
                "  mode: manifest",
                "  manifest: species_manifest.tsv",
                "  required:",
                "    pep: true",
                "    gff3: true",
                "species:",
                "  include: all",
                "  exclude: []",
            ]
        ),
        encoding="utf-8",
    )
    groups = tmp_path / "groups.yaml"
    groups.write_text("species_groups: {}\n", encoding="utf-8")
    out = tmp_path / "selected.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/discover_species.py",
            "--config",
            str(config),
            "--groups",
            str(groups),
            "--base-dir",
            str(tmp_path),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    text = out.read_text(encoding="utf-8")
    assert f"Demo_species\t{tmp_path / 'data/demo.pep.fa'}\t{tmp_path / 'data/demo.gff3'}\t\t\n" in text
