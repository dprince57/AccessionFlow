#!/usr/bin/env python3

import subprocess
import pandas as pd
import os
import numpy as np
import scanpy as sc
import sys
import shutil
from pathlib import Path

if shutil.which("prefetch") is None:
    sys.exit("prefetch not found on PATH; install sra-tools")

base_dir = Path.home() / "sra"

def sra_process(sra_raw):
    sra_base_dir = base_dir / sra_raw
    fastq_dir = sra_base_dir / "fastq"

    sra_base_dir.mkdir(parents=True, exist_ok=True)
    fastq_dir.mkdir(parents=True, exist_ok=True)
    
    prefetch = ["prefetch", sra_raw, "--output-directory", str(base_dir / sra_raw)]
    print(f"[INFO] Running prefetch for {sra_raw}")

    try:
        subprocess.run(prefetch, check = True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] prefetch failed for {sra_raw} (exit {e.returncode}), skipping to next sra")
        shutil.rmtree(sra_base_dir, ignore_errors=True)

def open_and_process_file(file):
    f = open(file, 'r')
    for sra_raw in f:
        sra_process(sra_raw.strip())

def main():
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            open_and_process_file(filename)
    else:
        print(f"usage: {sys.argv[0]} filename.txt")

if __name__ == "__main__":
    main()
