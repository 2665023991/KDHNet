"""Configuration entry point retained for the original experiment imports."""
import argparse
from pathlib import Path

import yaml

parser = argparse.ArgumentParser(description='Run a KDHNet experiment configuration.')
parser.add_argument('--f', default='etc/benchmark12.yaml', help='YAML configuration path')
options = parser.parse_args()
with Path(options.f).open(encoding='utf-8') as handle:
    config = yaml.safe_load(handle)


def get_global_conf():
    return config
