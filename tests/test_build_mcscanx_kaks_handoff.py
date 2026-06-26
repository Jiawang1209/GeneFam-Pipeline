from pathlib import Path

from bin.genefam.build_mcscanx_kaks_handoff import build_handoff


def test_build_handoff_converts_real_mcscanx_and_kaks_outputs(tmp_path):
    outdir = tmp_path / "handoff"

    outputs = build_handoff(
        collinearity=Path("tests/fixtures/mcscanx/sample.collinearity"),
        kaks=Path("tests/fixtures/kaks/kaks_calculator.tsv"),
        outdir=outdir,
    )

    assert outputs["syntenic_pairs"].read_text(encoding="utf-8").startswith(
        "block_id\tblock_score\tblock_evalue\tblock_pair_count\tgene_a\tgene_b\tpair_evalue\n"
    )
    assert outputs["duplicate_types"].read_text(encoding="utf-8") == (
        "gene_id\tduplicate_type\traw_duplicate_type\n"
        "AT1G01010\tWGD/segmental\tMCScanX_collinear\n"
        "AT1G01020\tWGD/segmental\tMCScanX_collinear\n"
        "BraA010001\tWGD/segmental\tMCScanX_collinear\n"
        "BraA010002\tWGD/segmental\tMCScanX_collinear\n"
    )
    assert outputs["kaks_pairs"].read_text(encoding="utf-8") == (
        "gene_a\tgene_b\tks\tka\tka_ks\tselection_category\n"
        "AT1G01010\tBraA010001\t0.10\t0.02\t0.2\tpurifying\n"
        "AT1G01020\tBraA010002\t0.10\t0.10\t1.0\tneutral\n"
    )
    assert "MCScanX/KaKs Handoff" in outputs["summary"].read_text(encoding="utf-8")


def test_build_handoff_can_prepare_pair_fastas_for_later_kaks_calculation(tmp_path):
    collinearity = tmp_path / "sample.collinearity"
    collinearity.write_text(
        "## Alignment 0: score=100 e_value=1e-10 N=1\n"
        "  0-  0: a1 b1 1e-20\n",
        encoding="utf-8",
    )
    cds_a = tmp_path / "a.cds.fa"
    cds_a.write_text(">a1\nATGGAA\n", encoding="utf-8")
    cds_b = tmp_path / "b.cds.fa"
    cds_b.write_text(">b1\nATGGAG\n", encoding="utf-8")

    outputs = build_handoff(collinearity=collinearity, kaks=None, outdir=tmp_path / "handoff", cds_a=cds_a, cds_b=cds_b)

    manifest = outputs["kaks_pair_manifest"].read_text(encoding="utf-8")
    assert "a1\tb1\t" in manifest
    assert (tmp_path / "handoff" / "kaks_pair_fastas" / "a1__b1.cds.fa").read_text(encoding="utf-8") == (
        ">a1\nATGGAA\n>b1\nATGGAG\n"
    )
    assert outputs["kaks_pairs"].read_text(encoding="utf-8") == "gene_a\tgene_b\tks\tka\tka_ks\tselection_category\n"
