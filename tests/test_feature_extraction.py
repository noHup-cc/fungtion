import importlib
import sys
import types

import pytest


@pytest.fixture
def feature_extraction_module(monkeypatch):
    fake_esm = types.SimpleNamespace()
    fake_torch = types.SimpleNamespace(
        cuda=types.SimpleNamespace(is_available=lambda: False)
    )
    monkeypatch.setitem(sys.modules, "esm", fake_esm)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    sys.modules.pop("fungtion.feature_extraction", None)

    module = importlib.import_module("fungtion.feature_extraction")
    yield module
    sys.modules.pop("fungtion.feature_extraction", None)


def test_resolve_device_auto_uses_cpu_when_cuda_is_unavailable(
    monkeypatch, feature_extraction_module
):
    monkeypatch.setattr(
        feature_extraction_module.torch.cuda, "is_available", lambda: False
    )

    assert feature_extraction_module._resolve_device("auto") == "cpu"


def test_resolve_device_raises_for_missing_cuda(monkeypatch, feature_extraction_module):
    monkeypatch.setattr(
        feature_extraction_module.torch.cuda, "is_available", lambda: False
    )

    with pytest.raises(RuntimeError, match="CUDA was requested"):
        feature_extraction_module._resolve_device("cuda")


def test_load_local_model_uses_torch_safe_globals(
    monkeypatch, feature_extraction_module
):
    calls = []

    class FakeSafeGlobals:
        def __init__(self, values):
            calls.append(("safe_globals", values))

        def __enter__(self):
            calls.append(("enter", None))

        def __exit__(self, exc_type, exc, traceback):
            calls.append(("exit", None))

    def fake_torch_load(path, map_location=None):
        calls.append(("torch_load", path, map_location))
        return {"model": "weights"}

    def fake_load_core(model_name, model_data):
        calls.append(("load_core", model_name, model_data))
        return "model", "alphabet"

    feature_extraction_module.torch.serialization = types.SimpleNamespace(
        safe_globals=FakeSafeGlobals
    )
    feature_extraction_module.torch.load = fake_torch_load
    feature_extraction_module.esm.pretrained = types.SimpleNamespace(
        load_model_and_alphabet_core=fake_load_core
    )

    model, alphabet = feature_extraction_module._load_local_model_and_alphabet(
        "/tmp/esm1b_t33_650M_UR50S.pt"
    )

    assert (model, alphabet) == ("model", "alphabet")
    assert calls[0][0] == "safe_globals"
    assert feature_extraction_module.argparse.Namespace in calls[0][1]
    assert calls[1:] == [
        ("enter", None),
        ("torch_load", "/tmp/esm1b_t33_650M_UR50S.pt", "cpu"),
        ("exit", None),
        ("load_core", "esm1b_t33_650M_UR50S", {"model": "weights"}),
    ]
