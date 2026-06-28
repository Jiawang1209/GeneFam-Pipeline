from pathlib import Path

from bin.genefam.normalize_reference_kaks_results import normalize_reference_kaks_results, read_tsv


def test_normalize_reference_kaks_results_keeps_nonempty_results_and_skips_failed(tmp_path):
    results_dir = tmp_path / "kaks_results"
    results_dir.mkdir()
    good = results_dir / "mcscanx__Arabidopsis_thaliana__AT1G01010__AT1G01020.kaks.tsv"
    good.write_text(
        "Sequence\tMethod\tKa\tKs\tKa/Ks\tP-Value(Fisher)\n"
        ">AT1G01010\tMA\t0.02\t0.10\t0.20\t0.01\n",
        encoding="utf-8",
    )
    failed = results_dir / "mcscanx__Arabidopsis_thaliana__AT1G01030__AT1G01040.kaks.tsv"
    failed.write_text("", encoding="utf-8")
    manifest = tmp_path / "kaks_calculator_results.tsv"
    manifest.write_text(
        "pair_id\tsource\tkaks_result\tstatus\tnote\n"
        f"mcscanx__Arabidopsis_thaliana__AT1G01010__AT1G01020\tmcscanx\t{good}\tavailable\tok\n"
        f"mcscanx__Arabidopsis_thaliana__AT1G01030__AT1G01040\tmcscanx\t{failed}\tfailed\tempty KaKs output\n",
        encoding="utf-8",
    )

    outputs = normalize_reference_kaks_results(results=read_tsv(manifest), outdir=tmp_path / "out")

    assert outputs["pairs"].read_text(encoding="utf-8") == (
        "gene_a\tgene_b\tks\tka\tka_ks\tp_value\tselection_category\tsource\tpair_id\tmethod\n"
        "AT1G01010\tAT1G01020\t0.10\t0.02\t0.20\t0.01\tpurifying\tmcscanx\tmcscanx__Arabidopsis_thaliana__AT1G01010__AT1G01020\tMA\n"
    )
    assert outputs["skipped"].read_text(encoding="utf-8") == (
        "pair_id\tsource\tkaks_result\treason\tnote\n"
        f"mcscanx__Arabidopsis_thaliana__AT1G01030__AT1G01040\tmcscanx\t{failed}\tcalculator_failed\tempty KaKs output\n"
    )
    assert outputs["summary"].read_text(encoding="utf-8") == (
        "status\tinput_count\tavailable_count\tskipped_count\tnote\n"
        "available\t2\t1\t1\tok\n"
    )
