import runpy

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
            "--output",
            "output.csv",
        ],
    )

    args = cli.parse_args()

    assert args.fasta == "input.fasta"
    assert args.output == "output.csv"
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
