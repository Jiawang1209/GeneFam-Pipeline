import subprocess
import sys


def test_run_species_selection_smoke_writes_manifest_and_run_plan(tmp_path):
    outdir = tmp_path / "species_selection_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_species_selection_smoke.py",
            "--config",
            "configs/example.config.yaml",
            "--groups",
            "configs/species_groups.yaml",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "species_manifest" in completed.stdout
    assert "run_plan" in completed.stdout
    manifest = (outdir / "tables/species_manifest.tsv").read_text(encoding="utf-8")
    assert manifest.startswith("species_id\tpep\tgff3\tcds\tgenome\n")
    assert "Arabidopsis_thaliana\t" in manifest
    assert "Brassica_rapa\t" in manifest
    assert "Brassica_oleracea" not in manifest

    run_plan = (outdir / "tables/run_plan.tsv").read_text(encoding="utf-8")
    assert "runtime\tenvironment\tGeneFamilyFlow\n" in run_plan
    assert "runtime\tr_bin\t/usr/local/bin/R\n" in run_plan
    assert "module\tidentification\tenabled\n" in run_plan
    assert "module\tduplication_retention\tdisabled\n" in run_plan

    summary = (outdir / "species_selection_smoke.md").read_text(encoding="utf-8")
    assert "Selected species: 2" in summary
    assert "Arabidopsis_thaliana, Brassica_rapa" in summary
