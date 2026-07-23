#!/usr/bin/env python3
"""
PGxBD Step 02: Compute allele frequencies from 1000G VCFs.

Fixes applied vs original implementation:
  - CYP3A5*3 (rs776746): allele orientation corrected to REF (minus strand)
  - G6PD (chrX): sex-aware counting (males hemizygous = 1 allele, females diploid = 2)
  - SAS_excl_BEB: independent South Asian comparison (SAS minus 86 BEB samples)
  - All positions from dbSNP chrpos_prev_assm (authoritative GRCh37 source)

Inputs:
  data/raw/1000g/vcfs/         - 23 pharmacogene region VCFs (GRCh37)
  data/raw/1000g/panel.txt     - 1000G integrated sample panel with pop/super_pop/gender
  data/raw/coordinates/snp_positions_from_dbsnp.csv - 29 key variants with GRCh37 positions

Outputs:
  data/processed/allele_frequencies/key_variant_frequencies.csv
  data/processed/allele_frequencies/corrected_frequencies.csv
  data/processed/allele_frequencies/beb_all_variants.csv
"""

import os
import sys
import json
import math
import pysam
import pandas as pd
import numpy as np
from collections import defaultdict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VCF_DIR = os.path.join(BASE_DIR, "data", "raw", "1000g", "vcfs")
PANEL_FILE = os.path.join(BASE_DIR, "data", "raw", "1000g", "panel.txt")
SNP_POS_FILE = os.path.join(BASE_DIR, "data", "raw", "coordinates", "snp_positions_from_dbsnp.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed", "allele_frequencies")

# Populations to compute
SUPER_POPS = ["BEB", "SAS", "SAS_EXCL_BEB", "EUR", "EAS", "AFR", "AMR"]

# Allele orientation: which 1000G allele (REF or ALT) represents the PGx variant.
# Determined from strand orientation and PharmVar/PyPGx definitions.
# Most PGx alleles = ALT. Exceptions:
#   rs776746 (CYP3A5*3): REF (CYP3A5 is minus strand; C=*3, T=*1)
#   rs6025  (F5 Leiden): REF (F5 is minus strand; T=Leiden, C=wild-type)
PGX_ALLELE_ORIENTATION = {
    "rs3892097":  "ALT",   # CYP2D6*4
    "rs1065852":  "ALT",   # CYP2D6*10
    "rs4244285":  "ALT",   # CYP2C19*2
    "rs4986893":  "ALT",   # CYP2C19*3
    "rs12248560": "ALT",   # CYP2C19*17
    "rs1799853":  "ALT",   # CYP2C9*2
    "rs1057910":  "ALT",   # CYP2C9*3
    "rs776746":   "REF",   # CYP3A5*3  (FIXED: minus strand, C=*3)
    "rs2242480":  "ALT",   # CYP3A4*1G (FIXED label: was *22)
    "rs35599367": "ALT",   # CYP3A4*22 (NEW: true *22)
    "rs3745274":  "ALT",   # CYP2B6*6
    "rs28399499": "ALT",   # CYP2B6*4
    "rs2108622":  "ALT",   # CYP4F2*3
    "rs9923231":  "ALT",   # VKORC1 -1639G>A
    "rs9934438":  "ALT",   # VKORC1 1542G>C
    "rs7294":     "ALT",   # VKORC1 2255C>T
    "rs1801133":  "ALT",   # MTHFR C677T
    "rs1801131":  "ALT",   # MTHFR A1298C
    "rs1800462":  "ALT",   # TPMT*2
    "rs1800460":  "ALT",   # TPMT*3A
    "rs1142345":  "ALT",   # TPMT*3C
    "rs2306283":  "ALT",   # SLCO1B1*1B
    "rs4149056":  "ALT",   # SLCO1B1*5
    "rs6025":     "REF",   # F5 Leiden (minus strand, T=Leiden)
    "rs1050828":  "ALT",   # G6PD A- (chrX)
    "rs1050829":  "ALT",   # G6PD Mediterranean (chrX)
    "rs1801265":  "ALT",   # DPYD C29R (FIXED label: was *2A)
    "rs3918290":  "ALT",   # DPYD *2A (NEW: true *2A, splice defect)
    "rs67376798": "ALT",   # DPYD c.2846A>T
}

# Star allele / function labels (corrected)
PGX_VARIANT_LABELS = {
    "rs3892097":  ("CYP2D6", "*4", "no function"),
    "rs1065852":  ("CYP2D6", "*10", "decreased function"),
    "rs4244285":  ("CYP2C19", "*2", "no function"),
    "rs4986893":  ("CYP2C19", "*3", "no function"),
    "rs12248560": ("CYP2C19", "*17", "increased function"),
    "rs1799853":  ("CYP2C9", "*2", "decreased function"),
    "rs1057910":  ("CYP2C9", "*3", "no function"),
    "rs776746":   ("CYP3A5", "*3", "no function"),
    "rs2242480":  ("CYP3A4", "*1G", "decreased function"),
    "rs35599367": ("CYP3A4", "*22", "decreased function"),
    "rs3745274":  ("CYP2B6", "*6", "decreased function"),
    "rs28399499": ("CYP2B6", "*4", "no function"),
    "rs2108622":  ("CYP4F2", "*3", "decreased function"),
    "rs9923231":  ("VKORC1", "-1639G>A", "sensitivity"),
    "rs9934438":  ("VKORC1", "1542G>C", "sensitivity"),
    "rs7294":     ("VKORC1", "2255C>T", "sensitivity"),
    "rs1801133":  ("MTHFR", "C677T", "decreased function"),
    "rs1801131":  ("MTHFR", "A1298C", "decreased function"),
    "rs1800462":  ("TPMT", "*2", "no function"),
    "rs1800460":  ("TPMT", "*3A", "no function"),
    "rs1142345":  ("TPMT", "*3C", "no function"),
    "rs2306283":  ("SLCO1B1", "*1B", "decreased function"),
    "rs4149056":  ("SLCO1B1", "*5", "decreased function"),
    "rs6025":     ("F5", "Leiden", "thrombophilia"),
    "rs1050828":  ("G6PD", "A-", "decreased function"),
    "rs1050829":  ("G6PD", "Mediterranean", "no function"),
    "rs1801265":  ("DPYD", "C29R", "decreased function"),
    "rs3918290":  ("DPYD", "*2A", "no function"),
    "rs67376798": ("DPYD", "c.2846A>T", "decreased function"),
}

# Variants not in 1000G phase 3 (document but skip)
MISSING_VARIANTS = {"rs5030862", "rs74601277", "rs116855232"}


def load_panel():
    """Load 1000G panel and build population → sample mappings."""
    pop_map = {}       # sample → population code
    super_pop_map = {} # sample → super population code
    sex_map = {}       # sample → 'male'/'female'

    with open(PANEL_FILE) as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 4:
                continue
            sample, pop, super_pop, gender = parts[0], parts[1], parts[2], parts[3]
            pop_map[sample] = pop
            super_pop_map[sample] = super_pop
            sex_map[sample] = gender

    # Build population sample sets
    pop_samples = {
        "BEB": [s for s in pop_map if pop_map[s] == "BEB"],
        "SAS": [s for s in super_pop_map if super_pop_map[s] == "SAS"],
        "EUR": [s for s in super_pop_map if super_pop_map[s] == "EUR"],
        "EAS": [s for s in super_pop_map if super_pop_map[s] == "EAS"],
        "AFR": [s for s in super_pop_map if super_pop_map[s] == "AFR"],
        "AMR": [s for s in super_pop_map if super_pop_map[s] == "AMR"],
    }
    # Independent SAS comparison: SAS minus BEB
    beb_set = set(pop_samples["BEB"])
    pop_samples["SAS_EXCL_BEB"] = [s for s in pop_samples["SAS"] if s not in beb_set]

    return pop_samples, sex_map


def load_snp_positions():
    """Load GRCh37 positions for key variants from dbSNP."""
    df = pd.read_csv(SNP_POS_FILE)
    positions = {}
    for _, row in df.iterrows():
        rsid = row["rsid"]
        if rsid in MISSING_VARIANTS:
            continue
        # chrpos_prev_assm format: "7:99270539"
        parts = str(row["chrpos_grch37"]).split(":")
        chrom = parts[0]
        pos = int(parts[1])
        positions[rsid] = (chrom, pos)
    return positions


def compute_frequency(rec, samples, sex_map, is_chrX):
    """
    Compute allele frequency for a VCF record.

    For autosomes: standard diploid counting (2 alleles per sample).
    For chrX: sex-aware counting (males = 1 allele, females = 2 alleles).

    Returns: (alt_af, ref_af, hom_ref, het, hom_alt, total_alleles, alt_count)
    """
    hom_ref = 0
    het = 0
    hom_alt = 0
    alt_count = 0
    total_alleles = 0

    for s in samples:
        gt = rec.samples[s]["GT"]
        alleles = [a for a in gt if a is not None]

        if len(alleles) == 0:
            continue

        if is_chrX and len(alleles) == 1:
            # Hemizygous male: 1 allele
            total_alleles += 1
            if alleles[0] == 1:
                alt_count += 1
                hom_alt += 1  # hemizygous alt
            else:
                hom_ref += 1  # hemizygous ref
        elif len(alleles) == 2:
            total_alleles += 2
            for a in alleles:
                if a == 1:
                    alt_count += 1
            if alleles == [0, 0]:
                hom_ref += 1
            elif sorted(alleles) == [0, 1]:
                het += 1
            elif alleles == [1, 1]:
                hom_alt += 1
        elif len(alleles) == 1 and not is_chrX:
            # Treat as diploid (shouldn't happen for autosomes in 1000G)
            total_alleles += 2
            if alleles[0] == 1:
                alt_count += 2
                hom_alt += 1
            else:
                hom_ref += 1

    alt_af = alt_count / total_alleles if total_alleles > 0 else 0.0
    ref_af = 1.0 - alt_af

    return alt_af, ref_af, hom_ref, het, hom_alt, total_alleles, alt_count


def find_variant_in_vcfs(chrom, pos, vcf_files):
    """Find a VCF record at the given chrom:pos across multiple VCF files."""
    for vcf_path in vcf_files:
        try:
            vcf = pysam.VariantFile(vcf_path)
        except Exception:
            continue
        for rec in vcf:
            if rec.chrom == chrom and rec.pos == pos:
                vcf.close()
                return rec, vcf_path
        vcf.close()
    return None, None


def wilson_ci(alt_count, total, z=1.96):
    """Wilson score 95% confidence interval for a proportion."""
    if total == 0:
        return "N/A"
    p = alt_count / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    lo = max(0.0, centre - spread)
    hi = min(1.0, centre + spread)
    return f"{lo:.4f}-{hi:.4f}"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading 1000G panel...")
    pop_samples, sex_map = load_panel()
    for pop, samples in pop_samples.items():
        print(f"  {pop}: {len(samples)} samples")

    print("\nLoading SNP positions from dbSNP...")
    snp_positions = load_snp_positions()
    print(f"  {len(snp_positions)} variants with GRCh37 positions")

    # Collect all VCF files
    vcf_files = []
    if os.path.isdir(VCF_DIR):
        vcf_files = sorted([
            os.path.join(VCF_DIR, f)
            for f in os.listdir(VCF_DIR)
            if f.endswith(".vcf") or f.endswith(".vcf.gz")
        ])
    else:
        # Fallback: use the old data/1000g_beb/ directory
        old_dir = os.path.join(BASE_DIR, "data", "1000g_beb")
        vcf_files = sorted([
            os.path.join(old_dir, f)
            for f in os.listdir(old_dir)
            if f.endswith(".vcf") or f.endswith(".vcf.gz")
        ])
    print(f"\nFound {len(vcf_files)} VCF files")

    # Compute frequencies for each key variant
    results = []
    all_beb_variants = []

    for rsid, (chrom, pos) in sorted(snp_positions.items(), key=lambda x: (x[1][0], x[1][1])):
        if rsid not in PGX_VARIANT_LABELS:
            print(f"  SKIP {rsid}: no label defined")
            continue

        gene, star_allele, function = PGX_VARIANT_LABELS[rsid]
        orientation = PGX_ALLELE_ORIENTATION.get(rsid, "ALT")
        is_chrX = (chrom == "X" or chrom == "chrX")

        print(f"\n  {rsid} ({gene} {star_allele}) at {chrom}:{pos} [{'chrX-aware' if is_chrX else 'diploid'}]")

        # Find the variant in VCFs
        # Need to re-open VCF to get the record (find_variant_in_vcfs closes the file)
        rec = None
        vcf_path_used = None
        for vcf_path in vcf_files:
            try:
                vcf = pysam.VariantFile(vcf_path)
            except Exception:
                continue
            for r in vcf:
                if r.chrom == chrom and r.pos == pos:
                    rec = r
                    vcf_path_used = vcf_path
                    break
            if rec is not None:
                # Don't close yet - we need to iterate samples
                break
            vcf.close()

        if rec is None:
            print(f"    NOT FOUND in any VCF — recording as AF=0.0 for all populations")
            for pop in SUPER_POPS:
                results.append({
                    "rsid": rsid, "gene": gene, "star_allele": star_allele,
                    "function": function, "chrom": chrom, "pos": pos,
                    "ref_allele": "N/A", "alt_allele": "N/A",
                    "pgx_allele": "N/A", "pgx_allele_orientation": orientation,
                    "population": pop, "sample_size": len(pop_samples.get(pop, [])),
                    "pgx_allele_frequency": 0.0,
                    "hom_ref": 0, "het": 0, "hom_alt": 0,
                    "total_alleles": 0, "alt_count": 0,
                    "confidence_interval": "N/A",
                    "notes": f"Variant not present in 1000G phase 3 VCFs",
                })
            continue

        ref_allele = rec.ref
        alt_allele = rec.alts[0] if rec.alts else "N/A"
        pgx_allele = ref_allele if orientation == "REF" else alt_allele

        print(f"    REF={ref_allele} ALT={alt_allele} PGx allele={pgx_allele} ({orientation})")

        # Compute frequency for each population
        for pop in SUPER_POPS:
            samples = [s for s in pop_samples.get(pop, []) if s in rec.samples]
            if not samples:
                continue

            alt_af, ref_af, hom_ref, het, hom_alt, total_alleles, alt_count = compute_frequency(
                rec, samples, sex_map, is_chrX
            )

            # Apply orientation
            pgx_af = ref_af if orientation == "REF" else alt_af

            # For REF orientation, swap hom_ref/hom_alt
            if orientation == "REF":
                hom_ref, hom_alt = hom_alt, hom_ref

            ci = wilson_ci(alt_count if orientation == "ALT" else (total_alleles - alt_count), total_alleles)

            results.append({
                "rsid": rsid, "gene": gene, "star_allele": star_allele,
                "function": function, "chrom": chrom, "pos": pos,
                "ref_allele": ref_allele, "alt_allele": alt_allele,
                "pgx_allele": pgx_allele, "pgx_allele_orientation": orientation,
                "population": pop, "sample_size": len(samples),
                "pgx_allele_frequency": round(pgx_af, 6),
                "hom_ref": hom_ref, "het": het, "hom_alt": hom_alt,
                "total_alleles": total_alleles,
                "alt_count": alt_count if orientation == "ALT" else (total_alleles - alt_count),
                "confidence_interval": ci,
                "notes": f"PGx allele: {pgx_allele} (orientation: {orientation})",
            })

            if pop == "BEB":
                print(f"    {pop}: AF={pgx_af:.6f} (hr={hom_ref} h={het} ha={hom_alt} N={len(samples)})")

        # Also collect ALL BEB variants from this VCF (for the full variant table)
        vcf_full = pysam.VariantFile(vcf_path_used)
        beb_samples = [s for s in pop_samples["BEB"] if s in vcf_full.header.samples]
        for r in vcf_full:
            if r.chrom == chrom:
                alt_af_beb, ref_af_beb, hr, h, ha, tot, ac = compute_frequency(
                    r, beb_samples, sex_map, is_chrX
                )
                if tot > 0:
                    all_beb_variants.append({
                        "chrom": r.chrom, "pos": r.pos,
                        "ref": r.ref, "alt": r.alts[0] if r.alts else ".",
                        "beb_af": round(alt_af_beb, 6),
                        "hom_ref": hr, "het": h, "hom_alt": ha,
                        "total_alleles": tot,
                    })
        vcf_full.close()

        if vcf_path_used:
            vcf = pysam.VariantFile(vcf_path_used)
            vcf.close()

    # Save results
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(OUTPUT_DIR, "corrected_frequencies.csv"), index=False)
    print(f"\nSaved corrected_frequencies.csv: {len(df)} rows")

    # Also save a key-variant-only summary
    key_df = df[df["population"].isin(["BEB", "SAS_EXCL_BEB", "EUR", "EAS", "AFR"])]
    key_df.to_csv(os.path.join(OUTPUT_DIR, "key_variant_frequencies.csv"), index=False)
    print(f"Saved key_variant_frequencies.csv: {len(key_df)} rows")

    # Save all BEB variants
    all_df = pd.DataFrame(all_beb_variants)
    all_df = all_df.drop_duplicates(subset=["chrom", "pos"])
    all_df.to_csv(os.path.join(OUTPUT_DIR, "beb_all_variants.csv"), index=False)
    print(f"Saved beb_all_variants.csv: {len(all_df)} unique variants")

    # Print summary of key changes
    print("\n" + "=" * 70)
    print("KEY FREQUENCY CHANGES (BEB):")
    print("=" * 70)
    for rsid in ["rs776746", "rs1050828", "rs1050829", "rs35599367", "rs3918290"]:
        rows = df[(df["rsid"] == rsid) & (df["population"] == "BEB")]
        if len(rows) > 0:
            r = rows.iloc[0]
            print(f"  {rsid} ({r['gene']} {r['star_allele']}): AF={r['pgx_allele_frequency']}")

    return df


if __name__ == "__main__":
    main()
