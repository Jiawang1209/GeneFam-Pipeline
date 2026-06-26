from pathlib import Path

from bin.genefam.build_promoter_cis_elements import build_promoter_cis_tables, read_tsv, write_tables


def test_build_promoter_cis_tables_normalizes_plantcare_columns_and_infers_categories(tmp_path):
    source = tmp_path / "plantcare.tsv"
    source.write_text(
        "\n".join(
            [
                "Species\tGene ID\tCAREs\tFunction\tSite",
                "Ath\tAT1G01010\tABRE\tabscisic acid responsiveness\t-210",
                "Ath\tAT1G01010\tLTR\tlow-temperature responsiveness\t-450",
                "Bra\tBnaA01G0001\tG-box\tlight responsiveness\t-120",
                "",
            ]
        ),
        encoding="utf-8",
    )

    tables = build_promoter_cis_tables(read_tsv(source))

    assert tables.normalized[0]["species_id"] == "Ath"
    assert tables.normalized[0]["gene_id"] == "AT1G01010"
    assert tables.normalized[0]["element"] == "ABRE"
    assert tables.normalized[0]["category"] == "hormone_responsive"
    assert tables.normalized[1]["category"] == "stress_responsive"
    assert tables.normalized[2]["category"] == "light_responsive"

    matrix_key = {
        (row["species_id"], row["gene_id"], row["category"]): row["count"]
        for row in tables.gene_category_matrix
    }
    assert matrix_key[("Ath", "AT1G01010", "hormone_responsive")] == "1"
    assert matrix_key[("Ath", "AT1G01010", "stress_responsive")] == "1"

    summary_key = {(row["category"], row["element"]): row for row in tables.category_summary}
    assert summary_key[("hormone_responsive", "ABRE")]["total_count"] == "1"
    assert summary_key[("stress_responsive", "LTR")]["gene_count"] == "1"

    element_matrix_key = {
        (row["species_id"], row["gene_id"], row["element"]): row
        for row in tables.gene_element_matrix
    }
    assert element_matrix_key[("Ath", "AT1G01010", "ABRE")] == {
        "species_id": "Ath",
        "gene_id": "AT1G01010",
        "element": "ABRE",
        "category": "hormone_responsive",
        "count": "1",
        "positions": "-210",
    }
    annotation_key = {row["element"]: row for row in tables.element_annotations}
    assert annotation_key["ABRE"] == {
        "element": "ABRE",
        "category": "hormone_responsive",
        "gene_count": "1",
        "species_count": "1",
        "total_count": "1",
        "position_min": "-210",
        "position_median": "-210",
        "position_max": "-210",
        "description": "abscisic acid responsiveness",
    }


def test_write_promoter_cis_tables_writes_expected_outputs(tmp_path):
    tables = build_promoter_cis_tables(
        [
            {
                "species_id": "Ath",
                "gene_id": "AT1G01010",
                "element": "MYB",
                "category": "stress_responsive",
                "position": "-300",
                "description": "drought inducibility",
            }
        ]
    )

    outputs = write_tables(tables, tmp_path)

    assert outputs["promoter_cis_elements"].name == "promoter_cis_elements.tsv"
    assert outputs["promoter_cis_gene_matrix"].name == "promoter_cis_gene_matrix.tsv"
    assert outputs["promoter_cis_gene_element_matrix"].name == "promoter_cis_gene_element_matrix.tsv"
    assert outputs["promoter_cis_category_summary"].name == "promoter_cis_category_summary.tsv"
    assert outputs["promoter_cis_element_annotations"].name == "promoter_cis_element_annotations.tsv"
    assert "MYB" in outputs["promoter_cis_elements"].read_text(encoding="utf-8")
