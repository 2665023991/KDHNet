"""Write a portable run configuration and launch the paper experiment."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parent
PAPER_METHODS = ['FBCCA', 'TRCA', 'TDCA', 'EEGNet', 'CCNN', 'FBtCNN', 'SSVEPNet', 'SSVEPformer', 'KDHNet']


def ids(value):
    return [int(x) for x in value.split(',') if x.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='etc/benchmark12.yaml')
    parser.add_argument('--name', default='reproduction')
    parser.add_argument('--gpu', default='0', help='CUDA device index, or cpu')
    parser.add_argument('--subjects', type=ids)
    parser.add_argument('--targets', type=ids)
    parser.add_argument('--folds', type=ids)
    parser.add_argument('--methods', nargs='+', choices=PAPER_METHODS)
    parser.add_argument('--window', type=float)
    parser.add_argument('--ratio', type=float)
    parser.add_argument('--epochs', type=int, help='override for a smoke run; changes the paper protocol')
    parser.add_argument('--data-root', type=Path, help='parent of benchmark12, benchmark40 and BETA folders')
    parser.add_argument('--output', type=Path, default=Path('results'))
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    os.chdir(ROOT)
    path = Path(args.config)
    cfg = yaml.safe_load(path.read_text(encoding='utf-8'))
    exp = cfg['experiment']
    exp['run_name'] = args.name
    exp['device'] = 'cpu' if args.gpu == 'cpu' else int(args.gpu)
    for argument, key in [(args.subjects, 'subject_ids'), (args.targets, 'target_subject_ids'), (args.folds, 'fold_ids')]:
        if argument is not None:
            exp[key] = argument
    if args.methods:
        exp['methods'] = {
            'traditional': [x for x in args.methods if x in {'FBCCA', 'TRCA', 'TDCA'}],
            'deep': [x for x in args.methods if x not in {'FBCCA', 'TRCA', 'TDCA', 'KDHNet'}],
            'hybrid': {'knowledge': ['TD-RCA'] if 'KDHNet' in args.methods else [],
                       'deep': ['SSVEPformer'] if 'KDHNet' in args.methods else []},
            'augmentation': [], 'diffusion': [], 'extra': [],
        }
    if args.window is not None:
        cfg['dataset']['window_sec'] = args.window
    if args.ratio is not None:
        cfg['dataset']['train_ratio'] = args.ratio
    if args.epochs is not None:
        cfg['training']['epochs'] = args.epochs
        for model in cfg.get('classification_models', {}).values():
            if isinstance(model, dict):
                model['epochs'] = args.epochs
    if args.data_root is not None:
        base = args.data_root.resolve()
        cfg['paths']['datasets'] = {'benchmark12': str(base / 'benchmark12'),
                                    'benchmark40': str(base / 'benchmark40'), 'beta': str(base / 'BETA')}
    cfg['paths']['outputs']['root'] = str(args.output.resolve())
    folder = ROOT / 'etc/generated'
    folder.mkdir(exist_ok=True)
    safe_name = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in args.name)
    output = folder / f'{safe_name}.yaml'
    output.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding='utf-8')
    print(f'Configuration: {output}', flush=True)
    if not args.dry_run:
        subprocess.run([sys.executable, str(ROOT / 'main.py'), '--f', str(output)], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
