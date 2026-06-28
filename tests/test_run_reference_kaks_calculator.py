from pathlib import Path

from bin.genefam.run_reference_kaks_calculator import plan_or_run_kaks, read_tsv


def test_plan_or_run_kaks_marks_missing_input_for_empty_manifest(tmp_path):
    manifest = tmp_path / "kaks_input_manifest.tsv"
    manifest.write_text("pair_id\tsource\tcds_fasta\tpep_fasta\texpected_kaks\tkaks_command\n", encoding="utf-8")

    outputs = plan_or_run_kaks(manifest=read_tsv(manifest), outdir=tmp_path / "out", executable="KaKs_Calculator")

    assert outputs["status"].read_text(encoding="utf-8") == (
        "status\tpair_count\tsucceeded_count\tfailed_count\tnote\n"
        "missing_input\t0\t0\t0\tNo Ka/Ks input pairs were prepared\n"
    )
    assert outputs["commands"].read_text(encoding="utf-8") == "pair_id\tcommand\n"
    assert outputs["failure_summary"].read_text(encoding="utf-8") == (
        "source\tcalculator_status\tcalculator_note\tqc_flags\tpair_count\texample_pair_ids\tinterpretation\n"
    )


def test_plan_or_run_kaks_marks_missing_dependency_without_running_pairs(tmp_path):
    cds = tmp_path / "pair.cds.fa"
    cds.write_text(">a\nATGAAA\n>b\nATGCCC\n", encoding="utf-8")
    manifest_rows = [
        {
            "pair_id": "pair1",
            "source": "mcscanx",
            "cds_fasta": str(cds),
            "pep_fasta": "",
            "expected_kaks": str(tmp_path / "pair1.kaks.tsv"),
            "kaks_command": "",
        }
    ]

    outputs = plan_or_run_kaks(manifest=manifest_rows, outdir=tmp_path / "out", executable="definitely_missing_kaks")

    assert outputs["status"].read_text(encoding="utf-8") == (
        "status\tpair_count\tsucceeded_count\tfailed_count\tnote\n"
        "missing_dependency\t1\t0\t0\tKaKs executable not found: definitely_missing_kaks\n"
    )
    assert "definitely_missing_kaks -i " in outputs["commands"].read_text(encoding="utf-8")
    assert outputs["failure_summary"].read_text(encoding="utf-8") == (
        "source\tcalculator_status\tcalculator_note\tqc_flags\tpair_count\texample_pair_ids\tinterpretation\n"
        "mcscanx\tmissing_dependency\tKaKs executable not found: definitely_missing_kaks\tclean_basic_qc\t1\tpair1\tKa/Ks was not calculated because the required executable or input was unavailable.\n"
    )


def test_plan_or_run_kaks_marks_empty_calculator_output_as_failed(tmp_path):
    executable = tmp_path / "fake_kaks"
    executable.write_text("#!/bin/sh\n: > \"$4\"\n", encoding="utf-8")
    executable.chmod(0o755)
    cds = tmp_path / "pair.cds.fa"
    cds.write_text(">a\nATGAAA\n>b\nATGCCC\n", encoding="utf-8")
    manifest_rows = [
        {
            "pair_id": "pair1",
            "source": "mcscanx",
            "cds_fasta": str(cds),
            "pep_fasta": "",
            "expected_kaks": str(tmp_path / "pair1.kaks.tsv"),
            "kaks_command": "",
        }
    ]

    outputs = plan_or_run_kaks(manifest=manifest_rows, outdir=tmp_path / "out", executable=str(executable))

    assert outputs["status"].read_text(encoding="utf-8") == (
        "status\tpair_count\tsucceeded_count\tfailed_count\tnote\n"
        "failed\t1\t0\t1\tSome Ka/Ks jobs failed\n"
    )
    assert "empty KaKs output" in outputs["results"].read_text(encoding="utf-8")
    qc = outputs["qc"].read_text(encoding="utf-8")
    assert "pair_id\tsource\tcds_fasta\tsequence_count\tgene_a\tgene_b" in qc
    assert "\t6\t0\tFalse\t0\t0\t6\t0\tFalse\t0\t0\t0\tclean_basic_qc\tfailed\tempty KaKs output\n" in qc
    assert outputs["failure_summary"].read_text(encoding="utf-8") == (
        "source\tcalculator_status\tcalculator_note\tqc_flags\tpair_count\texample_pair_ids\tinterpretation\n"
        "mcscanx\tfailed\tempty KaKs output\tclean_basic_qc\t1\tpair1\tKaKs_Calculator finished without a usable result file; inspect the pair CDS alignment and calculator log/output.\n"
    )


def test_plan_or_run_kaks_groups_failure_summary_by_source_note_and_qc(tmp_path):
    executable = tmp_path / "fake_kaks"
    executable.write_text("#!/bin/sh\n: > \"$4\"\n", encoding="utf-8")
    executable.chmod(0o755)
    cds_clean = tmp_path / "pair.clean.cds.fa"
    cds_clean.write_text(">a\nATGAAA\n>b\nATGCCC\n", encoding="utf-8")
    cds_terminal_stop = tmp_path / "pair.stop.cds.fa"
    cds_terminal_stop.write_text(">a\nATGTAA\n>b\nATGCCC\n", encoding="utf-8")
    manifest_rows = [
        {"pair_id": "mc1", "source": "mcscanx", "cds_fasta": str(cds_clean), "pep_fasta": "", "expected_kaks": "", "kaks_command": ""},
        {"pair_id": "mc2", "source": "mcscanx", "cds_fasta": str(cds_terminal_stop), "pep_fasta": "", "expected_kaks": "", "kaks_command": ""},
        {"pair_id": "jc1", "source": "jcvi", "cds_fasta": str(cds_clean), "pep_fasta": "", "expected_kaks": "", "kaks_command": ""},
    ]

    outputs = plan_or_run_kaks(manifest=manifest_rows, outdir=tmp_path / "out", executable=str(executable))

    assert outputs["failure_summary"].read_text(encoding="utf-8") == (
        "source\tcalculator_status\tcalculator_note\tqc_flags\tpair_count\texample_pair_ids\tinterpretation\n"
        "jcvi\tfailed\tempty KaKs output\tclean_basic_qc\t1\tjc1\tKaKs_Calculator finished without a usable result file; inspect the pair CDS alignment and calculator log/output.\n"
        "mcscanx\tfailed\tempty KaKs output\tclean_basic_qc\t1\tmc1\tKaKs_Calculator finished without a usable result file; inspect the pair CDS alignment and calculator log/output.\n"
        "mcscanx\tfailed\tempty KaKs output\tterminal_stop\t1\tmc2\tKaKs_Calculator finished without a usable result file; CDS QC flags suggest checking terminal stop codons before rerunning.\n"
    )
