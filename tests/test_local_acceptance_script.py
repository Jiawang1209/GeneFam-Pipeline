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
    assert "DELIVERY_OUTDIR=${DELIVERY_OUTDIR:-results/delivery_bundle}" in text
    assert "bin/genefam/run_release_checks.py" in text
    assert "bin/genefam/run_quickstart.py" in text
    assert "bin/genefam/run_delivery_bundle.py" in text
    assert "--conda-env \"$CONDA_ENV\"" in text
    assert "--quickstart \"$QUICKSTART_OUTDIR/quickstart_summary.tsv\"" in text
    assert "--outdir \"$DELIVERY_OUTDIR\"" in text
    assert text.index("bin/genefam/run_quickstart.py") < text.index("bin/genefam/run_delivery_bundle.py")
    assert "results/handoff/handoff_report.md" in text
    assert "${DELIVERY_OUTDIR}/delivery_manifest.tsv" in text
    assert "${DELIVERY_OUTDIR}/delivery_bundle.md" in text


def test_quickstart_mentions_local_acceptance_script():
    text = Path("docs/quickstart.md").read_text(encoding="utf-8")

    assert "bash scripts/run_local_acceptance.sh" in text
    assert "PYTHON_BIN" in text
    assert "CONDA_ENV" in text
