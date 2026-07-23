# PGxBD Data Limitations

Scope note: this database contains only 1000 Genomes Phase 3 data, CPIC guideline
annotations, and dbSNP global frequencies for BEB (Bengali-in-Bangladesh) vs. SAS/EUR/EAS/AFR/AMR
superpopulations. It does **not** include the 11 published Bangladeshi PGx literature studies or
PharmVar-linked star-allele definitions — that curation work is deferred to v2. Run the full
pipeline via `bash scripts/run_pipeline.sh` (stages `scripts/01_fetch_1000g.py` through
`scripts/06_validate.py`, plus `scripts/07_generate_figures.py`; see `data/raw/SOURCES.md` for
data provenance). The (now superseded) v1 patch-script sweep that originally found and fixed
these issues is described below; its orientation-check output is preserved at
`data/processed/orientation_verification_report.csv`. Pre-fix state is preserved in
`backup_pre_v1fix/`.

## Resolved (v1)

**CYP3A5\*3 (rs776746) orientation was flipped.** Reported "\*3" frequencies were EUR 5.7%/AFR 82%,
but established literature *3 frequency is ~92% in Europeans and ~24% (minor) in Africans — the
old values actually described the *1 (functional) allele. Fixed by flipping orientation to REF (C)
across all 6 populations. **After fix: BEB 0.634, SAS 0.668, EUR 0.943, EAS 0.713, AFR 0.180, AMR
0.797** — now consistent with literature. Confidence: High.

**rs2242480 was mislabeled CYP3A4\*22.** It's actually the CYP3A4\*1G defining variant; the true
*22 defining variant is rs35599367, which was missing from the dataset entirely. Fixed by
relabeling rs2242480 to *1G and fetching rs35599367 directly from 1000G (chr7:99,366,316 GRCh37,
G>A). **rs35599367 after fetch: BEB 0.0, SAS 0.006, EUR 0.050, EAS 0.0, AFR 0.001, AMR 0.026** —
matches published CYP3A4*22 frequencies (~2-5% in Europeans, near-absent elsewhere). *1G's
functional classification (previously inherited from the *22 mislabel as "decreased function") is
not independently confirmed for v1 and is marked "uncertain function" pending v2 review.

**CYP2C19 phenotype frequencies summed to 0.923, not 1.0.** The Hardy-Weinberg expansion omitted
the *2/*17 and *3/*17 compound-heterozygote (Intermediate Metabolizer) class. Fixed using the full
4-allele model (*1/*2/*3/*17): PM=q², IM=2pq+2qr, NM=p², RM=2pr, UM=r², which sums to exactly 1 by
construction. Applied to all 5 populations with CYP2C19 data (BEB/SAS/EUR/EAS/AFR); all now sum to
1.0000.

**G6PD (chrX) was processed with uniform diploid genotype counting**, with no handling of male
hemizygosity — `total_count += 2 # diploid` was applied even to hemizygous male calls. Root cause
was in the aggregation code only; the source 1000G VCF already correctly encodes male genotypes as
haploid (GT tuple length 1) vs. female diploid (length 2). Fixed by re-fetching both G6PD variants
(rs1050828, rs1050829) from the 1000G chrX VCF with per-sample sex from the population panel file,
counting males as 1 allele (hemizygous) and females as 2. Frequencies changed substantially: e.g.
rs1050828 (G6PD A-) BEB went from a spurious 0.244 to a correct **0.0** (this deficiency variant is
Africa-specific and essentially absent in South/East Asian and European populations per known
epidemiology; new AFR value 0.135 matches published G6PD A- frequency).

**Bug #8 root-cause sweep completed** (`scripts/06_verify_orientation.py`): systematically re-checked all 27
variants' orientation via a smell test (no-function/decreased-function allele >50% frequency in
2+ populations) plus an independent dbSNP global-1000G frequency cross-check. Found one additional
issue beyond the two above: **SLCO1B1\*1B (rs2306283) was labeled "decreased function"**, but this
is a well-documented common variant (BEB 56%, AFR 82%, matching known high-frequency epidemiology)
that current CPIC guidance does not classify as reducing transporter activity. Relabeled to
"normal/increased function" pending full v2 citation. All other 25 variants passed both checks
(full results in `orientation_verification_report.csv`).

## Stretch fixes applied (v1.1, bundled into the same WSL session)

**BEB-vs-SAS non-independence** (BEB is a 1000G SAS subpopulation) — beyond the originally-planned
documentation-only fix, a genuinely independent `SAS_other` population (SAS minus the 86 BEB
samples) was computed for all 27 original variants plus rs35599367 and G6PD, and added to the
database/API. Use BEB-vs-SAS_other (or BEB-vs-EUR/EAS/AFR/AMR) for independent contrasts;
BEB-vs-SAS remains available but is documented as non-independent in the API description.

## Known v1 Limitations (not fixed, by design)

**CYP2D6 phenotype frequencies are SNP-only, not CNV-aware.** The v1 model now incorporates both
*4 (no-function) and *10 (decreased-function, activity score 0.25) via a 3-allele activity-score
model, an improvement over the original *4-only calculation. However, CYP2D6*5 (whole-gene
deletion) and gene duplications (true Ultrarapid Metabolizer status) cannot be called from 1000G
short-read data — the model's maximum activity score is 2.0, so **no UM category is asserted**;
true UM/duplication carriers are undetermined in this dataset. Requires long-read sequencing or
targeted CNV assays to resolve — out of scope for v1.

**G6PD star-allele label for rs1050829 ("Mediterranean") is suspect.** The sex-aware recount shows
this variant near-absent in BEB/SAS/EAS (0.0) but common in AFR (0.338) — the opposite of the
epidemiology expected for the Mediterranean/Middle-Eastern G6PD deficiency variant, which should
track South Asian/Mediterranean populations, not Sub-Saharan Africa. This suggests rs1050829 may
actually be a different G6PD marker SNP (possibly the linked "A" silent marker rather than the
Mediterranean deficiency variant). Needs independent verification against PharmVar/OMIM G6PD
allele definitions in v2 — not resolved here to avoid asserting an unverified relabel.

**gnomAD cross-validation is not used.** Only 7 of 29 variants matched by rsID, and all
position-based queries failed (likely a genome-build or endpoint mismatch). Cross-validation for
v1 relies on 1000G-internal population comparisons and dbSNP global MAFs only. Debugging the
gnomAD integration is deferred to v2 as lower-value relative to effort.

**No literature curation.** The 11 published Bangladeshi PGx studies referenced in `PGxBD_PLAN.md`
are not in this database — `studies` currently only has 1000G/CPIC/dbSNP rows. **No star-allele
linkage.** The `star_alleles` table (755 rows) is an unlinked skeleton — `defining_variants` and
`pharmvar_id` are empty for all rows and are not cross-referenced to `allele_frequencies.allele_id`
(NULL for all rows). Both are explicitly deferred to v2, not silently dropped: they are the bulk of
the work needed to reach the original `PGxBD_PLAN.md` vision of Product 1.

**No web frontend.** FastAPI's built-in Swagger UI (`/docs`) is the de facto v1 interface. A
dedicated frontend is deferred to v2 alongside literature curation and star-allele linking.

## Resolved in v2.0.0

**DPYD\*2A (rs1801265) was mislabeled.** rs1801265 is actually C29R (c.85C>T), a distinct
low-impact DPYD variant — not \*2A. The true \*2A defining variant is rs3918290
(c.1905+1G>A, splice-site null). Both variants are now correctly labeled and carried
separately in `corrected_frequencies_full.csv` / the database.

**Project reorganized into a clean, reproducible structure**: pipeline rewritten from
patch-scripts (`01_fix_tier1.py` … `07_generate_outputs.py`, applied on top of prior data) into
a from-scratch, idempotent pipeline (`scripts/01_fetch_1000g.py` … `07_generate_figures.py`,
orchestrated by `scripts/run_pipeline.sh`); the API split from a single `bdpgx_api.py` file
into a package (`api/main.py`, `database.py`, `models.py`, `routers/`); tests moved to
`tests/test_api.py`; central config added at `config/settings.yaml`. See
`docs/v2_correction_plan.md` for the full fix/reorg plan and `report_bangladesh_bioinformatics_products.md`
for the current feature/correction summary.
