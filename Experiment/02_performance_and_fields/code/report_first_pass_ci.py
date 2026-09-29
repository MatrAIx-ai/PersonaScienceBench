#!/usr/bin/env python3
"""Delegate to the existing single-trial analysis; outputs remain under RUN/analysis."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[3]
    runpy.run_path(str(root/'scripts/report_first_pass_ci.py'), run_name='__main__')
