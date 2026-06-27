import subprocess
import sys

from bin.genefam.build_reference_from_tair_domains import (
    extract_reference_records,
    find_domain_protein_ids,
    read_tair_domains,
)


def test_find_domain_protein_ids_matches_terms_in_tair_domain_columns(tmp_path):
    domains = tmp_path / "all.domains.txt"
    domains.write_text(
        "AT1G06990.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t347\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n"
        "AT1G01010.1\t.\tGene3D\t3.30.310.150\tNAC_domain_superfamily\t12\t161\tNull\tNull\tIPR036093\tNAC domain superfamily\n"
        "AT1G09390.1\t.\tCDD\tcd01837\tGDSL_lipase/esterase-like,_plant\t36\t354\tNull\tNull\tIPR035669\tGDSL lipase/esterase-like, plant\n",
        encoding="utf-8",
    )

    rows = read_tair_domains(domains)
    assert find_domain_protein_ids(rows, ["PF00657"]) == ["AT1G06990"]


def test_extract_reference_records_uses_tair_domain_hits_to_write_peptides(tmp_path):
    domains = tmp_path / "all.domains.txt"
    domains.write_text(
        "AT1G06990.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t347\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n"
        "AT1G09390.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t351\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n",
        encoding="utf-8",
    )
    peptides = tmp_path / "Arabidopsis_thaliana.pep.fa"
    peptides.write_text(
        ">AT1G06990.1 TAIR peptide\nMAAA\n"
        ">AT1G09390.1\nMCCC\n"
        ">AT1G01010.1\nMNNN\n",
        encoding="utf-8",
    )

    records = extract_reference_records(domains, peptides, ["PF00657"])

    assert records == [("AT1G06990.1", "MAAA"), ("AT1G09390.1", "MCCC")]


def test_extract_reference_records_matches_peptide_headers_before_pipe_suffix(tmp_path):
    domains = tmp_path / "all.domains.txt"
    domains.write_text(
        "AT1G06990.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t347\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n",
        encoding="utf-8",
    )
    peptides = tmp_path / "Arabidopsis_thaliana.pep.fa"
    peptides.write_text(">AT1G06990.1|PACid:12345 TAIR peptide\nMAAA\n", encoding="utf-8")

    records = extract_reference_records(domains, peptides, ["PF00657"])

    assert records == [("AT1G06990.1|PACid:12345", "MAAA")]


def test_extract_reference_records_keeps_multiple_isoforms_matching_one_tair_gene_id(tmp_path):
    domains = tmp_path / "all.domains.txt"
    domains.write_text(
        "AT2G29300.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t347\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n",
        encoding="utf-8",
    )
    peptides = tmp_path / "Arabidopsis_thaliana.pep.fa"
    peptides.write_text(
        ">AT2G29300.1|PACid:1\nMAAA\n"
        ">AT2G29300.2|PACid:2\nMCCC\n",
        encoding="utf-8",
    )

    records = extract_reference_records(domains, peptides, ["PF00657"])

    assert records == [("AT2G29300.1|PACid:1", "MAAA"), ("AT2G29300.2|PACid:2", "MCCC")]


def test_build_reference_from_tair_domains_cli_writes_reference_fasta_and_ids(tmp_path):
    domains = tmp_path / "all.domains.txt"
    domains.write_text(
        "AT1G06990.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t347\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n",
        encoding="utf-8",
    )
    peptides = tmp_path / "Arabidopsis_thaliana.pep.fa"
    peptides.write_text(">AT1G06990.1\nMAAA\n", encoding="utf-8")
    out_fasta = tmp_path / "reference" / "GDSL_reference.pep.fa"
    out_ids = tmp_path / "reference" / "GDSL_reference.ids.txt"

    result = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_reference_from_tair_domains.py",
            "--domains",
            str(domains),
            "--peptides",
            str(peptides),
            "--terms",
            "PF00657",
            "--out",
            str(out_fasta),
            "--ids-out",
            str(out_ids),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Extracted 1 reference peptide records" in result.stdout
    assert out_fasta.read_text(encoding="utf-8") == ">AT1G06990.1\nMAAA\n"
    assert out_ids.read_text(encoding="utf-8") == "AT1G06990\n"


def test_build_reference_from_tair_domains_cli_can_report_and_allow_missing_ids(tmp_path):
    domains = tmp_path / "all.domains.txt"
    domains.write_text(
        "AT1G06990.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t347\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n"
        "AT4G16233.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t347\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n",
        encoding="utf-8",
    )
    peptides = tmp_path / "Arabidopsis_thaliana.pep.fa"
    peptides.write_text(">AT1G06990.1\nMAAA\n", encoding="utf-8")
    out_fasta = tmp_path / "reference" / "GDSL_reference.pep.fa"
    missing_out = tmp_path / "reference" / "GDSL_reference.missing_ids.txt"

    subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_reference_from_tair_domains.py",
            "--domains",
            str(domains),
            "--peptides",
            str(peptides),
            "--terms",
            "PF00657",
            "--out",
            str(out_fasta),
            "--allow-missing",
            "--missing-out",
            str(missing_out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert out_fasta.read_text(encoding="utf-8") == ">AT1G06990.1\nMAAA\n"
    assert missing_out.read_text(encoding="utf-8") == "AT4G16233\n"


def test_build_reference_from_tair_domains_cli_can_name_outputs_from_hmm_id(tmp_path):
    domains = tmp_path / "all.domains.txt"
    domains.write_text(
        "AT1G06990.1\t.\tPfam\tPF00657\tGDSL_lipase/esterase\t38\t347\tNull\tNull\tIPR001087\tGDSL lipase/esterase\n",
        encoding="utf-8",
    )
    peptides = tmp_path / "Arabidopsis_thaliana.pep.clean.fa"
    peptides.write_text(">AT1G06990\nMAAA\n", encoding="utf-8")
    outdir = tmp_path / "00_preprocess" / "reference"

    subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_reference_from_tair_domains.py",
            "--domains",
            str(domains),
            "--peptides",
            str(peptides),
            "--terms",
            "PF00657",
            "--hmm-id",
            "PF00657",
            "--outdir",
            str(outdir),
            "--allow-missing",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert (outdir / "PF00657.reference.pep.fa").read_text(encoding="utf-8") == ">AT1G06990\nMAAA\n"
    assert (outdir / "PF00657.TAIR.ID").read_text(encoding="utf-8") == "AT1G06990\n"
    assert (outdir / "PF00657.missing_ids.txt").read_text(encoding="utf-8") == ""
