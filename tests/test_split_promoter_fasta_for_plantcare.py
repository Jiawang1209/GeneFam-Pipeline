from pathlib import Path

from bin.genefam.split_promoter_fasta_for_plantcare import read_tsv, split_promoter_fasta


def test_split_promoter_fasta_writes_parts_and_manifest(tmp_path):
    fasta = tmp_path / "promoters.fa"
    fasta.write_text(
        ">A|gene1|chr1:1-10(+)\nAAAA\n"
        ">A|gene2|chr1:11-20(+)\nCCCC\n"
        ">B|gene3|chr2:1-10(-)\nGGGG\n"
        ">B|gene4|chr2:11-20(-)\nTTTT\n"
        ">C|gene5|chr3:1-10(+)\nACGT\n",
        encoding="utf-8",
    )

    outputs = split_promoter_fasta(
        promoter_fasta=fasta,
        outdir=tmp_path / "plantcare_submission",
        records_per_file=2,
        prefix="GDSL_promoters",
    )

    manifest_rows = read_tsv(outputs["manifest"])
    assert [row["part_id"] for row in manifest_rows] == [
        "GDSL_promoters.part001",
        "GDSL_promoters.part002",
        "GDSL_promoters.part003",
    ]
    assert [row["record_count"] for row in manifest_rows] == ["2", "2", "1"]
    assert (tmp_path / "plantcare_submission/GDSL_promoters.part001.fa").read_text(encoding="utf-8") == (
        ">A|gene1|chr1:1-10(+)\nAAAA\n>A|gene2|chr1:11-20(+)\nCCCC\n"
    )
    assert (tmp_path / "plantcare_submission/GDSL_promoters.part003.fa").read_text(encoding="utf-8") == (
        ">C|gene5|chr3:1-10(+)\nACGT\n"
    )
    assert outputs["status"].read_text(encoding="utf-8") == (
        "status\ttotal_records\tpart_count\trecords_per_file\tnote\n"
        "available\t5\t3\t2\tPlantCARE submission FASTA parts prepared\n"
    )


def test_split_promoter_fasta_records_missing_input_for_empty_fasta(tmp_path):
    fasta = tmp_path / "promoters.fa"
    fasta.write_text("", encoding="utf-8")

    outputs = split_promoter_fasta(
        promoter_fasta=fasta,
        outdir=tmp_path / "plantcare_submission",
        records_per_file=10,
        prefix="GDSL_promoters",
    )

    assert read_tsv(outputs["manifest"]) == []
    assert outputs["status"].read_text(encoding="utf-8") == (
        "status\ttotal_records\tpart_count\trecords_per_file\tnote\n"
        "missing_input\t0\t0\t10\tNo promoter FASTA records available for PlantCARE submission\n"
    )
