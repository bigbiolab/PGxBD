import { Suspense } from "react";
import { getFrequencies, getGenes } from "@/lib/api";
import FrequenciesExplorer from "@/components/FrequenciesExplorer";

export const metadata = { title: "Frequencies — PGxBD" };

export default async function FrequenciesPage() {
  const [genes, frequencies] = await Promise.all([getGenes(), getFrequencies()]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Allele Frequencies</h1>
      </div>
      <Suspense fallback={<div className="h-16 rounded-xl border border-border bg-surface" />}>
        <FrequenciesExplorer frequencies={frequencies} genes={genes} />
      </Suspense>
    </div>
  );
}
