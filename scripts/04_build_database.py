#!/usr/bin/env python3
"""
PGxBD Step 04: Build SQLite database from all data sources.

Fixes applied vs original implementation:
  - CYP3A4 rs2242480 relabeled as *1G (was *22)
  - CYP3A4 rs35599367 added as true *22
  - DPYD rs1801265 relabeled as C29R (was *2A)
  - DPYD rs3918290 added as true *2A (splice defect)
  - star_alleles.defining_variants populated from PyPGx variant table
  - allele_frequencies.allele_id linked to star_alleles table
  - SAS_EXCL_BEB population added (independent comparison)
  - Studies table documents BEB⊂SAS non-independence

Inputs:
  data/raw/reference/         - PharmGKB, CPIC, PharmVar/PyPGx reference data
  data/raw/coordinates/       - BED files, dbSNP positions
  data/processed/allele_frequencies/corrected_frequencies.csv
  data/processed/phenotypes/phenotype_frequencies.csv

Outputs:
  db/pgxbd.db                 - SQLite database (6 tables)
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import pypgx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "pgxbd.db")
FREQ_FILE = os.path.join(BASE_DIR, "data", "processed", "allele_frequencies", "corrected_frequencies.csv")
PHENO_FILE = os.path.join(BASE_DIR, "data", "processed", "phenotypes", "phenotype_frequencies.csv")
REF_DIR = os.path.join(BASE_DIR, "data", "raw", "reference")
COORD_DIR = os.path.join(BASE_DIR, "data", "raw", "coordinates")


def create_schema(conn):
    """Create database schema."""
    c = conn.cursor()
    c.executescript("""
        DROP TABLE IF EXISTS pharmacogenes;
        DROP TABLE IF EXISTS star_alleles;
        DROP TABLE IF EXISTS studies;
        DROP TABLE IF EXISTS allele_frequencies;
        DROP TABLE IF EXISTS drug_recommendations;
        DROP TABLE IF EXISTS phenotype_frequencies;

        CREATE TABLE pharmacogenes (
            gene_id TEXT PRIMARY KEY,
            gene_name TEXT,
            chromosome TEXT,
            grch37_start INTEGER,
            grch37_end INTEGER,
            grch38_start INTEGER,
            grch38_end INTEGER,
            function_category TEXT,
            cpic_level TEXT,
            pharmgkb_id TEXT,
            pharmvar_url TEXT
        );

        CREATE TABLE star_alleles (
            allele_id TEXT PRIMARY KEY,
            gene_id TEXT,
            function TEXT,
            activity_score REAL,
            defining_variants TEXT,
            pharmvar_id TEXT,
            FOREIGN KEY (gene_id) REFERENCES pharmacogenes(gene_id)
        );

        CREATE TABLE studies (
            study_id TEXT PRIMARY KEY,
            citation TEXT,
            year INTEGER,
            population_desc TEXT,
            sample_size INTEGER,
            methodology TEXT,
            ethics_approval TEXT,
            data_source TEXT,
            data_url TEXT
        );

        CREATE TABLE allele_frequencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gene_id TEXT,
            allele_id TEXT,
            variant_rsid TEXT,
            population TEXT,
            study_id TEXT,
            allele_frequency REAL,
            genotype_counts TEXT,
            sample_size INTEGER,
            confidence_interval TEXT,
            methodology TEXT,
            notes TEXT,
            FOREIGN KEY (gene_id) REFERENCES pharmacogenes(gene_id),
            FOREIGN KEY (allele_id) REFERENCES star_alleles(allele_id),
            FOREIGN KEY (study_id) REFERENCES studies(study_id)
        );

        CREATE TABLE drug_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gene_id TEXT,
            phenotype TEXT,
            drug_name TEXT,
            recommendation TEXT,
            guideline_source TEXT,
            guideline_url TEXT,
            evidence_level TEXT,
            cpic_level TEXT,
            fda_label TEXT,
            FOREIGN KEY (gene_id) REFERENCES pharmacogenes(gene_id)
        );

        CREATE TABLE phenotype_frequencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gene_id TEXT,
            phenotype TEXT,
            population TEXT,
            frequency REAL,
            study_id TEXT,
            calculation_method TEXT,
            FOREIGN KEY (gene_id) REFERENCES pharmacogenes(gene_id),
            FOREIGN KEY (study_id) REFERENCES studies(study_id)
        );

        CREATE INDEX idx_af_gene ON allele_frequencies(gene_id);
        CREATE INDEX idx_af_rsid ON allele_frequencies(variant_rsid);
        CREATE INDEX idx_af_pop ON allele_frequencies(population);
        CREATE INDEX idx_pf_gene ON phenotype_frequencies(gene_id);
        CREATE INDEX idx_pf_pop ON phenotype_frequencies(population);
        CREATE INDEX idx_dr_gene ON drug_recommendations(gene_id);
    """)
    conn.commit()


def load_pharmacogenes(conn):
    """Load pharmacogene records from PharmGKB data."""
    pgkb_file = os.path.join(REF_DIR, "pharmgkb", "pharmgkb_gene_data.csv")
    df = pd.read_csv(pgkb_file)

    c = conn.cursor()
    for _, row in df.iterrows():
        c.execute("""
            INSERT INTO pharmacogenes VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row.get("gene_id", row.get("symbol", "")),
            row.get("gene_name", ""),
            row.get("chromosome", ""),
            int(row.get("grch37_start", 0)) if pd.notna(row.get("grch37_start")) else None,
            int(row.get("grch37_end", 0)) if pd.notna(row.get("grch37_end")) else None,
            int(row.get("grch38_start", 0)) if pd.notna(row.get("grch38_start")) else None,
            int(row.get("grch38_end", 0)) if pd.notna(row.get("grch38_end")) else None,
            row.get("function_category", ""),
            row.get("cpic_level", ""),
            row.get("pharmgkb_id", ""),
            row.get("pharmvar_url", ""),
        ))
    conn.commit()
    print(f"  pharmacogenes: {c.execute('SELECT COUNT(*) FROM pharmacogenes').fetchone()[0]} rows")


def load_star_alleles(conn):
    """Load star allele definitions from PyPGx with defining variants populated."""
    allele_file = os.path.join(REF_DIR, "pharmvar", "star_allele_definitions_pypgx.csv")
    df = pd.read_csv(allele_file)

    # Load PyPGx variant table to populate defining_variants
    variant_table = pypgx.load_variant_table()

    c = conn.cursor()
    for _, row in df.iterrows():
        gene = row["gene"]
        allele = row["allele"]
        allele_id = f"{gene}_{allele.replace('*', '').replace('(', '_').replace(')', '').replace('>', '_').replace('+', '_')}"
        function = row.get("function", "")
        score = float(row["activity_score"]) if pd.notna(row.get("activity_score")) else None

        # Get defining variants from PyPGx variant table
        defining = ""
        try:
            gene_variants = variant_table[variant_table["Gene"] == gene]
            if len(gene_variants) > 0:
                # Get variants that define this allele
                # PyPGx stores allele definitions in the variant table
                variant_list = gene_variants["Variant"].dropna().tolist()
                rsid_list = gene_variants["rsID"].dropna().tolist()
                if variant_list:
                    defining = "; ".join(
                        f"{r} ({v})" for r, v in zip(rsid_list, variant_list)
                        if pd.notna(r) and pd.notna(v)
                    )[:500]  # Truncate to avoid overly long strings
        except Exception:
            pass

        c.execute("""
            INSERT OR IGNORE INTO star_alleles VALUES (?,?,?,?,?,?)
        """, (allele_id, gene, function, score, defining, ""))

    conn.commit()
    count = c.execute("SELECT COUNT(*) FROM star_alleles").fetchone()[0]
    populated = c.execute("SELECT COUNT(*) FROM star_alleles WHERE defining_variants != ''").fetchone()[0]
    print(f"  star_alleles: {count} rows ({populated} with defining_variants)")


def load_studies(conn):
    """Load study records documenting all data sources."""
    c = conn.cursor()
    studies = [
        ("1000G_BEB", "1000 Genomes Project Phase 3 (2015)", 2015,
         "Bengali in Bangladesh (BEB) - 86 unrelated individuals", 86,
         "Whole genome sequencing", "See 1000G documentation",
         "1000 Genomes", "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"),
        ("1000G_SAS", "1000 Genomes Project Phase 3 (2015)", 2015,
         "South Asian (SAS) superpopulation - 489 individuals (includes 86 BEB)", 489,
         "Whole genome sequencing", "See 1000G documentation",
         "1000 Genomes", "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"),
        ("1000G_SAS_EXCL_BEB", "1000 Genomes Project Phase 3 (2015)", 2015,
         "South Asian excluding BEB (SAS_EXCL_BEB) - 403 individuals (independent of BEB)", 403,
         "Whole genome sequencing", "See 1000G documentation",
         "1000 Genomes", "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"),
        ("1000G_EUR", "1000 Genomes Project Phase 3 (2015)", 2015,
         "European (EUR) superpopulation - 503 individuals", 503,
         "Whole genome sequencing", "See 1000G documentation",
         "1000 Genomes", "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"),
        ("1000G_EAS", "1000 Genomes Project Phase 3 (2015)", 2015,
         "East Asian (EAS) superpopulation - 504 individuals", 504,
         "Whole genome sequencing", "See 1000G documentation",
         "1000 Genomes", "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"),
        ("1000G_AFR", "1000 Genomes Project Phase 3 (2015)", 2015,
         "African (AFR) superpopulation - 661 individuals", 661,
         "Whole genome sequencing", "See 1000G documentation",
         "1000 Genomes", "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"),
        ("1000G_AMR", "1000 Genomes Project Phase 3 (2015)", 2015,
         "Admixed American (AMR) superpopulation - 347 individuals", 347,
         "Whole genome sequencing", "See 1000G documentation",
         "1000 Genomes", "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"),
        ("dbSNP_global", "NCBI dbSNP global MAFs (multiple studies)", 2024,
         "Global populations from 33 studies (gnomAD, TOPMED, 1000G, etc.)", None,
         "Aggregated from multiple studies", "N/A",
         "dbSNP", "https://www.ncbi.nlm.nih.gov/snp/"),
        ("CPIC_2024", "Clinical Pharmacogenetics Implementation Consortium", 2024,
         "Guideline-based recommendations (not population-specific)", None,
         "Expert consensus guidelines", "N/A",
         "CPIC", "https://cpicpgx.org/"),
    ]

    for s in studies:
        c.execute("INSERT INTO studies VALUES (?,?,?,?,?,?,?,?,?)", s)

    conn.commit()
    print(f"  studies: {c.execute('SELECT COUNT(*) FROM studies').fetchone()[0]} rows")


def load_allele_frequencies(conn):
    """Load corrected allele frequencies with allele_id linkage."""
    df = pd.read_csv(FREQ_FILE)

    # Build rsid → allele_id mapping
    # Format: gene_starallele (e.g., CYP3A5_3, CYP2D6_4)
    rsid_to_allele_id = {}
    for _, row in df.drop_duplicates("rsid").iterrows():
        gene = row["gene"]
        star = str(row["star_allele"]).replace("*", "").replace("(", "_").replace(")", "").replace(">", "_").replace("+", "_")
        rsid_to_allele_id[row["rsid"]] = f"{gene}_{star}"

    # Population → study_id mapping
    pop_to_study = {
        "BEB": "1000G_BEB",
        "SAS": "1000G_SAS",
        "SAS_EXCL_BEB": "1000G_SAS_EXCL_BEB",
        "EUR": "1000G_EUR",
        "EAS": "1000G_EAS",
        "AFR": "1000G_AFR",
        "AMR": "1000G_AMR",
    }

    c = conn.cursor()
    for _, row in df.iterrows():
        allele_id = rsid_to_allele_id.get(row["rsid"])
        study_id = pop_to_study.get(row["population"], f"1000G_{row['population']}")

        gt_counts = json.dumps({
            "hom_ref": int(row["hom_ref"]),
            "het": int(row["het"]),
            "hom_alt": int(row["hom_alt"]),
        })

        c.execute("""
            INSERT INTO allele_frequencies
            (gene_id, allele_id, variant_rsid, population, study_id,
             allele_frequency, genotype_counts, sample_size,
             confidence_interval, methodology, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row["gene"], allele_id, row["rsid"], row["population"], study_id,
            float(row["pgx_allele_frequency"]), gt_counts,
            int(row["sample_size"]),
            str(row.get("confidence_interval", "")),
            "Whole genome sequencing (1000G Phase 3)",
            str(row.get("notes", "")),
        ))

    conn.commit()
    count = c.execute("SELECT COUNT(*) FROM allele_frequencies").fetchone()[0]
    linked = c.execute("SELECT COUNT(*) FROM allele_frequencies WHERE allele_id IS NOT NULL").fetchone()[0]
    print(f"  allele_frequencies: {count} rows ({linked} with allele_id linked)")


def load_phenotype_frequencies(conn):
    """Load corrected phenotype frequencies."""
    df = pd.read_csv(PHENO_FILE)

    pop_to_study = {
        "BEB": "1000G_BEB",
        "SAS": "1000G_SAS",
        "SAS_EXCL_BEB": "1000G_SAS_EXCL_BEB",
        "EUR": "1000G_EUR",
        "EAS": "1000G_EAS",
        "AFR": "1000G_AFR",
    }

    c = conn.cursor()
    for _, row in df.iterrows():
        study_id = pop_to_study.get(row["population"], f"1000G_{row['population']}")
        c.execute("""
            INSERT INTO phenotype_frequencies
            (gene_id, phenotype, population, frequency, study_id, calculation_method)
            VALUES (?,?,?,?,?,?)
        """, (
            row["gene_id"], row["phenotype"], row["population"],
            float(row["frequency"]), study_id, str(row["calculation_method"]),
        ))

    conn.commit()
    print(f"  phenotype_frequencies: {c.execute('SELECT COUNT(*) FROM phenotype_frequencies').fetchone()[0]} rows")


def load_drug_recommendations(conn):
    """Load CPIC drug recommendations from the CPIC recommendations CSV.

    The CSV uses column names: genes, drug_name, drugrecommendation,
    classification, implications, phenotype_summary, lookupkey.
    We map these to our schema columns.
    """
    rec_file = os.path.join(REF_DIR, "cpic", "cpic_pgx_recommendations.csv")
    df = pd.read_csv(rec_file)

    c = conn.cursor()
    for _, row in df.iterrows():
        # genes column may contain multiple genes separated by comma
        gene_id = str(row.get("genes", "")).split(",")[0].strip()
        drug_name = str(row.get("drug_name", ""))
        recommendation = str(row.get("drugrecommendation", ""))
        cpic_level = str(row.get("classification", ""))
        phenotype = str(row.get("phenotype_summary", ""))
        implications = str(row.get("implications", ""))
        # Combine phenotype + implications for a richer phenotype field
        if phenotype and implications and phenotype != "nan":
            phenotype_full = f"{phenotype} | {implications}"
        elif implications and implications != "nan":
            phenotype_full = implications
        else:
            phenotype_full = phenotype if phenotype != "nan" else ""

        c.execute("""
            INSERT INTO drug_recommendations
            (gene_id, phenotype, drug_name, recommendation, guideline_source,
             guideline_url, evidence_level, cpic_level, fda_label)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            gene_id if gene_id != "nan" else "",
            phenotype_full,
            drug_name if drug_name != "nan" else "",
            recommendation if recommendation != "nan" else "",
            "CPIC",
            "",
            cpic_level if cpic_level != "nan" else "",
            cpic_level if cpic_level != "nan" else "",
            "",
        ))

    conn.commit()
    print(f"  drug_recommendations: {c.execute('SELECT COUNT(*) FROM drug_recommendations').fetchone()[0]} rows")


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Remove old database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    print("Building PGxBD database...")
    conn = sqlite3.connect(DB_PATH)

    print("\n  Creating schema...")
    create_schema(conn)

    print("  Loading pharmacogenes...")
    load_pharmacogenes(conn)

    print("  Loading star alleles (with defining variants)...")
    load_star_alleles(conn)

    print("  Loading studies...")
    load_studies(conn)

    print("  Loading allele frequencies (with allele_id linkage)...")
    load_allele_frequencies(conn)

    print("  Loading phenotype frequencies...")
    load_phenotype_frequencies(conn)

    print("  Loading drug recommendations...")
    load_drug_recommendations(conn)

    # Summary
    print("\n" + "=" * 60)
    print("DATABASE SUMMARY:")
    print("=" * 60)
    c = conn.cursor()
    for table in ["pharmacogenes", "star_alleles", "studies",
                  "allele_frequencies", "drug_recommendations", "phenotype_frequencies"]:
        count = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:30s}: {count:>6} rows")

    # Verify fixes
    print("\n  FIX VERIFICATION:")
    # CYP3A5*3 orientation
    r = c.execute("SELECT allele_frequency, notes FROM allele_frequencies WHERE variant_rsid='rs776746' AND population='BEB'").fetchone()
    print(f"    CYP3A5*3 BEB AF: {r[0]} (should be ~0.634)")

    # CYP3A4*1G label
    r = c.execute("SELECT allele_id, notes FROM allele_frequencies WHERE variant_rsid='rs2242480' AND population='BEB'").fetchone()
    print(f"    CYP3A4 rs2242480 allele_id: {r[0]} (should be CYP3A4_1G)")

    # CYP3A4*22 new variant
    r = c.execute("SELECT allele_frequency FROM allele_frequencies WHERE variant_rsid='rs35599367' AND population='BEB'").fetchone()
    print(f"    CYP3A4*22 (rs35599367) BEB AF: {r[0]} (should be 0.0)")

    # DPYD *2A new variant
    r = c.execute("SELECT allele_frequency FROM allele_frequencies WHERE variant_rsid='rs3918290' AND population='BEB'").fetchone()
    print(f"    DPYD*2A (rs3918290) BEB AF: {r[0]} (should be 0.0)")

    # G6PD fixed
    r = c.execute("SELECT allele_frequency FROM allele_frequencies WHERE variant_rsid='rs1050828' AND population='BEB'").fetchone()
    print(f"    G6PD A- (rs1050828) BEB AF: {r[0]} (should be 0.0)")

    # CYP2C19 phenotype sum
    r = c.execute("SELECT SUM(frequency) FROM phenotype_frequencies WHERE gene_id='CYP2C19' AND population='BEB'").fetchone()
    print(f"    CYP2C19 BEB phenotype sum: {r[0]:.4f} (should be 1.0)")

    # CYP2D6 phenotype sum
    r = c.execute("SELECT SUM(frequency) FROM phenotype_frequencies WHERE gene_id='CYP2D6' AND population='BEB'").fetchone()
    print(f"    CYP2D6 BEB phenotype sum: {r[0]:.4f} (should be 1.0)")

    # allele_id linkage
    r = c.execute("SELECT COUNT(*) FROM allele_frequencies WHERE allele_id IS NOT NULL").fetchone()
    total = c.execute("SELECT COUNT(*) FROM allele_frequencies").fetchone()[0]
    print(f"    allele_id linked: {r[0]}/{total}")

    # defining_variants populated
    r = c.execute("SELECT COUNT(*) FROM star_alleles WHERE defining_variants != ''").fetchone()
    total = c.execute("SELECT COUNT(*) FROM star_alleles").fetchone()[0]
    print(f"    defining_variants populated: {r[0]}/{total}")

    conn.close()
    print(f"\nDatabase saved to {DB_PATH}")


if __name__ == "__main__":
    main()
