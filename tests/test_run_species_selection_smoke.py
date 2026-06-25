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


def test_run_species_selection_smoke_supports_manifest_mode(tmp_path):
    manifest = tmp_path / "species_manifest.tsv"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        "Arabidopsis_thaliana\tath.pep.fa\tath.gff3\t\t\n"
        "Brassica_rapa\tbra.pep.fa\tbra.gff3\t\t\n",
        encoding="utf-8",
    )
    config = tmp_path / "manifest.config.yaml"
    config.write_text(
        "\n".join(
            [
                "project:",
                "  name: manifest_demo",
                "runtime:",
                "  environment: GeneFamilyFlow",
                "  r_bin: /usr/local/bin/R",
                "input:",
                "  mode: manifest",
                f"  manifest: {manifest}",
                "  required:",
                "    pep: true",
                "    gff3: true",
                "species:",
                "  include:",
                "    - Arabidopsis_thaliana",
                "  exclude: []",
                "gene_family:",
                "  name: GDSL",
                "identification:",
                "  final_rule: intersection",
                "plotting:",
                "  reuse_policy: adapt_not_modify",
                "modules:",
                "  identification: true",
            ]
        ),
        encoding="utf-8",
    )
    groups = tmp_path / "groups.yaml"
    groups.write_text("species_groups: {}\n", encoding="utf-8")
    outdir = tmp_path / "species_selection_manifest_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_species_selection_smoke.py",
            "--config",
            str(config),
            "--groups",
            str(groups),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    selected_manifest = (outdir / "tables/species_manifest.tsv").read_text(encoding="utf-8")
    assert "Arabidopsis_thaliana\tath.pep.fa\tath.gff3" in selected_manifest
    assert "Brassica_rapa" not in selected_manifest
    summary = (outdir / "species_selection_smoke.md").read_text(encoding="utf-8")
    assert "Input mode: `manifest`" in summary
    assert f"Species manifest input: `{manifest}`" in summary
