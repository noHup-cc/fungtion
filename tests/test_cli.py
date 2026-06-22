import runpy
import sys
import types
from pathlib import Path

import pytest

from fungtion import __version__, cli
from fungtion._paths import (
    ASSETS_DIR,
    MODEL_DIR,
    PREDICT_CORE_SCRIPT,
    REFERENCE_DATA_DIR,
)


def test_parse_args_with_required_arguments(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "fungtion",
            "--fasta",
            "input.fasta",
            "--output-dir",
            "outputs",
            "--prefix",
            "sample",
        ],
    )

    args = cli.parse_args()

    assert args.fasta == "input.fasta"
    assert args.output_dir == "outputs"
    assert args.prefix == "sample"
    assert args.device == "auto"
    assert args.skip_visualization is False


def test_version_flag_prints_package_version(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["fungtion", "--version"])

    with pytest.raises(SystemExit) as excinfo:
        cli.parse_args()

    captured = capsys.readouterr()
    assert excinfo.value.code == 0
    assert __version__ in captured.out


def test_python_dash_m_fungtion_invokes_cli_main(monkeypatch):
    called = {"value": False}

    def fake_main():
        called["value"] = True

    monkeypatch.setattr("fungtion.cli.main", fake_main)

    runpy.run_module("fungtion", run_name="__main__")

    assert called["value"] is True


def test_packaged_resource_paths_exist():
    assert ASSETS_DIR.exists()
    assert MODEL_DIR.exists()
    assert REFERENCE_DATA_DIR.exists()
    assert PREDICT_CORE_SCRIPT.exists()


def test_main_runs_end_to_end_with_skip_visualization(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("FUNGTION_MODEL_DIR", str(tmp_path / "models"))
    fasta_path = tmp_path / "input.fasta"
    fasta_path.write_text(">seq1\nMKT\n")
    output_root = tmp_path / "outputs" / "predictions"
    output_path = output_root / "predictions.csv"
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()

    def fake_extract(
        fasta_path_arg,
        feature_csv,
        header_txt,
        pretrained_weights_path=None,
        device="auto",
    ):
        assert Path(fasta_path_arg) == fasta_path
        assert pretrained_weights_path is None
        assert device == "auto"
        Path(feature_csv).write_text("esm_uniref50_0\n0.1\n")
        Path(header_txt).write_text("seq1\n")

    def fake_predict(
        feature_csv,
        header_txt,
        output_csv,
        fasta_path=None,
        reference_fasta=None,
    ):
        assert Path(feature_csv).exists()
        assert Path(header_txt).exists()
        assert Path(fasta_path) == fasta_path_arg
        assert Path(reference_fasta).exists()
        Path(output_csv).write_text(
            "header,score,decision,type,type_link\nseq1,0.800,yes,Pred.,\n"
        )

    fasta_path_arg = fasta_path
    monkeypatch.setitem(
        sys.modules,
        "fungtion.feature_extraction",
        types.SimpleNamespace(extract_esm_features=fake_extract),
    )
    monkeypatch.setitem(
        sys.modules,
        "fungtion.predict",
        types.SimpleNamespace(predict_with_r=fake_predict),
    )
    monkeypatch.setitem(
        sys.modules,
        "fungtion.analysis_outputs",
        types.SimpleNamespace(generate_visual_outputs=lambda **kwargs: None),
    )
    monkeypatch.setitem(
        sys.modules,
        "fungtion.html_report",
        types.SimpleNamespace(generate_html_report=lambda **kwargs: None),
    )
    monkeypatch.setattr("fungtion.cli.tempfile.mkdtemp", lambda: str(temp_dir))
    monkeypatch.setattr(
        "sys.argv",
        [
            "fungtion",
            "--fasta",
            str(fasta_path),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--prefix",
            "predictions",
            "--skip-visualization",
        ],
    )

    cli.main()

    captured = capsys.readouterr()
    assert output_path.exists()
    assert "Prediction finished. Results saved to" in captured.out
    assert not (temp_dir / "features.csv").exists()
    assert not (temp_dir / "headers.txt").exists()
    assert not temp_dir.exists()


def test_main_runs_visualization_and_html_paths(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("FUNGTION_MODEL_DIR", str(tmp_path / "models"))
    fasta_path = tmp_path / "input.fasta"
    fasta_path.write_text(">seq1\nMKT\n")
    output_root = tmp_path / "results" / "predictions"
    analysis_dir = output_root / "predictions_analysis"
    html_output = output_root / "predictions.html"
    html_assets_dir = output_root / "predictions_assets"
    temp_dir = output_root / "predictions_temp_folder"

    def fake_extract(
        fasta_path_arg,
        feature_csv,
        header_txt,
        pretrained_weights_path=None,
        device="auto",
    ):
        Path(feature_csv).write_text("esm_uniref50_0\n0.1\n")
        Path(header_txt).write_text("seq1\n")

    def fake_predict(
        feature_csv,
        header_txt,
        output_csv,
        fasta_path=None,
        reference_fasta=None,
    ):
        Path(output_csv).write_text(
            "header,score,decision,type,type_link\nseq1,0.800,yes,Pred.,\n"
        )

    def fake_generate_visual_outputs(
        fasta_path,
        feature_csv,
        prediction_csv,
        analysis_dir,
        reference_dir,
    ):
        manifest_path = Path(analysis_dir) / "manifest.csv"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text("sequence_id,page_path\nseq1,seq1.html\n")
        return str(manifest_path)

    def fake_generate_html_report(
        prediction_csv,
        output_html,
        manifest_csv=None,
        assets_dir=None,
    ):
        Path(output_html).parent.mkdir(parents=True, exist_ok=True)
        Path(output_html).write_text("<html></html>")
        if assets_dir:
            Path(assets_dir).mkdir(parents=True, exist_ok=True)

    monkeypatch.setitem(
        sys.modules,
        "fungtion.feature_extraction",
        types.SimpleNamespace(extract_esm_features=fake_extract),
    )
    monkeypatch.setitem(
        sys.modules,
        "fungtion.predict",
        types.SimpleNamespace(predict_with_r=fake_predict),
    )
    monkeypatch.setitem(
        sys.modules,
        "fungtion.analysis_outputs",
        types.SimpleNamespace(generate_visual_outputs=fake_generate_visual_outputs),
    )
    monkeypatch.setitem(
        sys.modules,
        "fungtion.html_report",
        types.SimpleNamespace(generate_html_report=fake_generate_html_report),
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "fungtion",
            "--fasta",
            str(fasta_path),
            "--output-dir",
            str(tmp_path / "results"),
            "--prefix",
            "predictions",
            "--html-report",
            "--keep-temp",
        ],
    )

    cli.main()

    captured = capsys.readouterr()
    assert (analysis_dir / "manifest.csv").exists()
    assert html_output.exists()
    assert html_assets_dir.exists()
    assert (temp_dir / "features.csv").exists()
    assert (temp_dir / "headers.txt").exists()
    assert "Visualization manifest saved to" in captured.out
    assert "HTML report saved to" in captured.out
    assert f"Intermediate files kept in {temp_dir}" in captured.out
