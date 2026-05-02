from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PACKAGE_ROOT / "assets"
MODEL_DIR = PACKAGE_ROOT / "model"
REFERENCE_DATA_DIR = PACKAGE_ROOT / "reference_data"
PREDICT_CORE_SCRIPT = PACKAGE_ROOT / "predict_core.R"
