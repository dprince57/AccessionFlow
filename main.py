#!/usr/bin/env python3

import subprocess
import pandas as pd
import os
import numpy as np
import scanpy as sc
import sys
import shutil
import logging
import logging.handlers
import getpass
import yaml
from pathlib import Path

if shutil.which("prefetch") is None:
    sys.exit("prefetch not found on PATH; install sra-tools")

USER = getpass.getuser()
BASE_DIR = None
log = logging.getLogger("accessionflow")

CONFIG_SEARCH = [ os.environ.get("ACCESSIONFLOW_CONFIG"), "/etc/accessionflow/config.yaml",
        str(Path.home() / ".config" / "accessionflow" / "config.yaml"),]

def load_config():
    for p in CONFIG_SEARCH:
        if p and Path(p).is_file():
            with open(p) as f:
                cfg = yaml.safe_load(f) or {}
            for key in ("base_dir", "log_dir"):
                if key not in cfg:
                    sys.exit(f"config {p} is missing required key: {key}")
            return cfg
    sys.exit("no config found; set ACCESSIONFLOW_CONFIG or create /etc/accessionflow/config.yaml")

def init():
    global BASE_DIR
    os.umask(0o002)
    cfg = load_config()
    BASE_DIR = Path(cfg["base_dir"]) / USER
    log_dir = Path(cfg["log_dir"])
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "accessionflow.log"

    with open(log_file, "a") as f:
        f.write("=" * 37 + "\n")
        f.write(f"user: {USER}\n")

    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s [%(levelname)s] [{USER}] %(message)s",
        handlers=[logging.handlers.WatchedFileHandler(log_file), logging.StreamHandler()],
    )

def run_step(sra, step, cmd):
    log.info(f"sra {sra}: {step} started")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        log.error(f"sra {sra}: failed at {step} (exit {e.returncode})")
        return False
    log.info(f"sra {sra}: {step} ok")
    return True

def sra_process(sra_raw):
    sra_base_dir = BASE_DIR / sra_raw
    fastq_dir = sra_base_dir / "fastq"

    sra_base_dir.mkdir(parents=True, exist_ok=True)
    fastq_dir.mkdir(parents=True, exist_ok=True)

    prefetch = ["prefetch", sra_raw, "--output-directory", str(sra_base_dir)]

    if not run_step(sra_raw, "prefetch", prefetch):
        shutil.rmtree(sra_base_dir, ignore_errors=True)
        return

    log.info(f"sra {sra_raw}: pipeline complete") 

def open_and_process_file(file):
    with open(file, 'r') as f:
        for sra_raw in f:
            sra_raw = sra_raw.strip()
            if not sra_raw or sra_raw.startswith("#"):
                continue
            sra_process(sra_raw)


def main():
    init()
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            open_and_process_file(filename)
    else:
        print(f"usage: {sys.argv[0]} filename.txt")

if __name__ == "__main__":
    main()
