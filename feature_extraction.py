import esm
import pandas as pd
import torch


def _resolve_device(device):
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested, but no GPU is available.")
    return device


def extract_esm_features(
    fasta_path,
    feature_csv,
    header_txt,
    pretrained_weights_path=None,
    device="auto",
):
    resolved_device = _resolve_device(device)
    if pretrained_weights_path:
        model, alphabet = esm.pretrained.load_model_and_alphabet_local(
            pretrained_weights_path
        )
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
            results = model(batch_tokens, repr_layers=[33], return_contacts=True)
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
