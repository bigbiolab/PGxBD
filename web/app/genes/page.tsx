import Link from "next/link";
import { getGenes } from "@/lib/api";

export const metadata = { title: "Genes — PGxBD" };

export default async function GenesPage() {
  const genes = await getGenes();

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Pharmacogenes</h1>
        <p className="mt-1 text-sm text-muted">{genes.length} genes in the database.</p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {genes.map((gene) => (
          <Link
            key={gene.gene_id}
            href={`/genes/${gene.gene_id}`}
            className="rounded-xl border border-border bg-surface p-4 transition-colors hover:border-accent"
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold">{gene.gene_id}</span>
              {gene.cpic_level && (
                <span className="rounded-md border border-border px-1.5 py-0.5 text-[10px] font-medium text-muted">
                  CPIC {gene.cpic_level}
                </span>
              )}
            </div>
            {gene.gene_name && (
              <p className="mt-1 text-xs text-muted">{gene.gene_name}</p>
            )}
            {gene.function_category && (
              <p className="mt-2 text-xs text-muted">{gene.function_category}</p>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
