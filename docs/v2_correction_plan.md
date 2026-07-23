# PGxBD: Fix Major Limitations + Project Reorganization

## Summary

Fix all 3 major limitations flagged by the scientific review (CYP3A5*3 allele flip, CYP3A4*22 mislabel, CYP2C19 HWE missing class) plus 7 additional issues discovered during audit (G6PD wrong frequencies, DPYD *2A mislabel, CYP2D6 phenotypes ignoring *10, chrX hemizygosity, SAS-BEB non-independence, empty star_allele defining_variants, NULL allele_id linkage). Then reorganize the entire project into a best-practice directory structure with reproducible scripts, proper data/raw/preprocessed separation, and a clean API package.

## Part A: Scientific Fixes (10 issues)

### A1. CYP3A5*3 allele orientation flip
- **Problem**: rs776746 at 7:99270539, REF=C ALT=T. CYP3A5 is minus strand: C(genomic)=G(coding)=*3, T(genomic)=A(coding)=*1. DB uses ALT (0.366) but *3 = REF (0.634).
- **Fix**: Flip orientation to REF for all 6 populations. Update allele_frequencies table, final_frequency_comparison.csv, corrected_pgx_variant_frequencies.csv. Regenerate CYP3A5 phenotype frequencies (CYP3A5 *3/*3 = poor, *1/*3 = intermediate, *1/*1 = normal).
- **Validation**: EUR *3 should be ~94% (corrected: 0.943), AFR *3 ~18% (corrected: 0.180).

### A2. CYP3A4*22 mislabel → relabel as *1G, add true *22
- **Problem**: rs2242480 (7:99361466) is CYP3A4*1G, not *22. True *22 = rs35599367 (7:99366316).
- **Fix**: Relabel rs2242480 as *1G in all tables. Add rs35599367 as CYP3A4*22 with frequencies from the extension VCF (BEB AF=0.0, EUR AF=0.050, SAS AF=0.006). Add 6 population records for rs35599367.

### A3. CYP2C19 HWE missing *2/*17 compound heterozygote
- **Problem**: *2/*17 and *3/*17 genotypes (classified as Intermediate by CPIC) are omitted. BEB phenotypes sum to 0.923.
- **Fix**: Recompute all CYP2C19 phenotype frequencies for all 5 populations using the full HWE formula: Intermediate = 2*f1*f2 + 2*f1*f3 + 2*f2*f17 + 2*f3*f17. All sums will equal 1.0.

### A4. G6PD frequencies completely wrong
- **Problem**: DB has BEB AF=0.244 for both rs1050828 and rs1050829. Actual VCF data at correct positions shows AF=0.0 for both (confirmed by 1000G INFO SAS_AF=0.0).
- **Fix**: Recompute G6PD frequencies from VCF at correct GRCh37 positions (153764217, 153763492) with chrX hemizygosity handling (males=1 allele, females=2 alleles). Update all 12 G6PD records (2 variants × 6 populations).

### A5. DPYD rs1801265 mislabeled as *2A
- **Problem**: rs1801265 (1:98348885) is C29R (c.85C>T), not *2A. True *2A = rs3918290 (1:97915614, c.1905+1G>A).
- **Fix**: Relabel rs1801265 as "C29R" with function "decreased function". Add rs3918290 as DPYD *2A with frequencies from VCF (BEB AF=0.0, EUR AF=0.005, SAS AF=0.008). Add 6 population records.

### A6. CYP2D6 phenotypes ignore *10 allele
- **Problem**: Phenotypes computed from *4 only. *10 (BEB AF=0.256, decreased function, activity score 0.25) is present but ignored.
- **Fix**: Recompute CYP2D6 phenotypes using 3-allele HWE (*1+*2 combined as normal score 1.0, *4 score 0.0, *10 score 0.25) with CPIC activity score thresholds (Poor: 0-0.25, Intermediate: 0.25-1.25, Normal: 1.25-2.5, Ultrarapid: ≥2.5). Update all 5 populations.

### A7. G6PD chrX hemizygosity
- **Problem**: chrX counted as diploid (2 alleles/sample) for all samples. Males are hemizygous.
- **Fix**: Use sex-aware counting from the 1000G panel. Males contribute 1 allele, females contribute 2. Total = n_males + 2*n_females. Apply to all chrX variants (G6PD).

### A8. SAS contains BEB (non-independent comparison)
- **Problem**: BEB is a subpopulation of the SAS superpopulation. BEB-vs-SAS contrasts are not independent.
- **Fix**: Add a `notes` field to the studies table and API response documenting this. Add a computed "SAS_excl_BEB" population (SAS minus 86 BEB samples = 403 individuals) for independent comparison. Recompute SAS_excl_BEB frequencies for all 27 variants.

### A9. Populate star_alleles.defining_variants
- **Problem**: All 755 star_alleles have empty defining_variants field.
- **Fix**: Populate from PyPGx variant table (load_variant_table) which maps gene+allele to defining variants (rsID, position, HGVS).

### A10. Link allele_frequencies.allele_id to star_alleles
- **Problem**: allele_id is NULL for all 162 allele_frequencies records.
- **Fix**: Set allele_id based on the gene+star_allele mapping (e.g., CYP3A5 *3 → CYP3A5_3).

## Part B: Project Reorganization

### Target directory structure
```
pgxbd/
├── README.md                    # Project overview, setup, usage
├── requirements.txt             # Python dependencies
├── config/
│   └── settings.yaml            # Database path, API port, population definitions
├── data/
│   ├── raw/                     # Immutable source data (never modified)
│   │   ├── 1000g/               # 1000G VCFs, panel file, sample lists
│   │   │   ├── vcfs/            # 23 pharmacogene region VCFs
│   │   │   ├── panel.txt        # 1000G integrated sample panel
│   │   │   └── beb_samples.txt  # 86 BEB sample IDs
│   │   ├── reference/           # PharmGKB, CPIC, PharmVar/PyPGx
│   │   │   ├── pharmgkb/
│   │   │   ├── cpic/
│   │   │   └── pharmvar/
│   │   ├── comparison/          # gnomAD, dbSNP MAFs
│   │   │   ├── gnomad/
│   │   │   └── dbsnp/
│   │   └── coordinates/         # BED files, dbSNP position lookups
│   │       ├── pharmacogene_regions_grch37.bed
│   │       └── snp_positions_from_dbsnp.csv
│   └── processed/               # Cleaned, harmonized intermediate data
│       ├── allele_frequencies/  # Computed frequency tables
│       │   ├── beb_all_variants.csv
│       │   ├── key_variant_frequencies.csv
│       │   └── corrected_frequencies.csv
│       ├── phenotypes/          # HWE phenotype estimates
│       │   └── phenotype_frequencies.csv
│       └── comparisons/         # Cross-population comparison tables
│           └── final_frequency_comparison.csv
├── db/
│   └── pgxbd.db                 # SQLite database (built from scripts)
├── scripts/                     # Reproducible pipeline scripts
│   ├── 01_fetch_1000g.py        # Download 1000G pharmacogene VCFs
│   ├── 02_compute_frequencies.py # Compute allele frequencies (sex-aware for chrX)
│   ├── 03_fetch_reference.py    # Download PharmGKB/CPIC/PyPGx reference data
│   ├── 04_build_database.py     # Build SQLite database from all sources
│   ├── 05_compute_phenotypes.py # HWE phenotype estimation
│   ├── 06_validate.py           # Validation checks (frequency sums, orientation)
│   └── run_pipeline.sh          # Run all steps in order
├── api/                         # REST API package
│   ├── __init__.py
│   ├── main.py                  # FastAPI app
│   ├── database.py              # DB connection helpers
│   ├── models.py                # Pydantic models
│   └── routers/                 # Endpoint modules
│       ├── genes.py
│       ├── frequencies.py
│       ├── phenotypes.py
│       ├── drugs.py
│       └── variants.py
├── output/                      # Final deliverables
│   ├── figures/                 # PNG visualizations
│   └── tables/                  # Final CSV tables for publication
└── tests/                       # Unit tests
    ├── test_frequencies.py      # Verify frequency computation
    ├── test_phenotypes.py       # Verify HWE sums = 1.0
    └── test_api.py              # API endpoint tests
```

### Reorganization steps
1. Create the directory structure above
2. Move raw VCFs to `data/raw/1000g/vcfs/`, panel to `data/raw/1000g/`
3. Move reference data (PharmGKB, CPIC, PharmVar) to `data/raw/reference/`
4. Move comparison data (gnomAD, dbSNP) to `data/raw/comparison/`
5. Move BED files and position CSVs to `data/raw/coordinates/`
6. Move processed frequency tables to `data/processed/`
7. Write modular pipeline scripts (01-06) that read from `data/raw/` and write to `data/processed/` and `db/`
8. Refactor API into a proper package (`api/` with routers)
9. Write validation script (`06_validate.py`) that checks:
   - All phenotype frequency sums = 1.0 ± 0.001
   - CYP3A5*3 EUR AF > 0.90 (sanity check)
   - G6PD BEB AF matches VCF (chrX-aware)
   - No NULL allele_id in allele_frequencies
   - All star_alleles have defining_variants populated
10. Write unit tests
11. Copy final deliverables to /mnt/results/

## Part C: Regenerate Visualizations

After fixes, regenerate all 5 figures with corrected data:
1. Frequency comparison bar chart (BEB vs EUR vs EAS vs AFR) — CYP3A5*3 will now show correct high frequency
2. Allele frequency heatmap — corrected values
3. BEB vs EUR scatter plot — CYP3A5*3 point will move above diagonal
4. Phenotype frequency comparison — corrected CYP2C19 and CYP2D6
5. Top 15 BEB-EUR differences — CYP3A5*3 will now show as one of the largest

## Execution Order

1. Write all pipeline scripts as reusable Python files in `scripts/`
2. Run frequency recomputation (fixes A1, A4, A7, A8)
3. Run phenotype recomputation (fixes A3, A6)
4. Update database with corrected labels and new variants (fixes A2, A5, A9, A10)
5. Run validation script
6. Reorganize directory structure
7. Refactor API
8. Regenerate visualizations
9. Copy deliverables to /mnt/results/

## Compute Estimate

- All work runs on the default machine (no HPC needed)
- VCF re-parsing: ~5 min (23 VCFs, 759MB total, pysam streaming)
- Database rebuild: ~1 min
- Visualization: ~2 min
- Total estimated: ~15 min
