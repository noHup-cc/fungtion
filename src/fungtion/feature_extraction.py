import argparse
import warnings
from pathlib import Path

import esm
import pandas as pd
import torch


def _resolve_device(device):
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested, but no GPU is available.")
    return device


def _load_local_model_and_alphabet(pretrained_weights_path):
    model_location = Path(pretrained_weights_path)
    model_name = model_location.stem
    safe_globals = getattr(getattr(torch, "serialization", None), "safe_globals", None)
    if safe_globals is None:
        model_data = torch.load(str(model_location), map_location="cpu")
        return _load_model_core_without_regression_warning(model_name, model_data)

    with safe_globals([argparse.Namespace]):
        model_data = torch.load(str(model_location), map_location="cpu")
    return _load_model_core_without_regression_warning(model_name, model_data)


def _load_model_core_without_regression_warning(model_name, model_data):
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Regression weights not found.*",
            category=UserWarning,
        )
        return esm.pretrained.load_model_and_alphabet_core(model_name, model_data)


def extract_esm_features(
    fasta_path,
    feature_csv,
    header_txt,
    pretrained_weights_path=None,
    device="auto",
):
    resolved_device = _resolve_device(device)
    if pretrained_weights_path:
        model, alphabet = _load_local_model_and_alphabet(pretrained_weights_path)
    else:
        model, alphabet = esm.pretrained.esm1b_t33_650M_UR50S()
    batch_converter = alphabet.get_batch_converter()
    model = model.to(resolved_device)
    model.eval()

    sequences = []
    headers = []
    for header, seq in esm.data.read_fasta(fasta_path):
        headers.append(header)
        if len(seq) > 1022:
            seq = seq[:1022]
        sequences.append((header, seq))

    feature_list = []
    for header, seq in sequences:
        batch_tokens = batch_converter([(header, seq)])[2].to(resolved_device)
        with torch.no_grad():
            results = model(batch_tokens, repr_layers=[33], return_contacts=False)
        token_representations = results["representations"][33]
        embedding = (
            token_representations[:, 1 : len(seq) + 1].mean(0).mean(0).cpu().numpy()
        )
        feature_list.append(embedding)

    df = pd.DataFrame(
        feature_list,
        columns=[f"esm_uniref50_{i}" for i in range(len(feature_list[0]))],
    )
    df.to_csv(feature_csv, index=False)
    with open(header_txt, "w") as f:
        for h in headers:
            f.write(h + "\n")
