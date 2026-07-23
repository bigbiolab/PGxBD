import { Suspense } from "react";
import { getDrugs, getGenes } from "@/lib/api";
import FilterBar from "@/components/FilterBar";
import Badge from "@/components/Badge";
import { cpicLevelColor } from "@/lib/colors";

export const metadata = { title: "Drugs — PGxBD" };

export default async function DrugsPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const gene = typeof params.gene === "string" ? params.gene : undefined;
  const drug_name = typeof params.drug_name === "string" ? params.drug_name : undefined;
  const cpic_level = typeof params.cpic_level === "string" ? params.cpic_level : undefined;

  const [genes, drugs] = await Promise.all([
    getGenes(),
    getDrugs({ gene, drug_name, cpic_level }),
  ]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Drug Recommendations</h1>
        <p className="mt-1 text-sm text-muted">{drugs.length} rows.</p>
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
            { name: "drug_name", label: "Drug name", type: "text", placeholder: "clopidogrel" },
            {
              name: "cpic_level",
              label: "CPIC level",
              type: "select",
              options: ["A", "B", "C", "D"].map((l) => ({ value: l, label: l })),
            },
          ]}
        />
      </Suspense>

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
            {drugs.map((d, i) => (
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
            {drugs.length === 0 && (
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
