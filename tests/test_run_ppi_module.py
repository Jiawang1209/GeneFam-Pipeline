import csv
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_ppi_module.py"
PLOT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts/plot_ppi_ggnetview_reference.R"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_fake_project(root: Path) -> Path:
    project = root / "projects/Whirly_2026"
    results = project / "results"
    clean = results / "01_preprocess/species_clean_bank/Arabidopsis_thaliana/clean"
    clean.mkdir(parents=True)
    clean.joinpath("Arabidopsis_thaliana.protein.clean.fa").write_text(
        ">AT1G01010\nMAAA\n>AT2G02020\nMBBB\n",
        encoding="utf-8",
    )
    manifest = results / "01_preprocess/species_clean_bank_manifest.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "species_id\tprotein\tcds\tgenome\tgff3\tstatus\n"
        f"Arabidopsis_thaliana\t{clean / 'Arabidopsis_thaliana.protein.clean.fa'}\t\t\t\tpass\n",
        encoding="utf-8",
    )
    candidates = results / "04_identification/tables/family_candidates.tsv"
    candidates.parent.mkdir(parents=True, exist_ok=True)
    candidates.write_text(
        "species_id\tgene_id\tevidence_sources\n"
        "Arabidopsis_thaliana\tAT1G01010\thmm,blastp\n"
        "Arabidopsis_thaliana\tAT2G02020\thmm,blastp\n",
        encoding="utf-8",
    )
    aranet = project / "config/AraNet.txt"
    aranet.parent.mkdir(parents=True, exist_ok=True)
    aranet.write_text("AT1G01010\tAT2G02020\t5\nAT1G01010\tAT3G03030\t2\n", encoding="utf-8")
    config = project / "project.yaml"
    config.write_text(
        "project:\n"
        "  name: Whirly_2026\n"
        "  outdir: projects/Whirly_2026/results\n"
        "species:\n"
        "  include:\n"
        "    - Arabidopsis_thaliana\n"
        "modules:\n"
        "  ppi: true\n"
        "ppi:\n"
        "  aranet: projects/Whirly_2026/config/AraNet.txt\n"
        "  run_blast: false\n"
        "  min_weight: 4\n"
        "  r_bin: Rscript\n",
        encoding="utf-8",
    )
    return config


def test_run_ppi_module_builds_aranet_subnetwork_and_status(tmp_path):
    config = write_fake_project(tmp_path)

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config), "--skip-plot"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/Whirly_2026/results/11_ppi"
    for subdir in ["inputs", "tables", "plots", "report", "logs"]:
        assert (outdir / subdir).is_dir()
    assert (outdir / "inputs/Arabidopsis_thaliana.GF.pep.fasta").exists()
    edges = read_tsv(outdir / "tables/ppi_edges.tsv")
    assert edges == [{"source": "AT1G01010", "target": "AT2G02020", "weight": "5.0000", "species": "Arabidopsis_thaliana"}]
    nodes = read_tsv(outdir / "tables/ppi_nodes.tsv")
    assert {row["node"] for row in nodes} == {"AT1G01010", "AT2G02020"}
    evidence = read_tsv(outdir / "tables/ppi_transfer_evidence.tsv")
    assert any(row["metric"] == "aranet_edges_read" and row["value"] == "2" for row in evidence)
    status = read_tsv(outdir / "logs/ppi_status.tsv")
    assert status[0]["status"] == "table_ready_plot_skipped"
    summary = (outdir / "report/ppi_summary.md").read_text(encoding="utf-8")
    assert "11_ppi" in summary
    assert "AraNet" in summary
    assert "ggNetView" in summary


def test_ppi_reference_plot_script_uses_ggnetview_reference_style():
    script_text = PLOT_SCRIPT.read_text(encoding="utf-8")
    assert "ggNetView::build_graph_from_df" in script_text
    assert "module.method = \"Fast_greedy\"" in script_text
    assert "layout = \"diamond\"" in script_text
    assert "layout.module = \"adjacent\"" in script_text
    assert "fill.by = \"Type\"" in script_text
    assert "ppi_ggnetview.pdf" in script_text
