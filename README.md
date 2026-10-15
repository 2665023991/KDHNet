<div align="center">
<h1>KDHNet</h1>
<h3>A Knowledge-Driven Hybrid Network for Limited-Calibration SSVEP Decoding</h3>

Zhentao He<sup>1</sup>, Ziwei Wang<sup>1 :email:</sup>, and Dongrui Wu<sup>1 :email:</sup>

<sup>1</sup> School of Artificial Intelligence and Automation, Huazhong University of Science and Technology

(<sup>:email:</sup>) Corresponding Authors
</div>

> This repository contains the implementation of our paper: **KDHNet: A Knowledge-Driven Hybrid Network for Limited-Calibration SSVEP Decoding**, as well as the eight baselines on three public SSVEP datasets. It includes the within-subject analysis-window and calibration-ratio experiments and the inter-subject experiments. Datasets, saved experimental results, pretrained weights, plotting scripts, and manuscript files are not included.

## Overview

KDHNet combines a TD-RCA knowledge front-end with an SSVEPformer decoder. After filter-bank preprocessing, TDCA extracts class-discriminative projections and TRCA enhances trial-reproducible components. Sub-band weighting combines the responses before classification. The TDCA projection is estimated analytically and frozen; the TRCA filters, sub-band weights, and neural decoder are optimized during training. In the inter-subject setting, target-guided least-squares transformation aligns source trials using one labeled target trial per class.

<div align="center">
<img width="1345" height="714" alt="image" src="https://github.com/user-attachments/assets/51636cd3-feb7-47f5-ac75-a15f0ba1e425" />
</div>

## Contents

| Item | Included |
|---|---|
| Proposed method | KDHNet, named `TD-RCA+SSVEPformer` in the code and generated results |
| Traditional baselines | FBCCA, TRCA, TDCA |
| Deep baselines | EEGNet, CCNN, FBtCNN, SSVEPNet, SSVEPformer |
| Dataset I | Nakanishi2015 / 12-target: 10 subjects, 12 classes, 8 channels |
| Dataset II | Benchmark: 35 subjects, 40 classes, 9 selected posterior channels |
| Dataset III | BETA: 70 subjects, 40 classes, 9 selected posterior channels |
| Evaluation | Accuracy and information transfer rate (ITR) |

## Installation

The source experiment environment used Python 3.10.14 and PyTorch 2.3.1. Dependency versions in
`requirements.txt` were collected from that environment. Python 3.10 is recommended.

```bash
cd KDHNet-code
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows instead: .venv\Scripts\activate
pip install -r requirements.txt
```

Install the PyTorch build appropriate for your GPU and CUDA installation if necessary. CPU execution
is available with `--gpu cpu`, although the full experiment suite is substantially slower on CPU.

## Data

Download the original MATLAB subject files and organize them as follows:

```text
KDHNet-code/
└── datasets/
    ├── benchmark12/S1.mat ... S10.mat
    ├── benchmark40/S1.mat ... S35.mat
    └── BETA/S1.mat ... S70.mat
```

- Dataset I: [Nakanishi2015 12-target dataset](https://github.com/mnakanishi/12JFPM_SSVEP).
- Datasets II and III: Benchmark and BETA, available from the
  [Tsinghua BCI dataset download page](http://bci.med.tsinghua.edu.cn/download.html).

The loader expects the original `eeg` array for Dataset I, the `data` array for Benchmark, and the
original BETA MATLAB structure. Files are named `S<subject>.mat`, with subject indices starting at 1.
Do not flatten or reorder the source files. Configure `paths.datasets` in a YAML file, or pass
`--data-root /path/to/datasets` to `run.py`. No EMG/EOG artifact library is required for this paper.

## Running one experiment

The following runs KDHNet on subject 1, fold 0 of Dataset I at a 1.0 s window and a training ratio of 0.2:

```bash
python run.py --config etc/benchmark12.yaml --name kdhnet_b12_s1_f0 \
    --gpu 0 --subjects 1 --folds 0 --methods KDHNet
```

To compare KDHNet with all eight baselines for the same subject and fold, omit `--methods`:

```bash
python run.py --config etc/benchmark12.yaml --name comparison_b12_s1_f0 \
    --gpu 0 --subjects 1 --folds 0
```

Select one or more methods with `--methods KDHNet TRCA TDCA SSVEPformer`. Other useful options are
`--window`, `--ratio`, `--data-root`, and `--output`. `--dry-run` saves the effective configuration
without starting training. `--epochs 1` is useful for checking the setup, but changes the training
protocol and must not be used to reproduce paper numbers.

For inter-subject KDHNet evaluation on target subject 1:

```bash
python run.py --config etc/paper/loso_benchmark12.yaml --name loso_b12_t1 \
    --gpu 0 --targets 1 --folds 0 --methods KDHNet
```

Prepared base configurations are `etc/benchmark12.yaml`, `etc/benchmark40.yaml`, and `etc/beta.yaml`.
Their model settings are derived from the corresponding experiment snapshots, rather than from the
old generic development configuration.

## Main comparisons

```bash
# Print all 27 experiment commands without training.
python scripts/run_main_comparison.py --dry-run

# All datasets and both protocols, sequentially on GPU 0.
python scripts/run_main_comparison.py --gpu 0

# Only Dataset II within-subject experiments.
python scripts/run_main_comparison.py --dataset benchmark40 --split intra --gpu 0

# Summarize newly generated experimental results.
python scripts/summarize.py --results results --out results/summary
```

The suite contains 22 within-subject settings, three main inter-subject settings, and two separate
inter-subject traditional-baseline settings:

| Dataset | Analysis windows in seconds | Ratios at 1.0 s |
|---|---|---|
| I | 0.4, 0.6, 0.8, 1.0, 1.2 at r = 0.2 | 0.2, 0.4, 0.6, 0.8 |
| II | 0.4, 0.6, 0.8, 1.0, 1.2 at r = 0.5 | 0.35, 0.5, 0.7, 0.85 |
| III | 0.4, 0.6, 0.8, 1.0, 1.2 at r = 0.5 | 0.5, 0.75 |

Shared 1.0 s settings run only once. Each command includes all subjects and configured folds;
27 commands therefore represent many individual model trainings. For multiple GPUs, use the printed
commands to divide distinct settings between devices. Keep each setting's subject ordering and seed
fixed when comparing methods.

The Dataset II and III inter-subject TRCA/TDCA runs use separate saved baseline protocols, with LST
disabled, rather than training those template baselines on the KDHNet-aligned source/target mixture.
Their configurations are `loso_benchmark40_traditional.yaml` and `loso_beta_traditional.yaml`.
Do not combine the same method's records from incompatible protocols.

## Evaluation and outputs

- Training and test indices are generated by the original dataset-specific split routines in
  `Data/core.py`. Inter-subject LST calibration and target holdout selection are in `Data/transfer.py`.
- KDHNet uses `tdca_init_mode: analytical_frozen`, `trca_init_mode: analytical_trainable`, and
  `fb_init_mode: analytical_trainable`. The TDCA component count is 3 within subject and 1 across subjects.
- The release explicitly selects final-epoch scoring for deep models. KDHNet also reports final-epoch
  accuracy. Historical best-test-epoch scoring is not the default release protocol.
- Test loaders retain all samples, including incomplete final batches (`drop_last=False`).
- Accuracy is stored as a fraction in raw output files; the summary converts it to percent.
  Fold accuracies are averaged within each subject before computing the mean and standard deviation
  across subjects. ITR uses the configured decision window and decision overhead.

`run.py` writes the effective YAML to `etc/generated/`. Every run writes an independent folder below
`results/<dataset>/<split>/downstream_only/standard/` containing a configuration snapshot and
`results/experiment_results.csv`. The summary script writes `subjects.csv` and `summary.csv`; subject and
fold counts are included so incomplete experiments can be identified. It rejects duplicate records.

The supplied configurations preserve the paper settings, but independent reruns can differ numerically
with library versions, GPU hardware, or different subject chunking. This release covers the main
comparisons; plotting, decoder-replacement figures, interpretability analyses, and archived ablation
searches are outside its scope.

## Code structure

```text
KDHNet-code/
├── README.md
├── requirements.txt
├── main.py                       # execute one YAML configuration
├── run.py                        # overrides, portable paths, and run launcher
├── etc/
│   ├── benchmark12.yaml
│   ├── benchmark40.yaml
│   ├── beta.yaml
│   └── paper/                    # 27 main-comparison configurations and job index
├── Data/                         # loading, trial splits, filtering, and LST alignment
├── Models/Classification/
│   ├── HZTKD/Hztlayer.py          # TDCA/TRCA front-end and sub-band weighting
│   ├── DeepL/SSVEPformer.py       # the deep decoder used by KDHNet
│   └── KNoW/                     # analytical baselines
├── Trainers/Classification/
│   ├── hybrid.py                 # KDHNet model construction and training
│   └── core.py                   # method dispatch and baseline evaluation
├── Support/                      # experiment loop, configuration, metrics, utilities
└── scripts/
    ├── run_main_comparison.py
    └── summarize.py
```

Some classifier helper modules remain because the original dispatch imports them. They are not
additional methods in the main comparison. The release excludes all augmentation and diffusion model
packages and removes their dispatch branches. Model equations, parameter initialization, analytical
estimators, preprocessing, and classification training were retained from the experiment code.

`SOURCE_MANIFEST.json` records hashes of the original server source files. The release adjusts the
entry points, makes dataset paths portable, removes unused experiment branches, and moves the unchanged
ITR function into `Support/metrics.py`. Configuration defaults explicitly set the paper initialization
modes and final-epoch reporting. No dataset, existing experimental result, manuscript, credential,
checkpoint, or plotting artifact is part of the code archive.

## Citation and acknowledgments

Please cite the accompanying paper, *KDHNet: A Knowledge-Driven Hybrid Network for Limited-Calibration
SSVEP Decoding*, by Zhentao He, Ziwei Wang, and Dongrui Wu. Publication metadata will be added when available.
The repository retains the authors' implementations of KDHNet and the baseline implementations used
in the experiments. Please also acknowledge the original datasets and baseline methods.
