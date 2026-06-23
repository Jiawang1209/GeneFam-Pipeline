from pathlib import Path

from bin.genefam.parse_hmmer_domtbl import parse_domtblout


def test_parse_domtblout_normalizes_hits(tmp_path):
    domtbl = tmp_path / "hits.domtbl"
    domtbl.write_text(
        "# comment\n"
        "AT1G01010 - 120 PF00657 - 200 1e-40 100.0 0.0 1 1 1e-42 1e-40 100.0 0.0 5 80 10 90 8 95 0.95 description\n",
        encoding="utf-8",
    )

    rows = parse_domtblout(domtbl, species_id="Arabidopsis_thaliana")

    assert rows == [
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01010",
            "hmm_id": "PF00657",
            "hmm_length": "200",
            "hmm_from": "5",
            "hmm_to": "80",
            "ali_from": "10",
            "ali_to": "90",
            "domain_coverage": "0.3800",
            "evalue": "1e-40",
            "bitscore": "100.0",
        }
    ]
