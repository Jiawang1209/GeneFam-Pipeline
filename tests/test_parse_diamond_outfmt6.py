from pathlib import Path

from bin.genefam.parse_diamond_outfmt6 import parse_outfmt6


def test_parse_outfmt6_normalizes_target_gene_hits(tmp_path):
    outfmt6 = tmp_path / "hits.tsv"
    outfmt6.write_text(
        "AT_REF\tBraA010001\t92.5\t300\t1\t0\t1\t300\t4\t303\t1e-45\t210.0\n",
        encoding="utf-8",
    )

    rows = parse_outfmt6(outfmt6, species_id="Brassica_rapa")

    assert rows == [
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA010001",
            "reference_hit": "AT_REF",
            "evalue": "1e-45",
            "bitscore": "210.0",
        }
    ]


def test_parse_outfmt6_keeps_best_hit_per_gene_by_evalue_then_bitscore(tmp_path):
    outfmt6 = tmp_path / "hits.tsv"
    outfmt6.write_text(
        "AT_REF_LOW\tAT1G01010\t90.0\t250\t1\t0\t1\t250\t1\t250\t1e-20\t120.0\n"
        "AT_REF_BEST\tAT1G01010\t95.0\t250\t1\t0\t1\t250\t1\t250\t1e-40\t180.0\n",
        encoding="utf-8",
    )

    rows = parse_outfmt6(outfmt6, species_id="Arabidopsis_thaliana")

    assert rows[0]["gene_id"] == "AT1G01010"
    assert rows[0]["reference_hit"] == "AT_REF_BEST"
    assert rows[0]["evalue"] == "1e-40"
