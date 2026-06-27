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


def test_build_hmmer_inputs_respects_disabled_hmmer_flag():
    manifest_rows = [{"species_id": "Arabidopsis_thaliana", "pep": "ath.pep.fa"}]
    config = {
        "identification": {"use_hmmer": False},
        "gene_family": {"hmm_profiles": [{"id": "PF00657", "path": "pf00657.hmm"}]},
    }

    assert build_hmmer_inputs(manifest_rows, config) == []


def test_build_diamond_inputs_uses_reference_peptides_when_configured():
    manifest_rows = [{"species_id": "Arabidopsis_thaliana", "pep": "ath.pep.fa"}]
    config = {"gene_family": {"reference_peptides": "reference.fa"}}

    assert build_diamond_inputs(manifest_rows, config) == [
        {"species_id": "Arabidopsis_thaliana", "pep": "ath.pep.fa", "reference_peptides": "reference.fa"}
    ]


def test_build_diamond_inputs_can_use_generated_reference_peptides_override():
    manifest_rows = [{"species_id": "Arabidopsis_thaliana", "pep": "ath.clean.fa"}]
    config = {"gene_family": {"reference_peptides": ""}}

    assert build_diamond_inputs(
        manifest_rows,
        config,
        reference_peptides_override="results/00_preprocess/reference/PF00657.reference.pep.fa",
    ) == [
        {
            "species_id": "Arabidopsis_thaliana",
            "pep": "ath.clean.fa",
            "reference_peptides": "results/00_preprocess/reference/PF00657.reference.pep.fa",
        }
    ]


def test_resolve_reference_override_rebases_generated_reference_path(tmp_path):
    reference = tmp_path / "PF00657.reference.pep.fa"
    reference.write_text(">AT1G06990\nMAAA\n", encoding="utf-8")

    rows = build_diamond_inputs(
        [{"species_id": "Arabidopsis_thaliana", "pep": "ath.clean.fa"}],
        {"gene_family": {}},
        reference_peptides_override=str(reference),
    )

    assert rows[0]["reference_peptides"] == str(reference)


def test_build_diamond_inputs_respects_disabled_diamond_flag():
    manifest_rows = [{"species_id": "Arabidopsis_thaliana", "pep": "ath.pep.fa"}]
    config = {
        "identification": {"use_diamond": False},
        "gene_family": {"reference_peptides": "reference.fa"},
    }

    assert build_diamond_inputs(manifest_rows, config) == []


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
            str(Path.cwd() / "bin/genefam/build_identification_inputs.py"),
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


def test_build_identification_inputs_cli_writes_empty_disabled_tool_tables(tmp_path):
    manifest = tmp_path / "species_manifest.tsv"
    config = tmp_path / "config.yaml"
    outdir = tmp_path / "inputs"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        "Arabidopsis_thaliana\tath.pep.fa\tath.gff3\t\t\n",
        encoding="utf-8",
    )
    config.write_text(
        "identification:\n"
        "  use_hmmer: false\n"
        "  use_diamond: false\n"
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
            str(Path.cwd() / "bin/genefam/build_identification_inputs.py"),
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
    assert (outdir / "hmmer_inputs.tsv").read_text(encoding="utf-8") == "species_id\tpep\thmm_id\thmm_profile\n"
    assert (outdir / "diamond_inputs.tsv").read_text(encoding="utf-8") == "species_id\tpep\treference_peptides\n"


def test_build_identification_inputs_cli_writes_absolute_generated_reference_override(tmp_path):
    manifest = tmp_path / "species_manifest.tsv"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        "Arabidopsis_thaliana\tath.clean.fa\tath.gff3\tath.cds.clean.fa\t\n",
        encoding="utf-8",
    )
    config = tmp_path / "config.yaml"
    config.write_text(
        "gene_family:\n"
        "  hmm_profiles: []\n"
        "identification:\n"
        "  use_hmmer: false\n"
        "  use_diamond: true\n",
        encoding="utf-8",
    )
    reference = tmp_path / "PF00657.reference.pep.fa"
    reference.write_text(">AT1G06990\nMAAA\n", encoding="utf-8")
    outdir = tmp_path / "inputs"

    subprocess.run(
        [
            sys.executable,
            str(Path.cwd() / "bin/genefam/build_identification_inputs.py"),
            "--config",
            str(config),
            "--species-manifest",
            str(manifest),
            "--outdir",
            str(outdir),
            "--reference-peptides",
            str(reference.name),
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    assert str(reference.resolve()) in (outdir / "diamond_inputs.tsv").read_text(encoding="utf-8")


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
