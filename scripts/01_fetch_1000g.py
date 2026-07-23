#!/usr/bin/env python3
"""
PGxBD Step 01: Download 1000 Genomes pharmacogene region VCFs.

Downloads pharmacogene regions for all 2504 1000G samples via tabix from
the EBI FTP server. Only pharmacogene intervals are fetched (not whole
chromosomes) to minimize download size.

Inputs:
  data/raw/coordinates/pharmacogene_regions_grch37_noprefix.bed

Outputs:
  data/raw/1000g/vcfs/         - 23 pharmacogene region VCFs (GRCh37)
  data/raw/1000g/panel.txt     - 1000G integrated sample panel
  data/raw/1000g/beb_samples.txt - 86 BEB sample IDs
"""

import os
import subprocess
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BED_FILE = os.path.join(BASE_DIR, "data", "raw", "coordinates", "pharmacogene_regions_grch37_noprefix.bed")
VCF_DIR = os.path.join(BASE_DIR, "data", "raw", "1000g", "vcfs")
PANEL_DIR = os.path.join(BASE_DIR, "data", "raw", "1000g")

# 1000G FTP base URL
FTP_BASE = "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502"

# Chromosome VCF filename mapping (autosomes use v1b, chrX uses v1c)
def get_vcf_filename(chrom):
    if chrom == "X":
        return "ALL.chrX.phase3_shapeit2_mvncall_integrated_v1c.20130502.genotypes.vcf.gz"
    else:
        return f"ALL.chr{chrom}.phase3_shapeit2_mvncall_integrated_v1b.20130502.genotypes.vcf.gz"


def download_panel():
    """Download the 1000G sample panel."""
    panel_url = f"{FTP_BASE}/integrated_call_samples_v3.20130502.ALL.panel"
    panel_path = os.path.join(PANEL_DIR, "panel.txt")
    if os.path.exists(panel_path):
        print(f"  Panel already exists: {panel_path}")
        return
    print(f"  Downloading panel...")
    urllib.request.urlretrieve(panel_url, panel_path)

    # Extract BEB samples
    beb_path = os.path.join(PANEL_DIR, "beb_samples.txt")
    with open(panel_path) as f:
        next(f)  # skip header
        beb_samples = [line.strip().split("\t")[0] for line in f if "\tBEB\t" in line]
    with open(beb_path, "w") as f:
        f.write("\n".join(beb_samples) + "\n")
    print(f"  Extracted {len(beb_samples)} BEB samples")


def download_regions():
    """Download pharmacogene regions via tabix."""
    os.makedirs(VCF_DIR, exist_ok=True)

    with open(BED_FILE) as f:
        regions = []
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 4:
                continue
            chrom, start, end, name = parts[0], parts[1], parts[2], parts[3]
            regions.append((chrom, int(start), int(end), name))

    print(f"  {len(regions)} regions to download")

    for chrom, start, end, name in regions:
        # Create a safe filename
        safe_name = name.replace(" ", "_").replace("/", "_")
        # Adjust start to 0-based for tabix (BED is 0-based, tabix is 1-based)
        tabix_start = start + 1
        vcf_filename = f"beb_{safe_name}_chr{chrom}_{start}_{end}.vcf"
        vcf_path = os.path.join(VCF_DIR, vcf_filename)

        if os.path.exists(vcf_path) and os.path.getsize(vcf_path) > 0:
            print(f"  SKIP {safe_name} (already downloaded)")
            continue

        remote_vcf = get_vcf_filename(chrom)
        url = f"{FTP_BASE}/{remote_vcf}"
        region = f"{chrom}:{tabix_start}-{end}"

        print(f"  Downloading {safe_name} ({chrom}:{tabix_start}-{end})...")
        cmd = ["tabix", "-h", url, region]
        try:
            with open(vcf_path, "w") as out:
                subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, timeout=120)
            size = os.path.getsize(vcf_path)
            print(f"    Saved {vcf_filename} ({size:,} bytes)")
        except subprocess.TimeoutExpired:
            print(f"    TIMEOUT for {safe_name}")
        except Exception as e:
            print(f"    ERROR for {safe_name}: {e}")


def main():
    print("PGxBD Step 01: Download 1000G pharmacogene VCFs")
    os.makedirs(PANEL_DIR, exist_ok=True)
    os.makedirs(VCF_DIR, exist_ok=True)

    print("\n  Downloading sample panel...")
    download_panel()

    print("\n  Downloading pharmacogene regions...")
    download_regions()

    print("\n  Done. VCF files in", VCF_DIR)


if __name__ == "__main__":
    main()
