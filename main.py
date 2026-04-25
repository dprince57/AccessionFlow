#!/usr/bin/env python3

import subprocess
import pandas as pd
import os
import numpy as np
import scanpy as sc
import sys
from pathlib import Path

base_dir = Path.home() / "sra"

def sra_process(sra_raw):
    sra_base_dir = base_dir / sra_raw
    fastq_dir = sra_base_dir / "fastq"

    sra_base_dir.mkdir(parents=True, exist_ok=True)
    fastq_dir.mkdir(parents=True, exist_ok=True)
    prefetch = ["prefetch", sra_raw, "--output-directory", str(base_dir / sra_raw)]

    print(f"[INFO] Running prefetch for {sra_raw}")
    subprocess.run(prefetch, check = True)
    

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
