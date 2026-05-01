import csv
import os
import shutil
import subprocess

import pandas as pd

from ._paths import PREDICT_CORE_SCRIPT


def _read_fasta_sequences(fasta_path):
    sequences = []
    current_header = None
    current_seq = []
    with open(fasta_path) as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current_header is not None:
                    sequences.append((current_header, "".join(current_seq).upper()))
                current_header = line[1:]
                current_seq = []
            else:
                current_seq.append(line)
    if current_header is not None:
        sequences.append((current_header, "".join(current_seq).upper()))
    return sequences


def _format_score(score_value, exact_positive=False):
    if exact_positive or abs(float(score_value) - 1.0) < 1e-12:
        return "1"
    return f"{float(score_value):.3f}"


def _build_type_link(reference_header):
    if not reference_header:
        return ""
    token = reference_header.split()[0]
    parts = token.split("|")
    if len(parts) < 2:
        return ""
    prefix = parts[0].lower()
    accession = parts[1]
    if prefix in {"tr", "sp"} and accession:
        return f"https://www.uniprot.org/uniprot/{accession}"
    if prefix == "ncbi" and accession:
        return f"https://www.ncbi.nlm.nih.gov/protein/{accession}"
    return ""


def predict_with_r(
    feature_csv, header_txt, output_csv, fasta_path=None, reference_fasta=None
):
    if not shutil.which("Rscript"):
        raise RuntimeError(
            "Rscript not found on PATH. R must be installed along with the packages "
            "e1071, caret, and optparse before using fungtion.\n"
            "Install via conda: conda install -c conda-forge "
            "r-base r-e1071 r-caret r-optparse\n"
            "See also: https://github.com/noHup-cc/fungtion#install"
        )
    temp_pred = output_csv + ".tmp"
    cmd = [
        "Rscript",
        str(PREDICT_CORE_SCRIPT),
        "--features",
        feature_csv,
        "--output",
        temp_pred,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("R prediction failed")
    with open(header_txt) as f:
        headers = [line.strip() for line in f]
    scores = pd.read_csv(temp_pred, header=None)[0].tolist()
    exact_positive_matches = {}
    if fasta_path and reference_fasta and os.path.exists(reference_fasta):
        reference_sequences = {
            sequence: header
            for header, sequence in _read_fasta_sequences(reference_fasta)
            if sequence
        }
        exact_positive_matches = {
            header: reference_sequences[sequence]
            for header, sequence in _read_fasta_sequences(fasta_path)
            if sequence and sequence in reference_sequences
        }
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["header", "score", "decision", "type", "type_link"])
        for h, s in zip(headers, scores, strict=False):
            reference_header = exact_positive_matches.get(h, "")
            exact_positive = bool(reference_header)
            if exact_positive:
                s = 1.0
            decision = "yes" if s >= 0.5 else "no"
            result_type = "Exp." if exact_positive else "Pred."
            writer.writerow(
                [
                    h,
                    _format_score(s, exact_positive=exact_positive),
                    decision,
                    result_type,
                    _build_type_link(reference_header),
                ]
            )
    os.remove(temp_pred)
