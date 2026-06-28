from pathlib import Path

from bin.genefam.run_jcvi_collinearity import run_jcvi_collinearity


def test_run_jcvi_collinearity_marks_missing_dependency(tmp_path):
    jcvi_dir = tmp_path / "jcvi_collinearity"
    (jcvi_dir / "commands").mkdir(parents=True)
    (jcvi_dir / "commands" / "jcvi_commands.sh").write_text("python -m jcvi.graphics.karyotype seqids layout\n", encoding="utf-8")

    outputs = run_jcvi_collinearity(jcvi_dir=jcvi_dir, executable="definitely_missing_jcvi_python")

    assert outputs["status"].read_text(encoding="utf-8") == (
        "status\tcommand_count\tsucceeded_count\tfailed_count\tnote\n"
        "missing_dependency\t1\t0\t0\tJCVI Python module is not importable with definitely_missing_jcvi_python\n"
    )
    assert outputs["commands"].read_text(encoding="utf-8") == (
        "command_index\tcommand\tstatus\texit_code\tnote\n"
        "1\tpython -m jcvi.graphics.karyotype seqids layout\tnot_run\t\tmissing_dependency\n"
    )


def test_run_jcvi_collinearity_marks_missing_commands(tmp_path):
    jcvi_dir = tmp_path / "jcvi_collinearity"
    jcvi_dir.mkdir()

    outputs = run_jcvi_collinearity(jcvi_dir=jcvi_dir)

    assert outputs["status"].read_text(encoding="utf-8") == (
        "status\tcommand_count\tsucceeded_count\tfailed_count\tnote\n"
        "missing_input\t0\t0\t0\tcommands/jcvi_commands.sh not found\n"
    )
