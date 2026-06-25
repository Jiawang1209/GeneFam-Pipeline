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
    assert "ACCEPTANCE_OUTDIR=${ACCEPTANCE_OUTDIR:-results/local_acceptance}" in text
    assert "bin/genefam/run_release_checks.py" in text
    assert "bin/genefam/run_quickstart.py" in text
    assert "bin/genefam/run_delivery_bundle.py" in text
    assert "bin/genefam/write_local_acceptance_summary.py" in text
    assert "--conda-env \"$CONDA_ENV\"" in text
    assert "--quickstart \"$QUICKSTART_OUTDIR/quickstart_summary.tsv\"" in text
    assert "--outdir \"$DELIVERY_OUTDIR\"" in text
    assert "--outdir \"$ACCEPTANCE_OUTDIR\"" in text
    assert text.index("bin/genefam/run_quickstart.py") < text.index("bin/genefam/run_delivery_bundle.py")
    assert text.index("bin/genefam/run_delivery_bundle.py") < text.index("bin/genefam/write_local_acceptance_summary.py")
    assert text.count("bin/genefam/run_delivery_bundle.py") == 2
    assert text.rindex("bin/genefam/write_local_acceptance_summary.py") < text.rindex(
        "bin/genefam/run_delivery_bundle.py"
    )
    assert "results/handoff/handoff_report.md" in text
    assert "${DELIVERY_OUTDIR}/delivery_manifest.tsv" in text
    assert "${DELIVERY_OUTDIR}/delivery_bundle.md" in text
    assert "${ACCEPTANCE_OUTDIR}/local_acceptance_summary.tsv" in text
    assert "${ACCEPTANCE_OUTDIR}/local_acceptance_summary.md" in text


def test_quickstart_mentions_local_acceptance_script():
    text = Path("docs/quickstart.md").read_text(encoding="utf-8")

    assert "bash scripts/run_local_acceptance.sh" in text
    assert "PYTHON_BIN" in text
    assert "CONDA_ENV" in text
    assert "results/local_acceptance/local_acceptance_summary.md" in text
