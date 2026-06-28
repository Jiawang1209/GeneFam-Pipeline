from pathlib import Path

from bin.genefam.prepare_reference_kaks_inputs import prepare_reference_kaks_inputs, read_tsv
from bin.genefam.prepare_reference_kaks_inputs import read_jcvi_gene_pairs


def test_prepare_reference_kaks_inputs_writes_multispecies_pair_fastas(tmp_path):
    species_manifest = tmp_path / "species_manifest.tsv"
    species_manifest.write_text(
        "species_id\tpep\tcds\tgff3\tgenome\n"
        f"Arabidopsis_thaliana\t{tmp_path / 'ara.pep.fa'}\t{tmp_path / 'ara.cds.fa'}\t\t\n"
        f"Brassica_rapa\t{tmp_path / 'bra.pep.fa'}\t{tmp_path / 'bra.cds.fa'}\t\t\n",
        encoding="utf-8",
    )
    (tmp_path / "ara.pep.fa").write_text(">AT1G01010\nMKK\n>AT1G01020\nMPP\n", encoding="utf-8")
    (tmp_path / "ara.cds.fa").write_text(">AT1G01010\nATGAAAAAA\n>AT1G01020\nATGCCCCCC\n", encoding="utf-8")
    (tmp_path / "bra.pep.fa").write_text(">BraA010001\nMFF\n>BraA010002\nMGG\n", encoding="utf-8")
    (tmp_path / "bra.cds.fa").write_text(">BraA010001\nATGTTTTTT\n>BraA010002\nATGGGGGGG\n", encoding="utf-8")

    mcscanx_pairs = tmp_path / "mcscanx_gene_pairs.tsv"
    mcscanx_pairs.write_text(
        "species_id\ttype\tgene_a\tgene_b\n"
        "Arabidopsis_thaliana\tWGD\tAT1G01010\tAT1G01020\n"
        "Brassica_rapa\ttandem\tBraA010001\tBraA010002\n",
        encoding="utf-8",
    )
    outdir = tmp_path / "kaks_ready"

    outputs = prepare_reference_kaks_inputs(
        species_manifest=read_tsv(species_manifest),
        pair_sources=[("mcscanx", read_tsv(mcscanx_pairs))],
        outdir=outdir,
    )

    assert outputs["status"].read_text(encoding="utf-8") == "source\tstatus\tpair_count\tprepared_count\tmissing_count\tnote\nmcscanx\tavailable\t2\t2\t0\tok\n"
    assert outputs["gene_pairs"].read_text(encoding="utf-8") == (
        "pair_id\tsource\tspecies_a\tspecies_b\tgene_a\tgene_b\tpair_type\n"
        "mcscanx__Arabidopsis_thaliana__AT1G01010__AT1G01020\tmcscanx\tArabidopsis_thaliana\tArabidopsis_thaliana\tAT1G01010\tAT1G01020\tWGD\n"
        "mcscanx__Brassica_rapa__BraA010001__BraA010002\tmcscanx\tBrassica_rapa\tBrassica_rapa\tBraA010001\tBraA010002\ttandem\n"
    )
    assert (outdir / "pair_fastas" / "mcscanx__Arabidopsis_thaliana__AT1G01010__AT1G01020.cds.fa").read_text(
        encoding="utf-8"
    ) == ">AT1G01010\nATGAAAAAA\n>AT1G01020\nATGCCCCCC\n"
    assert (outdir / "pair_fastas" / "mcscanx__Brassica_rapa__BraA010001__BraA010002.pep.fa").read_text(
        encoding="utf-8"
    ) == ">BraA010001\nMFF\n>BraA010002\nMGG\n"
    manifest = outputs["manifest"].read_text(encoding="utf-8")
    assert "KaKs_Calculator" in manifest
    assert "mcscanx__Brassica_rapa__BraA010001__BraA010002" in manifest


def test_prepare_reference_kaks_inputs_strips_terminal_stop_codons_for_kaks_fastas(tmp_path):
    species_manifest = tmp_path / "species_manifest.tsv"
    species_manifest.write_text(
        "species_id\tpep\tcds\n"
        f"Arabidopsis_thaliana\t{tmp_path / 'ara.pep.fa'}\t{tmp_path / 'ara.cds.fa'}\n",
        encoding="utf-8",
    )
    (tmp_path / "ara.pep.fa").write_text(">AT1G01010\nMKK*\n>AT1G01020\nMPP*\n", encoding="utf-8")
    (tmp_path / "ara.cds.fa").write_text(
        ">AT1G01010\nATGAAAAAATAA\n>AT1G01020\nATGCCCCCCtag\n",
        encoding="utf-8",
    )

    outputs = prepare_reference_kaks_inputs(
        species_manifest=read_tsv(species_manifest),
        pair_sources=[
            (
                "mcscanx",
                [
                    {
                        "species_id": "Arabidopsis_thaliana",
                        "type": "WGD",
                        "gene_a": "AT1G01010",
                        "gene_b": "AT1G01020",
                    }
                ],
            )
        ],
        outdir=tmp_path / "kaks_ready",
    )

    assert outputs["status"].read_text(encoding="utf-8") == (
        "source\tstatus\tpair_count\tprepared_count\tmissing_count\tnote\n"
        "mcscanx\tavailable\t1\t1\t0\tok\n"
    )
    assert (tmp_path / "kaks_ready/pair_fastas/mcscanx__Arabidopsis_thaliana__AT1G01010__AT1G01020.cds.fa").read_text(
        encoding="utf-8"
    ) == ">AT1G01010\nATGAAAAAA\n>AT1G01020\nATGCCCCCC\n"
    assert (tmp_path / "kaks_ready/pair_fastas/mcscanx__Arabidopsis_thaliana__AT1G01010__AT1G01020.pep.fa").read_text(
        encoding="utf-8"
    ) == ">AT1G01010\nMKK\n>AT1G01020\nMPP\n"


def test_prepare_reference_kaks_inputs_records_missing_sequences_without_failing(tmp_path):
    species_manifest = tmp_path / "species_manifest.tsv"
    species_manifest.write_text(
        "species_id\tpep\tcds\n"
        f"Arabidopsis_thaliana\t{tmp_path / 'ara.pep.fa'}\t{tmp_path / 'ara.cds.fa'}\n",
        encoding="utf-8",
    )
    (tmp_path / "ara.pep.fa").write_text(">AT1G01010\nMKK\n", encoding="utf-8")
    (tmp_path / "ara.cds.fa").write_text(">AT1G01010\nATGAAAAAA\n", encoding="utf-8")

    pairs = [
        {"species_id": "Arabidopsis_thaliana", "type": "WGD", "gene_a": "AT1G01010", "gene_b": "AT1G99999"}
    ]
    outputs = prepare_reference_kaks_inputs(
        species_manifest=read_tsv(species_manifest),
        pair_sources=[("mcscanx", pairs)],
        outdir=tmp_path / "kaks_ready",
    )

    assert outputs["status"].read_text(encoding="utf-8") == (
        "source\tstatus\tpair_count\tprepared_count\tmissing_count\tnote\n"
        "mcscanx\tmissing_sequence\t1\t0\t1\tmissing CDS/pep records for at least one pair\n"
    )
    assert "AT1G99999" in outputs["missing"].read_text(encoding="utf-8")


def test_prepare_reference_kaks_inputs_reads_jcvi_color2_gene_pairs(tmp_path):
    species_manifest = tmp_path / "species_manifest.tsv"
    species_manifest.write_text(
        "species_id\tpep\tcds\n"
        f"Arabidopsis_thaliana\t{tmp_path / 'ara.pep.fa'}\t{tmp_path / 'ara.cds.fa'}\n"
        f"Capsella_rubella\t{tmp_path / 'cap.pep.fa'}\t{tmp_path / 'cap.cds.fa'}\n",
        encoding="utf-8",
    )
    (tmp_path / "ara.pep.fa").write_text(">AT1G01010\nMKK\n", encoding="utf-8")
    (tmp_path / "ara.cds.fa").write_text(">AT1G01010\nATGAAAAAA\n", encoding="utf-8")
    (tmp_path / "cap.pep.fa").write_text(">Carub.0001\nMFF\n", encoding="utf-8")
    (tmp_path / "cap.cds.fa").write_text(">Carub.0001\nATGTTTTTT\n", encoding="utf-8")

    jcvi_dir = tmp_path / "jcvi_collinearity"
    jcvi_dir.mkdir()
    (jcvi_dir / "jcvi_pair_manifest.tsv").write_text(
        "pair_id\tquery_species\tsubject_species\tquery_bed\tsubject_bed\tquery_pep\tsubject_pep\n"
        "Arabidopsis_thaliana.Capsella_rubella\tArabidopsis_thaliana\tCapsella_rubella\t\t\t\t\n",
        encoding="utf-8",
    )
    (jcvi_dir / "Arabidopsis_thaliana.Capsella_rubella.color2").write_text(
        "g*AT1G01010\tAT1G01010\tCarub.0001\tCarub.0001\t42\t+\n",
        encoding="utf-8",
    )

    outputs = prepare_reference_kaks_inputs(
        species_manifest=read_tsv(species_manifest),
        pair_sources=[("jcvi", read_jcvi_gene_pairs(jcvi_dir))],
        outdir=tmp_path / "kaks_ready",
    )

    assert outputs["status"].read_text(encoding="utf-8") == (
        "source\tstatus\tpair_count\tprepared_count\tmissing_count\tnote\n"
        "jcvi\tavailable\t1\t1\t0\tok\n"
    )
    assert outputs["gene_pairs"].read_text(encoding="utf-8") == (
        "pair_id\tsource\tspecies_a\tspecies_b\tgene_a\tgene_b\tpair_type\n"
        "jcvi__Arabidopsis_thaliana__AT1G01010__Carub.0001\tjcvi\tArabidopsis_thaliana\tCapsella_rubella\tAT1G01010\tCarub.0001\tJCVI_collinear\n"
    )


def test_read_jcvi_gene_pairs_falls_back_when_screen_simple_is_empty(tmp_path):
    jcvi_dir = tmp_path / "jcvi_collinearity"
    jcvi_dir.mkdir()
    (jcvi_dir / "jcvi_pair_manifest.tsv").write_text(
        "pair_id\tquery_species\tsubject_species\tquery_bed\tsubject_bed\tquery_pep\tsubject_pep\n"
        "Arabidopsis_thaliana.Brassica_rapa\tArabidopsis_thaliana\tBrassica_rapa\t\t\t\t\n",
        encoding="utf-8",
    )
    (jcvi_dir / "Arabidopsis_thaliana.Brassica_rapa.anchors.simple").write_text("", encoding="utf-8")
    (jcvi_dir / "Arabidopsis_thaliana.Brassica_rapa.anchors").write_text(
        "AT1G01010\tBraA010001\t100\n",
        encoding="utf-8",
    )

    assert read_jcvi_gene_pairs(jcvi_dir) == [
        {
            "query_species": "Arabidopsis_thaliana",
            "subject_species": "Brassica_rapa",
            "query_gene": "AT1G01010",
            "subject_gene": "BraA010001",
            "pair_type": "JCVI_collinear",
        }
    ]
