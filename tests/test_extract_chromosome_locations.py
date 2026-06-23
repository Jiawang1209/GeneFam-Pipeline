import pytest

from bin.genefam.extract_chromosome_locations import extract_locations, extract_locations_for_manifest


def test_extract_locations_reads_gene_coordinates_from_gff3(tmp_path):
    gff3 = tmp_path / "species.gff3"
    gff3.write_text(
        "Chr1\ttest\tgene\t100\t500\t.\t+\t.\tID=gene1;Name=Gene One\n"
        "Chr2\ttest\tmRNA\t700\t900\t.\t-\t.\tID=tx1;Parent=gene2\n"
        "Chr2\ttest\tgene\t700\t900\t.\t-\t.\tID=gene2\n",
        encoding="utf-8",
    )

    rows = extract_locations(gff3, species_id="Test_species", gene_ids={"gene2", "gene1"})

    assert rows == [
        {
            "species_id": "Test_species",
            "gene_id": "gene1",
            "seqid": "Chr1",
            "start": "100",
            "end": "500",
            "strand": "+",
        },
        {
            "species_id": "Test_species",
            "gene_id": "gene2",
            "seqid": "Chr2",
            "start": "700",
            "end": "900",
            "strand": "-",
        },
    ]


def test_extract_locations_fails_for_missing_gene_ids(tmp_path):
    gff3 = tmp_path / "species.gff3"
    gff3.write_text("Chr1\ttest\tgene\t100\t500\t.\t+\t.\tID=gene1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing GFF3 gene IDs: gene2"):
        extract_locations(gff3, species_id="Test_species", gene_ids={"gene2"})


def test_extract_locations_for_manifest_reads_multiple_species_gff3(tmp_path):
    species_a_gff3 = tmp_path / "species_a.gff3"
    species_b_gff3 = tmp_path / "species_b.gff3"
    species_a_gff3.write_text("Chr1\ttest\tgene\t100\t500\t.\t+\t.\tID=geneA\n", encoding="utf-8")
    species_b_gff3.write_text("Chr2\ttest\tgene\t700\t900\t.\t-\t.\tID=geneB\n", encoding="utf-8")
    species_manifest = [
        {"species_id": "Species_a", "gff3": str(species_a_gff3)},
        {"species_id": "Species_b", "gff3": str(species_b_gff3)},
    ]
    family_candidates = [
        {"species_id": "Species_b", "gene_id": "geneB"},
        {"species_id": "Species_a", "gene_id": "geneA"},
    ]

    rows = extract_locations_for_manifest(family_candidates, species_manifest)

    assert rows == [
        {
            "species_id": "Species_a",
            "gene_id": "geneA",
            "seqid": "Chr1",
            "start": "100",
            "end": "500",
            "strand": "+",
        },
        {
            "species_id": "Species_b",
            "gene_id": "geneB",
            "seqid": "Chr2",
            "start": "700",
            "end": "900",
            "strand": "-",
        },
    ]
