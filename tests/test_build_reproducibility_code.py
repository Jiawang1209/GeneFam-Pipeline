import subprocess
import sys


def test_build_reproducibility_code_md_collects_analysis_commands(tmp_path):
    config = tmp_path / "config.yaml"
    config.write_text("project:\n  name: My_3species_GDSL\n", encoding="utf-8")
    clean_manifest = tmp_path / "species_manifest.clean.tsv"
    clean_manifest.write_text("species_id\tpep\tgff3\tcds\tgenome\nArabidopsis_thaliana\tath.clean.fa\tath.gff3\tath.cds.clean.fa\t\n", encoding="utf-8")
    reference_manifest = tmp_path / "reference_generation.tsv"
    reference_manifest.write_text(
        "hmm_id\treference_peptides\tids\tmissing_ids\n"
        "PF00657\tresults/00_preprocess/reference/PF00657.reference.pep.fa\tresults/00_preprocess/reference/PF00657.TAIR.ID\tresults/00_preprocess/reference/PF00657.missing_ids.txt\n",
        encoding="utf-8",
    )
    family_candidates = tmp_path / "family_candidates.tsv"
    family_candidates.write_text("species_id\tgene_id\nArabidopsis_thaliana\tAT1G06990\n", encoding="utf-8")
    out = tmp_path / "reproducibility_code.md"

    subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_reproducibility_code.py",
            "--config",
            str(config),
            "--clean-species-manifest",
            str(clean_manifest),
            "--reference-manifest",
            str(reference_manifest),
            "--family-candidates",
            str(family_candidates),
            "--out",
            str(out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    text = out.read_text(encoding="utf-8")
    assert "# Analysis Reproducibility Code" in text
    assert "python bin/genefam/preprocess_species.py" in text
    assert "python bin/genefam/build_reference_from_config.py" in text
    assert "nextflow run workflows/main.nf" in text
    assert "results/00_preprocess/reference/PF00657.reference.pep.fa" in text
    assert str(family_candidates) in text
