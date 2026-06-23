from bin.genefam.filter_hmmer_domains import filter_domains

import csv
import subprocess
import sys


def test_filter_domains_applies_evalue_bitscore_and_coverage():
    rows = [
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01010",
            "hmm_id": "PF00657",
            "evalue": "1e-40",
            "bitscore": "100.0",
            "domain_coverage": "0.80",
        },
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01020",
            "hmm_id": "PF00657",
            "evalue": "1e-4",
            "bitscore": "90.0",
            "domain_coverage": "0.90",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA010001",
            "hmm_id": "PF00657",
            "evalue": "1e-45",
            "bitscore": "10.0",
            "domain_coverage": "0.95",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA010002",
            "hmm_id": "PF00657",
            "evalue": "1e-30",
            "bitscore": "80.0",
            "domain_coverage": "0.20",
        },
    ]

    filtered = filter_domains(rows, max_evalue=1e-10, min_bitscore=50.0, min_domain_coverage=0.5)

    assert [row["gene_id"] for row in filtered] == ["AT1G01010"]


def test_filter_domains_cli_works_when_invoked_by_script_path(tmp_path):
    input_tsv = tmp_path / "hmmer.tsv"
    output_tsv = tmp_path / "filtered.tsv"
    input_tsv.write_text(
        "\t".join(
            [
                "species_id",
                "gene_id",
                "hmm_id",
                "hmm_length",
                "hmm_from",
                "hmm_to",
                "ali_from",
                "ali_to",
                "domain_coverage",
                "evalue",
                "bitscore",
            ]
        )
        + "\n"
        "Arabidopsis_thaliana\tAT1G01010\tPF00657\t200\t1\t180\t5\t190\t0.9000\t1e-40\t100.0\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/filter_hmmer_domains.py",
            "--input",
            str(input_tsv),
            "--max-evalue",
            "1e-10",
            "--min-bitscore",
            "50",
            "--min-domain-coverage",
            "0.5",
            "--out",
            str(output_tsv),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    with output_tsv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [row["gene_id"] for row in rows] == ["AT1G01010"]
