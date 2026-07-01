import csv
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "bin/genefam/run_genefamily_info_module.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_project_inputs(root: Path) -> Path:
    clean_bank = root / "projects/GDSL_2026/results/01_preprocess/species_clean_bank"
    ath = clean_bank / "Arabidopsis_thaliana/clean"
    bra = clean_bank / "Brassica_rapa/clean"
    ath.mkdir(parents=True)
    bra.mkdir(parents=True)
    ath.joinpath("Arabidopsis_thaliana.gff3").write_text(
        "Chr1\tsrc\tgene\t10\t90\t.\t+\t.\tID=AT1G00010;Name=AT1G00010\n"
        "Chr1\tsrc\tgene\t120\t210\t.\t-\t.\tID=AT1G00020;Name=AT1G00020\n",
        encoding="utf-8",
    )
    bra.joinpath("Brassica_rapa.gff3").write_text(
        "A01\tsrc\tgene\t50\t150\t.\t+\t.\tID=BraA01g000010;Name=BraA01g000010\n",
        encoding="utf-8",
    )
    ath.joinpath("Arabidopsis_thaliana.protein.clean.fa").write_text(">AT1G00010\nMAAA\n>AT1G00020\nMBBB\n", encoding="utf-8")
    bra.joinpath("Brassica_rapa.protein.clean.fa").write_text(">BraA01g000010\nMCCC\n", encoding="utf-8")

    identify = root / "projects/GDSL_2026/results/04_identification/fasta/identify.ID.fa"
    identify.parent.mkdir(parents=True)
    identify.write_text(
        ">Arabidopsis_thaliana|AT1G00010\nMAAA\n"
        ">Brassica_rapa|BraA01g000010\nMCCC\n",
        encoding="utf-8",
    )
    config = root / "projects/GDSL_2026/project.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        "project:\n"
        "  outdir: projects/GDSL_2026/results\n"
        "database:\n"
        f"  species_clean_bank: {clean_bank}\n"
        "genefamily_info:\n"
        "  plot: false\n",
        encoding="utf-8",
    )
    return config


def test_run_genefamily_info_module_builds_physical_and_protein_tables(tmp_path):
    config = write_project_inputs(tmp_path)
    legacy_bed = tmp_path / "projects/GDSL_2026/results/05_genefamily_info/tables/species_10.bed"
    legacy_bed.parent.mkdir(parents=True, exist_ok=True)
    legacy_bed.write_text("stale legacy bed\n", encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--config", str(config), "--skip-plot"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    outdir = tmp_path / "projects/GDSL_2026/results/05_genefamily_info"
    info = read_tsv(outdir / "tables/Gene_Information.tsv")
    assert [(row["Species"], row["ID"], row["Chr"], row["Start"], row["End"], row["Strand"]) for row in info] == [
        ("Arabidopsis_thaliana", "AT1G00010", "Chr1", "10", "90", "+"),
        ("Brassica_rapa", "BraA01g000010", "A01", "50", "150", "+"),
    ]
    assert info[0]["Length"] == "4"
    assert info[0]["MW_kDa"]
    assert info[0]["pI"]
    assert info[0]["hydrophobicity"]

    stats = read_tsv(outdir / "tables/Gene_Information_stat.tsv")
    by_species = {row["Species"]: row for row in stats}
    assert by_species["Arabidopsis_thaliana"]["count"] == "1"
    assert by_species["Brassica_rapa"]["count"] == "1"

    copy_number = read_tsv(outdir / "tables/gene_family_copy_number.tsv")
    assert {row["species_id"]: row["member_count"] for row in copy_number} == {
        "Arabidopsis_thaliana": "1",
        "Brassica_rapa": "1",
    }
    assert (outdir / "tables/all_species_gene.bed").exists()
    assert not (outdir / "tables/species_10.bed").exists()
    assert (outdir / "tables/Gene_Information.xlsx").exists()
    assert (outdir / "tables/Gene_Information_stat.xlsx").exists()
