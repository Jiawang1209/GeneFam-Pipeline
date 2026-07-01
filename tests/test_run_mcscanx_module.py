import csv
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_mcscanx_module.py"
CIRCOS_SCRIPT = Path(__file__).resolve().parents[1] / "scripts/plot_mcscanx_circlize_reference.R"
KAKS_SCRIPT = Path(__file__).resolve().parents[1] / "scripts/plot_mcscanx_kaks_reference.R"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_fake_project(root: Path) -> Path:
    project = root / "projects/Whirly_2026"
    results = project / "results"
    clean = results / "01_preprocess/species_clean_bank/Arabidopsis_thaliana/clean"
    clean.mkdir(parents=True)
    clean.joinpath("Arabidopsis_thaliana.gff3").write_text(
        "Chr1\tsrc\tgene\t10\t90\t.\t+\t.\tID=AT1G01010;Name=AT1G01010\n"
        "Chr1\tsrc\tgene\t120\t210\t.\t-\t.\tID=AT2G02020;Name=AT2G02020\n",
        encoding="utf-8",
    )
    clean.joinpath("Arabidopsis_thaliana.protein.clean.fa").write_text(
        ">AT1G01010\nMAAA\n>AT2G02020\nMBBB\n",
        encoding="utf-8",
    )
    clean.joinpath("Arabidopsis_thaliana.chromosome.lengths.tsv").write_text(
        "Chr\tStart\tEnd\nChr1\t1\t1000\n",
        encoding="utf-8",
    )
    manifest = results / "01_preprocess/species_clean_bank_manifest.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "species_id\tprotein\tcds\tgenome\tgff3\tchromosome_lengths\tstatus\n"
        f"Arabidopsis_thaliana\t{clean / 'Arabidopsis_thaliana.protein.clean.fa'}\t\t\t{clean / 'Arabidopsis_thaliana.gff3'}\t{clean / 'Arabidopsis_thaliana.chromosome.lengths.tsv'}\tpass\n",
        encoding="utf-8",
    )
    candidates = results / "04_identification/tables/family_candidates.tsv"
    candidates.parent.mkdir(parents=True, exist_ok=True)
    candidates.write_text(
        "species_id\tgene_id\tevidence_sources\n"
        "Arabidopsis_thaliana\tAT1G01010\thmm,blastp\n",
        encoding="utf-8",
    )
    config = project / "project.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        "project:\n"
        "  name: Whirly_2026\n"
        "  outdir: projects/Whirly_2026/results\n"
        "species:\n"
        "  include:\n"
        "    - Arabidopsis_thaliana\n"
        "modules:\n"
        "  mcscanx: true\n"
        "mcscanx:\n"
        "  execute: false\n"
        "  search_tool: diamond\n"
        "  window_size: 500000\n"
        "  r_bin: Rscript\n",
        encoding="utf-8",
    )
    return config


def test_run_mcscanx_module_prepares_self_inputs_and_reference_tables(tmp_path):
    config = write_fake_project(tmp_path)

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/Whirly_2026/results/09_mcscanx"
    for subdir in ["inputs", "tables", "plots", "report", "logs"]:
        assert (outdir / subdir).is_dir()

    assert (outdir / "inputs/family_beds/Arabidopsis_thaliana.GF.bed").exists()
    assert (outdir / "inputs/mcscanx_run/Arabidopsis_thaliana.gff").exists()
    assert (outdir / "logs/mcscanx_self_commands.sh").exists()
    assert "MCScanX Arabidopsis_thaliana" in (outdir / "logs/mcscanx_self_commands.sh").read_text(encoding="utf-8")
    assert (outdir / "tables/mcscanx_self_status.tsv").exists()
    assert (outdir / "tables/mcscanx_run_status.tsv").exists()
    assert (outdir / "logs/mcscanx_execution_status.tsv").exists()
    execution = read_tsv(outdir / "logs/mcscanx_execution_status.tsv")
    assert execution[0]["status"] in {"ready_not_executed", "missing_dependency", "missing_input"}
    chromosomes = read_tsv(outdir / "tables/circlize_chromosomes.tsv")
    assert chromosomes == [{"species_id": "Arabidopsis_thaliana", "Chr": "Chr1", "Start": "1", "End": "1000"}]
    density = read_tsv(outdir / "tables/circlize_gene_density.tsv")
    assert density[0]["species_id"] == "Arabidopsis_thaliana"
    assert density[0]["Chr"] == "Chr1"
    gene_types = read_tsv(outdir / "tables/circlize_gene_types.tsv")
    assert gene_types[0]["gene_id"] == "AT1G01010"
    summary = (outdir / "report/mcscanx_summary.md").read_text(encoding="utf-8")
    assert "09_mcscanx" in summary
    assert "MCScanX self" in summary
    assert "circlize" in summary


def test_mcscanx_reference_plot_scripts_reuse_reference_style():
    circos_text = CIRCOS_SCRIPT.read_text(encoding="utf-8")
    assert "circlize::circos.genomicInitialize" in circos_text
    assert "circlize::circos.genomicLabels" in circos_text
    assert "circlize::circos.genomicLink" in circos_text
    assert "ComplexHeatmap::Legend" in circos_text
    assert "Gene Duplicate" in circos_text
    kaks_text = KAKS_SCRIPT.read_text(encoding="utf-8")
    assert "ggbeeswarm::geom_quasirandom" in kaks_text
    assert "ggplot2::facet_grid(`Duplicate Type`~Type, scales = \"free\")" in kaks_text
    assert "9.mcscanx_Kaks.pdf" in kaks_text
