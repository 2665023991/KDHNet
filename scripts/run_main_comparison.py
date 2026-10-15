"""Run the saved main comparison settings sequentially on one GPU."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', choices=['all', 'benchmark12', 'benchmark40', 'beta'], default='all')
    parser.add_argument('--split', choices=['all', 'intra', 'loso'], default='all')
    parser.add_argument('--gpu', default='0')
    parser.add_argument('--data-root', type=Path)
    parser.add_argument('--dry-run', action='store_true', help='print commands without launching experiments')
    args = parser.parse_args()
    jobs = json.loads((ROOT / 'etc/paper/jobs.json').read_text())
    for job in jobs:
        if args.dataset != 'all' and job['dataset'] != args.dataset:
            continue
        if args.split != 'all' and job['split'] != args.split:
            continue
        command = [sys.executable, str(ROOT / 'run.py'), '--config', job['config'],
                   '--name', Path(job['config']).stem, '--gpu', args.gpu]
        if args.data_root:
            command.extend(['--data-root', str(args.data_root.resolve())])
        print(subprocess.list2cmdline(command), flush=True)
        if not args.dry_run:
            subprocess.run(command, cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
