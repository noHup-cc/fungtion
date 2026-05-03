from pathlib import Path

import pandas as pd
import pytest

from fungtion.predict import (
    _build_type_link,
    _format_score,
    _read_fasta_sequences,
    predict_with_r,
)


def test_read_fasta_sequences_skips_blank_lines_and_uppercases(tmp_path):
    fasta_path = tmp_path / "input.fasta"
    fasta_path.write_text(">seq1\nmk\n\nTa\n>seq2\npp\n")

    assert _read_fasta_sequences(fasta_path) == [("seq1", "MKTA"), ("seq2", "PP")]


def test_format_score_and_type_link_edge_cases():
    assert _format_score(1.0) == "1"
    assert _format_score(0.12345) == "0.123"
    assert _format_score(0.2, exact_positive=True) == "1"
    assert _build_type_link("tr|Q12345|desc") == "https://www.uniprot.org/uniprot/Q12345"
    assert (
        _build_type_link("ncbi|ABC123|desc")
        == "https://www.ncbi.nlm.nih.gov/protein/ABC123"
    )
    assert _build_type_link("unknown_header") == ""


def test_predict_with_r_generates_expected_csv_and_exact_matches(
    monkeypatch, tmp_path
):
    feature_csv = tmp_path / "features.csv"
    feature_csv.write_text("esm_uniref50_0\n0.1\n0.2\n")
    header_txt = tmp_path / "headers.txt"
    header_txt.write_text("query_exact\nquery_pred\n")
    output_csv = tmp_path / "predictions.csv"
    fasta_path = tmp_path / "queries.fasta"
    fasta_path.write_text(">query_exact\nMKT\n>query_pred\nPPP\n")
    reference_fasta = tmp_path / "reference.fasta"
    reference_fasta.write_text(">tr|Q12345 exact reference\nMKT\n")

    monkeypatch.setattr("fungtion.predict.shutil.which", lambda _: "/usr/bin/Rscript")

    def fake_run(cmd, capture_output=True, text=True):
        temp_pred = Path(cmd[-1])
        temp_pred.write_text("0.25\n0.75\n")

        class Result:
            returncode = 0
            stderr = ""

        return Result()

    monkeypatch.setattr("fungtion.predict.subprocess.run", fake_run)
    monkeypatch.setattr(
        "fungtion.predict.pd.read_csv",
        lambda *args, **kwargs: pd.DataFrame([0.25, 0.75]),
    )

    predict_with_r(
        str(feature_csv),
        str(header_txt),
        str(output_csv),
        fasta_path=str(fasta_path),
        reference_fasta=str(reference_fasta),
    )

    rows = output_csv.read_text().strip().splitlines()
    assert rows[0] == "header,score,decision,type,type_link"
    assert rows[1] == "query_exact,1,yes,Exp.,https://www.uniprot.org/uniprot/Q12345"
    assert rows[2] == "query_pred,0.750,yes,Pred.,"
    assert not (tmp_path / "predictions.csv.tmp").exists()


def test_predict_with_r_raises_when_rscript_is_missing(monkeypatch, tmp_path):
    feature_csv = tmp_path / "features.csv"
    feature_csv.write_text("esm_uniref50_0\n0.1\n")
    header_txt = tmp_path / "headers.txt"
    header_txt.write_text("query\n")
    output_csv = tmp_path / "predictions.csv"

    monkeypatch.setattr("fungtion.predict.shutil.which", lambda _: None)

    with pytest.raises(RuntimeError, match="Rscript not found on PATH"):
        predict_with_r(str(feature_csv), str(header_txt), str(output_csv))
