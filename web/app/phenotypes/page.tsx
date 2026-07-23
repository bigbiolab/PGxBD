import { Suspense } from "react";
import { getPhenotypes, getGenes } from "@/lib/api";
import PhenotypesExplorer from "@/components/PhenotypesExplorer";

export const metadata = { title: "Phenotypes — PGxBD" };

export default async function PhenotypesPage() {
  const [genes, phenotypes] = await Promise.all([getGenes(), getPhenotypes()]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Phenotype Frequencies</h1>
      </div>
      <Suspense fallback={<div className="h-16 rounded-xl border border-border bg-surface" />}>
        <PhenotypesExplorer phenotypes={phenotypes} genes={genes} />
      </Suspense>
    </div>
  );
}
