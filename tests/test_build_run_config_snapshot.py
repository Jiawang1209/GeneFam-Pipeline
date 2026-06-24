import subprocess
import sys

from bin.genefam.build_run_config_snapshot import build_snapshot


def test_build_snapshot_records_species_selection_and_runtime_context():
    rows = build_snapshot(
        {
            "project": {"name": "demo"},
            "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
            "input": {"root": "data/species_bank"},
            "species": {"include": ["A", "B"], "exclude": ["C"]},
            "run": {"species_group": "brassicaceae"},
            "gene_family": {
                "name": "GDSL",
                "hmm_profiles": [{"id": "PF00657", "path": "PF00657.hmm"}],
                "reference_peptides": "reference.fa",
            },
            "identification": {
                "use_hmmer": True,
                "use_diamond": False,
                "final_rule": "union",
                "hmm_evalue": 1e-10,
                "diamond_evalue": 1e-5,
            },
            "dev": {"mock_external_tools": True},
            "modules": {"identification": True, "synteny": False, "report": True},
        },
        ["A", "B"],
        source_config="configs/example.config.yaml",
        species_manifest="results/run/tables/species_manifest.tsv",
    )

    by_key = {row["key"]: row["value"] for row in rows}
    assert by_key["source_config"] == "configs/example.config.yaml"
    assert by_key["species_manifest"] == "results/run/tables/species_manifest.tsv"
    assert by_key["project.name"] == "demo"
    assert by_key["runtime.environment"] == "GeneFamilyFlow"
    assert by_key["runtime.r_bin"] == "/usr/local/bin/R"
    assert by_key["selected_species"] == "A,B"
    assert by_key["selected_species_count"] == "2"
    assert by_key["species.include"] == "A,B"
    assert by_key["species.exclude"] == "C"
    assert by_key["gene_family.hmm_profiles"] == "PF00657"
    assert by_key["identification.use_hmmer"] == "True"
    assert by_key["identification.use_diamond"] == "False"
    assert by_key["modules.enabled"] == "identification,report"


def test_build_run_config_snapshot_cli_writes_key_value_tsv(tmp_path):
    out = tmp_path / "run_config_snapshot.tsv"
    species_manifest = tmp_path / "species_manifest.tsv"
    species_manifest.write_text(
        "species_id\tpep\tcds\tgenome\tgff3\n"
        "Arabidopsis_thaliana\tA.pep.fa\t\t\tA.gff3\n"
        "Brassica_rapa\tB.pep.fa\t\t\tB.gff3\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_run_config_snapshot.py",
            "--config",
            "configs/example.config.yaml",
            "--species-manifest",
            str(species_manifest),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    text = out.read_text(encoding="utf-8")
    assert text.startswith("key\tvalue\n")
    assert "project.name\tGDSL_demo\n" in text
    assert "gene_family.name\tGDSL\n" in text
