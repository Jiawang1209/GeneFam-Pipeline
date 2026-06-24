import csv
import subprocess
import sys
from pathlib import Path

from bin.genefam.build_identification_inputs import (
    build_diamond_inputs,
    build_hmmer_inputs,
    read_tsv,
    resolve_input_paths,
)


def test_build_hmmer_inputs_expands_species_by_hmm_profiles():
    manifest_rows = [
        {"species_id": "Arabidopsis_thaliana", "pep": "ath.pep.fa", "gff3": "", "cds": "", "genome": ""},
        {"species_id": "Brassica_rapa", "pep": "bra.pep.fa", "gff3": "", "cds": "", "genome": ""},
    ]
    config = {
        "gene_family": {
            "hmm_profiles": [
                {"id": "PF00657", "path": "pf00657.hmm"},
                {"id": "PF00001", "path": "pf00001.hmm"},
            ]
        }
    }

    assert build_hmmer_inputs(manifest_rows, config) == [
        {
            "species_id": "Arabidopsis_thaliana",
            "pep": "ath.pep.fa",
            "hmm_id": "PF00657",
            "hmm_profile": "pf00657.hmm",
        },
        {
            "species_id": "Arabidopsis_thaliana",
            "pep": "ath.pep.fa",
            "hmm_id": "PF00001",
            "hmm_profile": "pf00001.hmm",
        },
        {"species_id": "Brassica_rapa", "pep": "bra.pep.fa", "hmm_id": "PF00657", "hmm_profile": "pf00657.hmm"},
        {"species_id": "Brassica_rapa", "pep": "bra.pep.fa", "hmm_id": "PF00001", "hmm_profile": "pf00001.hmm"},
    ]


def test_build_diamond_inputs_uses_reference_peptides_when_configured():
    manifest_rows = [{"species_id": "Arabidopsis_thaliana", "pep": "ath.pep.fa"}]
    config = {"gene_family": {"reference_peptides": "reference.fa"}}

    assert build_diamond_inputs(manifest_rows, config) == [
        {"species_id": "Arabidopsis_thaliana", "pep": "ath.pep.fa", "reference_peptides": "reference.fa"}
    ]


def test_resolve_input_paths_rebases_relative_manifest_and_family_paths(tmp_path):
    base_dir = tmp_path / "repo"
    manifest_rows = [{"species_id": "Arabidopsis_thaliana", "pep": "tests/ath.pep.fa"}]
    config = {
        "gene_family": {
            "hmm_profiles": [{"id": "PF00657", "path": "Reference/PF00657.hmm"}],
            "reference_peptides": "tests/reference.fa",
        }
    }

    resolved_manifest, resolved_config = resolve_input_paths(manifest_rows, config, base_dir)

    assert resolved_manifest[0]["pep"] == str(base_dir / "tests/ath.pep.fa")
    assert resolved_config["gene_family"]["hmm_profiles"][0]["path"] == str(base_dir / "Reference/PF00657.hmm")
    assert resolved_config["gene_family"]["reference_peptides"] == str(base_dir / "tests/reference.fa")


def test_build_identification_inputs_cli_writes_hmmer_and_diamond_tables(tmp_path):
    manifest = tmp_path / "species_manifest.tsv"
    config = tmp_path / "config.yaml"
    outdir = tmp_path / "inputs"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        "Arabidopsis_thaliana\tath.pep.fa\tath.gff3\t\t\n",
        encoding="utf-8",
    )
    config.write_text(
        "gene_family:\n"
        "  hmm_profiles:\n"
        "    - id: PF00657\n"
        "      path: pf00657.hmm\n"
        "  reference_peptides: reference.fa\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_identification_inputs.py",
            "--config",
            str(config),
            "--species-manifest",
            str(manifest),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert read_tsv(outdir / "hmmer_inputs.tsv") == [
        {
            "species_id": "Arabidopsis_thaliana",
            "pep": "ath.pep.fa",
            "hmm_id": "PF00657",
            "hmm_profile": "pf00657.hmm",
        }
    ]
    with (outdir / "diamond_inputs.tsv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert rows == [{"species_id": "Arabidopsis_thaliana", "pep": "ath.pep.fa", "reference_peptides": "reference.fa"}]


def test_example_config_builds_diamond_inputs_for_identification_branch(tmp_path):
    manifest = tmp_path / "species_manifest.tsv"
    outdir = tmp_path / "inputs"

    subprocess.run(
        [
            sys.executable,
            "bin/genefam/discover_species.py",
            "--config",
            "configs/example.config.yaml",
            "--groups",
            "configs/species_groups.yaml",
            "--out",
            str(manifest),
        ],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_identification_inputs.py",
            "--config",
            "configs/example.config.yaml",
            "--species-manifest",
            str(manifest),
            "--outdir",
            str(outdir),
        ],
        check=True,
    )

    rows = read_tsv(outdir / "diamond_inputs.tsv")
    assert rows
    assert {row["reference_peptides"] for row in rows} == {"tests/fixtures/reference/GDSL_reference.pep.fa"}
