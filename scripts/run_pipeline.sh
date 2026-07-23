#!/usr/bin/env bash
# =============================================================================
# run_pipeline.sh
# =============================================================================
# Orchestrates the full PGxBD pipeline: fetch raw data -> compute frequencies
# -> fetch reference -> build database -> compute phenotypes -> validate.
#
# Usage:
#   bash scripts/run_pipeline.sh            # run all steps
#   bash scripts/run_pipeline.sh --skip-fetch  # skip data download (use staged VCFs)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# ---- configuration ---------------------------------------------------------
SKIP_FETCH=false
SKIP_DOWNLOAD_REF=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-fetch)        SKIP_FETCH=true; shift ;;
        --skip-download-ref) SKIP_DOWNLOAD_REF=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "============================================================"
echo "  PGxBD Pipeline"
echo "  Project root: ${PROJECT_ROOT}"
echo "  $(date)"
echo "============================================================"

# ---- Step 01: Fetch 1000 Genomes VCFs --------------------------------------
if [[ "${SKIP_FETCH}" == "false" ]]; then
    echo ""
    echo ">>> [01/06] Fetching 1000 Genomes VCFs ..."
    python scripts/01_fetch_1000g.py
else
    echo ""
    echo ">>> [01/06] Skipped (--skip-fetch)"
fi

# ---- Step 02: Compute allele frequencies -----------------------------------
echo ""
echo ">>> [02/06] Computing allele frequencies ..."
python scripts/02_compute_frequencies.py

# ---- Step 03: Fetch reference data -----------------------------------------
echo ""
echo ">>> [03/06] Fetching / verifying reference data ..."
if [[ "${SKIP_DOWNLOAD_REF}" == "true" ]]; then
    python scripts/03_fetch_reference.py
else
    python scripts/03_fetch_reference.py --download
fi

# ---- Step 04: Build SQLite database ----------------------------------------
echo ""
echo ">>> [04/06] Building SQLite database ..."
python scripts/04_build_database.py

# ---- Step 05: Compute phenotype frequencies --------------------------------
echo ""
echo ">>> [05/06] Computing phenotype frequencies ..."
python scripts/05_compute_phenotypes.py

# ---- Step 06: Validate -----------------------------------------------------
echo ""
echo ">>> [06/06] Running validation checks ..."
python scripts/06_validate.py

echo ""
echo "============================================================"
echo "  Pipeline complete."
echo "  Database: ${PROJECT_ROOT}/db/pgxbd.db"
echo "  Frequencies: ${PROJECT_ROOT}/data/processed/allele_frequencies/"
echo "  Phenotypes: ${PROJECT_ROOT}/data/processed/phenotypes/"
echo "  $(date)"
echo "============================================================"
