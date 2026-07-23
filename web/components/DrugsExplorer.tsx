"use client";

import { useMemo } from "react";
import { useSearchParams } from "next/navigation";
import FilterBar from "@/components/FilterBar";
import Badge from "@/components/Badge";
import { cpicLevelColor } from "@/lib/colors";
import type { DrugRecommendation, Pharmacogene } from "@/lib/types";

export default function DrugsExplorer({
  drugs,
  genes,
}: {
  drugs: DrugRecommendation[];
  genes: Pharmacogene[];
}) {
  const searchParams = useSearchParams();
  const gene = searchParams.get("gene") ?? undefined;
  const drugName = searchParams.get("drug_name") ?? undefined;
  const cpicLevel = searchParams.get("cpic_level") ?? undefined;

  const filtered = useMemo(
    () =>
      drugs.filter(
        (d) =>
          (!gene || d.gene_id === gene) &&
          (!drugName || d.drug_name?.toLowerCase().includes(drugName.toLowerCase())) &&
          (!cpicLevel || d.cpic_level === cpicLevel)
      ),
    [drugs, gene, drugName, cpicLevel]
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
          { name: "drug_name", label: "Drug name", type: "text", placeholder: "clopidogrel" },
          {
            name: "cpic_level",
            label: "CPIC level",
            type: "select",
            options: ["A", "B", "C", "D"].map((l) => ({ value: l, label: l })),
          },
        ]}
      />

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[720px] text-sm">
          <thead className="bg-surface-muted text-left text-xs text-muted">
            <tr>
              <th className="px-3 py-2 font-medium">Gene</th>
              <th className="px-3 py-2 font-medium">Drug</th>
              <th className="px-3 py-2 font-medium">Phenotype</th>
              <th className="px-3 py-2 font-medium">Recommendation</th>
              <th className="px-3 py-2 font-medium">Source</th>
              <th className="px-3 py-2 font-medium">CPIC</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {filtered.map((d, i) => (
              <tr key={`${d.gene_id}-${d.drug_name}-${i}`} className="bg-surface align-top">
                <td className="px-3 py-2 font-medium">{d.gene_id}</td>
                <td className="px-3 py-2">{d.drug_name}</td>
                <td className="px-3 py-2 text-muted">{d.phenotype}</td>
                <td className="px-3 py-2 text-muted">{d.recommendation}</td>
                <td className="px-3 py-2 text-muted">{d.guideline_source}</td>
                <td className="px-3 py-2">
                  {d.cpic_level ? (
                    <Badge color={cpicLevelColor(d.cpic_level)}>{d.cpic_level}</Badge>
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={6} className="px-3 py-6 text-center text-muted">
                  No drug recommendations match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
