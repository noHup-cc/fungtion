import argparse
import os
import sys
import tempfile

from . import __version__
from ._paths import REFERENCE_DATA_DIR
from .setup_models import download_pretrained_weights, resolve_pretrained_weights_path


def _predict_parser():
    parser = argparse.ArgumentParser(description="Fungal effector prediction tool.")
    parser.add_argument("--fasta", required=True, help="Input FASTA file")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the prefixed output folder will be created",
    )
    parser.add_argument(
        "--prefix",
        required=True,
        help="Naming identifier for the output folder and generated files",
    )
    parser.add_argument("--pretrain", help="Optional local ESM-1b weights path")
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Device for ESM-1b feature extraction",
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML report and bundled assets",
    )
    parser.add_argument(
        "--skip-visualization",
        action="store_true",
        help="Skip network and tree generation",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep intermediate files under the prefixed output folder",
    )
    parser.set_defaults(command="predict")
    return parser


def _setup_models_parser():
    parser = argparse.ArgumentParser(
        prog="fungtion setup-models",
        description="Download the pretrained ESM-1b weights used by Fungtion.",
    )
    parser.add_argument(
        "--model-dir",
        help="Optional directory where the downloaded ESM-1b weights should be stored",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download the ESM-1b weights even if they already exist locally",
    )
    parser.set_defaults(command="setup-models")
    return parser


def parse_args(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    top_level_parser = argparse.ArgumentParser(add_help=False)
    top_level_parser.add_argument(
        "--version", "-v", action="version", version=__version__
    )
    top_level_parser.parse_known_args(argv)
    if argv and argv[0] == "setup-models":
        return _setup_models_parser().parse_args(argv[1:])
    return _predict_parser().parse_args(argv)


def _run_setup_models(args):
    weights_path, downloaded = download_pretrained_weights(
        model_dir=args.model_dir, force=args.force
    )
    if downloaded:
        print(f"Downloaded ESM-1b weights to {weights_path}")
    else:
        print(f"ESM-1b weights already exist at {weights_path}")


def main(argv=None):
    args = parse_args(argv)
    if args.command == "setup-models":
        _run_setup_models(args)
        return

    from .analysis_outputs import generate_visual_outputs
    from .feature_extraction import extract_esm_features
    from .html_report import generate_html_report
    from .predict import predict_with_r

    fasta_path = args.fasta
    output_root = os.path.join(args.output_dir, args.prefix)
    output_csv = os.path.join(output_root, f"{args.prefix}.csv")
    pretrained_weights_path = resolve_pretrained_weights_path(args.pretrain)
    device = args.device
    analysis_dir = os.path.join(output_root, f"{args.prefix}_analysis")
    html_output = os.path.join(output_root, f"{args.prefix}.html")
    html_assets_dir = os.path.join(output_root, f"{args.prefix}_assets")
    html_report = args.html_report
    skip_visualization = args.skip_visualization
    keep_temp = args.keep_temp

    print("Starting Fungtion prediction run")
    print(f"Input FASTA: {fasta_path}")
    print(f"Output directory: {output_root}")
    print(f"Using ESM-1b weights: {pretrained_weights_path}")
    print(f"Feature extraction device: {device}")

    os.makedirs(output_root, exist_ok=True)

    if keep_temp:
        temp_dir = os.path.join(output_root, f"{args.prefix}_temp_folder")
        os.makedirs(temp_dir, exist_ok=True)
    else:
        temp_dir = tempfile.mkdtemp()
    feature_csv = os.path.join(temp_dir, "features.csv")
    header_txt = os.path.join(temp_dir, "headers.txt")
    manifest_path = None

    print("Extracting ESM-1b features...")
    extract_esm_features(
        fasta_path,
        feature_csv,
        header_txt,
        pretrained_weights_path=pretrained_weights_path,
        device=device,
    )
    print(f"ESM-1b features saved to {feature_csv}")

    print("Running fungal effector prediction...")
    predict_with_r(
        feature_csv,
        header_txt,
        output_csv,
        fasta_path=fasta_path,
        reference_fasta=REFERENCE_DATA_DIR / "FungalEffector_positive.fasta",
    )
    print(f"Prediction CSV saved to {output_csv}")

    if not skip_visualization:
        print("Generating network and tree visualizations...")
        manifest_path = generate_visual_outputs(
            fasta_path=fasta_path,
            feature_csv=feature_csv,
            prediction_csv=output_csv,
            analysis_dir=analysis_dir,
            reference_dir=REFERENCE_DATA_DIR,
        )
        print(f"Visualization manifest saved to {manifest_path}")
    else:
        print("Skipping network and tree visualizations")

    if html_report:
        print("Generating HTML report...")
        generate_html_report(
            prediction_csv=output_csv,
            output_html=html_output,
            manifest_csv=manifest_path,
            assets_dir=html_assets_dir,
        )
        print(f"HTML report saved to {html_output}")

    if not keep_temp:
        print("Cleaning up intermediate files...")
        try:
            os.remove(feature_csv)
            os.remove(header_txt)
            os.rmdir(temp_dir)
        except Exception:
            pass
    else:
        print(f"Intermediate files kept in {temp_dir}")
    print(f"Prediction finished. Results saved to {output_csv}")


if __name__ == "__main__":
    main()
