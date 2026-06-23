from bin.genefam.merge_identification_evidence import merge_evidence


HMMER_ROWS = [
    {
        "species_id": "Arabidopsis_thaliana",
        "gene_id": "AT1G01010",
        "hmm_id": "PF00657",
        "evalue": "1e-40",
    },
    {
        "species_id": "Arabidopsis_thaliana",
        "gene_id": "AT1G01020",
        "hmm_id": "PF00657",
        "evalue": "1e-20",
    },
]

DIAMOND_ROWS = [
    {
        "species_id": "Arabidopsis_thaliana",
        "gene_id": "AT1G01010",
        "reference_hit": "AT_REF",
        "evalue": "1e-30",
    },
    {
        "species_id": "Arabidopsis_thaliana",
        "gene_id": "AT1G09999",
        "reference_hit": "AT_REF",
        "evalue": "1e-25",
    },
]


def test_merge_evidence_intersection_keeps_only_shared_candidates():
    rows = merge_evidence(HMMER_ROWS, DIAMOND_ROWS, final_rule="intersection")

    assert [row["gene_id"] for row in rows] == ["AT1G01010"]
    assert rows[0]["evidence_sources"] == "diamond,hmmer"
    assert rows[0]["hmmer_evalue"] == "1e-40"
    assert rows[0]["diamond_evalue"] == "1e-30"


def test_merge_evidence_union_keeps_all_candidates():
    rows = merge_evidence(HMMER_ROWS, DIAMOND_ROWS, final_rule="union")

    assert [row["gene_id"] for row in rows] == ["AT1G01010", "AT1G01020", "AT1G09999"]


def test_merge_evidence_hmmer_only_ignores_diamond_only_candidates():
    rows = merge_evidence(HMMER_ROWS, DIAMOND_ROWS, final_rule="hmmer_only")

    assert [row["gene_id"] for row in rows] == ["AT1G01010", "AT1G01020"]
