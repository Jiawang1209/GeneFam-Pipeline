import csv
from pathlib import Path

from bin.genefam.prepare_jcvi_collinearity import prepare_jcvi_inputs, read_tsv


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_prepare_jcvi_inputs_writes_beds_peptides_layout_and_commands(tmp_path):
    ath_gff = write(
        tmp_path / "Arabidopsis_thaliana.gff3",
        "Chr1\tTAIR\tgene\t10\t90\t.\t+\t.\tID=AT1G01010;Name=AT1G01010\n",
    )
    bra_gff = write(
        tmp_path / "Brassica_rapa.gff3",
        "A01\tJGI\tgene\t100\t240\t.\t-\t.\tID=BraA01g001.v1.1;Name=BraA01g001\n",
    )
    ath_pep = write(tmp_path / "Arabidopsis_thaliana.pep.clean.fa", ">AT1G01010\nMAAA\n")
    bra_pep = write(tmp_path / "Brassica_rapa.pep.clean.fa", ">BraA01g001\nMBBBB\n")
    family_candidates = [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA01g001"},
    ]
    species_manifest = [
        {"species_id": "Arabidopsis_thaliana", "pep": str(ath_pep), "gff3": str(ath_gff), "cds": "", "genome": ""},
        {"species_id": "Brassica_rapa", "pep": str(bra_pep), "gff3": str(bra_gff), "cds": "", "genome": ""},
    ]

    outputs = prepare_jcvi_inputs(family_candidates=family_candidates, species_manifest=species_manifest, outdir=tmp_path / "jcvi")

    assert outputs["pair_manifest"].exists()
    assert (tmp_path / "jcvi/Arabidopsis_thaliana.bed").read_text(encoding="utf-8").splitlines()[0] == "Chr1\t9\t90\tAT1G01010\t0\t+"
    assert (tmp_path / "jcvi/Brassica_rapa.bed").read_text(encoding="utf-8").splitlines()[0] == "A01\t99\t240\tBraA01g001\t0\t-"
    assert (tmp_path / "jcvi/Arabidopsis_thaliana.pep").read_text(encoding="utf-8").startswith(">AT1G01010\nMAAA\n")
    assert (tmp_path / "jcvi/peptides/Brassica_rapa.pep").exists()
    pairs = read_tsv(tmp_path / "jcvi/jcvi_pair_manifest.tsv")
    assert pairs == [
        {
            "pair_id": "Arabidopsis_thaliana.Brassica_rapa",
            "query_species": "Arabidopsis_thaliana",
            "subject_species": "Brassica_rapa",
            "query_bed": "beds/Arabidopsis_thaliana.bed",
            "subject_bed": "beds/Brassica_rapa.bed",
            "query_pep": "peptides/Arabidopsis_thaliana.pep",
            "subject_pep": "peptides/Brassica_rapa.pep",
        }
    ]
    assert (tmp_path / "jcvi/seqids").read_text(encoding="utf-8") == "Chr1\nA01\n"
    layout = (tmp_path / "jcvi/layout").read_text(encoding="utf-8")
    assert "Arabidopsis_thaliana.bed" in layout
    assert "e, 0, 1, Arabidopsis_thaliana.Brassica_rapa.anchors.simple" in layout
    commands = (tmp_path / "jcvi/commands/jcvi_commands.sh").read_text(encoding="utf-8")
    assert "python -m jcvi.compara.catalog ortholog --dbtype prot --notex --no_strip_names Arabidopsis_thaliana Brassica_rapa" in commands
    assert "python -m jcvi.compara.synteny screen --minspan=30 --simple Arabidopsis_thaliana.Brassica_rapa.anchors Arabidopsis_thaliana.Brassica_rapa.anchors.simple" in commands
    assert "python -m jcvi.graphics.karyotype seqids layout --notex --figsize=14x12 --chrstyle=roundrect" in commands
    status = read_tsv(tmp_path / "jcvi/jcvi_input_status.tsv")
    assert {row["status"] for row in status} == {"ok"}


def test_prepare_jcvi_inputs_records_missing_peptide_records(tmp_path):
    gff = write(tmp_path / "A.gff3", "chr1\tx\tgene\t1\t20\t.\t+\t.\tID=gene1\n")
    pep = write(tmp_path / "A.pep.clean.fa", ">other\nMA\n")

    prepare_jcvi_inputs(
        family_candidates=[{"species_id": "A", "gene_id": "gene1"}],
        species_manifest=[{"species_id": "A", "pep": str(pep), "gff3": str(gff), "cds": "", "genome": ""}],
        outdir=tmp_path / "jcvi",
    )

    status = {row["check"]: row for row in read_tsv(tmp_path / "jcvi/jcvi_input_status.tsv")}
    assert status["A.bed_genes"]["status"] == "ok"
    assert status["A.pep_genes"]["status"] == "missing_records"
    assert status["A.pep_genes"]["detail"] == "written=0 missing=1"
