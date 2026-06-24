import subprocess
import sys


def test_run_domain_filter_smoke_writes_filtered_domains_and_summary(tmp_path):
    outdir = tmp_path / "domain_filter_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_domain_filter_smoke.py",
            "--input",
            "tests/fixtures/hmmer_domains/domains.tsv",
            "--max-evalue",
            "1e-10",
            "--min-bitscore",
            "50",
            "--min-domain-coverage",
            "0.5",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "filtered_domains" in completed.stdout
    filtered = outdir / "tables/filtered_domains.tsv"
    assert filtered.read_text(encoding="utf-8") == (
        "species_id\tgene_id\thmm_id\thmm_length\thmm_from\thmm_to\tali_from\tali_to\tdomain_coverage\tevalue\tbitscore\n"
        "Arabidopsis_thaliana\tAT1G01010\tPF00657\t200\t1\t180\t5\t190\t0.9000\t1e-40\t100.0\n"
        "Brassica_rapa\tBraA010001\tPF00657\t200\t10\t190\t12\t210\t0.9050\t1e-35\t120.0\n"
    )
    summary = (outdir / "domain_filter_smoke.md").read_text(encoding="utf-8")
    assert "Input domains: 4" in summary
    assert "Filtered domains: 2" in summary
