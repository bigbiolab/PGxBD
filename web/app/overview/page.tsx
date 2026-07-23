import Link from "next/link";
import { getApiInfo, getGenes } from "@/lib/api";
import StatCard from "@/components/StatCard";
import PopulationBadge from "@/components/PopulationBadge";
import { POPULATION_ORDER } from "@/lib/types";

export const metadata = { title: "Overview — PGxBD" };

const CORRECTIONS = [
  "CYP3A5*3 allele orientation corrected (BEB 0.366 → 0.634)",
  "CYP3A4*22 vs *1G mislabel fixed; true *22 (rs35599367) added",
  "CYP2C19 compound heterozygotes (*2/*17, *3/*17) now included in HWE",
  "G6PD frequencies recomputed with chrX-aware hemizygous counting",
  "DPYD *2A vs C29R mislabel fixed",
  "CYP2D6 *10 decreased-function allele included (activity score 0.25)",
  "SAS_EXCL_BEB added as an independent comparison population",
];

export default async function OverviewPage() {
  const [info, genes] = await Promise.all([getApiInfo(), getGenes()]);

  return (
    <div className="flex flex-col gap-10">
      <section>
        <p className="text-xs font-medium uppercase tracking-wide text-accent">
          v{info.version}
        </p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight">Database Overview</h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-muted">
          {info.description} Frequencies are computed for 29 key PGx variants across 7
          populations, with star-allele and phenotype frequencies derived under
          Hardy-Weinberg equilibrium.
        </p>
      </section>

      <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <StatCard label="Pharmacogenes" value={info.statistics.pharmacogenes} />
        <StatCard label="Star alleles" value={info.statistics.star_alleles} />
        <StatCard label="Allele frequencies" value={info.statistics.allele_frequencies} />
        <StatCard
          label="Phenotype frequencies"
          value={info.statistics.phenotype_frequencies}
        />
        <StatCard label="Drug recommendations" value={info.statistics.drug_recommendations} />
        <StatCard label="Source studies" value={info.statistics.studies} />
      </section>

      <section>
        <h2 className="text-sm font-semibold">Populations</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {POPULATION_ORDER.map((pop) => (
            <PopulationBadge key={pop} population={pop} withN />
          ))}
        </div>
      </section>

      <section>
        <div className="flex items-baseline justify-between">
          <h2 className="text-sm font-semibold">Pharmacogenes ({genes.length})</h2>
          <Link href="/genes" className="text-xs text-accent hover:underline">
            View all
          </Link>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
          {genes.map((gene) => (
            <Link
              key={gene.gene_id}
              href={`/genes/${gene.gene_id}`}
              className="rounded-lg border border-border bg-surface px-3 py-2.5 text-sm font-medium transition-colors hover:border-accent hover:text-accent"
            >
              {gene.gene_id}
            </Link>
          ))}
        </div>
      </section>

      <section id="corrections">
        <h2 className="text-sm font-semibold">Corrections applied (through v2.0.0)</h2>
        <ul className="mt-3 grid gap-2 sm:grid-cols-2">
          {CORRECTIONS.map((item) => (
            <li
              key={item}
              className="flex gap-2 rounded-lg border border-border bg-surface px-3 py-2.5 text-sm leading-5"
            >
              <span className="mt-0.5 text-accent">✓</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
