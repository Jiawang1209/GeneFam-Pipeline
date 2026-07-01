import csv
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_promoter_module.py"
PLOT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts/plot_promoter_cis_reference.R"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_fake_project(root: Path) -> Path:
    project = root / "projects/Whirly_2026"
    results = project / "results"
    clean = results / "01_preprocess/species_clean_bank/Arabidopsis_thaliana/clean"
    clean.mkdir(parents=True)
    clean.joinpath("Arabidopsis_thaliana.gff3").write_text(
        "Chr1\tsrc\tgene\t100\t180\t.\t+\t.\tID=AT1G01010;Name=AT1G01010\n"
        "Chr1\tsrc\tgene\t300\t380\t.\t-\t.\tID=AT2G02020;Name=AT2G02020\n",
        encoding="utf-8",
    )
    clean.joinpath("Arabidopsis_thaliana.genome.fa").write_text(
        ">Chr1\n" + "ACGT" * 200 + "\n",
        encoding="utf-8",
    )
    manifest = results / "01_preprocess/species_clean_bank_manifest.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "species_id\tprotein\tcds\tgenome\tgff3\tstatus\n"
        f"Arabidopsis_thaliana\t\t\t{clean / 'Arabidopsis_thaliana.genome.fa'}\t{clean / 'Arabidopsis_thaliana.gff3'}\tpass\n",
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
        "  promoter: true\n"
        "promoter:\n"
        "  upstream_bp: 50\n"
        "  split_records: 1\n"
        "  r_bin: Rscript\n",
        encoding="utf-8",
    )
    return config


def test_run_promoter_module_extracts_promoters_and_records_missing_cis(tmp_path):
    config = write_fake_project(tmp_path)

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/Whirly_2026/results/10_promoter"
    for subdir in ["inputs", "tables", "sequences", "plantcare_submission", "plots", "report", "logs"]:
        assert (outdir / subdir).is_dir()
    promoters = read_tsv(outdir / "tables/promoters.bed")
    assert promoters[0]["species_id"] == "Arabidopsis_thaliana"
    assert promoters[0]["gene_id"] == "AT1G01010"
    assert promoters[0]["start"] == "49"
    assert promoters[0]["end"] == "99"
    assert (outdir / "sequences/promoters.fa").exists()
    fasta_text = (outdir / "sequences/promoters.fa").read_text(encoding="utf-8")
    assert ">Arabidopsis_thaliana|AT1G01010" in fasta_text
    assert ">Arabidopsis_thaliana|AT2G02020" in fasta_text
    assert (outdir / "plantcare_submission/Whirly_promoters.part001.fa").exists()
    status = read_tsv(outdir / "logs/promoter_cis_status.tsv")
    assert status[0]["status"] == "missing_input"
    summary = (outdir / "report/promoter_summary.md").read_text(encoding="utf-8")
    assert "10_promoter" in summary
    assert "PlantCARE" in summary
    assert "missing_input" in summary


def test_promoter_reference_plot_script_reuses_reference_heatmap_style():
    script_text = PLOT_SCRIPT.read_text(encoding="utf-8")
    assert "guide_axis_nested" in script_text
    assert "geom_tile(fill = \"#ffffff\"" in script_text
    assert "geom_point" in script_text
    assert "geom_text" in script_text
    assert "aplot::insert_top" in script_text
    assert "promoter1.pdf" in script_text
    assert "species_promoter2.pdf" in script_text
