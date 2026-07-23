export type Population =
  | "BEB"
  | "SAS_EXCL_BEB"
  | "SAS"
  | "EUR"
  | "EAS"
  | "AFR"
  | "AMR";

export const POPULATION_ORDER: Population[] = [
  "BEB",
  "SAS_EXCL_BEB",
  "SAS",
  "EUR",
  "EAS",
  "AFR",
  "AMR",
];

export const POPULATION_LABELS: Record<Population, string> = {
  BEB: "Bengali (Bangladesh)",
  SAS_EXCL_BEB: "South Asian, excl. BEB",
  SAS: "South Asian (all)",
  EUR: "European",
  EAS: "East Asian",
  AFR: "African",
  AMR: "Admixed American",
};

export const POPULATION_N: Record<Population, number> = {
  BEB: 86,
  SAS_EXCL_BEB: 403,
  SAS: 489,
  EUR: 503,
  EAS: 504,
  AFR: 661,
  AMR: 347,
};

export interface ApiInfo {
  name: string;
  version: string;
  description: string;
  statistics: {
    pharmacogenes: number;
    star_alleles: number;
    studies: number;
    allele_frequencies: number;
    drug_recommendations: number;
    phenotype_frequencies: number;
  };
  endpoints: string[];
}

export interface Pharmacogene {
  gene_id: string;
  gene_name: string;
  chromosome: string;
  grch37_start: number | null;
  grch37_end: number | null;
  grch38_start: number | null;
  grch38_end: number | null;
  function_category: string;
  cpic_level: string;
  pharmgkb_id: string;
  pharmvar_url: string;
}

export interface StarAllele {
  allele_id: number;
  gene_id: string;
  star_allele: string;
  function: string;
  defining_variants: string | null;
  pharmvar_id: string | null;
}

export interface AlleleFrequency {
  gene_id: string;
  star_allele?: string;
  variant_rsid: string;
  population: Population;
  allele_frequency: number;
  pgx_allele_frequency?: number;
  sample_size: number;
  confidence_interval: string | null;
  genotype_counts: Record<string, number> | null;
  notes?: string | null;
}

export interface PhenotypeFrequency {
  gene_id: string;
  population: Population;
  phenotype: string;
  frequency: number;
  sample_size?: number;
}

export interface DrugRecommendation {
  gene_id: string;
  drug_name: string;
  phenotype: string;
  recommendation: string;
  guideline_source: string;
  evidence_level: string;
  cpic_level: string;
  fda_label?: string;
}

export interface GeneDetail {
  gene: Pharmacogene;
  star_alleles: StarAllele[];
  beb_allele_frequencies: AlleleFrequency[];
  beb_phenotype_frequencies: PhenotypeFrequency[];
  drug_recommendations: DrugRecommendation[];
}

export interface PopulationBreakdown {
  allele_frequency: number;
  sample_size: number;
  confidence_interval: string | null;
  genotype_counts: Record<string, number> | null;
}

export interface VariantComparison {
  gene: string;
  rsid: string;
  populations: Record<string, PopulationBreakdown>;
}
