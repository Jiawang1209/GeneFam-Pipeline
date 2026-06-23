from pathlib import Path


def test_hmmer_module_writes_normalized_tsv():
    module = Path("workflows/modules/hmmer_search.nf").read_text(encoding="utf-8")

    assert "parse_hmmer_domtbl.py" in module
    assert "filter_hmmer_domains.py" in module
    assert "--species-id ${species_id}" in module
    assert "--min-domain-coverage ${params.hmmer_min_domain_coverage}" in module
    assert 'path("${species_id}.${hmm_id}.hmmer.tsv")' in module


def test_diamond_module_writes_normalized_tsv():
    module = Path("workflows/modules/diamond_search.nf").read_text(encoding="utf-8")

    assert "parse_diamond_outfmt6.py" in module
    assert "--species-id ${species_id}" in module
    assert "--out ${species_id}.diamond.tsv" in module
