import { Suspense } from "react";
import { getFrequencies, getGenes } from "@/lib/api";
import FilterBar from "@/components/FilterBar";
import FrequencyBar from "@/components/FrequencyBar";
import PopulationBadge from "@/components/PopulationBadge";
import { POPULATION_ORDER, type Population } from "@/lib/types";

export const metadata = { title: "Frequencies — PGxBD" };

export default async function FrequenciesPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const gene = typeof params.gene === "string" ? params.gene : undefined;
  const population = typeof params.population === "string" ? params.population : undefined;
  const rsid = typeof params.rsid === "string" ? params.rsid : undefined;

  const [genes, frequencies] = await Promise.all([
    getGenes(),
    getFrequencies({ gene, population, rsid }),
  ]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Allele Frequencies</h1>
        <p className="mt-1 text-sm text-muted">{frequencies.length} rows.</p>
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
            { name: "rsid", label: "rsID", type: "text", placeholder: "rs776746" },
          ]}
        />
      </Suspense>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[720px] text-sm">
          <thead className="bg-surface-muted text-left text-xs text-muted">
            <tr>
              <th className="px-3 py-2 font-medium">Gene</th>
              <th className="px-3 py-2 font-medium">rsID</th>
              <th className="px-3 py-2 font-medium">Star allele</th>
              <th className="px-3 py-2 font-medium">Population</th>
              <th className="px-3 py-2 font-medium">Frequency</th>
              <th className="px-3 py-2 font-medium">N</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {frequencies.map((f, i) => (
              <tr key={`${f.gene_id}-${f.variant_rsid}-${f.population}-${i}`} className="bg-surface">
                <td className="px-3 py-2 font-medium">{f.gene_id}</td>
                <td className="px-3 py-2 font-mono text-xs">{f.variant_rsid}</td>
                <td className="px-3 py-2 text-muted">{f.star_allele || "—"}</td>
                <td className="px-3 py-2">
                  <PopulationBadge population={f.population as Population} />
                </td>
                <td className="px-3 py-2">
                  <FrequencyBar value={f.allele_frequency} population={f.population as Population} />
                </td>
                <td className="px-3 py-2 text-muted">{f.sample_size ?? "—"}</td>
              </tr>
            ))}
            {frequencies.length === 0 && (
              <tr>
                <td colSpan={6} className="px-3 py-6 text-center text-muted">
                  No frequencies match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
