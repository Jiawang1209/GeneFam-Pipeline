from pathlib import Path


def test_reference_mapping_is_strict_reference_audit_not_success_claim():
    text = Path("docs/reference_to_pipeline_mapping.md").read_text(encoding="utf-8")

    assert "不是结果宣传页" in text
    assert "`exact`" in text
    assert "`adapted`" in text
    assert "`partial`" in text
    assert "`missing`" in text
    assert "`skip-by-input`" in text


def test_reference_mapping_covers_all_reference_steps_and_r_scripts():
    text = Path("docs/reference_to_pipeline_mapping.md").read_text(encoding="utf-8")

    for step in [
        "1.database",
        "2.hmmsearch",
        "3.blast",
        "4.identification",
        "5.genefamily_info",
        "6.tree",
        "7.motif_genestructure",
        "8.collinearity",
        "8.1 KaKs",
        "9.mcscanx",
        "9.1 KaKs",
        "10.promoter",
        "11.ppi",
        "12.rnaseq",
    ]:
        assert step in text

    for script in [
        "5.GeneFamily_Info.R",
        "6.tree.R",
        "8.collinearity_kaks.R",
        "9.Circos_*.R",
        "9.mcscanx_KaKs.R",
        "10.promoter.R",
        "11.ppi.R",
        "12.rnaseq.R",
    ]:
        assert script in text


def test_reference_mapping_reports_current_real_three_species_kaks_evidence():
    text = Path("docs/reference_to_pipeline_mapping.md").read_text(encoding="utf-8")

    assert "230 pairs" in text
    assert "125 个非空结果" in text
    assert "105 个失败" in text
    assert "终止密码子清洗已处理" in text
