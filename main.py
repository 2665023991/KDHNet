"""Run one saved configuration from any working directory."""
import os
from pathlib import Path

if __name__ == '__main__':
    os.chdir(Path(__file__).resolve().parent)
    from Support.experiment import run
    run()
