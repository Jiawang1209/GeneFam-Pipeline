import csv
import subprocess
import sys
from pathlib import Path

from bin.genefam.build_species_clean_bank import classify_genome_sequence
from bin.genefam.preprocess_species import (
    clean_sequence_records,
    infer_gene_id,
    parse_gff3_transcript_gene_map,
    read_fasta_records,
)


def test_infer_gene_id_prefers_gff3_mapping_and_falls_back_to_common_patterns():
    mapping = {"AT1G01010.2": "AT1G01010"}

    assert infer_gene_id("AT1G01010.2|PACid:123", mapping) == ("AT1G01010.2", "AT1G01010", "gff3")
    assert infer_gene_id("BraA01g000010.3C", {}) == ("BraA01g000010.3C", "BraA01g000010", "auto_suffix")
    assert infer_gene_id("gene001.t1", {}) == ("gene001.t1", "gene001", "auto_suffix")
    assert infer_gene_id("gene001-RA", {}) == ("gene001-RA", "gene001", "auto_suffix")
    assert infer_gene_id("Zm00001d001234_T001", {}) == ("Zm00001d001234_T001", "Zm00001d001234", "auto_suffix")


def test_parse_gff3_transcript_gene_map_reads_mrna_parent_relationships(tmp_path):
    gff3 = tmp_path / "demo.gff3"
    gff3.write_text(
        "chr1\tTAIR\tgene\t1\t900\t.\t+\t.\tID=AT1G01010\n"
        "chr1\tTAIR\tmRNA\t1\t900\t.\t+\t.\tID=AT1G01010.1;Parent=AT1G01010\n"
        "chr1\tTAIR\tCDS\t1\t300\t.\t+\t0\tID=cds1;Parent=AT1G01010.1\n",
        encoding="utf-8",
    )

    assert parse_gff3_transcript_gene_map(gff3) == {"AT1G01010.1": "AT1G01010"}


def test_parse_gff3_transcript_gene_map_uses_name_as_transcript_alias(tmp_path):
    gff3 = tmp_path / "demo.gff3"
    gff3.write_text(
        "chr1\tPhytozome\tgene\t1\t900\t.\t+\t.\tID=AT1G01010;Name=AT1G01010\n"
        "chr1\tPhytozome\tmRNA\t1\t900\t.\t+\t.\tID=PAC:19656964;Name=AT1G01010.1;Parent=AT1G01010\n",
        encoding="utf-8",
    )

    mapping = parse_gff3_transcript_gene_map(gff3)

    assert mapping["PAC:19656964"] == "AT1G01010"
    assert mapping["AT1G01010.1"] == "AT1G01010"


def test_classify_genome_sequence_accepts_species_prefix_chromosome_ids():
    assert classify_genome_sequence("Bd1", "Bd1") == "chromosome"
    assert classify_genome_sequence("Tu7", "Tu7") == "chromosome"
    assert (
        classify_genome_sequence("Bd1_centromere_containing_Bradi1g41430", "Bd1_centromere_containing_Bradi1g41430")
        == "unclassified"
    )
    assert classify_genome_sequence("TuUngrouped_contig_1", "TuUngrouped_contig_1") == "unassembled"


def test_clean_sequence_records_selects_longest_pep_and_removes_terminal_stop(tmp_path):
    pep = tmp_path / "demo.pep.fa"
    pep.write_text(
        ">AT1G01010.1|PACid:1\nMAA*\n"
        ">AT1G01010.2|PACid:2\nMAAAA*\n"
        ">gene001.t1\nMCC*\n",
        encoding="utf-8",
    )
    cds = tmp_path / "demo.cds.fa"
    cds.write_text(
        ">AT1G01010.1|PACid:1\nATGGCTGCTTAA\n"
        ">AT1G01010.2|PACid:2\nATGGCTGCTGCTGCTTAA\n"
        ">gene001.t1\nATGTGTTGTTAA\n",
        encoding="utf-8",
    )
    mapping = {"AT1G01010.1": "AT1G01010", "AT1G01010.2": "AT1G01010"}

    cleaned_pep, cleaned_cds, transcript_rows, representative_rows, warnings = clean_sequence_records(
        species_id="Demo_species",
        pep_records=read_fasta_records(pep),
        cds_records=read_fasta_records(cds),
        transcript_gene_map=mapping,
    )

    assert cleaned_pep == [("AT1G01010", "MAAAA"), ("gene001", "MCC")]
    assert cleaned_cds == [("AT1G01010", "ATGGCTGCTGCTGCTTAA"), ("gene001", "ATGTGTTGTTAA")]
    assert [row["selected_transcript_id"] for row in representative_rows] == ["AT1G01010.2", "gene001.t1"]
    assert {row["source"] for row in transcript_rows} == {"gff3", "auto_suffix"}
    assert warnings == []


def test_clean_sequence_records_matches_phytozome_pep_and_cds_header_attributes(tmp_path):
    pep = tmp_path / "bra.pep.fa"
    pep.write_text(
        ">BrO_302V.01G000100.1.p pacid=52833220 transcript=BrO_302V.01G000100.1 locus=BrO_302V.01G000100\nMAA*\n",
        encoding="utf-8",
    )
    cds = tmp_path / "bra.cds.fa"
    cds.write_text(
        ">BrO_302V.01G000100.1 pacid=52833220 polypeptide=BrO_302V.01G000100.1.p locus=BrO_302V.01G000100\nATGGCTTAA\n",
        encoding="utf-8",
    )

    cleaned_pep, cleaned_cds, transcript_rows, representative_rows, warnings = clean_sequence_records(
        species_id="Brassica_rapa",
        pep_records=read_fasta_records(pep),
        cds_records=read_fasta_records(cds),
        transcript_gene_map={},
    )

    assert cleaned_pep == [("BrO_302V.01G000100", "MAA")]
    assert cleaned_cds == [("BrO_302V.01G000100", "ATGGCTTAA")]
    assert transcript_rows[0]["clean_transcript_id"] == "BrO_302V.01G000100.1"
    assert representative_rows[0]["selected_transcript_id"] == "BrO_302V.01G000100.1"
    assert warnings == []


def test_clean_sequence_records_matches_ensembl_colon_transcript_attributes(tmp_path):
    pep = tmp_path / "wheat.pep.fa"
    pep.write_text(
        ">TraesCS1A02G000100.1.cds1 pep chromosome:IWGSC:1A:40098:70338:-1 gene:TraesCS1A02G000100 transcript:TraesCS1A02G000100.1 gene_biotype:protein_coding\nMAAA\n",
        encoding="utf-8",
    )
    cds = tmp_path / "wheat.cds.fa"
    cds.write_text(
        ">TraesCS1A02G000100.1 cds chromosome:IWGSC:1A:40098:70338:-1 gene:TraesCS1A02G000100 gene_biotype:protein_coding\nATGGCTGCTGCT\n",
        encoding="utf-8",
    )
    gff3 = tmp_path / "wheat.gff3"
    gff3.write_text(
        "1A\tIWGSC\tgene\t40098\t70338\t.\t-\t.\tID=gene:TraesCS1A02G000100;gene_id=TraesCS1A02G000100\n"
        "1A\tIWGSC\tmRNA\t40098\t70338\t.\t-\t.\tID=transcript:TraesCS1A02G000100.1;Parent=gene:TraesCS1A02G000100;transcript_id=TraesCS1A02G000100.1\n",
        encoding="utf-8",
    )

    mapping = parse_gff3_transcript_gene_map(gff3)
    cleaned_pep, cleaned_cds, transcript_rows, representative_rows, warnings = clean_sequence_records(
        species_id="Triticum_aestivum",
        pep_records=read_fasta_records(pep),
        cds_records=read_fasta_records(cds),
        transcript_gene_map=mapping,
    )

    assert mapping["TraesCS1A02G000100.1"] == "TraesCS1A02G000100"
    assert cleaned_pep == [("TraesCS1A02G000100", "MAAA")]
    assert cleaned_cds == [("TraesCS1A02G000100", "ATGGCTGCTGCT")]
    assert transcript_rows[0]["clean_transcript_id"] == "TraesCS1A02G000100.1"
    assert representative_rows[0]["selected_transcript_id"] == "TraesCS1A02G000100.1"
    assert warnings == []


def test_preprocess_species_cli_writes_clean_manifest_and_audit_tables(tmp_path):
    species_dir = tmp_path / "species_bank" / "Demo_species"
    species_dir.mkdir(parents=True)
    pep = species_dir / "Demo_species.pep.fa"
    pep.write_text(">AT1G01010.1|PACid:1\nMAA*\n>AT1G01010.2|PACid:2\nMAAAA*\n", encoding="utf-8")
    cds = species_dir / "Demo_species.cds.fa"
    cds.write_text(
        ">AT1G01010.1|PACid:1\nATGGCTGCTTAA\n>AT1G01010.2|PACid:2\nATGGCTGCTGCTGCTTAA\n",
        encoding="utf-8",
    )
    gff3 = species_dir / "Demo_species.gff3"
    gff3.write_text(
        "chr1\tTAIR\tgene\t1\t900\t.\t+\t.\tID=AT1G01010\n"
        "chr1\tTAIR\tmRNA\t1\t900\t.\t+\t.\tID=AT1G01010.1;Parent=AT1G01010\n"
        "chr1\tTAIR\tmRNA\t1\t900\t.\t+\t.\tID=AT1G01010.2;Parent=AT1G01010\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "species_manifest.tsv"
    manifest.write_text(
        "species_id\tpep\tgff3\tcds\tgenome\n"
        f"Demo_species\t{pep}\t{gff3}\t{cds}\t\n",
        encoding="utf-8",
    )
    outdir = tmp_path / "01_preprocess"

    subprocess.run(
        [
            sys.executable,
            "bin/genefam/preprocess_species.py",
            "--species-manifest",
            str(manifest),
            "--outdir",
            str(outdir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    clean_manifest = outdir / "species_manifest.clean.tsv"
    with clean_manifest.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert rows[0]["pep"].endswith("species_bank_clean/Demo_species/Demo_species.pep.clean.fa")
    assert rows[0]["cds"].endswith("species_bank_clean/Demo_species/Demo_species.cds.clean.fa")
    assert (outdir / "species_manifest.raw.tsv").exists()
    assert (outdir / "species_bank_clean/Demo_species/Demo_species.pep.clean.fa").read_text(encoding="utf-8") == (
        ">AT1G01010\nMAAAA\n"
    )
    assert (outdir / "species_bank_clean/Demo_species/Demo_species.cds.clean.fa").exists()
    assert (outdir / "species_bank_clean/Demo_species/transcript_gene_map.tsv").exists()
    assert (outdir / "species_bank_clean/Demo_species/representative_transcripts.tsv").exists()
    assert (outdir / "species_bank_clean/Demo_species/preprocess_warnings.tsv").exists()
    assert (outdir / "all_transcript_gene_map.tsv").exists()
    assert (outdir / "all_representative_transcripts.tsv").exists()
    assert (outdir / "all_preprocess_warnings.tsv").exists()

    with (outdir / "all_transcript_gene_map.tsv").open("r", encoding="utf-8", newline="") as handle:
        trace_rows = list(csv.DictReader(handle, delimiter="\t"))
    assert trace_rows == [
        {
            "species_id": "Demo_species",
            "raw_transcript_id": "AT1G01010.1|PACid:1",
            "clean_transcript_id": "AT1G01010.1",
            "gene_id": "AT1G01010",
            "source": "gff3",
        },
        {
            "species_id": "Demo_species",
            "raw_transcript_id": "AT1G01010.2|PACid:2",
            "clean_transcript_id": "AT1G01010.2",
            "gene_id": "AT1G01010",
            "source": "gff3",
        },
    ]
