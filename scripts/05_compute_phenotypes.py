#!/usr/bin/env python3
"""
PGxBD Step 05: Compute phenotype frequencies via Hardy-Weinberg equilibrium.

Fixes applied vs original implementation:
  - CYP2C19: includes *2/*17 and *3/*17 compound heterozygotes as Intermediate
    Metabolizer (per CPIC). Previous code omitted these, causing sums < 1.0.
  - CYP2D6: uses 3-allele HWE with *4 (no function, score 0.0) AND *10
    (decreased function, score 0.25), plus *1+*2 (normal, score 1.0).
    Previous code used only *4.
  - CYP3A5: phenotype frequencies recomputed with corrected *3 allele
    orientation (REF, not ALT).

Phenotype assignments follow CPIC/PyPGx activity score systems.

Inputs:
  data/processed/allele_frequencies/corrected_frequencies.csv

Outputs:
  data/processed/phenotypes/phenotype_frequencies.csv
"""

import os
import sys
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREQ_FILE = os.path.join(BASE_DIR, "data", "processed", "allele_frequencies", "corrected_frequencies.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed", "phenotypes")

# Populations to compute phenotypes for
POPS = ["BEB", "SAS", "SAS_EXCL_BEB", "EUR", "EAS", "AFR"]


def get_allele_freq(df, rsid, pop):
    """Get PGx allele frequency for a variant in a population."""
    rows = df[(df["rsid"] == rsid) & (df["population"] == pop)]
    if len(rows) == 0:
        return 0.0
    return rows.iloc[0]["pgx_allele_frequency"]


def compute_cyp2c19_phenotypes(df, pop):
    """
    CYP2C19 phenotype frequencies via 4-allele HWE.
    Alleles: *1 (normal), *2 (no function), *3 (no function), *17 (increased)

    CPIC phenotype mapping:
      *1/*1              → Normal Metabolizer
      *1/*17             → Rapid Metabolizer
      *17/*17            → Ultrarapid Metabolizer
      *1/*2, *1/*3       → Intermediate Metabolizer
      *2/*17, *3/*17     → Intermediate Metabolizer  (WAS MISSING)
      *2/*2, *2/*3, *3/*3 → Poor Metabolizer
    """
    f2 = get_allele_freq(df, "rs4244285", pop)   # *2
    f3 = get_allele_freq(df, "rs4986893", pop)   # *3
    f17 = get_allele_freq(df, "rs12248560", pop) # *17
    f1 = 1.0 - f2 - f3 - f17                      # *1 (residual)

    # HWE genotype frequencies
    normal      = f1**2                                    # *1/*1
    rapid       = 2 * f1 * f17                             # *1/*17
    ultrarapid  = f17**2                                   # *17/*17
    intermediate = (2 * f1 * f2 +                          # *1/*2
                     2 * f1 * f3 +                          # *1/*3
                     2 * f2 * f17 +                         # *2/*17 (FIXED)
                     2 * f3 * f17)                          # *3/*17 (FIXED)
    poor        = f2**2 + 2 * f2 * f3 + f3**2              # *2/*2, *2/*3, *3/*3

    total = normal + rapid + ultrarapid + intermediate + poor
    assert abs(total - 1.0) < 0.01, f"CYP2C19 {pop} sum={total:.4f} != 1.0"

    return {
        "Normal Metabolizer": normal,
        "Rapid Metabolizer": rapid,
        "Ultrarapid Metabolizer": ultrarapid,
        "Intermediate Metabolizer": intermediate,
        "Poor Metabolizer": poor,
    }


def compute_cyp2d6_phenotypes(df, pop):
    """
    CYP2D6 phenotype frequencies via 3-allele HWE with activity scores.
    Alleles: *1+*2 (normal, score 1.0), *4 (no function, score 0.0),
             *10 (decreased, score 0.25)

    CPIC activity score thresholds (PyPGx equation table):
      0 <= score < 0.25    → Poor Metabolizer
      0.25 <= score < 1.25 → Intermediate Metabolizer
      1.25 <= score < 2.5  → Normal Metabolizer
      score >= 2.5         → Ultrarapid Metabolizer

    Diplotype → score → phenotype:
      N/N    (1.0+1.0=2.0)  → Normal
      N/*10  (1.0+0.25=1.25) → Normal  (>= 1.25)
      N/*4   (1.0+0.0=1.0)   → Intermediate
      *10/*10 (0.25+0.25=0.5) → Intermediate
      *4/*10  (0.0+0.25=0.25) → Intermediate  (>= 0.25)
      *4/*4   (0.0+0.0=0.0)   → Poor
    """
    f4 = get_allele_freq(df, "rs3892097", pop)    # *4
    f10 = get_allele_freq(df, "rs1065852", pop)   # *10
    f_n = 1.0 - f4 - f10                           # *1 + *2 (normal, combined)

    # HWE diplotype frequencies
    nn     = f_n ** 2           # N/N: score 2.0 → Normal
    n_4    = 2 * f_n * f4       # N/*4: score 1.0 → Intermediate
    n_10   = 2 * f_n * f10      # N/*10: score 1.25 → Normal
    f4_f4  = f4 ** 2            # *4/*4: score 0.0 → Poor
    f4_10  = 2 * f4 * f10       # *4/*10: score 0.25 → Intermediate
    f10_10 = f10 ** 2           # *10/*10: score 0.5 → Intermediate

    normal       = nn + n_10
    intermediate = n_4 + f4_10 + f10_10
    poor         = f4_f4

    total = normal + intermediate + poor
    assert abs(total - 1.0) < 0.01, f"CYP2D6 {pop} sum={total:.4f} != 1.0"

    return {
        "Normal Metabolizer": normal,
        "Intermediate Metabolizer": intermediate,
        "Poor Metabolizer": poor,
    }


def compute_cyp2c9_phenotypes(df, pop):
    """
    CYP2C9 phenotype frequencies via 3-allele HWE.
    Alleles: *1 (normal), *2 (decreased), *3 (no function)

    CPIC phenotype mapping:
      *1/*1              → Normal Metabolizer
      *1/*2, *1/*3       → Intermediate Metabolizer
      *2/*2, *2/*3       → Intermediate Metabolizer
      *3/*3              → Poor Metabolizer
    """
    f2 = get_allele_freq(df, "rs1799853", pop)   # *2
    f3 = get_allele_freq(df, "rs1057910", pop)   # *3
    f1 = 1.0 - f2 - f3

    normal       = f1 ** 2
    intermediate = 2 * f1 * f2 + 2 * f1 * f3 + f2 ** 2 + 2 * f2 * f3
    poor         = f3 ** 2

    total = normal + intermediate + poor
    assert abs(total - 1.0) < 0.01, f"CYP2C9 {pop} sum={total:.4f} != 1.0"

    return {
        "Normal Metabolizer": normal,
        "Intermediate Metabolizer": intermediate,
        "Poor Metabolizer": poor,
    }


def compute_cyp3a5_phenotypes(df, pop):
    """
    CYP3A5 phenotype frequencies via 2-allele HWE.
    Alleles: *1 (normal, expresser), *3 (no function, non-expresser)

    CPIC phenotype mapping:
      *1/*1 → Normal Metabolizer (expresser)
      *1/*3 → Intermediate Metabolizer (expresser)
      *3/*3 → Poor Metabolizer (non-expresser)

    Note: *3 frequency now uses corrected REF orientation.
    """
    f3 = get_allele_freq(df, "rs776746", pop)  # *3 (corrected: REF)
    f1 = 1.0 - f3

    normal       = f1 ** 2       # *1/*1
    intermediate = 2 * f1 * f3   # *1/*3
    poor         = f3 ** 2       # *3/*3

    total = normal + intermediate + poor
    assert abs(total - 1.0) < 0.01, f"CYP3A5 {pop} sum={total:.4f} != 1.0"

    return {
        "Normal Metabolizer": normal,
        "Intermediate Metabolizer": intermediate,
        "Poor Metabolizer": poor,
    }


def compute_tpmt_phenotypes(df, pop):
    """
    TPMT phenotype frequencies via 4-allele HWE.
    Alleles: *1 (normal), *2 (no function), *3A (no function), *3C (no function)

    CPIC phenotype mapping:
      *1/*1                    → Normal Metabolizer
      *1/*2, *1/*3A, *1/*3C    → Intermediate Metabolizer
      *2/*2, *2/*3A, *2/*3C,
        *3A/*3A, *3A/*3C, *3C/*3C → Poor Metabolizer
    """
    f2 = get_allele_freq(df, "rs1800462", pop)    # *2
    f3a = get_allele_freq(df, "rs1800460", pop)   # *3A
    f3c = get_allele_freq(df, "rs1142345", pop)   # *3C
    f1 = 1.0 - f2 - f3a - f3c

    # All no-function alleles combined
    f_nf = f2 + f3a + f3c

    normal       = f1 ** 2
    intermediate = 2 * f1 * f_nf
    poor         = f_nf ** 2

    total = normal + intermediate + poor
    assert abs(total - 1.0) < 0.01, f"TPMT {pop} sum={total:.4f} != 1.0"

    return {
        "Normal Metabolizer": normal,
        "Intermediate Metabolizer": intermediate,
        "Poor Metabolizer": poor,
    }


def compute_slco1b1_phenotypes(df, pop):
    """
    SLCO1B1 phenotype frequencies via 3-allele HWE.
    Alleles: *1A (normal), *1B (decreased), *5 (low function)

    CPIC phenotype mapping:
      *1A/*1A, *1A/*1B        → Normal Function
      *1B/*1B, *1A/*5, *1B/*5 → Decreased Function
      *5/*5                   → Low Function
    """
    f1b = get_allele_freq(df, "rs2306283", pop)   # *1B
    f5 = get_allele_freq(df, "rs4149056", pop)    # *5
    f1a = 1.0 - f1b - f5                           # *1A

    normal    = f1a ** 2 + 2 * f1a * f1b           # *1A/*1A + *1A/*1B
    decreased = f1b ** 2 + 2 * f1a * f5 + 2 * f1b * f5  # *1B/*1B + *1A/*5 + *1B/*5
    low       = f5 ** 2                             # *5/*5

    total = normal + decreased + low
    assert abs(total - 1.0) < 0.01, f"SLCO1B1 {pop} sum={total:.4f} != 1.0"

    return {
        "Normal Function": normal,
        "Decreased Function": decreased,
        "Low Function": low,
    }


def compute_vkorc1_phenotypes(df, pop):
    """
    VKORC1 sensitivity phenotypes from -1639G>A (rs9923231).
    GG = normal sensitivity, GA = intermediate, AA = high sensitivity.
    """
    f_a = get_allele_freq(df, "rs9923231", pop)  # A allele (sensitivity)
    f_g = 1.0 - f_a

    gg = f_g ** 2       # normal sensitivity
    ga = 2 * f_g * f_a  # intermediate sensitivity
    aa = f_a ** 2       # high sensitivity

    total = gg + ga + aa
    assert abs(total - 1.0) < 0.01, f"VKORC1 {pop} sum={total:.4f} != 1.0"

    return {
        "GG (normal sensitivity)": gg,
        "GA (intermediate sensitivity)": ga,
        "AA (high sensitivity)": aa,
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading corrected frequencies...")
    df = pd.read_csv(FREQ_FILE)
    print(f"  {len(df)} rows, {df['rsid'].nunique()} variants")

    # Gene → phenotype computation function mapping
    gene_functions = {
        "CYP2C19": compute_cyp2c19_phenotypes,
        "CYP2D6": compute_cyp2d6_phenotypes,
        "CYP2C9": compute_cyp2c9_phenotypes,
        "CYP3A5": compute_cyp3a5_phenotypes,
        "TPMT": compute_tpmt_phenotypes,
        "SLCO1B1": compute_slco1b1_phenotypes,
        "VKORC1": compute_vkorc1_phenotypes,
    }

    # Method descriptions for each gene
    gene_methods = {
        "CYP2C19": "HWE from *2, *3, *17 frequencies (includes *2/*17, *3/*17 compound het)",
        "CYP2D6": "HWE from *4, *10 frequencies with CPIC activity score (3-allele)",
        "CYP2C9": "HWE from *2, *3 frequencies",
        "CYP3A5": "HWE from *3 frequency (corrected REF orientation)",
        "TPMT": "HWE from *2, *3A, *3C frequencies",
        "SLCO1B1": "HWE from *1B, *5 frequencies",
        "VKORC1": "HWE from -1639G>A (rs9923231) frequency",
    }

    results = []

    for gene, compute_fn in gene_functions.items():
        print(f"\nComputing {gene} phenotypes...")
        for pop in POPS:
            try:
                phenotypes = compute_fn(df, pop)
                for pheno, freq in phenotypes.items():
                    results.append({
                        "gene_id": gene,
                        "phenotype": pheno,
                        "population": pop,
                        "frequency": round(freq, 4),
                        "study_id": f"1000G_{pop}",
                        "calculation_method": gene_methods[gene],
                    })
                # Verify sum
                total = sum(phenotypes.values())
                status = "OK" if abs(total - 1.0) < 0.001 else "FAIL"
                print(f"  {pop:15}: sum={total:.4f} [{status}]")
            except AssertionError as e:
                print(f"  {pop:15}: ERROR - {e}")
            except Exception as e:
                print(f"  {pop:15}: ERROR - {e}")

    # Save
    result_df = pd.DataFrame(results)
    output_file = os.path.join(OUTPUT_DIR, "phenotype_frequencies.csv")
    result_df.to_csv(output_file, index=False)
    print(f"\nSaved {output_file}: {len(result_df)} rows")

    # Print BEB summary
    print("\n" + "=" * 70)
    print("BEB PHENOTYPE SUMMARY (corrected):")
    print("=" * 70)
    beb = result_df[result_df["population"] == "BEB"]
    for gene in gene_functions:
        gene_beb = beb[beb["gene_id"] == gene]
        if len(gene_beb) > 0:
            print(f"\n  {gene}:")
            for _, r in gene_beb.iterrows():
                print(f"    {r['phenotype']:40s}: {r['frequency']:.4f}")

    return result_df


if __name__ == "__main__":
    main()
