import subprocess
import sys

from bin.genefam.extract_family_sequences import extract_family_sequences, read_tsv


def test_extract_family_sequences_reads_species_specific_peptide_fastas(tmp_path):
    ath = tmp_path / "ath.pep.fa"
    bra = tmp_path / "bra.pep.fa"
    ath.write_text(">AT1G01010\nMAAA\n>AT1G01020\nMCCC\n", encoding="utf-8")
    bra.write_text(">BraA010001\nMGGG\n", encoding="utf-8")
    manifest_rows = [
        {"species_id": "Arabidopsis_thaliana", "pep": str(ath)},
        {"species_id": "Brassica_rapa", "pep": str(bra)},
    ]
    family_rows = [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA010001"},
    ]

    assert extract_family_sequences(family_rows, manifest_rows) == [
        ("Arabidopsis_thaliana|AT1G01010", "MAAA"),
        ("Brassica_rapa|BraA010001", "MGGG"),
    ]


def test_extract_family_sequences_cli_writes_family_members_faa(tmp_path):
    pep = tmp_path / "ath.pep.fa"
    manifest = tmp_path / "species_manifest.tsv"
    candidates = tmp_path / "family_candidates.tsv"
    out = tmp_path / "family_members.faa"
    pep.write_text(">AT1G01010\nMAAA\n", encoding="utf-8")
    manifest.write_text(f"species_id\tpep\tgff3\tcds\tgenome\nArabidopsis_thaliana\t{pep}\t\t\t\n", encoding="utf-8")
    candidates.write_text(
        "species_id\tgene_id\tevidence_sources\thmmer_evalue\tdiamond_evalue\tbest_reference_hit\n"
        "Arabidopsis_thaliana\tAT1G01010\thmmer,diamond\t1e-40\t1e-30\tAT_REF\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/extract_family_sequences.py",
            "--family-candidates",
            str(candidates),
            "--species-manifest",
            str(manifest),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert out.read_text(encoding="utf-8") == ">Arabidopsis_thaliana|AT1G01010\nMAAA\n"
    assert read_tsv(candidates)[0]["gene_id"] == "AT1G01010"
