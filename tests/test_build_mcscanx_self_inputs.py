from pathlib import Path

from bin.genefam.build_mcscanx_self_inputs import build_mcscanx_self_inputs, read_tsv


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_build_mcscanx_self_inputs_marks_missing_self_files(tmp_path):
    gff3 = write(tmp_path / "A.gff3", "chr1\tx\tgene\t1\t100\t.\t+\t.\tID=gene1\n")
    pep = write(tmp_path / "A.pep.fa", ">gene1\nMKK\n")
    species_manifest = [{"species_id": "A", "pep": str(pep), "gff3": str(gff3), "cds": "", "genome": ""}]
    family_candidates = [{"species_id": "A", "gene_id": "gene1"}]

    build_mcscanx_self_inputs(
        family_candidates=family_candidates,
        species_manifest=species_manifest,
        outdir=tmp_path / "mcscanx",
        mcscanx_self_dir=None,
    )

    assert (tmp_path / "mcscanx/family_beds/A.GF.bed").exists()
    status = read_tsv(tmp_path / "mcscanx/mcscanx_self_status.tsv")
    assert status[0]["status"] == "missing_input"
    assert ".tandem/.collinearity" in status[0]["note"]
    run_status = read_tsv(tmp_path / "mcscanx/mcscanx_run_status.tsv")
    assert run_status == [
        {
            "species_id": "A",
            "status": "prepared",
            "mcscanx_gff": "mcscanx_run/A.gff",
            "pep": str(pep),
            "command": "commands/mcscanx_self_commands.sh",
            "note": "MCScanX self-run inputs prepared; execute command script when blastp and MCScanX are available",
        }
    ]
    assert (tmp_path / "mcscanx/mcscanx_run/A.gff").read_text(encoding="utf-8") == "chr1\tgene1\t1\t100\n"
    command_text = (tmp_path / "mcscanx/commands/mcscanx_self_commands.sh").read_text(encoding="utf-8")
    assert "diamond makedb --in" in command_text
    assert "diamond blastp --query" in command_text
    assert "--outfmt 6" in command_text
    assert "MCScanX A" in command_text


def test_build_mcscanx_self_inputs_can_prepare_ncbi_blast_commands(tmp_path):
    gff3 = write(tmp_path / "A.gff3", "chr1\tx\tgene\t1\t100\t.\t+\t.\tID=gene1\n")
    pep = write(tmp_path / "A.pep.fa", ">gene1\nMKK\n")

    build_mcscanx_self_inputs(
        family_candidates=[{"species_id": "A", "gene_id": "gene1"}],
        species_manifest=[{"species_id": "A", "pep": str(pep), "gff3": str(gff3), "cds": "", "genome": ""}],
        outdir=tmp_path / "mcscanx",
        mcscanx_self_dir=None,
        search_tool="blastp",
    )

    command_text = (tmp_path / "mcscanx/commands/mcscanx_self_commands.sh").read_text(encoding="utf-8")
    assert "makeblastdb -in" in command_text
    assert "blastp -query" in command_text


def test_build_mcscanx_self_inputs_parses_tandem_and_collinearity_pairs(tmp_path):
    gff3 = write(
        tmp_path / "A.gff3",
        "chr1\tx\tgene\t1\t100\t.\t+\t.\tID=gene1\n"
        "chr1\tx\tgene\t200\t300\t.\t+\t.\tID=gene2\n"
        "chr1\tx\tgene\t400\t500\t.\t+\t.\tID=gene3\n",
    )
    mcscanx_dir = tmp_path / "mcscanx_self"
    write(mcscanx_dir / "A.gene_type", "gene1\t3\n")
    write(mcscanx_dir / "A.tandem2", "gene1\tgene2\n")
    write(mcscanx_dir / "A.collinearity2", "gene1\tgene3\n")

    build_mcscanx_self_inputs(
        family_candidates=[{"species_id": "A", "gene_id": "gene1"}],
        species_manifest=[{"species_id": "A", "pep": "", "gff3": str(gff3), "cds": "", "genome": ""}],
        outdir=tmp_path / "out",
        mcscanx_self_dir=mcscanx_dir,
    )

    status = read_tsv(tmp_path / "out/mcscanx_self_status.tsv")
    assert status[0]["status"] == "available"
    pairs = read_tsv(tmp_path / "out/species_pairs/A.gene_pairs.csv")
    assert pairs == [
        {"species_id": "A", "type": "tandem", "gene_a": "gene1", "gene_b": "gene2"},
        {"species_id": "A", "type": "WGD", "gene_a": "gene1", "gene_b": "gene3"},
    ]
    ids = read_tsv(tmp_path / "out/species_pairs/A.gene_pairs.ID.csv")
    assert ids == [
        {"species_id": "A", "gene_id": "gene1"},
        {"species_id": "A", "gene_id": "gene2"},
        {"species_id": "A", "gene_id": "gene3"},
    ]


def test_build_mcscanx_self_inputs_does_not_require_gene_type_file(tmp_path):
    gff3 = write(
        tmp_path / "A.gff3",
        "chr1\tx\tgene\t1\t100\t.\t+\t.\tID=gene1\n"
        "chr1\tx\tgene\t200\t300\t.\t+\t.\tID=gene2\n",
    )
    mcscanx_dir = tmp_path / "mcscanx_run"
    write(mcscanx_dir / "A.tandem", "gene1\tgene2\n")

    build_mcscanx_self_inputs(
        family_candidates=[{"species_id": "A", "gene_id": "gene1"}],
        species_manifest=[{"species_id": "A", "pep": "", "gff3": str(gff3), "cds": "", "genome": ""}],
        outdir=tmp_path / "out",
        mcscanx_self_dir=mcscanx_dir,
    )

    status = read_tsv(tmp_path / "out/mcscanx_self_status.tsv")
    assert status[0]["status"] == "available"
    assert status[0]["gene_type"] == ""
    assert status[0]["tandem"] == "A.tandem"
    assert status[0]["note"] == "ok"


def test_build_mcscanx_self_inputs_parses_native_mcscanx_collinearity_lines(tmp_path):
    gff3 = write(
        tmp_path / "A.gff3",
        "chr1\tx\tgene\t1\t100\t.\t+\t.\tID=gene1\n"
        "chr1\tx\tgene\t200\t300\t.\t+\t.\tID=gene2\n",
    )
    mcscanx_dir = tmp_path / "mcscanx_run"
    write(mcscanx_dir / "A.gene_type", "gene1\t4\n")
    write(mcscanx_dir / "A.tandem", "")
    write(
        mcscanx_dir / "A.collinearity",
        "## Alignment 0: score=100 e_value=1e-20 N=1 chr1&chr1 plus\n"
        "  0-  0: gene1 gene2 1e-40\n",
    )

    build_mcscanx_self_inputs(
        family_candidates=[{"species_id": "A", "gene_id": "gene1"}],
        species_manifest=[{"species_id": "A", "pep": "", "gff3": str(gff3), "cds": "", "genome": ""}],
        outdir=tmp_path / "out",
        mcscanx_self_dir=mcscanx_dir,
    )

    pairs = read_tsv(tmp_path / "out/mcscanx_gene_pairs.tsv")
    assert pairs == [{"species_id": "A", "type": "WGD", "gene_a": "gene1", "gene_b": "gene2"}]
