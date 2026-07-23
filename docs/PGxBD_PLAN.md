# PGxBD: Bangladeshi Pharmacogenomic Frequency Database

## 1. Summary

Build the first consolidated pharmacogenomic allele frequency database for the Bangladeshi population by harmonizing 11 published pharmacogenetic studies, 1000 Genomes BEB data, and publicly available Genes & Health summary statistics into a single standardized, queryable resource. This requires no sample collection, no wet-lab work, and modest compute — the work is data harmonization, curation, annotation, and database/API building. The database becomes the company's first defensible data asset and the foundation for a clinical interpretation product (Product 2), a publishable paper for grant eligibility, and a demonstrable proof of concept for investor pitches.

## 2. Data Sources and Access Paths

### 2.1 Freely Available — Start Immediately (No Application Needed)

| Source                                      | What You Get                                                          | Format                                                                                  | Access Method                                            | Compute Need                                                                                                                           |
| ------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1000 Genomes BEB (86 unrelated individuals) | Whole-genome variants for Bengali-in-Bangladesh samples               | Multi-individual VCF (all populations combined); filter for BEB using sample panel file | FTP/Aspera/Globus from IGSR; also on AWS public datasets | Low — bcftools/vcftools filtering on laptop; ~5-10 GB download per chromosome VCF, filter to BEB samples and pharmacogene regions only |
| PharmGKB                                    | All drug-gene associations, clinical annotations, variant annotations | TSV/CSV downloads                                                                       | Free registration at pharmgkb.org                        | Trivial — flat file downloads                                                                                                          |
| CPIC Guidelines                             | All clinical dosing recommendations by gene/drug/phenotype            | PDF + structured data at cpicpgx.org                                                    | Free download                                            | Trivial — manual curation into structured format                                                                                       |
| DPWG Guidelines                             | European dosing recommendations                                       | Via PharmGKB mapping                                                                    | Free                                                     | Trivial                                                                                                                                |
| PharmVar                                    | Star allele definitions for CYP2D6, CYP2C19, etc.                     | Structured data at pharmvar.org                                                         | Free                                                     | Trivial                                                                                                                                |
| gnomAD                                      | Global allele frequencies for comparison                              | VCF + API at gnomad.broadinstitute.org                                                  | Free                                                     | Low — API queries or downloaded frequency VCFs for pharmacogene regions                                                                |
| IndiGen / SAGE (Indian databases)           | South Asian comparison frequencies                                    | Web browser + downloadable VCFs                                                         | Free at clingen.igib.res.in                              | Low — download specific gene regions                                                                                                   |
| Genes & Health GWAS Summary Statistics      | Publicly available GWAS summary stats for British-Bangladeshi cohort  | TSV files via Google Cloud bucket (gs://genesandhealth_publicdatasets/)                 | gsutil download, no application needed                   | Low — summary statistics are small files                                                                                               |

### 2.2 Requires Application — Start Process Early, Use While Waiting

| Source                               | What You Get                                                                              | Format                                                           | Access Method                                                                                               | Timeline                                                   |
| ------------------------------------ | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Genes & Health Individual-Level Data | Imputed genotypes for ~28,000 British-Bangladeshi individuals; exome sequences for 44,028 | EGA controlled access                                            | Application through Genes & Health TRE (Trusted Research Environment); bona fide researcher status required | 2–6 months for approval; may require academic collaborator |
| Published PGx Study Raw Data         | Individual-level genotype data from the 11 published studies                              | Varies (some in supplementary materials, some by author request) | Contact corresponding authors; check supplementary files                                                    | 1–8 weeks per study, variable                              |

### 2.3 Data Extraction from Publications — Manual Curation

The 11 published pharmacogenetic studies contain allele frequency tables in their papers and supplementary materials. These must be manually extracted and standardized:

| Study                                                        | Gene(s)                   | Sample Size                 | Data Location                |
| ------------------------------------------------------------ | ------------------------- | --------------------------- | ---------------------------- |
| Sayeed et al. 2015                                           | CYP2C19 (*2, *17)         | 163 patients + 165 controls | Paper tables                 |
| Chowdhury et al. 2017                                        | VKORC1, CYP2C9 (*2, *3)   | 87 heart valve patients     | Paper tables                 |
| Drug-response SNP analysis                                   | 156 drug-response SNPs    | BEB data from 1000 Genomes  | Paper tables + supplementary |
| Mostaid et al. 2023 (review)                                 | Summary of all 11 studies | Various                     | Review paper tables          |
| Additional studies (TPMT, MTHFR, DPYD, CYP2D6, CYP3A5, etc.) | Various                   | 87–328 each                 | Individual papers            |

**Action:** Assign one team member to systematically extract all allele frequency data from these publications into a standardized spreadsheet template. This is the most labor-intensive but lowest-compute part of the project.

---

## 3. Technical Architecture

### 3.1 Database Schema

```
TABLE pharmacogenes (
    gene_id          VARCHAR(20) PRIMARY KEY,   -- e.g., CYP2D6
    gene_name        VARCHAR(100),
    chromosome       VARCHAR(5),
    grch37_start     INTEGER,
    grch37_end       INTEGER,
    grch38_start     INTEGER,
    grch38_end       INTEGER,
    function_category VARCHAR(50),              -- metabolism, transport, target, etc.
    cpic_level       CHAR(1),                    -- A, B, C, D
    pharmvar_url     TEXT
)

TABLE star_alleles (
    allele_id        VARCHAR(30) PRIMARY KEY,   -- e.g., CYP2D6*4
    gene_id          VARCHAR(20) REFERENCES pharmacogenes,
    function         VARCHAR(50),               -- no function, decreased, normal, increased, uncertain
    activity_score   DECIMAL(3,1),              -- CPIC activity score
    defining_variants TEXT,                     -- rsIDs or HGVS
    pharmvar_id      VARCHAR(50)
)

TABLE allele_frequencies (
    id               SERIAL PRIMARY KEY,
    gene_id          VARCHAR(20) REFERENCES pharmacogenes,
    allele_id        VARCHAR(30) REFERENCES star_alleles,
    variant_rsid     VARCHAR(20),               -- rsID if SNP-level
    population       VARCHAR(50),               -- BEB, Bangladeshi-resident, British-Bangladeshi, etc.
    study_id         VARCHAR(50) REFERENCES studies,
    allele_frequency DECIMAL(6,4),
    genotype_counts  JSONB,                     -- {"*1/*1": 45, "*1/*2": 12, ...}
    sample_size      INTEGER,
    confidence_interval TEXT,
    methodology      VARCHAR(100),              -- PCR-RFLP, TaqMan, NGS, array, etc.
    notes            TEXT
)

TABLE studies (
    study_id         VARCHAR(50) PRIMARY KEY,
    citation         TEXT,
    year             INTEGER,
    population_desc  TEXT,
    sample_size      INTEGER,
    methodology      VARCHAR(100),
    ethics_approval  TEXT,
    data_source      VARCHAR(50),               -- publication, 1000G, Genes&Health, etc.
    data_url         TEXT
)

TABLE drug_recommendations (
    id               SERIAL PRIMARY KEY,
    gene_id          VARCHAR(20) REFERENCES pharmacogenes,
    phenotype        VARCHAR(50),               -- poor, intermediate, normal, rapid, ultrarapid
    drug_name        VARCHAR(100),
    recommendation   TEXT,
    guideline_source VARCHAR(20),               -- CPIC, DPWG, FDA
    guideline_url    TEXT,
    evidence_level   VARCHAR(10)
)

TABLE phenotype_frequencies (
    id               SERIAL PRIMARY KEY,
    gene_id          VARCHAR(20) REFERENCES pharmacogenes,
    phenotype        VARCHAR(50),
    population       VARCHAR(50),
    frequency        DECIMAL(6,4),
    study_id         VARCHAR(50) REFERENCES studies,
    calculation_method TEXT
)
```

### 3.2 Processing Pipeline

**Step 1: Data Extraction and Harmonization (Manual + Scripted)**

- Extract allele frequencies from 11 published studies into standardized CSV template
- Download 1000 Genomes BEB VCFs, filter to pharmacogene regions using bcftools
- Calculate allele frequencies from BEB data using vcftools (`--freq2` command)
- Download Genes & Health GWAS summary statistics from public Google Cloud bucket
- Download gnomAD, IndiGen, SAGE frequency data for pharmacogene regions
- Harmonize all data to common schema (star allele nomenclature, GRCh38 coordinates, consistent population labels)

**Step 2: Variant Annotation**

- Annotate all variants with VEP or ANNOVAR (can run on laptop for pharmacogene regions only — ~20 genes, manageable size)
- Map variants to PharmVar star allele definitions
- Cross-reference with PharmGKB clinical annotations
- Assign CPIC function categories and activity scores

**Step 3: Phenotype Frequency Calculation**

- For each gene, calculate predicted metabolizer phenotype frequencies from genotype data
- Use CPIC activity score system: sum of allele activity scores → phenotype
- Calculate for each population (BEB, British-Bangladeshi, published study cohorts)
- Compare across populations

**Step 4: Drug Recommendation Mapping**

- Curate CPIC and DPWG guidelines into structured drug_recommendations table
- Map each gene-phenotype combination to drug recommendations
- Include affected drugs, dose adjustments, clinical significance

**Step 5: Database and API**

- Load all harmonized data into PostgreSQL database
- Build REST API with FastAPI (endpoints: query by gene, drug, variant, population)
- Build simple web browser for interactive queries
- Generate comparison visualizations (Bangladeshi vs global vs South Asian frequencies)

### 3.3 Technology Stack

| Component           | Tool                       | Why                                                  | Compute Need                            |
| ------------------- | -------------------------- | ---------------------------------------------------- | --------------------------------------- |
| VCF processing      | bcftools, vcftools         | Standard, lightweight, runs on laptop                | Low — filtering 86 samples to ~20 genes |
| Variant annotation  | VEP (via cache) or ANNOVAR | Industry standard; can run locally for small regions | Low — pharmacogene regions only         |
| Star allele mapping | PyPGx (Python library)     | Supports 88 pharmacogenes, open source               | Trivial — Python library                |
| Database            | PostgreSQL                 | Free, robust, supports JSONB for genotype data       | Low — database will be <1 GB            |
| API                 | FastAPI (Python)           | Fast, modern, auto-generates documentation           | Low                                     |
| Web frontend        | React or Flask + Jinja2    | Simple query interface                               | Low                                     |
| Data harmonization  | Python (pandas), R         | Standard data manipulation                           | Low                                     |
| Visualization       | Plotly, matplotlib         | Frequency comparison plots                           | Low                                     |
| Version control     | Git + GitHub/GitLab        | Code and data versioning                             | Free                                    |

### 3.4 Compute Strategy for Limited Infrastructure

**What can be done on a laptop (16–32 GB RAM):**

- All VCF filtering and allele frequency calculation for 86 BEB samples
- All variant annotation for pharmacogene regions (~20 genes, ~2 MB of sequence)
- All data harmonization and database loading
- API and web frontend development
- All visualization generation

**What would need cloud (and when):**

- If Genes & Health individual-level data is approved: processing 28,000+ exomes requires cloud compute (AWS/GCP spot instances, ~$50–100 for the job)
- If scaling to whole-genome processing later: cloud or HPC needed
- Database hosting for public access: small cloud instance (~$20–50/month)

**Recommendation:** Start entirely on local machines. Budget ~$200–500 for cloud compute when Genes & Health data access is approved. Budget ~$50/month for cloud database hosting when the product launches.

---

## 4. Team Allocation (4–8 People)

### 4.1 Minimum Viable Team (4 people)

| Role                             | Responsibility                                                                                     | Time Allocation     |
| -------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------- |
| Bioinformatician 1 (Pipeline)    | VCF processing, BEB data filtering, allele frequency calculation, variant annotation               | 100% for 3 months   |
| Bioinformatician 2 (Curation)    | Manual data extraction from 11 studies, harmonization, star allele mapping, PharmGKB/CPIC curation | 100% for 3 months   |
| Developer (Database + API)       | PostgreSQL schema, FastAPI backend, web frontend                                                   | 100% for months 2–4 |
| Founder/PI (Strategy + Outreach) | Data access applications (Genes & Health), author contacts, publication writing, investor pitches  | 50% throughout      |

### 4.2 Expanded Team (6–8 people) — Parallel Workstreams

| Role                          | Responsibility                                                                       | Time Allocation   |
| ----------------------------- | ------------------------------------------------------------------------------------ | ----------------- |
| Bioinformatician 1            | VCF processing, BEB data, annotation pipeline                                        | 100%              |
| Bioinformatician 2            | Published study data extraction and harmonization                                    | 100%              |
| Bioinformatician 3            | Genes & Health data processing (when approved), cross-population comparison analysis | 100% from month 2 |
| Developer 1                   | Database schema, API backend                                                         | 100% from month 2 |
| Developer 2                   | Web frontend, visualization, API documentation                                       | 100% from month 3 |
| Data Curator                  | CPIC/DPWG guideline curation into structured format, drug-gene mapping               | 50% for 3 months  |
| Founder/PI                    | Strategy, partnerships, publication, funding                                         | 50% throughout    |
| Scientific Writer (part-time) | Manuscript drafting, documentation                                                   | 25% from month 3  |

---

## 5. Timeline and Milestones

### Month 1: Data Collection and Harmonization

| Week | Task                                                                        | Owner                             | Deliverable                                              |
| ---- | --------------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------- |
| 1    | Download 1000 Genomes BEB VCFs; identify BEB samples from panel file        | Bioinformatician 1                | BEB VCF files filtered to pharmacogene regions           |
| 1    | Begin systematic extraction of allele frequencies from 11 published studies | Bioinformatician 2                | Standardized CSV template with first 3 studies extracted |
| 2    | Calculate allele frequencies from BEB data using vcftools                   | Bioinformatician 1                | BEB allele frequency table for all pharmacogenes         |
| 2    | Continue study extraction (studies 4–7)                                     | Bioinformatician 2                | Updated CSV with 7 studies                               |
| 3    | Download PharmGKB, CPIC, PharmVar data; begin curation                      | Bioinformatician 2 + Data Curator | Structured guideline data                                |
| 3    | Download Genes & Health GWAS summary statistics from public bucket          | Bioinformatician 1                | G&H summary stats files                                  |
| 4    | Download gnomAD, IndiGen, SAGE comparison data                              | Bioinformatician 1                | Comparison frequency tables                              |
| 4    | Complete study extraction (all 11 studies)                                  | Bioinformatician 2                | Complete raw frequency CSV                               |
| 4    | Submit Genes & Health data access application                               | Founder/PI                        | Application submitted                                    |

**Milestone 1 (End of Month 1):** All raw data collected. BEB frequencies calculated. All 11 published studies extracted. Comparison data downloaded. Genes & Health application submitted.

### Month 2: Harmonization, Annotation, and Database Building

| Week | Task                                                                                      | Owner                            | Deliverable                       |
| ---- | ----------------------------------------------------------------------------------------- | -------------------------------- | --------------------------------- |
| 5    | Harmonize all data to common schema (star allele nomenclature, GRCh38, population labels) | Bioinformatician 2               | Harmonized master frequency table |
| 5    | Annotate variants with VEP/ANNOVAR for pharmacogene regions                               | Bioinformatician 1               | Annotated variant set             |
| 6    | Map variants to PharmVar star alleles using PyPGx                                         | Bioinformatician 1               | Star allele calls for BEB samples |
| 6    | Calculate predicted phenotype frequencies using CPIC activity scores                      | Bioinformatician 1               | Phenotype frequency table         |
| 7    | Design and implement PostgreSQL database schema                                           | Developer 1                      | Database schema deployed          |
| 7    | Curate CPIC/DPWG drug recommendations into structured format                              | Data Curator                     | Drug recommendation table         |
| 8    | Load all harmonized data into PostgreSQL                                                  | Developer 1 + Bioinformatician 2 | Populated database                |

**Milestone 2 (End of Month 2):** Database populated with all harmonized data. Phenotype frequencies calculated. Drug recommendations curated. Database queryable internally.

### Month 3: API, Web Interface, and Validation

| Week | Task                                                                 | Owner                                  | Deliverable                       |
| ---- | -------------------------------------------------------------------- | -------------------------------------- | --------------------------------- |
| 9    | Build FastAPI REST API (query by gene, drug, variant, population)    | Developer 1                            | API endpoints functional          |
| 10   | Build web frontend for interactive queries                           | Developer 2                            | Web browser interface             |
| 10   | Generate comparison visualizations (population frequency plots)      | Developer 2                            | Visualization dashboard           |
| 11   | Validate data: cross-check frequencies against original publications | Bioinformatician 2                     | Validation report                 |
| 11   | Generate summary statistics and database description for publication | Bioinformatician 1 + Scientific Writer | Publication draft outline         |
| 12   | Internal testing and bug fixes                                       | All                                    | Tested, functional database + API |
| 12   | Prepare demo for investors and potential customers                   | Founder/PI                             | Investor demo deck                |

**Milestone 3 (End of Month 3):** Functional database with web interface and API. Data validated against source publications. Demo ready for investors. Publication outline drafted.

### Months 4–6: Publication, Product 2 Development, and Funding

| Month | Task                                                                                                                       | Owner                            | Deliverable                                    |
| ----- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | ---------------------------------------------- |
| 4     | Write and submit manuscript: "First consolidated pharmacogenomic allele frequency resource for the Bangladeshi population" | Founder/PI + Scientific Writer   | Manuscript submitted                           |
| 4     | Begin building Product 2 (PGx Clinical Decision Support Reporter) on top of database                                       | Developer 1 + Bioinformatician 1 | Reporter prototype                             |
| 5     | Approach diagnostic centers with database demo and reporter prototype                                                      | Founder/PI                       | First customer conversations                   |
| 5     | If Genes & Health approved: process data on cloud, add to database                                                         | Bioinformatician 3               | Expanded database with G&H data                |
| 6     | Launch Product 2 (PGx reporter) as first revenue-generating product                                                        | All                              | Product launched, first paying customer target |
| 6     | Apply for grants (Wellcome, BMGF, NIH Fogarty) using database + publication as evidence                                    | Founder/PI                       | Grant applications submitted                   |

**Milestone 6 (End of Month 6):** Manuscript submitted. Product 2 launched. First customer conversations underway. Grant applications submitted. Genes & Health data integrated (if approved).

---

## 6. Funding Strategy

### 6.1 Using the Database to Attract Investment

The PGxBD database is specifically designed to be a demonstrable proof of concept for investors because it shows three things simultaneously:

1. **Technical capability:** Your team can harmonize heterogeneous genomic data, build databases, and create APIs — the core skills for a bioinformatics company.
2. **Market opportunity:** The database quantifies a real gap (no Bangladeshi pharmacogenomic reference exists) and shows the product that fills it.
3. **Defensible asset:** The database is the first of its kind and compounds with every new sample — a moat investors can understand.

### 6.2 Funding Targets

| Funder                           | Program                              | Amount     | Timeline          | What You Need                                |
| -------------------------------- | ------------------------------------ | ---------- | ----------------- | -------------------------------------------- |
| Wellcome Trust                   | Discovery Awards or Climate & Health | £100K–500K | 6–12 month review | Database + publication + partnership letter  |
| Bill & Melinda Gates Foundation  | Grand Challenges or INVOLVE          | $100K–500K | Rolling           | Database + public health impact narrative    |
| NIH Fogarty International Center | R21 or D43 training grants           | $100K–300K | 6–9 month review  | Academic collaborator + publication          |
| USAID / Global Health            | Digital Health or One Health         | $50K–200K  | Variable          | Government partnership                       |
| Local investors (Bangladesh)     | Seed funding                         | $50K–200K  | 3–6 months        | Working product + first customer LOI         |
| Pharma partnerships              | Data licensing pilot                 | $10K–50K   | 3–6 months        | Database demo + population coverage analysis |

### 6.3 Bootstrapping Revenue (While Seeking Funding)

- **Training workshops (Product 6):** Charge BDT 5,000–15,000 per participant for bioinformatics workshops using the database as a case study. Target 20–30 participants per workshop. Revenue: BDT 100K–450K per workshop.
- **Consulting:** Offer variant interpretation consulting to diagnostic labs. Revenue: BDT 50K–200K per project.
- **Database preview access:** Offer early access to the database API to research groups for a fee. Revenue: BDT 20K–50K per group.

This revenue funds cloud hosting, compute for Genes & Health processing, and team salaries while grant and investment funding is secured.

---

## 7. Publication Strategy

### 7.1 Primary Publication

**Title:** "PGxBD: First Consolidated Pharmacogenomic Allele Frequency Resource for the Bangladeshi Population"

**Target journals (in order of fit):**

1. _Nucleic Acids Research_ (Database Issue) — ideal fit for a new database resource
2. _Clinical Pharmacology & Therapeutics_ — clinical pharmacogenomics audience
3. _Pharmacogenomics and Genomics_ — specialized audience
4. _Frontiers in Pharmacology_ — open access, faster review

**Content:**

- Description of all data sources and harmonization methods
- Allele frequency tables for all pharmacogenes across populations
- Phenotype frequency comparisons (Bangladeshi vs South Asian vs global)
- Key findings (e.g., 17 SNPs where global minor allele is major in Bangladeshis)
- Database access instructions and API documentation
- Clinical implications for drug prescribing in Bangladesh

### 7.2 Secondary Publications (Year 2)

- Population-specific pharmacogenomic analysis using Genes & Health data (if approved)
- Clinical case study: impact of Bangladeshi-specific frequencies on drug dosing recommendations
- Comparison paper: Bangladeshi vs Indian vs diaspora pharmacogenomic profiles

---

## 8. Risk Mitigation

| Risk                                           | Likelihood | Impact | Mitigation                                                                                                                                                        |
| ---------------------------------------------- | ---------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Genes & Health data access denied or delayed   | Medium     | Medium | Start with BEB + published studies; G&H is enhancement, not foundation. Summary statistics are public and usable immediately.                                     |
| Published study data is incomplete or unusable | Low        | Medium | 11 studies provide enough data for a credible database even if 2–3 are unusable. Contact authors for raw data.                                                    |
| Compute limitations block processing           | Low        | Low    | All core work fits on laptop. Cloud budget of $200–500 covers G&H processing when needed.                                                                         |
| Investor interest is low                       | Medium     | High   | Database + publication + first customer LOI is a strong pitch. Training revenue sustains operations while seeking funding.                                        |
| Competitor builds similar resource             | Low        | Medium | First-mover advantage + local curation expertise. Speed of execution is key — 3-month timeline is aggressive but achievable.                                      |
| Regulatory concerns about data usage           | Low        | Medium | Using published, publicly available data is standard scientific practice. Ensure proper attribution. Consult with local ethics committee on database publication. |
| Team member turnover                           | Medium     | Medium | Documentation of all data sources and methods. Git version control for all code. Cross-training between bioinformaticians.                                        |

---

## 9. Success Criteria

### 3-Month Success (Database Complete)

- [ ] All 11 published PGxBD studies extracted and harmonized
- [ ] 1000 Genomes BEB allele frequencies calculated for all pharmacogenes
- [ ] Genes & Health summary statistics integrated
- [ ] PostgreSQL database populated and queryable
- [ ] REST API functional with documentation
- [ ] Web interface for interactive queries
- [ ] Data validated against source publications
- [ ] Comparison visualizations generated
- [ ] Investor demo prepared

### 6-Month Success (Product + Publication)

- [ ] Manuscript submitted to peer-reviewed journal
- [ ] Product 2 (PGxBD Clinical Reporter) prototype functional
- [ ] First customer conversations with diagnostic centers
- [ ] Grant applications submitted (at least 2)
- [ ] Training workshop delivered (revenue generated)
- [ ] Genes & Health data integrated (if approved)

### 12-Month Success (Revenue + Funding)

- [ ] Publication accepted
- [ ] Product 2 generating revenue (first paying customers)
- [ ] Grant funding secured (at least 1)
- [ ] Database cited or used by external researchers
- [ ] Second product (variant browser or cancer database) in development

---

## 10. Assumptions

1. Team members have working knowledge of Python, R, and basic bioinformatics tools (bcftools, VEP/ANNOVAR). If not, 2 weeks of training is needed before Month 1.
2. At least one team member can build a PostgreSQL database and FastAPI backend. If not, a part-time developer is needed from Month 2.
3. Internet access is sufficient to download 1000 Genomes VCFs (~5–10 GB per chromosome) and Genes & Health summary statistics.
4. The 11 published studies are accessible through university library access or open access. If some are paywalled, contact authors directly.
5. Genes & Health data access application is submitted in Month 1 but approval is not required for the core database — it is an enhancement.
6. The team can dedicate the specified time allocations. If team members have other commitments, timeline extends proportionally.
7. Local ethical review is not required for database construction from published, publicly available data. This should be confirmed with a local ethics committee, but standard scientific practice supports this.
