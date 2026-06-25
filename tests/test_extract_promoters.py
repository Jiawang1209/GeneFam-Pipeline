import subprocess
import sys
from pathlib import Path

from bin.genefam.extract_promoters import extract_promoters, read_fasta


def test_extract_promoters_respects_strand_and_sequence_bounds(tmp_path):
    genome = tmp_path / "genome.fa"
    genome.write_text(">Chr1\nAACCGGTTAACCGGTTAACCGGTT\n", encoding="utf-8")
    gff3 = tmp_path / "genes.gff3"
    gff3.write_text(
        "\n".join(
            [
                "Chr1\ttest\tgene\t5\t9\t.\t+\t.\tID=gene_plus",
                "Chr1\ttest\tgene\t15\t18\t.\t-\t.\tID=gene_minus",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    family_rows = [
        {"species_id": "Demo", "gene_id": "gene_plus"},
        {"species_id": "Demo", "gene_id": "gene_minus"},
    ]
    manifest_rows = [{"species_id": "Demo", "gff3": str(gff3), "genome": str(genome)}]

    bed_rows, fasta_records = extract_promoters(
        family_rows,
        manifest_rows,
        upstream_bp=4,
        downstream_bp=2,
    )

    assert bed_rows == [
        {
            "species_id": "Demo",
            "gene_id": "gene_minus",
            "seqid": "Chr1",
            "strand": "-",
            "gene_start": "15",
            "gene_end": "18",
            "promoter_start": "17",
            "promoter_end": "22",
            "promoter_length": "6",
            "boundary_clipped": "false",
        },
        {
            "species_id": "Demo",
            "gene_id": "gene_plus",
            "seqid": "Chr1",
            "strand": "+",
            "gene_start": "5",
            "gene_end": "9",
            "promoter_start": "1",
            "promoter_end": "6",
            "promoter_length": "6",
            "boundary_clipped": "false",
        },
    ]
    assert fasta_records == [
        ("Demo|gene_minus|Chr1:17-22(-)", "CCGGTT"),
        ("Demo|gene_plus|Chr1:1-6(+)", "AACCGG"),
    ]


def test_extract_promoters_cli_writes_bed_and_fasta(tmp_path):
    genome = tmp_path / "genome.fa"
    genome.write_text(">Chr1\nAACCGGTTAACCGGTTAACCGGTT\n", encoding="utf-8")
    gff3 = tmp_path / "genes.gff3"
    gff3.write_text("Chr1\ttest\tgene\t5\t9\t.\t+\t.\tID=gene_plus\n", encoding="utf-8")
    family = tmp_path / "family.tsv"
    family.write_text("species_id\tgene_id\nDemo\tgene_plus\n", encoding="utf-8")
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text(f"species_id\tgff3\tgenome\nDemo\t{gff3}\t{genome}\n", encoding="utf-8")
    out_bed = tmp_path / "promoters.tsv"
    out_fasta = tmp_path / "promoters.fa"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/extract_promoters.py",
            "--family-candidates",
            str(family),
            "--species-manifest",
            str(manifest),
            "--upstream-bp",
            "4",
            "--downstream-bp",
            "2",
            "--out-bed",
            str(out_bed),
            "--out-fasta",
            str(out_fasta),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert out_bed.read_text(encoding="utf-8").splitlines()[0].startswith("species_id\tgene_id")
    assert read_fasta(out_fasta) == {"Demo|gene_plus|Chr1:1-6(+)": "AACCGG"}
