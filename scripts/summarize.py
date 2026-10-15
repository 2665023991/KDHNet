"""Average folds within subjects, then report subject-level ACC and ITR."""
import argparse
from pathlib import Path

import pandas as pd
import yaml


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, default=Path('results'))
    parser.add_argument('--out', type=Path, default=Path('results/summary'))
    args = parser.parse_args()
    frames = []
    for path in sorted(args.results.rglob('experiment_results.csv')):
        snapshot = path.parents[1] / 'config/experiment_config_snapshot.yaml'
        if not snapshot.exists():
            raise ValueError(f'Missing configuration snapshot for {path}')
        cfg = yaml.safe_load(snapshot.read_text(encoding='utf-8'))
        frame = pd.read_csv(path)
        frame = frame[(frame.train_view == 'clean') & (frame.test_view == 'clean')].copy()
        frame['dataset'] = cfg['dataset']['active']
        frame['window_sec'] = cfg['dataset']['window_sec']
        frame['train_ratio'] = cfg['dataset']['train_ratio']
        frame['entity'] = frame['target_subject'] if cfg['experiment']['split_mode'] == 'loso' else frame['subject']
        frames.append(frame)
    if not frames:
        raise SystemExit(f'No experiment_results.csv found under {args.results}')
    data = pd.concat(frames, ignore_index=True)
    setting = ['dataset', 'split_mode', 'window_sec', 'train_ratio', 'downstream_method']
    if data.duplicated(setting + ['entity', 'fold']).any():
        raise ValueError('Duplicate subject/fold records: summarize independent reruns separately.')
    subject = data.groupby(setting + ['entity'], as_index=False).agg(
        acc=('acc', 'mean'), itr=('itr', 'mean'), n_folds=('fold', 'nunique'))
    subject['acc'] *= 100
    summary = subject.groupby(setting, as_index=False).agg(
        acc_mean=('acc', 'mean'), acc_std=('acc', 'std'), itr_mean=('itr', 'mean'),
        itr_std=('itr', 'std'), n_subjects=('entity', 'nunique'),
        min_folds=('n_folds', 'min'), max_folds=('n_folds', 'max'))
    args.out.mkdir(parents=True, exist_ok=True)
    subject.to_csv(args.out / 'subjects.csv', index=False)
    summary.to_csv(args.out / 'summary.csv', index=False)
    print(summary.to_string(index=False))
    print('Partial runs are identifiable by n_subjects and min_folds/max_folds; do not treat them as full-paper results.')


if __name__ == '__main__':
    main()
