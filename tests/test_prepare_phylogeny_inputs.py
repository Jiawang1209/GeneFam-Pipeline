from bin.genefam.prepare_phylogeny_inputs import prepare_phylogeny_manifest


def test_prepare_phylogeny_manifest_prefers_trimmed_alignment(tmp_path):
    alignment_rows = [
        {
            "family_name": "GDSL",
            "aligner": "mafft",
            "sequence_count": "12",
            "input_fasta": "family.faa",
            "raw_alignment": "alignment/GDSL.mafft.aln.faa",
            "trimmed_alignment": "alignment/GDSL.mafft.trimmed.aln.faa",
        }
    ]

    rows = prepare_phylogeny_manifest(alignment_rows, outdir=tmp_path, tree_builder="iqtree")

    assert rows == [
        {
            "family_name": "GDSL",
            "tree_builder": "iqtree",
            "alignment": "alignment/GDSL.mafft.trimmed.aln.faa",
            "treefile": str(tmp_path / "GDSL.iqtree.treefile"),
            "support_file": str(tmp_path / "GDSL.iqtree.support.tsv"),
        }
    ]


def test_prepare_phylogeny_manifest_falls_back_to_raw_alignment(tmp_path):
    alignment_rows = [
        {
            "family_name": "GDSL",
            "aligner": "mafft",
            "sequence_count": "12",
            "input_fasta": "family.faa",
            "raw_alignment": "alignment/GDSL.mafft.aln.faa",
            "trimmed_alignment": "",
        }
    ]

    rows = prepare_phylogeny_manifest(alignment_rows, outdir=tmp_path, tree_builder="fasttree")

    assert rows[0]["alignment"] == "alignment/GDSL.mafft.aln.faa"
    assert rows[0]["treefile"].endswith("GDSL.fasttree.treefile")
