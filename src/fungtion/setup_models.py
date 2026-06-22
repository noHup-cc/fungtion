import os
from pathlib import Path
from urllib.request import urlopen

ESM1B_MODEL_FILENAME = "esm1b_t33_650M_UR50S.pt"
ESM1B_MODEL_URL = (
    "https://dl.fbaipublicfiles.com/fair-esm/models/esm1b_t33_650M_UR50S.pt"
)


def get_model_cache_dir():
    override_dir = os.environ.get("FUNGTION_MODEL_DIR")
    if override_dir:
        return Path(override_dir).expanduser()

    xdg_cache_home = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache_home:
        return Path(xdg_cache_home).expanduser() / "fungtion" / "models"

    return Path.home() / ".cache" / "fungtion" / "models"


def get_default_pretrained_weights_path(model_dir=None):
    base_dir = Path(model_dir).expanduser() if model_dir else get_model_cache_dir()
    return base_dir / ESM1B_MODEL_FILENAME


def resolve_pretrained_weights_path(pretrained_weights_path=None):
    if pretrained_weights_path:
        return Path(pretrained_weights_path).expanduser()

    default_path = get_default_pretrained_weights_path()
    if default_path.exists():
        return default_path
    return None


def _format_size(num_bytes):
    return f"{num_bytes / (1024 * 1024):.1f} MB"


def _content_length(response):
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    value = headers.get("Content-Length")
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _print_download_progress(downloaded, total_size):
    if total_size:
        percent = downloaded / total_size * 100
        message = (
            f"\rDownloading ESM-1b weights: {percent:5.1f}% "
            f"({_format_size(downloaded)} / {_format_size(total_size)})"
        )
    else:
        message = f"\rDownloading ESM-1b weights: {_format_size(downloaded)}"
    print(message, end="", flush=True)


def _download_file(url, destination):
    temp_path = destination.with_suffix(destination.suffix + ".part")
    try:
        with urlopen(url) as response, temp_path.open("wb") as handle:
            total_size = _content_length(response)
            downloaded = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                downloaded += len(chunk)
                _print_download_progress(downloaded, total_size)
            print()
        temp_path.replace(destination)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def download_pretrained_weights(model_dir=None, force=False):
    model_path = get_default_pretrained_weights_path(model_dir)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    need_model = force or not model_path.exists()

    if not need_model:
        return model_path, False

    if need_model:
        _download_file(ESM1B_MODEL_URL, model_path)

    return model_path, True
