from pathlib import Path

from bin.genefam.build_rebuilt_hmmer_inputs import build_rebuilt_hmmer_inputs, read_tsv


def test_build_rebuilt_hmmer_inputs_extracts_first_pass_hits(tmp_path: Path):
    pep = tmp_path / "Ath.pep.clean.fa"
    pep.write_text(">AT1G01010\nMAAA\n>AT1G02020\nMBBB\n", encoding="utf-8")
    manifest = tmp_path / "species_manifest.clean.tsv"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        f"Arabidopsis_thaliana\t{pep}\t\t\t\n",
        encoding="utf-8",
    )
    hmmer = tmp_path / "Ath.PF00657.hmmer.tsv"
    hmmer.write_text(
        "species_id\tgene_id\thmm_id\thmm_length\thmm_from\thmm_to\tali_from\tali_to\tdomain_coverage\tevalue\tbitscore\n"
        "Arabidopsis_thaliana\tAT1G01010\tPF00657\t200\t1\t80\t2\t81\t0.4\t1e-20\t80\n",
        encoding="utf-8",
    )

    outputs = build_rebuilt_hmmer_inputs(
        hmmer_tables=[hmmer],
        species_manifest=manifest,
        family_name="GDSL",
        outdir=tmp_path / "two_pass_hmmer",
    )

    assert outputs["hits_fasta"].read_text(encoding="utf-8") == ">Arabidopsis_thaliana|AT1G01010\nMAAA\n"
    assert read_tsv(outputs["inputs"]) == [
        {
            "species_id": "Arabidopsis_thaliana",
            "pep": str(pep),
            "hmm_id": "GDSL_rebuilt",
            "hmm_profile": str((tmp_path / "two_pass_hmmer/GDSL.rebuilt.hmm").resolve()),
        }
    ]
    assert read_tsv(outputs["status"]) == [
        {
            "status": "available",
            "hit_count": "1",
            "species_count": "1",
            "note": "First-pass HMMER hits extracted for HMM rebuild",
        }
    ]


def test_build_rebuilt_hmmer_inputs_records_missing_hits(tmp_path: Path):
    pep = tmp_path / "Ath.pep.clean.fa"
    pep.write_text(">AT1G01010\nMAAA\n", encoding="utf-8")
    manifest = tmp_path / "species_manifest.clean.tsv"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        f"Arabidopsis_thaliana\t{pep}\t\t\t\n",
        encoding="utf-8",
    )
    hmmer = tmp_path / "Ath.PF00657.hmmer.tsv"
    hmmer.write_text(
        "species_id\tgene_id\thmm_id\thmm_length\thmm_from\thmm_to\tali_from\tali_to\tdomain_coverage\tevalue\tbitscore\n"
        "Arabidopsis_thaliana\tAT9G99999\tPF00657\t200\t1\t80\t2\t81\t0.4\t1e-20\t80\n",
        encoding="utf-8",
    )

    outputs = build_rebuilt_hmmer_inputs(
        hmmer_tables=[hmmer],
        species_manifest=manifest,
        family_name="GDSL",
        outdir=tmp_path / "two_pass_hmmer",
    )

    assert outputs["hits_fasta"].read_text(encoding="utf-8") == ""
    status = read_tsv(outputs["status"])[0]
    assert status["status"] == "missing_input"
    assert status["hit_count"] == "0"
    assert "No first-pass HMMER hits could be matched" in status["note"]
