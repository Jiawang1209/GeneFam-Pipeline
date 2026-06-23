from bin.genefam.parse_meme_motifs import parse_meme_text


def test_parse_meme_text_extracts_motif_summary(tmp_path):
    meme_txt = tmp_path / "meme.txt"
    meme_txt.write_text(
        "MEME version 5\n\n"
        "MOTIF 1 GDSL_motif_1\n"
        "letter-probability matrix: alength= 20 w= 11 nsites= 18 E= 2.3e-12\n"
        "0.1 0.2 0.3\n\n"
        "MOTIF 2 GDSL_motif_2\n"
        "letter-probability matrix: alength= 20 w= 7 nsites= 12 E= 4.8e-06\n",
        encoding="utf-8",
    )

    rows = parse_meme_text(meme_txt, family_name="GDSL")

    assert rows == [
        {
            "family_name": "GDSL",
            "motif_id": "1",
            "motif_name": "GDSL_motif_1",
            "width": "11",
            "sites": "18",
            "evalue": "2.3e-12",
        },
        {
            "family_name": "GDSL",
            "motif_id": "2",
            "motif_name": "GDSL_motif_2",
            "width": "7",
            "sites": "12",
            "evalue": "4.8e-06",
        },
    ]


def test_parse_meme_text_fails_when_matrix_is_missing(tmp_path):
    meme_txt = tmp_path / "meme.txt"
    meme_txt.write_text("MOTIF 1 GDSL_motif_1\n", encoding="utf-8")

    try:
        parse_meme_text(meme_txt, family_name="GDSL")
    except ValueError as error:
        assert "Missing letter-probability matrix for motif 1" in str(error)
    else:
        raise AssertionError("Expected ValueError for incomplete MEME motif")
