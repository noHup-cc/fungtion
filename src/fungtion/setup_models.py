import os
import shutil
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
    return default_path if default_path.exists() else None


def download_pretrained_weights(model_dir=None, force=False):
    destination = get_default_pretrained_weights_path(model_dir)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists() and not force:
        return destination, False

    temp_path = destination.with_suffix(destination.suffix + ".part")
    try:
        with urlopen(ESM1B_MODEL_URL) as response, temp_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        temp_path.replace(destination)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    return destination, True
