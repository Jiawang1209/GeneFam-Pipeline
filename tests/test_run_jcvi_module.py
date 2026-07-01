import csv
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_jcvi_module.py"
PLOT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts/plot_jcvi_kaks.R"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_fake_project(root: Path) -> Path:
    project = root / "projects/Whirly_2026"
    results = project / "results"
    clean_bank = results / "01_preprocess/species_clean_bank"
    ath = clean_bank / "Arabidopsis_thaliana/clean"
    oryza = clean_bank / "Oryza_sativa/clean"
    ath.mkdir(parents=True)
    oryza.mkdir(parents=True)
    ath.joinpath("Arabidopsis_thaliana.gff3").write_text(
        "Chr1\tsrc\tgene\t10\t90\t.\t+\t.\tID=AT1G01010;Name=AT1G01010\n"
        "Chr1\tsrc\tmRNA\t10\t90\t.\t+\t.\tID=AT1G01010.1;Parent=AT1G01010\n"
        "Chr2\tsrc\tgene\t120\t210\t.\t-\t.\tID=AT2G02020;Name=AT2G02020\n",
        encoding="utf-8",
    )
    oryza.joinpath("Oryza_sativa.gff3").write_text(
        "Chr01\tsrc\tgene\t50\t150\t.\t+\t.\tID=LOC_Os01g01010;Name=LOC_Os01g01010\n"
        "Chr01\tsrc\tmRNA\t50\t150\t.\t+\t.\tID=LOC_Os01g01010.1;Parent=LOC_Os01g01010\n",
        encoding="utf-8",
    )
    ath.joinpath("Arabidopsis_thaliana.protein.clean.fa").write_text(
        ">AT1G01010\nMAAA\n>AT2G02020\nMBBB\n",
        encoding="utf-8",
    )
    oryza.joinpath("Oryza_sativa.protein.clean.fa").write_text(
        ">LOC_Os01g01010\nMCCC\n",
        encoding="utf-8",
    )
    manifest = results / "01_preprocess/species_clean_bank_manifest.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "species_id\tpep\tcds\tgff3\tgenome\tstatus\n"
        f"Arabidopsis_thaliana\t{ath / 'Arabidopsis_thaliana.protein.clean.fa'}\t\t{ath / 'Arabidopsis_thaliana.gff3'}\t\tok\n"
        f"Oryza_sativa\t{oryza / 'Oryza_sativa.protein.clean.fa'}\t\t{oryza / 'Oryza_sativa.gff3'}\t\tok\n",
        encoding="utf-8",
    )
    candidates = results / "04_identification/tables/family_candidates.tsv"
    candidates.parent.mkdir(parents=True, exist_ok=True)
    candidates.write_text(
        "species_id\tgene_id\tevidence_sources\n"
        "Arabidopsis_thaliana\tAT1G01010\thmm,blastp\n"
        "Oryza_sativa\tLOC_Os01g01010\thmm,blastp\n",
        encoding="utf-8",
    )
    config = project / "project.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        "project:\n"
        "  name: Whirly_2026\n"
        "  outdir: projects/Whirly_2026/results\n"
        "database:\n"
        "  species_clean_bank: projects/Whirly_2026/results/01_preprocess/species_clean_bank\n"
        "species:\n"
        "  include:\n"
        "    - Arabidopsis_thaliana\n"
        "    - Oryza_sativa\n"
        "modules:\n"
        "  jcvi: true\n"
        "jcvi:\n"
        "  python_bin: python\n"
        "  run: false\n"
        "  minspan: 30\n"
        "  figsize: 14x12\n"
        "  chrstyle: roundrect\n",
        encoding="utf-8",
    )
    return config


def test_run_jcvi_module_prepares_reference_style_inputs_and_report(tmp_path):
    config = write_fake_project(tmp_path)

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/Whirly_2026/results/08_jcvi"
    for subdir in ["inputs", "tables", "plots", "report", "logs"]:
        assert (outdir / subdir).is_dir()

    assert (outdir / "inputs/beds/Arabidopsis_thaliana.bed").exists()
    assert (outdir / "inputs/beds/Oryza_sativa.bed").exists()
    assert (outdir / "inputs/peptides/Arabidopsis_thaliana.pep").exists()
    assert (outdir / "inputs/peptides/Oryza_sativa.pep").exists()
    assert (outdir / "inputs/seqids").exists()
    assert (outdir / "inputs/layout").exists()
    assert (outdir / "logs/jcvi_commands.sh").exists()
    assert "jcvi.compara.catalog ortholog" in (outdir / "logs/jcvi_commands.sh").read_text(encoding="utf-8")
    assert "jcvi.graphics.karyotype seqids layout" in (outdir / "logs/jcvi_commands.sh").read_text(encoding="utf-8")

    pair_manifest = read_tsv(outdir / "tables/jcvi_pair_manifest.tsv")
    assert pair_manifest == [
        {
            "pair_id": "Arabidopsis_thaliana.Oryza_sativa",
            "query_species": "Arabidopsis_thaliana",
            "subject_species": "Oryza_sativa",
            "query_bed": "inputs/beds/Arabidopsis_thaliana.bed",
            "subject_bed": "inputs/beds/Oryza_sativa.bed",
            "query_pep": "inputs/peptides/Arabidopsis_thaliana.pep",
            "subject_pep": "inputs/peptides/Oryza_sativa.pep",
        }
    ]
    input_status = read_tsv(outdir / "tables/jcvi_input_status.tsv")
    assert {row["check"] for row in input_status} >= {
        "Arabidopsis_thaliana.bed_genes",
        "Arabidopsis_thaliana.pep_genes",
        "Oryza_sativa.bed_genes",
        "Oryza_sativa.pep_genes",
    }
    command_status = read_tsv(outdir / "logs/jcvi_command_status.tsv")
    assert command_status[0]["status"] in {"planned", "not_run", "failed", "available"}
    run_status = read_tsv(outdir / "logs/jcvi_run_status.tsv")
    assert run_status[0]["status"] in {"planned", "missing_dependency", "failed", "available", "partial"}
    summary = (outdir / "report/jcvi_summary.md").read_text(encoding="utf-8")
    assert "08_jcvi" in summary
    assert "Arabidopsis_thaliana.Oryza_sativa" in summary
    assert "python -m jcvi.compara.catalog ortholog" in summary
    assert "Ka/Ks" in summary


def test_plot_jcvi_kaks_r_reuses_reference_style():
    script_text = PLOT_SCRIPT.read_text(encoding="utf-8")
    assert "ggbeeswarm::geom_quasirandom" in script_text
    assert "ggplot2::geom_boxplot" in script_text
    assert "ggplot2::geom_hline(yintercept = 1" in script_text
    assert "ggplot2::facet_wrap(~Type, scales = \"free\")" in script_text
    assert "Ka_Ks" in script_text
    assert "8.jcvi_Kaks.pdf" in script_text
