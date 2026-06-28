from pathlib import Path

from bin.genefam.build_mcscanx_duplicate_types import build_duplicate_type_rows, write_tsv


def test_build_duplicate_type_rows_from_mcscanx_self_pairs():
    rows = build_duplicate_type_rows(
        [
            {"species_id": "Arabidopsis_thaliana", "type": "WGD", "gene_a": "AT1G01010", "gene_b": "AT1G02020"},
            {"species_id": "Arabidopsis_thaliana", "type": "tandem", "gene_a": "AT1G02020", "gene_b": "AT1G02030"},
            {"species_id": "Brassica_rapa", "type": "segmental", "gene_a": "BraA01g001", "gene_b": "BraA02g002"},
        ]
    )

    assert rows == [
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01010",
            "duplicate_type": "WGD/segmental",
            "raw_duplicate_type": "WGD",
            "evidence_pair_count": "1",
        },
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G02020",
            "duplicate_type": "tandem",
            "raw_duplicate_type": "WGD,tandem",
            "evidence_pair_count": "2",
        },
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G02030",
            "duplicate_type": "tandem",
            "raw_duplicate_type": "tandem",
            "evidence_pair_count": "1",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA01g001",
            "duplicate_type": "WGD/segmental",
            "raw_duplicate_type": "segmental",
            "evidence_pair_count": "1",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA02g002",
            "duplicate_type": "WGD/segmental",
            "raw_duplicate_type": "segmental",
            "evidence_pair_count": "1",
        },
    ]


def test_write_tsv_keeps_header_for_empty_mcscanx_pairs(tmp_path: Path):
    out = tmp_path / "duplicate_types.tsv"

    write_tsv([], out)

    assert out.read_text(encoding="utf-8") == "species_id\tgene_id\tduplicate_type\traw_duplicate_type\tevidence_pair_count\n"
