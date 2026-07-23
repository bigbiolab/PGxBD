"use client";

import { useMemo } from "react";
import { useSearchParams } from "next/navigation";
import FilterBar from "@/components/FilterBar";
import FrequencyBar from "@/components/FrequencyBar";
import PopulationBadge from "@/components/PopulationBadge";
import { POPULATION_ORDER, type PhenotypeFrequency, type Pharmacogene, type Population } from "@/lib/types";

export default function PhenotypesExplorer({
  phenotypes,
  genes,
}: {
  phenotypes: PhenotypeFrequency[];
  genes: Pharmacogene[];
}) {
  const searchParams = useSearchParams();
  const gene = searchParams.get("gene") ?? undefined;
  const population = searchParams.get("population") ?? undefined;

  const filtered = useMemo(
    () =>
      phenotypes.filter(
        (p) => (!gene || p.gene_id === gene) && (!population || p.population === population)
      ),
    [phenotypes, gene, population]
  );

  return (
    <div className="flex flex-col gap-6">
      <p className="text-sm text-muted">
        {filtered.length} rows — Hardy-Weinberg-derived metabolizer/function phenotype
        frequencies.
      </p>

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
            {filtered.map((p, i) => (
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
            {filtered.length === 0 && (
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
