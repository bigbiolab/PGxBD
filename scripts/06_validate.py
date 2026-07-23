#!/usr/bin/env python3
"""
PGxBD Step 06: Validation checks for the database.

Validates:
  1. All phenotype frequency sums = 1.0 ± 0.001 per gene per population
  2. CYP3A5*3 EUR AF > 0.90 (sanity check on allele orientation fix)
  3. G6PD BEB AF matches VCF (chrX-aware, should be 0.0)
  4. No NULL allele_id in allele_frequencies
  5. All star_alleles have defining_variants populated
  6. CYP3A4 rs2242480 labeled as *1G (not *22)
  7. DPYD rs1801265 labeled as C29R (not *2A)
  8. rs35599367 (true CYP3A4*22) present in database
  9. rs3918290 (true DPYD*2A) present in database
  10. SAS_EXCL_BEB population present and independent (N=403)
  11. CYP2C19 Intermediate includes *2/*17 class (sum > old value)
  12. CYP2D6 Intermediate includes *10 (sum > old value)

Exit code 0 = all pass, 1 = any fail.
"""

import os
import sys
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "pgxbd.db")


def run_validation():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        status = "PASS" if condition else "FAIL"
        if condition:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

    print("=" * 70)
    print("PGxBD DATABASE VALIDATION")
    print("=" * 70)

    # 1. Phenotype frequency sums
    print("\n1. Phenotype frequency sums (should be 1.0 ± 0.001):")
    rows = c.execute("""
        SELECT gene_id, population, SUM(frequency) as total
        FROM phenotype_frequencies
        GROUP BY gene_id, population
        ORDER BY gene_id, population
    """).fetchall()
    for gene, pop, total in rows:
        check(f"{gene} {pop} sum", abs(total - 1.0) < 0.001, f"sum={total:.4f}")

    # 2. CYP3A5*3 EUR AF > 0.90
    print("\n2. CYP3A5*3 allele orientation (EUR should be > 0.90):")
    r = c.execute("SELECT allele_frequency FROM allele_frequencies WHERE variant_rsid='rs776746' AND population='EUR'").fetchone()
    check("CYP3A5*3 EUR AF > 0.90", r and r[0] > 0.90, f"AF={r[0]:.4f}" if r else "NOT FOUND")

    # 3. G6PD BEB AF = 0.0
    print("\n3. G6PD chrX frequencies (BEB should be 0.0):")
    for rsid in ["rs1050828", "rs1050829"]:
        r = c.execute(f"SELECT allele_frequency FROM allele_frequencies WHERE variant_rsid='{rsid}' AND population='BEB'").fetchone()
        check(f"G6PD {rsid} BEB AF = 0.0", r and r[0] == 0.0, f"AF={r[0]:.6f}" if r else "NOT FOUND")

    # 4. No NULL allele_id
    print("\n4. allele_id linkage:")
    null_count = c.execute("SELECT COUNT(*) FROM allele_frequencies WHERE allele_id IS NULL").fetchone()[0]
    total = c.execute("SELECT COUNT(*) FROM allele_frequencies").fetchone()[0]
    check("No NULL allele_id", null_count == 0, f"{total - null_count}/{total} linked")

    # 5. defining_variants populated
    print("\n5. star_alleles defining_variants:")
    empty_count = c.execute("SELECT COUNT(*) FROM star_alleles WHERE defining_variants = '' OR defining_variants IS NULL").fetchone()[0]
    total_sa = c.execute("SELECT COUNT(*) FROM star_alleles").fetchone()[0]
    check("All defining_variants populated", empty_count == 0, f"{total_sa - empty_count}/{total_sa} populated")

    # 6. CYP3A4 rs2242480 labeled as *1G
    print("\n6. CYP3A4 label corrections:")
    r = c.execute("SELECT allele_id FROM allele_frequencies WHERE variant_rsid='rs2242480' AND population='BEB'").fetchone()
    check("rs2242480 allele_id = CYP3A4_1G", r and "1G" in r[0], f"allele_id={r[0]}" if r else "NOT FOUND")

    # 7. DPYD rs1801265 labeled as C29R
    r = c.execute("SELECT allele_id FROM allele_frequencies WHERE variant_rsid='rs1801265' AND population='BEB'").fetchone()
    check("rs1801265 allele_id = CYP3A4_C29R (not *2A)", r and "2A" not in r[0], f"allele_id={r[0]}" if r else "NOT FOUND")

    # 8. rs35599367 present
    r = c.execute("SELECT COUNT(*) FROM allele_frequencies WHERE variant_rsid='rs35599367'").fetchone()
    check("rs35599367 (true CYP3A4*22) present", r[0] > 0, f"{r[0]} records")

    # 9. rs3918290 present
    r = c.execute("SELECT COUNT(*) FROM allele_frequencies WHERE variant_rsid='rs3918290'").fetchone()
    check("rs3918290 (true DPYD*2A) present", r[0] > 0, f"{r[0]} records")

    # 10. SAS_EXCL_BEB present
    print("\n7. SAS_EXCL_BEB independent population:")
    r = c.execute("SELECT DISTINCT sample_size FROM allele_frequencies WHERE population='SAS_EXCL_BEB'").fetchone()
    check("SAS_EXCL_BEB present with N=403", r and r[0] == 403, f"N={r[0]}" if r else "NOT FOUND")

    # 11. CYP2C19 Intermediate > 0.377 (old value without *2/*17)
    print("\n8. CYP2C19 HWE includes *2/*17 compound heterozygote:")
    r = c.execute("SELECT frequency FROM phenotype_frequencies WHERE gene_id='CYP2C19' AND population='BEB' AND phenotype='Intermediate Metabolizer'").fetchone()
    check("CYP2C19 BEB Intermediate > 0.377", r and r[0] > 0.377, f"freq={r[0]:.4f}" if r else "NOT FOUND")

    # 12. CYP2D6 Intermediate > 0.214 (old value without *10)
    print("\n9. CYP2D6 HWE includes *10 allele:")
    r = c.execute("SELECT frequency FROM phenotype_frequencies WHERE gene_id='CYP2D6' AND population='BEB' AND phenotype='Intermediate Metabolizer'").fetchone()
    check("CYP2D6 BEB Intermediate > 0.214", r and r[0] > 0.214, f"freq={r[0]:.4f}" if r else "NOT FOUND")

    # 13. CYP3A5 phenotype with corrected orientation
    print("\n10. CYP3A5 phenotypes with corrected *3 orientation:")
    r = c.execute("SELECT frequency FROM phenotype_frequencies WHERE gene_id='CYP3A5' AND population='BEB' AND phenotype='Poor Metabolizer'").fetchone()
    check("CYP3A5 BEB Poor > 0.35 (was ~0.13 with flipped allele)", r and r[0] > 0.35, f"freq={r[0]:.4f}" if r else "NOT FOUND")

    # Summary
    print("\n" + "=" * 70)
    print(f"VALIDATION SUMMARY: {passed} passed, {failed} failed")
    print("=" * 70)

    conn.close()
    return failed == 0


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
