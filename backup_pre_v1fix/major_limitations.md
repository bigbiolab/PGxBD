Major Limitations
The CYP3A5*3 (rs776746) allele orientation is flipped: reported *3 frequencies are EUR 5.7% and AFR 82%, whereas the established *3 frequency is ~92% in Europeans and the minor allele (~24%) in Africans, so the reported values actually correspond to the *1 (functional) allele. Confidence: High.

Evidence: "CYP3A5 *3 ... 0.3663 0.3323 0.0567 0.2867 0.8200" 

rs2242480 is mislabeled as CYP3A422; it is in fact the CYP3A41G defining variant, and the true *22 variant is rs35599367, so the reported "CYP3A4 *22" frequencies (BEB 37%, AFR 85%) describe *1G, not *22. Confidence: High.

Evidence: "'rs2242480': {'gene': 'CYP3A4', ... 'star_allele': '*22', 'function': 'decreased function'}" 

The CYP2C19 Hardy-Weinberg phenotype expansion omits the no-function/*17 compound-heterozygote class, so the BEB phenotype frequencies sum to only 0.923 rather than 1.0. Confidence: High.

Evidence: "Poor Metabolizer: 0.1217 ... Intermediate Metabolizer: 0.3772 ... Normal Metabolizer: 0.2924 ... Rapid Metabolizer: 0.1195 ... Ultrarapid Metabolizer: 0.0122" 

Other Limitations
CYP2D6 phenotype frequencies were computed from a single SNP (rs3892097, *4) via HWE, ignoring the *10 allele (BEB 0.256, decreased function) that was already in hand as well as CNVs (*5 deletion, duplications), which understates intermediate metabolizers.

Evidence: "CYP2D6: use *4 (rs3892097) as primary no-function allele" 

The chrX gene G6PD was processed with uniform diploid genotype counting (two alleles per sample) with no handling of male hemizygosity, biasing X-linked allele-frequency and genotype-count estimates.

Evidence: "total_count += 2 # diploid" 

The primary "South Asian" comparison (SAS) contains the BEB samples themselves, since BEB is a subpopulation of the 1000G SAS superpopulation, so BEB-vs-SAS contrasts are not independent.

Evidence: "'SAS': set(panel_df[panel_df['super_pop'] == 'SAS']['sample'].tolist())" 

gnomAD integration largely failed (only 7 of 29 variants retrieved by rsID; all position-based queries returned nothing), so cross-cohort validation relies on 1000G INFO-field and dbSNP MAFs rather than an independent reference.

Evidence: "rs1057910: NOT FOUND by position 10:96741053 A>C ... Total gnomAD variants: 7" 

Allele orientation was decided by matching each variant to a manually entered "expected" frequency rather than an authoritative strand-aware definition, making REF/ALT assignment (and the CYP3A5 error above) dependent on the correctness of those hardcoded expectations.

Evidence: "'rs776746': {'gene': 'CYP3A5', 'star': '*3', 'expected_beb': 0.37, 'pgx_allele': 'ALT'}"