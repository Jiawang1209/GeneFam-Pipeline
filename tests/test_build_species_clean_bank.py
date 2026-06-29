import csv
import subprocess
import sys
from pathlib import Path


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_demo_species(root: Path, species: str = "Demo_species") -> Path:
    species_dir = root / species
    species_dir.mkdir(parents=True)
    (species_dir / f"{species}.pep.fa").write_text(
        ">GeneA.1|PACid:1\nMAA*\n"
        ">GeneA.2|PACid:2\nMAAAA*\n"
        ">GeneB.1|PACid:3\nMCC*\n",
        encoding="utf-8",
    )
    (species_dir / f"{species}.cds.fa").write_text(
        ">GeneA.1|PACid:1\nATGGCTGCTTAA\n"
        ">GeneA.2|PACid:2\nATGGCTGCTGCTGCTTAA\n"
        ">GeneB.1|PACid:3\nATGTGTTGTTAA\n",
        encoding="utf-8",
    )
    (species_dir / f"{species}.genome.fa").write_text(
        ">chr1 chromosome 1\nATGCATGC\n"
        ">scaffold_1 unplaced scaffold\nATGC\n"
        ">ChrC chloroplast\nATGCAT\n",
        encoding="utf-8",
    )
    (species_dir / f"{species}.gff3").write_text(
        "chr1\tDemo\tgene\t1\t900\t.\t+\t.\tID=GeneA;Name=GeneA\n"
        "chr1\tDemo\tmRNA\t1\t900\t.\t+\t.\tID=PAC:1;Name=GeneA.1;Parent=GeneA\n"
        "chr1\tDemo\tmRNA\t1\t900\t.\t+\t.\tID=PAC:2;Name=GeneA.2;Parent=GeneA\n"
        "chr1\tDemo\tgene\t1000\t1800\t.\t+\t.\tID=GeneB;Name=GeneB\n"
        "chr1\tDemo\tmRNA\t1000\t1800\t.\t+\t.\tID=PAC:3;Name=GeneB.1;Parent=GeneB\n",
        encoding="utf-8",
    )
    return species_dir


def test_build_species_clean_bank_writes_raw_clean_audit_and_global_tables(tmp_path):
    raw_root = tmp_path / "species_bank"
    write_demo_species(raw_root)
    out_root = tmp_path / "species_clean_bank"
    manifest = tmp_path / "species_clean_bank_manifest.tsv"
    qc = tmp_path / "species_clean_bank_qc.tsv"
    qc_excel = tmp_path / "species_clean_bank_qc.xlsx"
    failed = tmp_path / "species_clean_bank_failed.tsv"
    summary = tmp_path / "species_clean_bank_summary.md"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_species_clean_bank.py",
            "--raw-root",
            str(raw_root),
            "--out-root",
            str(out_root),
            "--manifest",
            str(manifest),
            "--qc",
            str(qc),
            "--qc-excel",
            str(qc_excel),
            "--failed",
            str(failed),
            "--summary",
            str(summary),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    species_root = out_root / "Demo_species"
    assert (species_root / "raw/Demo_species.pep.fa").exists()
    assert (species_root / "raw/Demo_species.cds.fa").exists()
    assert (species_root / "raw/Demo_species.genome.fa").exists()
    assert (species_root / "raw/Demo_species.gff3").exists()
    protein_clean = species_root / "clean/Demo_species.protein.clean.fa"
    cds_clean = species_root / "clean/Demo_species.cds.clean.fa"
    assert protein_clean.read_text(encoding="utf-8") == ">GeneA\nMAAAA\n>GeneB\nMCC\n"
    assert cds_clean.read_text(encoding="utf-8") == ">GeneA\nATGGCTGCTGCTGCTTAA\n>GeneB\nATGTGTTGTTAA\n"
    assert (species_root / "clean/Demo_species.genome.fa").exists()
    assert (species_root / "clean/Demo_species.gff3").exists()
    assert (species_root / "clean/Demo_species.chromosome.lengths.tsv").exists()
    assert (species_root / "audit/Demo_species.gene_id_map.tsv").exists()
    assert (species_root / "audit/Demo_species.genome.lengths.tsv").exists()
    assert (species_root / "audit/Demo_species.representative_transcripts.tsv").exists()
    assert (species_root / "audit/Demo_species.preprocess_qc.tsv").exists()
    assert (species_root / "audit/Demo_species.preprocess_warnings.tsv").exists()
    chromosome_rows = read_tsv(species_root / "clean/Demo_species.chromosome.lengths.tsv")
    assert chromosome_rows == [{"Chr": "chr1", "Start": "1", "End": "8"}]
    genome_rows = read_tsv(species_root / "audit/Demo_species.genome.lengths.tsv")
    assert [row["SeqType"] for row in genome_rows] == ["chromosome", "unassembled", "organelle"]

    manifest_rows = read_tsv(manifest)
    assert manifest_rows[0]["species_id"] == "Demo_species"
    assert manifest_rows[0]["status"] == "pass"
    assert manifest_rows[0]["protein"].endswith("clean/Demo_species.protein.clean.fa")
    assert manifest_rows[0]["cds"].endswith("clean/Demo_species.cds.clean.fa")
    assert manifest_rows[0]["genome"].endswith("clean/Demo_species.genome.fa")
    assert manifest_rows[0]["gff3"].endswith("clean/Demo_species.gff3")
    assert manifest_rows[0]["genome_lengths"].endswith("audit/Demo_species.genome.lengths.tsv")
    assert manifest_rows[0]["chromosome_lengths"].endswith("clean/Demo_species.chromosome.lengths.tsv")

    qc_rows = read_tsv(qc)
    assert qc_rows[0]["raw_pep_count"] == "3"
    assert qc_rows[0]["clean_pep_count"] == "2"
    assert qc_rows[0]["raw_cds_count"] == "3"
    assert qc_rows[0]["clean_cds_count"] == "2"
    assert qc_rows[0]["genome_seq_count"] == "3"
    assert qc_rows[0]["chromosome_seq_count"] == "1"
    assert qc_rows[0]["unassembled_seq_count"] == "1"
    assert qc_rows[0]["organelle_seq_count"] == "1"
    assert qc_rows[0]["total_genome_bp"] == "18"
    assert qc_rows[0]["chromosome_bp"] == "8"
    assert qc_rows[0]["assembly_level"] == "chromosome"
    assert qc_rows[0]["chromosome_analysis_ready"] == "TRUE"
    assert qc_rows[0]["terminal_stop_removed_count"] == "3"
    assert qc_rows[0]["cds_match_rate"] == "1.0000"
    assert qc_rows[0]["status"] == "pass"
    assert qc_excel.exists()
    from openpyxl import load_workbook

    workbook = load_workbook(qc_excel, read_only=True)
    assert workbook.sheetnames == ["species_qc", "assembly_summary"]
    sheet = workbook["species_qc"]
    assert [cell.value for cell in next(sheet.iter_rows(min_row=1, max_row=1))] == [
        "species_id",
        "raw_pep_count",
        "raw_cds_count",
        "clean_pep_count",
        "clean_cds_count",
        "genome_seq_count",
        "chromosome_seq_count",
        "unassembled_seq_count",
        "organelle_seq_count",
        "total_genome_bp",
        "chromosome_bp",
        "assembly_level",
        "chromosome_analysis_ready",
        "gff3_transcript_map_count",
        "gff3_mapping_rate",
        "fallback_mapping_rate",
        "cds_match_rate",
        "terminal_stop_removed_count",
        "warning_count",
        "status",
        "note",
    ]
    assert read_tsv(failed) == []
    assert "Species Clean Bank Summary" in summary.read_text(encoding="utf-8")
