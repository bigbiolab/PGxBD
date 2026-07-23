#!/usr/bin/env python3
"""
03_fetch_reference.py
=====================
Download and stage pharmacogenomic reference data from PharmGKB, CPIC,
and PyPGx for the PGxBD database build.

Outputs are written to data/raw/reference/{pharmgkb,cpic,pharmvar}/.

Usage:
    python scripts/03_fetch_reference.py [--download]

Without --download the script only verifies that the staged reference
files already exist (useful when the data has been pre-staged).
"""

import argparse
import os
import sys
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REF_DIR = PROJECT_ROOT / "data" / "raw" / "reference"

PHARMGKB_DIR = REF_DIR / "pharmgkb"
CPIC_DIR = REF_DIR / "cpic"
PHARMVAR_DIR = REF_DIR / "pharmvar"

# ---------------------------------------------------------------------------
# Reference data sources (all public, trusted scientific databases)
# ---------------------------------------------------------------------------
PHARMGKB_URLS = {
    "genes.tsv": "https://api.pharmgkb.org/v1/download/file/data/genes.zip",
    "variants.tsv": "https://api.pharmgkb.org/v1/download/file/data/variants.zip",
    "clinical_ann.tsv": "https://api.pharmgkb.org/v1/download/file/data/clinicalAnnotations.zip",
    "drug_labels.tsv": "https://api.pharmgkb.org/v1/download/file/data/drugLabels.zip",
}

CPIC_URLS = {
    # CPIC guideline tables (public GitHub raw)
    "gene_phenotype_groups.csv": (
        "https://raw.githubusercontent.com/cpic-genome/cpic-data/master/"
        "data/gene_phenotype_groups.csv"
    ),
}

# PyPGx star-allele defining-variant table is bundled in the pypgx package;
# we extract it at runtime rather than downloading.
PYPGX_VARIANT_TABLE = "pypgx"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ensure_dirs():
    for d in (PHARMGKB_DIR, CPIC_DIR, PHARMVAR_DIR):
        d.mkdir(parents=True, exist_ok=True)


def download(url: str, dest: Path):
    """Download a file with a progress indicator."""
    print(f"  Downloading {url} ...")
    try:
        urllib.request.urlretrieve(url, str(dest))
        print(f"  -> {dest.name} ({dest.stat().st_size:,} bytes)")
    except Exception as exc:  # noqa: BLE001
        print(f"  !! Failed: {exc}", file=sys.stderr)


def extract_pypgx_variant_table():
    """
    Extract the PyPGx star-allele defining-variant table from the installed
    pypgx package and save it as a CSV.
    """
    dest = PHARMVAR_DIR / "pypgx_star_allele_variants.csv"
    if dest.exists():
        print(f"  [skip] {dest.name} already exists")
        return
    try:
        import pandas as pd
        import pypgx
        # The variant table is stored as a CSV inside the package
        pkg_dir = Path(pypgx.__file__).parent
        candidates = list(pkg_dir.rglob("*variant*.csv")) + list(pkg_dir.rglob("*allele*.csv"))
        if candidates:
            import shutil
            shutil.copy2(candidates[0], dest)
            print(f"  -> Copied {candidates[0].name} to {dest.name}")
        else:
            print("  !! Could not locate PyPGx variant table inside package", file=sys.stderr)
    except ImportError:
        print("  !! pypgx not installed; skipping variant table extraction", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        print(f"  !! Error extracting PyPGx table: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download reference data from upstream sources.",
    )
    args = parser.parse_args()

    ensure_dirs()
    print("=== 03_fetch_reference.py ===")

    if not args.download:
        # Verification mode – just check that staged files exist
        print("Verification mode (no --download). Checking staged reference files...")
        all_files = []
        for d in (PHARMGKB_DIR, CPIC_DIR, PHARMVAR_DIR):
            all_files.extend(d.glob("*"))
        if not all_files:
            print("  No reference files found. Run with --download to fetch them.")
            sys.exit(1)
        for f in sorted(all_files):
            print(f"  [ok] {f.relative_to(REF_DIR)} ({f.stat().st_size:,} bytes)")
        print(f"\nTotal: {len(all_files)} reference files staged.")
        return

    # Download mode
    print("\n--- PharmGKB ---")
    for name, url in PHARMGKB_URLS.items():
        dest = PHARMGKB_DIR / name
        if dest.exists():
            print(f"  [skip] {name} already exists")
            continue
        download(url, dest)

    print("\n--- CPIC ---")
    for name, url in CPIC_URLS.items():
        dest = CPIC_DIR / name
        if dest.exists():
            print(f"  [skip] {name} already exists")
            continue
        download(url, dest)

    print("\n--- PyPGx variant table ---")
    extract_pypgx_variant_table()

    print("\nDone. Reference data staged in data/raw/reference/.")


if __name__ == "__main__":
    main()
