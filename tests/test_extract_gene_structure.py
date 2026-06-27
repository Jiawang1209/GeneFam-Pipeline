import subprocess
import sys

from bin.genefam.extract_gene_structure import extract_structure, summarize_structure


def test_extract_gene_structure_counts_exons_cds_and_lengths(tmp_path):
    gff3 = tmp_path / "species.gff3"
    gff3.write_text(
        "Chr1\ttest\tgene\t100\t500\t.\t+\t.\tID=gene1\n"
        "Chr1\ttest\tmRNA\t100\t500\t.\t+\t.\tID=gene1.t1;Parent=gene1\n"
        "Chr1\ttest\texon\t100\t180\t.\t+\t.\tID=gene1.e1;Parent=gene1.t1\n"
        "Chr1\ttest\texon\t250\t320\t.\t+\t.\tID=gene1.e2;Parent=gene1.t1\n"
        "Chr1\ttest\tCDS\t120\t180\t.\t+\t0\tID=gene1.cds1;Parent=gene1.t1\n"
        "Chr1\ttest\tCDS\t250\t300\t.\t+\t0\tID=gene1.cds2;Parent=gene1.t1\n"
        "Chr1\ttest\tgene\t900\t1200\t.\t-\t.\tID=gene2\n"
        "Chr1\ttest\texon\t900\t1000\t.\t-\t.\tID=gene2.e1;Parent=gene2\n",
        encoding="utf-8",
    )

    rows = extract_structure(gff3, species_id="Test_species", gene_ids={"gene1", "gene2"})

    assert rows == [
        {
            "species_id": "Test_species",
            "gene_id": "gene1",
            "gene_length": "401",
            "transcript_count": "1",
            "exon_count": "2",
            "cds_count": "2",
            "exon_total_length": "152",
            "cds_total_length": "112",
        },
        {
            "species_id": "Test_species",
            "gene_id": "gene2",
            "gene_length": "301",
            "transcript_count": "0",
            "exon_count": "1",
            "cds_count": "0",
            "exon_total_length": "101",
            "cds_total_length": "0",
        },
    ]


def test_summarize_structure_reads_manifest_and_family_candidates(tmp_path):
    gff3 = tmp_path / "species.gff3"
    gff3.write_text(
        "Chr1\ttest\tgene\t100\t500\t.\t+\t.\tID=gene1\n"
        "Chr1\ttest\texon\t100\t180\t.\t+\t.\tParent=gene1\n",
        encoding="utf-8",
    )

    rows = summarize_structure(
        [{"species_id": "Test_species", "gene_id": "gene1"}],
        [{"species_id": "Test_species", "gff3": str(gff3)}],
    )

    assert rows[0]["gene_id"] == "gene1"
    assert rows[0]["gene_length"] == "401"
    assert rows[0]["exon_count"] == "1"


def test_extract_gene_structure_matches_phytozome_versioned_gene_ids(tmp_path):
    gff3 = tmp_path / "brassica.gff3"
    gff3.write_text(
        "Chr01\tphytozomev13\tgene\t1629\t3263\t.\t+\t.\t"
        "ID=BrO_302V.01G000100.v1.1;Name=BrO_302V.01G000100\n"
        "Chr01\tphytozomev13\tmRNA\t1629\t3263\t.\t+\t.\t"
        "ID=BrO_302V.01G000100.1.v1.1;Name=BrO_302V.01G000100.1;Parent=BrO_302V.01G000100.v1.1\n"
        "Chr01\tphytozomev13\tCDS\t1629\t3263\t.\t+\t0\t"
        "ID=BrO_302V.01G000100.1.v1.1.CDS.1;Parent=BrO_302V.01G000100.1.v1.1\n",
        encoding="utf-8",
    )

    rows = extract_structure(gff3, species_id="Brassica_rapa", gene_ids={"BrO_302V.01G000100"})

    assert rows == [
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BrO_302V.01G000100",
            "gene_length": "1635",
            "transcript_count": "1",
            "exon_count": "0",
            "cds_count": "1",
            "exon_total_length": "0",
            "cds_total_length": "1635",
        }
    ]


def test_extract_gene_structure_cli_writes_tsv(tmp_path):
    gff3 = tmp_path / "species.gff3"
    gff3.write_text("Chr1\ttest\tgene\t100\t500\t.\t+\t.\tID=gene1\n", encoding="utf-8")
    candidates = tmp_path / "family_candidates.tsv"
    candidates.write_text("species_id\tgene_id\nTest_species\tgene1\n", encoding="utf-8")
    manifest = tmp_path / "species_manifest.tsv"
    manifest.write_text(f"species_id\tpep\tgff3\tcds\tgenome\nTest_species\t\t{gff3}\t\t\n", encoding="utf-8")
    out = tmp_path / "gene_structure_summary.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/extract_gene_structure.py",
            "--family-candidates",
            str(candidates),
            "--species-manifest",
            str(manifest),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert out.read_text(encoding="utf-8").startswith(
        "species_id\tgene_id\tgene_length\ttranscript_count\texon_count\tcds_count\texon_total_length\tcds_total_length\n"
    )
