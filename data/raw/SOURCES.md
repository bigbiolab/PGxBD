# Raw Data Sources

Tracks every source named in `docs/PGxBD_PLAN.md` section 2, what's actually been curated into
`data/raw/` so far, and what's still pending. `data/raw/` holds data as fetched/downloaded,
before any correctness fixes or harmonization; `data/processed/` holds the curated/harmonized
output of the preprocessing pipeline (`scripts/01_fix_tier1.py` onward).

| Source | Status | Raw file(s) | Notes |
|---|---|---|---|
| 1000 Genomes Phase 3 - BEB + comparison superpopulations (SAS, EUR, EAS, AFR, AMR) | **Curated** | `key_pgx_variant_frequencies.csv`, `panel.txt` | Allele frequencies computed directly from remote-tabix VCF queries (`scripts/02_fetch_g6pd_wsl.py`, `scripts/04_fetch_stretch_wsl.py`); `panel.txt` is the 1000G sample-to-population/sex panel. |
| 1000 Genomes - SAS minus BEB (`SAS_other`) | **Curated** | `stretch_variants.csv` | Added in the v1 fix pass so BEB-vs-SAS has an independent contrast (BEB is a subset of SAS). |
| 1000 Genomes - G6PD (chrX) sex-aware recount | **Curated** | `g6pd_corrected.csv`, `g6pd_sas_other.csv` | Original pipeline miscounted hemizygous males as diploid; refetched with per-sample sex from `panel.txt`. |
| dbSNP global MAFs | **Curated** (pre-existing) | — (loaded into `db/pgxbd.db`; no raw file preserved) | Study id `dbSNP_global`. Also used live (not cached) by `scripts/06_verify_orientation.py` for QA cross-checks. |
| PharmGKB / ClinPGx (drug-gene associations, clinical annotations, dosing guidelines) | **Curated** | `clinpgx/genes/`, `clinpgx/drugs/`, `clinpgx/relationships/`, `clinpgx/clinicalAnnotations/`, `clinpgx/clinicalVariants/`, `clinpgx/dosingGuidelines/` | PharmGKB rebranded to **ClinPGx** (pharmgkb.org now redirects to clinpgx.org). Bulk TSV/JSON downloads are free, no login needed, via `api.clinpgx.org/v1/download/file/data/{name}.zip` (legacy `api.pharmgkb.org` still works too). ~48 MB total. Needed for v2 star-allele linkage and drug-gene mapping. |
| PharmVar (star allele definitions) | **Blocked** | — | PharmVar's API now requires a registered account + API key (`errorCode 401`), and the download page is a JS SPA with no static file links to scrape. This is a change from the plan's assumption of no-signup access. Needed to populate `star_alleles.defining_variants`/`pharmvar_id` (currently an unlinked 755-row skeleton) - requires a human to register at pharmvar.org and generate a key. |
| DPWG Guidelines | **Partially curated** | `clinpgx/dosingGuidelines/` | DPWG guidance is mapped through ClinPGx per the plan; `dosingGuidelines.json.zip` includes CPIC *and* other-source (incl. DPWG-referencing) guideline annotations. Not yet parsed/separated out. |
| gnomAD (global allele frequencies) | **Attempted, mostly failed** | — | Only 7/29 variants matched by rsID, all position queries failed. Not retried; see `docs/major_limitations.md`. |
| IndiGen / SAGE (South Asian comparison) | **Blocked (unreachable)** | — | `clingen.igib.res.in` times out on HTTPS (TCP-level hang, ~21s, consistent across retries) from this environment. HTTP redirects to HTTPS then hangs. Could be a transient outage or a network path issue specific to this environment - worth retrying manually from a normal browser/connection. |
| Genes & Health GWAS summary statistics (British-Bangladeshi) | **Blocked** | — | The public GCS bucket (`gs://genesandhealth_publicdatasets/`) returns `SecurityPolicyViolated` / VPC Service Controls when accessed anonymously over HTTPS from this environment - confirmed this is bucket-specific (other public GCS buckets, e.g. `gcp-public-data-landsat`, work fine), so Genes & Health's own org policy is restricting access despite the plan describing it as open. `gsutil` with a real Google account (rather than anonymous HTTPS) may work where this didn't - worth trying from the user's own machine. |
| Genes & Health individual-level data | **Not started** (requires application) | — | EGA controlled access, bona fide researcher status, 2-6 month approval. |
| CPIC structured API data (genes, drugs, guidelines, pairs, recommendations, alleles, allele definitions, allele frequencies, populations, diplotypes, publications) | **Curated** | `cpic/*.json` | Free PostgREST API at `api.cpicpgx.org`, no auth. `diplotype.json` (113 MB) and `gene_result_diplotype.json` (22 MB) are large full lookup tables across all CPIC genes; `allele_frequency.json` (34 MB) is CPIC's own population allele-frequency reference (distinct from our 1000G-derived data). ~167 MB total. Note: `db/pgxbd.db`'s existing `drug_recommendations`/`studies` (study id `CPIC_2024`) were loaded from CPIC before this raw-data pull, with no raw file preserved at the time - this row is the first actual raw CPIC snapshot on disk. |
| 11 published Bangladeshi PGx studies (allele frequency tables) | **Not started** | — | Manual extraction from papers/supplementary materials - see `docs/PGxBD_PLAN.md` section 2.3 for the study list. This is the bulk of the work needed to reach the original Product 1 vision; requires a human to read and transcribe each paper, not automatable from here. |

## Curation conventions for anything added to `data/raw/`

- Store data exactly as fetched - no orientation flips, no relabeling, no merging across sources.
  All correctness fixes and harmonization happen in the preprocessing stages
  (`scripts/01_fix_tier1.py` onward) and land in `data/processed/`.
- Record provenance in this file when adding a new raw source: what it is, where it came from,
  which script fetched it, and what's still missing.
- If adding a manually-curated source (e.g. a literature study's frequency table), name the file
  after the study/source and add a row here rather than merging it directly into an existing file.
