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
