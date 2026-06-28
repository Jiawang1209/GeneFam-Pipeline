from pathlib import Path

from bin.genefam.run_pfam_confirmation import run_pfam_confirmation


def test_pfam_confirmation_writes_reference_step4_files_when_db_missing(tmp_path):
    family_candidates = tmp_path / "family_candidates.tsv"
    family_candidates.write_text(
        "species_id\tgene_id\tevidence_sources\n"
        "Arabidopsis_thaliana\tAT1G01010\tdiamond,hmmer\n"
        "Brassica_rapa\tBraA010001\thmmer\n",
        encoding="utf-8",
    )
    family_members = tmp_path / "family_members.faa"
    family_members.write_text(">AT1G01010\nMKK\n>BraA010001\nMFF\n", encoding="utf-8")

    outputs = run_pfam_confirmation(
        family_candidates=family_candidates,
        family_members=family_members,
        hmm_id="PF00657",
        pfam_db=None,
        hmmscan_domtbl=None,
        outdir=tmp_path / "pfam_confirmation",
        executable="hmmscan",
    )

    assert outputs["status"].read_text(encoding="utf-8") == (
        "status\thmm_id\tcandidate_count\tconfirmed_count\tnote\n"
        "missing_input\tPF00657\t2\t0\tNo Pfam HMM database or precomputed hmmscan domtblout was provided\n"
    )
    assert outputs["inter_ids"].read_text(encoding="utf-8") == "AT1G01010\n"
    assert outputs["union_ids"].read_text(encoding="utf-8") == "AT1G01010\nBraA010001\n"
    assert outputs["pfam_ids"].read_text(encoding="utf-8") == ""
    assert outputs["pfam_scan_ids"].read_text(encoding="utf-8") == ""
    assert outputs["identify_fasta"].read_text(encoding="utf-8") == ">AT1G01010\nMKK\n>BraA010001\nMFF\n"


def test_pfam_confirmation_parses_precomputed_hmmscan_domtblout(tmp_path):
    family_candidates = tmp_path / "family_candidates.tsv"
    family_candidates.write_text(
        "species_id\tgene_id\tevidence_sources\n"
        "Arabidopsis_thaliana\tAT1G01010\tdiamond,hmmer\n"
        "Brassica_rapa\tBraA010001\tdiamond,hmmer\n",
        encoding="utf-8",
    )
    family_members = tmp_path / "family_members.faa"
    family_members.write_text(">AT1G01010\nMKK\n>BraA010001\nMFF\n", encoding="utf-8")
    domtbl = tmp_path / "pfam.domtblout"
    domtbl.write_text(
        "# hmmscan domtblout\n"
        "GDSL PF00657.24 300 AT1G01010 - 380 1e-50 180.0 0.0 1 1 1e-50 1e-50 180.0 0.0 1 200 5 250 1 260 0.98 desc\n",
        encoding="utf-8",
    )

    outputs = run_pfam_confirmation(
        family_candidates=family_candidates,
        family_members=family_members,
        hmm_id="PF00657",
        pfam_db=None,
        hmmscan_domtbl=domtbl,
        outdir=tmp_path / "pfam_confirmation",
        executable="hmmscan",
    )

    assert outputs["status"].read_text(encoding="utf-8") == (
        "status\thmm_id\tcandidate_count\tconfirmed_count\tnote\n"
        "available\tPF00657\t2\t1\tPfam confirmation completed\n"
    )
    assert outputs["pfam_scan_ids"].read_text(encoding="utf-8") == "AT1G01010\n"
    assert outputs["identify_fasta"].read_text(encoding="utf-8") == ">AT1G01010\nMKK\n"


def test_pfam_confirmation_identify_fasta_matches_species_prefixed_family_headers(tmp_path):
    family_candidates = tmp_path / "family_candidates.tsv"
    family_candidates.write_text(
        "species_id\tgene_id\tevidence_sources\n"
        "Arabidopsis_thaliana\tAT1G01010\tdiamond,hmmer\n",
        encoding="utf-8",
    )
    family_members = tmp_path / "family_members.faa"
    family_members.write_text(">Arabidopsis_thaliana|AT1G01010\nMKK\n", encoding="utf-8")

    outputs = run_pfam_confirmation(
        family_candidates=family_candidates,
        family_members=family_members,
        hmm_id="PF00657",
        pfam_db=None,
        hmmscan_domtbl=None,
        outdir=tmp_path / "pfam_confirmation",
        executable="hmmscan",
    )

    assert outputs["identify_fasta"].read_text(encoding="utf-8") == ">AT1G01010\nMKK\n"


def test_pfam_confirmation_preserves_multiple_species_prefixed_headers_from_same_species(tmp_path):
    family_candidates = tmp_path / "family_candidates.tsv"
    family_candidates.write_text(
        "species_id\tgene_id\tevidence_sources\n"
        "Capsella_rubella\tCarub.0001s0627\tdiamond,hmmer\n"
        "Capsella_rubella\tCarub.0001s0873\tdiamond,hmmer\n",
        encoding="utf-8",
    )
    family_members = tmp_path / "family_members.faa"
    family_members.write_text(
        ">Capsella_rubella|Carub.0001s0627\nMKK\n"
        ">Capsella_rubella|Carub.0001s0873\nMFF\n",
        encoding="utf-8",
    )

    outputs = run_pfam_confirmation(
        family_candidates=family_candidates,
        family_members=family_members,
        hmm_id="PF00657",
        pfam_db=None,
        hmmscan_domtbl=None,
        outdir=tmp_path / "pfam_confirmation",
        executable="hmmscan",
    )

    assert outputs["identify_fasta"].read_text(encoding="utf-8") == (
        ">Carub.0001s0627\nMKK\n>Carub.0001s0873\nMFF\n"
    )
