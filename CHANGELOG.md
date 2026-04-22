# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - yyyy-mm-dd

### Added

- Initial release of Fungtion CLI tool
- ESM-1b transformer-based feature extraction for protein sequences
- 5-model SVM ensemble prediction via R (e1071)
- Exact-match flagging against experimentally validated effectors
- Interactive HTML report with network and phylogenetic tree visualizations
- `--skip-visualization` flag for lightweight CSV-only runs
- `--keep-temp` flag to retain intermediate embedding files
- `--pretrain` option to use locally cached ESM-1b weights
- `--device` option for CPU/CUDA selection
- Added setup for linters, formatters, and pre-commit hooks
