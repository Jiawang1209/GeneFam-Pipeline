from bin.genefam.build_gene_family_info import build_gene_family_info_tables


def test_build_gene_family_info_tables_classifies_copy_number_and_protein_properties():
    tables = build_gene_family_info_tables(
        family_counts=[
            {"species_id": "Ath", "member_count": "1", "hmmer_count": "1", "diamond_count": "1"},
            {"species_id": "Bra", "member_count": "4", "hmmer_count": "4", "diamond_count": "3"},
            {"species_id": "Bna", "member_count": "9", "hmmer_count": "9", "diamond_count": "8"},
        ],
        fasta_records=[
            ("Ath|AT1G01010", "MAAAAA"),
            ("Bra|BnaA01G0001", "MKWVTFISLL"),
            ("Bna|BnaA02G0002", "MDEKRR"),
        ],
    )

    copy_by_species = {row["species_id"]: row for row in tables.copy_number}
    assert copy_by_species["Ath"]["copy_number_class"] == "single_copy"
    assert copy_by_species["Bra"]["copy_number_class"] == "multi_copy"
    assert copy_by_species["Bna"]["copy_number_class"] == "high_copy"
    assert copy_by_species["Bna"]["copy_number_rank"] == "1"
    assert copy_by_species["Bna"]["percent_of_max"] == "100.0000"

    summary_by_class = {row["copy_number_class"]: row for row in tables.copy_number_summary}
    assert summary_by_class["single_copy"]["species_count"] == "1"
    assert summary_by_class["high_copy"]["mean_member_count"] == "9.0000"
    assert tables.species_order == [
        {
            "species_id": "Bna",
            "member_count": "9",
            "copy_number_class": "high_copy",
            "copy_number_rank": "1",
            "plot_order": "1",
        },
        {
            "species_id": "Bra",
            "member_count": "4",
            "copy_number_class": "multi_copy",
            "copy_number_rank": "2",
            "plot_order": "2",
        },
        {
            "species_id": "Ath",
            "member_count": "1",
            "copy_number_class": "single_copy",
            "copy_number_rank": "3",
            "plot_order": "3",
        },
    ]
    expansion_by_species = {row["species_id"]: row for row in tables.copy_number_expansion}
    assert expansion_by_species["Bna"]["expansion_status"] == "expanded"
    assert expansion_by_species["Bra"]["expansion_status"] == "baseline"
    assert expansion_by_species["Ath"]["expansion_status"] == "contracted"
    assert expansion_by_species["Bna"]["fold_change_vs_median"] == "2.2500"

    protein_by_gene = {row["gene_id"]: row for row in tables.protein_properties}
    assert protein_by_gene["AT1G01010"]["species_id"] == "Ath"
    assert protein_by_gene["AT1G01010"]["protein_length"] == "6"
    assert float(protein_by_gene["AT1G01010"]["molecular_weight_kda"]) > 0
    assert protein_by_gene["AT1G01010"]["isoelectric_point"]
    assert protein_by_gene["AT1G01010"]["gravy"]
