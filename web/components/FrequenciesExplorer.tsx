"use client";

import { useMemo } from "react";
import { useSearchParams } from "next/navigation";
import FilterBar from "@/components/FilterBar";
import FrequencyBar from "@/components/FrequencyBar";
import PopulationBadge from "@/components/PopulationBadge";
import { POPULATION_ORDER, type AlleleFrequency, type Pharmacogene, type Population } from "@/lib/types";

export default function FrequenciesExplorer({
  frequencies,
  genes,
}: {
  frequencies: AlleleFrequency[];
  genes: Pharmacogene[];
}) {
  const searchParams = useSearchParams();
  const gene = searchParams.get("gene") ?? undefined;
  const population = searchParams.get("population") ?? undefined;
  const rsid = searchParams.get("rsid") ?? undefined;

  const filtered = useMemo(
    () =>
      frequencies.filter(
        (f) =>
          (!gene || f.gene_id === gene) &&
          (!population || f.population === population) &&
          (!rsid || f.variant_rsid?.toLowerCase().includes(rsid.toLowerCase()))
      ),
    [frequencies, gene, population, rsid]
  );

  return (
    <div className="flex flex-col gap-6">
      <p className="text-sm text-muted">{filtered.length} rows.</p>

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
            {filtered.map((f, i) => (
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
            {filtered.length === 0 && (
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
