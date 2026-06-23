from bin.genefam.summarize_family import summarize_candidates


def test_summarize_candidates_counts_evidence_by_species():
    rows = [
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01010",
            "evidence_sources": "diamond,hmmer",
        },
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01020",
            "evidence_sources": "hmmer",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA010001",
            "evidence_sources": "diamond",
        },
    ]

    summary = summarize_candidates(rows)

    assert summary == [
        {
            "species_id": "Arabidopsis_thaliana",
            "member_count": 2,
            "hmmer_count": 2,
            "diamond_count": 1,
            "intersection_count": 1,
        },
        {
            "species_id": "Brassica_rapa",
            "member_count": 1,
            "hmmer_count": 0,
            "diamond_count": 1,
            "intersection_count": 0,
        },
    ]
