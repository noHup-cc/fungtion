import argparse
import os
import tempfile
from analysis_outputs import generate_visual_outputs
from feature_extraction import extract_esm_features
from html_report import generate_html_report
from predict import predict_with_r

def parse_args():
    parser = argparse.ArgumentParser(description="Fungal effector prediction tool.")
    parser.add_argument('--fasta', required=True, help='Input FASTA file')
    parser.add_argument('--output', required=True, help='Output CSV file')
    parser.add_argument('--pretrain', help='Optional local ESM-1b weights path')
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto', help='Device for ESM-1b feature extraction')
    parser.add_argument('--analysis-dir', help='Directory for network and tree outputs')
    parser.add_argument('--html-output', help='Optional HTML report output path')
    parser.add_argument('--html-assets-dir', help='Optional directory for HTML assets and per-sequence pages')
    parser.add_argument('--skip-visualization', action='store_true', help='Skip network and tree generation')
    parser.add_argument('--keep-temp', action='store_true', help='Keep intermediate feature files')
    return parser.parse_args()

def main():
    args = parse_args()
    fasta_path = args.fasta
    output_path = args.output
    pretrained_weights_path = args.pretrain
    device = args.device
    analysis_dir = args.analysis_dir
    html_output = args.html_output
    html_assets_dir = args.html_assets_dir
    skip_visualization = args.skip_visualization
    keep_temp = args.keep_temp

    for path_value in (output_path, analysis_dir, html_output, html_assets_dir):
        if path_value:
            parent_dir = path_value if path_value == analysis_dir or path_value == html_assets_dir else os.path.dirname(path_value)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

    temp_dir = tempfile.mkdtemp()
    feature_csv = os.path.join(temp_dir, 'features.csv')
    header_txt = os.path.join(temp_dir, 'headers.txt')
    manifest_path = None

    extract_esm_features(
        fasta_path,
        feature_csv,
        header_txt,
        pretrained_weights_path=pretrained_weights_path,
        device=device,
    )

    predict_with_r(
        feature_csv,
        header_txt,
        output_path,
        fasta_path=fasta_path,
        reference_fasta=os.path.join(os.path.dirname(__file__), "reference_data", "FungalEffector_positive.fasta"),
    )

    if not skip_visualization:
        if analysis_dir is None:
            output_base, _output_ext = os.path.splitext(output_path)
            analysis_dir = output_base + "_analysis"
        manifest_path = generate_visual_outputs(
            fasta_path=fasta_path,
            feature_csv=feature_csv,
            prediction_csv=output_path,
            analysis_dir=analysis_dir,
            reference_dir=os.path.join(os.path.dirname(__file__), "reference_data"),
        )
        print(f"Visualization manifest saved to {manifest_path}")

    if html_output:
        generate_html_report(
            prediction_csv=output_path,
            output_html=html_output,
            manifest_csv=manifest_path,
            assets_dir=html_assets_dir,
        )
        print(f"HTML report saved to {html_output}")

    if not keep_temp:
        try:
            os.remove(feature_csv)
            os.remove(header_txt)
            os.rmdir(temp_dir)
        except Exception:
            pass
    print(f"Prediction finished. Results saved to {output_path}")

if __name__ == '__main__':
    main()
