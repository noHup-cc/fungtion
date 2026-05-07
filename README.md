<p align="center">
  <img src="src/fungtion/assets/images/Fungtion_logo_with_black_text_dpi_150.png" alt="Fungtion logo" width="320">
</p>

# Fungtion

Predict fungal effectors from FASTA files using ESM-1b embeddings and R SVM models.

Paper: [https://doi.org/10.1016/j.jmb.2024.168613](https://doi.org/10.1016/j.jmb.2024.168613)

For sequences predicted as fungal effectors, this project also generates:

- ESM-1b-based similarity network visualization
- relationship tree visualization
- an HTML report in the style of the original Fungtion web page

## Clone the Repository

```bash
git clone https://github.com/noHup-cc/fungtion.git
cd fungtion
```

## Install

Option 1: create the full Conda environment from `environment.yml` (recommended)

```bash
conda env create -f environment.yml
conda activate fungtion

# optional: install Fungtion as a local editable package
pip install -e .
```

Option 2: create the Conda environment manually

```bash
conda create -n fungtion -c conda-forge python=3.10 r-base=4.4 r-e1071 r-caret r-optparse
conda activate fungtion

# install the Python package in editable mode
pip install -e .
```

Developer tooling:

```bash
pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
```

## PyTorch Compatibility

The default installation will install `torch` automatically.

If your system has specific CPU/GPU or CUDA driver requirements, you may need to reinstall a compatible PyTorch build manually after installation. For example:

```bash
# CPU only
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu

# Example: CUDA 12.6
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu126
```

Please choose the PyTorch build that matches your local hardware and driver setup:
- https://pytorch.org/get-started/locally/

## Example Run

Example FASTA:

- `data/examples/example.fasta`

## Download ESM-1b Weights

Before prediction, you can download the pretrained ESM-1b weights through a
separate setup step. This downloads the same ESM-1b model files that Fungtion
would otherwise fetch automatically through `fair-esm`:

```bash
fungtion setup-models
```

By default, the downloaded files are stored at:

```text
~/.cache/fungtion/models/esm1b_t33_650M_UR50S.pt
~/.cache/fungtion/models/esm1b_t33_650M_UR50S-contact-regression.pt
```

You can also choose a custom directory:

```bash
fungtion setup-models --model-dir /path/to/models
```

If the weights already exist locally, the setup step will skip downloading by
default. To force a fresh download and overwrite the existing local copy, use:

```bash
fungtion setup-models --force
```

Simple:

```bash
fungtion \
  --fasta data/examples/example.fasta \
  --output outputs/example_prediction.csv \
  --device auto \
  --skip-visualization
```

With HTML report:

```bash
fungtion \
  --fasta data/examples/example.fasta \
  --output outputs/example_prediction.csv \
  --device auto \
  --analysis-dir outputs/example_analysis \
  --html-output outputs/example_prediction.html \
  --html-assets-dir outputs/example_prediction_assets
```

With GPU:

```bash
fungtion \
  --fasta data/examples/example.fasta \
  --output outputs/example_prediction.csv \
  --device cuda \
  --skip-visualization
```

## Note

If the setup-downloaded weights exist in the default Fungtion cache directory,
the prediction command will use them automatically.

If you pass `--pretrain`, Fungtion will use that explicit local path in
preference to the default setup location.

If you provide `--pretrain`, the matching
`esm1b_t33_650M_UR50S-contact-regression.pt` file should be present alongside
the main weights file so `fair-esm` can load the local model correctly.

You can also download the model files manually to a local path and run
Fungtion with `--pretrain /path/to/esm1b_t33_650M_UR50S.pt`.

```bash
fungtion \
  --fasta data/examples/example.fasta \
  --output outputs/example_prediction.csv \
  --pretrain /path/to/esm1b_t33_650M_UR50S.pt \
  --device auto \
  --skip-visualization
```

Official ESM-1b weights:
- https://dl.fbaipublicfiles.com/fair-esm/models/esm1b_t33_650M_UR50S.pt
- https://dl.fbaipublicfiles.com/fair-esm/regression/esm1b_t33_650M_UR50S-contact-regression.pt

## Example Run Output

The HTML example above generates:

- `example_prediction.csv`: prediction results
- `example_analysis/`: network and tree intermediate outputs
- `example_prediction.html`: HTML report
- `example_prediction_assets/`: HTML report assets and per-sequence visualization pages

## Example Run Output CSV Columns

- `header`: FASTA header
- `score`: prediction score
- `decision`: `yes` or `no`
- `type`: `Exp.` or `Pred.`
- `type_link`: external link for `Exp.` entries when available

## Notes

- If an input sequence is identical to a reference positive sequence, it is marked as `Exp.` and its score is shown as `1`.
- Other sequences are marked as `Pred.` and scored by the R SVM models.
- The HTML report supports search, sorting, pagination, column toggling, export, help popovers, and visualization links.
- The ESM-1b network page supports clicking non-query nodes to open UniProt or NCBI Protein pages.
- Before committing code changes, run `pre-commit run --all-files` to apply Ruff fixes/formatting and basic whitespace checks.

## More Parameters On Run

- `--fasta`: input FASTA file
- `--output`: output CSV file for prediction results
- `--pretrain`: optional local path to pretrained ESM-1b weights
- `--device`: device for ESM-1b feature extraction; choose from `auto`, `cpu`, or `cuda`
- `--analysis-dir`: output directory for network and tree files
- `--html-output`: output HTML report path
- `--html-assets-dir`: output directory for HTML assets and per-sequence visualization pages
- `--skip-visualization`: skip network and tree generation
- `--keep-temp`: keep intermediate temporary files

## Data

**`data/`**

- `Fungtion_Independent_Dataset/`: full independent test dataset used in the paper
- `Fungtion_Training_Dataset/`: full training dataset used in the paper
- `examples/`: example FASTA files for demonstration and example runs

**`src/fungtion/reference_data/`**

- `FungalEffector_positive.fasta`: experimentally validated fungal effector proteins
- `FungalEffector_positive_esm_uniref50.csv`: ESM-1b features of the experimentally validated fungal effector proteins
- `FungalEffector_positive_similarity_matrix/`: precomputed reference similarity matrices used for network and relationship tree visualization

## Citation

If you use this project, please cite:

```bibtex
@article{li2024fungtion,
  title={Fungtion: A Server for Predicting and Visualizing Fungal Effector Proteins},
  author={Li, Jiahui and Ren, Jinzheng and Dai, Wei and Stubenrauch, Christopher and Finn, Robert D. and Wang, Jiawei},
  journal={Journal of Molecular Biology},
  volume={436},
  number={17},
  pages={168613},
  year={2024},
  doi={10.1016/j.jmb.2024.168613}
}
```
