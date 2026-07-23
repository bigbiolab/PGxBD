#!/bin/bash
# Bootstrap the WSL Python environment needed by the WSL pipeline stages
# (02_fetch_g6pd_wsl.py, 04_fetch_stretch_wsl.py - both need pysam for
# remote-tabix access to 1000 Genomes VCFs over HTTPS).
#
# Ubuntu 24.04's system Python is "externally managed" (PEP 668) and ships
# without pip or venv, and python3-venv/python3-pip require apt+sudo. This
# bootstraps pip into user space via get-pip.py with --break-system-packages,
# which needs no sudo. Safe to re-run (idempotent: skips steps already done).
set -e

if python3 -m pip --version >/dev/null 2>&1; then
    echo "[setup] pip already present: $(python3 -m pip --version)"
else
    echo "[setup] bootstrapping pip (no sudo required)..."
    curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
    python3 /tmp/get-pip.py --user --break-system-packages
fi

echo "[setup] installing pysam + pandas..."
python3 -m pip install --user --break-system-packages pysam pandas

python3 -c "import pysam, pandas; print(f'[setup] OK: pysam {pysam.__version__}, pandas {pandas.__version__}')"
