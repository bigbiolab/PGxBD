import { Suspense } from "react";
import { getDrugs, getGenes } from "@/lib/api";
import DrugsExplorer from "@/components/DrugsExplorer";

export const metadata = { title: "Drugs — PGxBD" };

export default async function DrugsPage() {
  const [genes, drugs] = await Promise.all([getGenes(), getDrugs()]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Drug Recommendations</h1>
      </div>
      <Suspense fallback={<div className="h-16 rounded-xl border border-border bg-surface" />}>
        <DrugsExplorer drugs={drugs} genes={genes} />
      </Suspense>
    </div>
  );
}
