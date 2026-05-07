import os
import shutil
from pathlib import Path
from urllib.request import urlopen

ESM1B_MODEL_FILENAME = "esm1b_t33_650M_UR50S.pt"
ESM1B_MODEL_URL = (
    "https://dl.fbaipublicfiles.com/fair-esm/models/esm1b_t33_650M_UR50S.pt"
)
ESM1B_REGRESSION_FILENAME = "esm1b_t33_650M_UR50S-contact-regression.pt"
ESM1B_REGRESSION_URL = (
    "https://dl.fbaipublicfiles.com/fair-esm/regression/"
    "esm1b_t33_650M_UR50S-contact-regression.pt"
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


def get_default_regression_weights_path(model_dir=None):
    base_dir = Path(model_dir).expanduser() if model_dir else get_model_cache_dir()
    return base_dir / ESM1B_REGRESSION_FILENAME


def resolve_pretrained_weights_path(pretrained_weights_path=None):
    if pretrained_weights_path:
        return Path(pretrained_weights_path).expanduser()

    default_path = get_default_pretrained_weights_path()
    regression_path = get_default_regression_weights_path()
    if default_path.exists() and regression_path.exists():
        return default_path
    return None


def _download_file(url, destination):
    temp_path = destination.with_suffix(destination.suffix + ".part")
    try:
        with urlopen(url) as response, temp_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        temp_path.replace(destination)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def download_pretrained_weights(model_dir=None, force=False):
    model_path = get_default_pretrained_weights_path(model_dir)
    regression_path = get_default_regression_weights_path(model_dir)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    need_model = force or not model_path.exists()
    need_regression = force or not regression_path.exists()

    if not need_model and not need_regression:
        return model_path, False

    if need_model:
        _download_file(ESM1B_MODEL_URL, model_path)
    if need_regression:
        _download_file(ESM1B_REGRESSION_URL, regression_path)

    return model_path, True
