from pathlib import Path


def test_local_acceptance_script_runs_release_gate_and_quickstart():
    script = Path("scripts/run_local_acceptance.sh")

    assert script.exists()
    text = script.read_text(encoding="utf-8")
    assert "set -u" in text
    assert "PYTHON_BIN=${PYTHON_BIN:-python}" in text
    assert "CONDA_ENV=${CONDA_ENV:-GeneFamilyFlow}" in text
    assert "RELEASE_OUTDIR=${RELEASE_OUTDIR:-results/release_checks}" in text
    assert "QUICKSTART_OUTDIR=${QUICKSTART_OUTDIR:-results/quickstart}" in text
    assert "bin/genefam/run_release_checks.py" in text
    assert "bin/genefam/run_quickstart.py" in text
    assert "--conda-env \"$CONDA_ENV\"" in text
    assert "results/handoff/handoff_report.md" in text


def test_quickstart_mentions_local_acceptance_script():
    text = Path("docs/quickstart.md").read_text(encoding="utf-8")

    assert "bash scripts/run_local_acceptance.sh" in text
    assert "PYTHON_BIN" in text
    assert "CONDA_ENV" in text
