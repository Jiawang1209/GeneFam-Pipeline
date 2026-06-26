from bin.genefam.build_circlize_inputs import build_circlize_inputs


def test_build_circlize_inputs_joins_mcscanx_pairs_to_gene_coordinates():
    locations = [
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01010",
            "seqid": "Chr1",
            "start": "100",
            "end": "500",
            "strand": "+",
        },
        {
            "species_id": "Arabidopsis_thaliana",
            "gene_id": "AT1G01020",
            "seqid": "Chr1",
            "start": "800",
            "end": "1100",
            "strand": "+",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA010001",
            "seqid": "A01",
            "start": "200",
            "end": "900",
            "strand": "-",
        },
    ]
    syntenic_pairs = [
        {
            "block_id": "0",
            "gene_a": "AT1G01010",
            "gene_b": "BraA010001",
            "pair_evalue": "1e-50",
        },
        {
            "block_id": "0",
            "gene_a": "AT1G01020",
            "gene_b": "BraA010002",
            "pair_evalue": "2e-40",
        },
    ]

    chromosomes, links, skipped = build_circlize_inputs(locations, syntenic_pairs)

    assert chromosomes == [
        {
            "chr_id": "Arabidopsis_thaliana|Chr1",
            "species_id": "Arabidopsis_thaliana",
            "seqid": "Chr1",
            "start": "1",
            "end": "1100",
            "gene_count": "2",
        },
        {
            "chr_id": "Brassica_rapa|A01",
            "species_id": "Brassica_rapa",
            "seqid": "A01",
            "start": "1",
            "end": "900",
            "gene_count": "1",
        },
    ]
    assert links == [
        {
            "block_id": "0",
            "gene_a": "AT1G01010",
            "gene_a_chr": "Arabidopsis_thaliana|Chr1",
            "gene_a_start": "100",
            "gene_a_end": "500",
            "gene_b": "BraA010001",
            "gene_b_chr": "Brassica_rapa|A01",
            "gene_b_start": "200",
            "gene_b_end": "900",
            "pair_evalue": "1e-50",
        }
    ]
    assert skipped == [
        {
            "block_id": "0",
            "gene_a": "AT1G01020",
            "gene_b": "BraA010002",
            "reason": "missing_gene_b_coordinate",
        }
    ]


def test_build_circlize_inputs_can_build_density_and_duplicate_type_tracks():
    locations = [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1", "seqid": "Chr1", "start": "100", "end": "200", "strand": "+"},
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT2", "seqid": "Chr1", "start": "900", "end": "1000", "strand": "+"},
        {"species_id": "Brassica_rapa", "gene_id": "BR1", "seqid": "A01", "start": "150", "end": "250", "strand": "-"},
        {"species_id": "Brassica_rapa", "gene_id": "BR2", "seqid": "A01", "start": "1200", "end": "1400", "strand": "+"},
    ]
    syntenic_pairs = [
        {"block_id": "blockA", "gene_a": "AT1", "gene_b": "BR1", "pair_evalue": "1e-20"},
        {"block_id": "blockB", "gene_a": "AT2", "gene_b": "BR2", "pair_evalue": "1e-30"},
    ]
    duplicate_types = [
        {"gene_id": "AT1", "duplicate_type": "WGD"},
        {"gene_id": "AT2", "duplicate_type": "tandem"},
        {"gene_id": "BR1", "duplicate_type": "WGD"},
        {"gene_id": "BR2", "duplicate_type": "dispersed"},
    ]

    chromosomes, links, skipped, density, duplicate_tracks = build_circlize_inputs(
        locations,
        syntenic_pairs,
        duplicate_types=duplicate_types,
        density_window_size=1000,
        include_tracks=True,
    )

    assert skipped == []
    assert len(chromosomes) == 2
    assert len(links) == 2
    assert density == [
        {
            "chr_id": "Arabidopsis_thaliana|Chr1",
            "window_start": "1",
            "window_end": "1000",
            "linked_gene_count": "2",
            "link_count": "2",
        },
        {
            "chr_id": "Brassica_rapa|A01",
            "window_start": "1",
            "window_end": "1000",
            "linked_gene_count": "1",
            "link_count": "1",
        },
        {
            "chr_id": "Brassica_rapa|A01",
            "window_start": "1001",
            "window_end": "1400",
            "linked_gene_count": "1",
            "link_count": "1",
        },
    ]
    assert duplicate_tracks == [
        {
            "chr_id": "Arabidopsis_thaliana|Chr1",
            "gene_id": "AT1",
            "start": "100",
            "end": "200",
            "duplicate_type": "WGD",
            "link_count": "1",
        },
        {
            "chr_id": "Arabidopsis_thaliana|Chr1",
            "gene_id": "AT2",
            "start": "900",
            "end": "1000",
            "duplicate_type": "tandem",
            "link_count": "1",
        },
        {
            "chr_id": "Brassica_rapa|A01",
            "gene_id": "BR1",
            "start": "150",
            "end": "250",
            "duplicate_type": "WGD",
            "link_count": "1",
        },
        {
            "chr_id": "Brassica_rapa|A01",
            "gene_id": "BR2",
            "start": "1200",
            "end": "1400",
            "duplicate_type": "dispersed",
            "link_count": "1",
        },
    ]
