import io

from fungtion import cli
from fungtion.setup_models import (
    ESM1B_MODEL_FILENAME,
    download_pretrained_weights,
    get_default_pretrained_weights_path,
    get_default_regression_weights_path,
    resolve_pretrained_weights_path,
)


def test_parse_args_for_setup_models_command():
    args = cli.parse_args(["setup-models", "--model-dir", "/tmp/models", "--force"])

    assert args.command == "setup-models"
    assert args.model_dir == "/tmp/models"
    assert args.force is True


def test_setup_models_main_prints_download_location(monkeypatch, capsys, tmp_path):
    weights_path = tmp_path / "models" / ESM1B_MODEL_FILENAME

    monkeypatch.setattr(
        "fungtion.cli.download_pretrained_weights",
        lambda **kwargs: (weights_path, True),
    )

    cli.main(["setup-models", "--model-dir", str(tmp_path / "models")])

    captured = capsys.readouterr()
    assert "Downloaded ESM-1b weights to" in captured.out
    assert str(weights_path) in captured.out


def test_resolve_pretrained_weights_path_prefers_existing_default(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("FUNGTION_MODEL_DIR", str(tmp_path / "models"))
    default_path = get_default_pretrained_weights_path()
    regression_path = get_default_regression_weights_path()
    default_path.parent.mkdir(parents=True, exist_ok=True)
    default_path.write_text("weights")
    regression_path.write_text("regression")

    assert resolve_pretrained_weights_path() == default_path


def test_resolve_pretrained_weights_path_respects_explicit_path(tmp_path):
    explicit_path = tmp_path / "custom" / ESM1B_MODEL_FILENAME

    assert resolve_pretrained_weights_path(str(explicit_path)) == explicit_path


def test_download_pretrained_weights_skips_existing_file(tmp_path):
    existing_path = get_default_pretrained_weights_path(tmp_path / "models")
    regression_path = get_default_regression_weights_path(tmp_path / "models")
    existing_path.parent.mkdir(parents=True, exist_ok=True)
    existing_path.write_text("existing")
    regression_path.write_text("existing-regression")

    resolved_path, downloaded = download_pretrained_weights(
        model_dir=tmp_path / "models", force=False
    )

    assert resolved_path == existing_path
    assert downloaded is False


def test_download_pretrained_weights_writes_downloaded_file(monkeypatch, tmp_path):
    downloaded_urls = []

    def fake_urlopen(_url):
        downloaded_urls.append(_url)
        if _url.endswith(ESM1B_MODEL_FILENAME):
            return io.BytesIO(b"fake-weights")
        return io.BytesIO(b"fake-regression")

    monkeypatch.setattr("fungtion.setup_models.urlopen", fake_urlopen)

    resolved_path, downloaded = download_pretrained_weights(
        model_dir=tmp_path / "models"
    )
    regression_path = get_default_regression_weights_path(tmp_path / "models")

    assert resolved_path.read_bytes() == b"fake-weights"
    assert regression_path.read_bytes() == b"fake-regression"
    assert downloaded is True
    assert len(downloaded_urls) == 2


def test_resolve_pretrained_weights_path_returns_none_without_regression(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("FUNGTION_MODEL_DIR", str(tmp_path / "models"))
    default_path = get_default_pretrained_weights_path()
    default_path.parent.mkdir(parents=True, exist_ok=True)
    default_path.write_text("weights")

    assert resolve_pretrained_weights_path() is None
