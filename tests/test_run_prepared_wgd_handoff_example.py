import subprocess
import sys


def test_prepared_wgd_handoff_cli_reports_copyable_missing_nextflow_command(tmp_path):
    outdir = tmp_path / "prepared_wgd"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_prepared_wgd_handoff_example.py",
            "--nextflow-bin",
            "/definitely/missing/nextflow",
            "--example-dir",
            "examples/prepared_wgd_handoff",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    tsv = (outdir / "prepared_wgd_handoff_example.tsv").read_text(encoding="utf-8")
    assert "missing_nextflow" in tsv
    assert (
        "--wgd_event_args '--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta'"
        in tsv
    )
    assert "Prepared WGD Handoff Example" in (outdir / "prepared_wgd_handoff_example.md").read_text(
        encoding="utf-8"
    )
