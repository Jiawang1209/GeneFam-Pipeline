from bin.genefam.prepare_alignment_inputs import prepare_alignment_manifest


def test_prepare_alignment_manifest_counts_sequences_and_sets_outputs(tmp_path):
    fasta = tmp_path / "family_members.faa"
    fasta.write_text(">gene1\nMAAA\n>gene2\nMCCC\n", encoding="utf-8")
    outdir = tmp_path / "alignment"

    rows = prepare_alignment_manifest(family_name="GDSL", fasta_path=fasta, outdir=outdir, aligner="mafft")

    assert rows == [
        {
            "family_name": "GDSL",
            "aligner": "mafft",
            "sequence_count": "2",
            "input_fasta": str(fasta),
            "raw_alignment": str(outdir / "GDSL.mafft.aln.faa"),
            "trimmed_alignment": str(outdir / "GDSL.mafft.trimmed.aln.faa"),
        }
    ]


def test_prepare_alignment_manifest_requires_two_sequences(tmp_path):
    fasta = tmp_path / "family_members.faa"
    fasta.write_text(">gene1\nMAAA\n", encoding="utf-8")

    try:
        prepare_alignment_manifest(family_name="GDSL", fasta_path=fasta, outdir=tmp_path, aligner="mafft")
    except ValueError as error:
        assert "At least two sequences are required for alignment" in str(error)
    else:
        raise AssertionError("Expected ValueError for a single-sequence FASTA")
