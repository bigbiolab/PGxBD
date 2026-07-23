import type {
  ApiInfo,
  DrugRecommendation,
  GeneDetail,
  AlleleFrequency,
  Pharmacogene,
  PhenotypeFrequency,
  VariantComparison,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, params?: Record<string, string | undefined>): Promise<T> {
  const url = new URL(path, API_BASE);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value) url.searchParams.set(key, value);
    }
  }
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`PGxBD API request failed: ${res.status} ${url.toString()}`);
  }
  return res.json() as Promise<T>;
}

export const getApiInfo = () => apiFetch<ApiInfo>("/");

export const getGenes = () => apiFetch<Pharmacogene[]>("/genes");

export async function getGeneDetail(geneId: string): Promise<GeneDetail | null> {
  const url = new URL(`/genes/${encodeURIComponent(geneId)}`, API_BASE);
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`PGxBD API request failed: ${res.status} ${url.toString()}`);
  return res.json() as Promise<GeneDetail>;
}

export const getFrequencies = (filters?: {
  gene?: string;
  population?: string;
  rsid?: string;
}) => apiFetch<AlleleFrequency[]>("/frequencies", filters);

export const comparePopulations = (filters?: { gene?: string; rsid?: string }) =>
  apiFetch<VariantComparison[]>("/frequencies/compare", filters);

export const getPhenotypes = (filters?: { gene?: string; population?: string }) =>
  apiFetch<PhenotypeFrequency[]>("/phenotypes", filters);

export const getDrugs = (filters?: {
  gene?: string;
  drug_name?: string;
  cpic_level?: string;
}) => apiFetch<DrugRecommendation[]>("/drugs", filters);

export const getVariants = () => apiFetch<VariantComparison[]>("/variants");
