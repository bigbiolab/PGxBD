import { Suspense } from "react";
import { getPhenotypes, getGenes } from "@/lib/api";
import FilterBar from "@/components/FilterBar";
import FrequencyBar from "@/components/FrequencyBar";
import PopulationBadge from "@/components/PopulationBadge";
import { POPULATION_ORDER, type Population } from "@/lib/types";

export const metadata = { title: "Phenotypes — PGxBD" };

export default async function PhenotypesPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const gene = typeof params.gene === "string" ? params.gene : undefined;
  const population = typeof params.population === "string" ? params.population : undefined;

  const [genes, phenotypes] = await Promise.all([
    getGenes(),
    getPhenotypes({ gene, population }),
  ]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Phenotype Frequencies</h1>
        <p className="mt-1 text-sm text-muted">
          {phenotypes.length} rows — Hardy-Weinberg-derived metabolizer/function phenotype
          frequencies.
        </p>
      </div>

      <Suspense fallback={<div className="h-16 rounded-xl border border-border bg-surface" />}>
        <FilterBar
          fields={[
            {
              name: "gene",
              label: "Gene",
              type: "select",
              options: genes.map((g) => ({ value: g.gene_id, label: g.gene_id })),
            },
            {
              name: "population",
              label: "Population",
              type: "select",
              options: POPULATION_ORDER.map((p) => ({ value: p, label: p })),
            },
          ]}
        />
      </Suspense>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[560px] text-sm">
          <thead className="bg-surface-muted text-left text-xs text-muted">
            <tr>
              <th className="px-3 py-2 font-medium">Gene</th>
              <th className="px-3 py-2 font-medium">Phenotype</th>
              <th className="px-3 py-2 font-medium">Population</th>
              <th className="px-3 py-2 font-medium">Frequency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {phenotypes.map((p, i) => (
              <tr key={`${p.gene_id}-${p.phenotype}-${p.population}-${i}`} className="bg-surface">
                <td className="px-3 py-2 font-medium">{p.gene_id}</td>
                <td className="px-3 py-2">{p.phenotype}</td>
                <td className="px-3 py-2">
                  <PopulationBadge population={p.population as Population} />
                </td>
                <td className="px-3 py-2">
                  <FrequencyBar value={p.frequency} population={p.population as Population} />
                </td>
              </tr>
            ))}
            {phenotypes.length === 0 && (
              <tr>
                <td colSpan={4} className="px-3 py-6 text-center text-muted">
                  No phenotype frequencies match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
