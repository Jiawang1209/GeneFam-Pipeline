import csv
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_full_bioinformatics_report.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_fake_project(root: Path) -> Path:
    project = root / "projects/Whirly_2026"
    results = project / "results"
    for module in ["08_jcvi", "09_mcscanx", "10_promoter", "11_ppi"]:
        (results / module / "report").mkdir(parents=True, exist_ok=True)
        (results / module / "plots").mkdir(parents=True, exist_ok=True)
        (results / module / "report" / f"{module}_summary.md").write_text(f"# {module} Summary\n\nResult text for {module}.\n", encoding="utf-8")
    (results / "11_ppi/plots/ppi_ggnetview.pdf").write_bytes(b"%PDF fake")
    (results / "11_ppi/plots/ppi_ggnetview.png").write_bytes(b"fake png")
    (results / "11_ppi/logs").mkdir(parents=True, exist_ok=True)
    (results / "11_ppi/logs/ppi_status.tsv").write_text("status\tedge_count\tnode_count\tplot_status\tnote\ntable_ready_plot_ready\t2\t3\tready\tok\n", encoding="utf-8")
    config = project / "project.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        "project:\n"
        "  name: Whirly_2026\n"
        "  outdir: projects/Whirly_2026/results\n"
        "report:\n"
        "  r_bin: Rscript\n",
        encoding="utf-8",
    )
    return config


def test_run_full_report_module_writes_methods_results_and_figure_interpretations(tmp_path):
    config = write_fake_project(tmp_path)

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/Whirly_2026/results/12_full_bioinformatics_report"
    report = outdir / "report/full_bioinformatics_report.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "# Whirly_2026 Gene Family Bioinformatics Report" in text
    assert "## Methods" in text
    assert "Software Versions" in text
    assert "## Results" in text
    assert "## Figure-by-Figure Interpretation" in text
    assert "ppi_ggnetview.pdf" in text
    assert "## Reproducibility Commands" in text
    figure_index = read_tsv(outdir / "tables/figure_interpretation_index.tsv")
    assert figure_index[0]["module"] == "11_ppi"
    assert figure_index[0]["interpretation"]
    versions = read_tsv(outdir / "tables/software_versions.tsv")
    assert {row["software"] for row in versions} >= {"python", "R", "JCVI", "MCScanX", "ggNetView"}
    module_status = read_tsv(outdir / "tables/module_status_overview.tsv")
    assert any(row["module"] == "11_ppi" and row["status"] == "table_ready_plot_ready" for row in module_status)
