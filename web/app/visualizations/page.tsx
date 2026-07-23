import Link from "next/link";
import { getFrequencies, getPhenotypes, getVariants } from "@/lib/api";
import SequentialHeatmap from "@/components/charts/SequentialHeatmap";
import GroupedBarChart from "@/components/charts/GroupedBarChart";
import DivergingPhenotypeBars from "@/components/charts/DivergingPhenotypeBars";

export const metadata = { title: "Visualizations — PGxBD" };

export default async function VisualizationsPage() {
  const [variants, frequencies, phenotypes] = await Promise.all([
    getVariants(),
    getFrequencies(),
    getPhenotypes(),
  ]);

  return (
    <div className="flex flex-col gap-12">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Visualizations</h1>
        <p className="mt-1 max-w-2xl text-sm text-muted">
          Interactive views of the same data behind the Frequencies, Phenotypes, and
          Variants tables. Hover or focus any mark for the exact value.
        </p>
      </div>

      <section className="flex flex-col gap-3">
        <div className="flex items-baseline justify-between">
          <div>
            <h2 className="text-sm font-semibold">
              Key clinical variants — allele frequency by population
            </h2>
            <p className="mt-1 text-xs text-muted">
              24 clinically actionable star alleles, 4 comparison populations.
            </p>
          </div>
          <Link href="/frequencies" className="shrink-0 text-xs text-accent hover:underline">
            View as table →
          </Link>
        </div>
        <GroupedBarChart frequencies={frequencies} />
      </section>

      <section className="flex flex-col gap-3">
        <div className="flex items-baseline justify-between">
          <div>
            <h2 className="text-sm font-semibold">All variants across all populations</h2>
            <p className="mt-1 text-xs text-muted">
              Every key PGx variant, allele frequency by population (magnitude, one hue).
            </p>
          </div>
          <Link href="/variants" className="shrink-0 text-xs text-accent hover:underline">
            View as table →
          </Link>
        </div>
        <SequentialHeatmap variants={variants} />
      </section>

      <section className="flex flex-col gap-3">
        <div className="flex items-baseline justify-between">
          <div>
            <h2 className="text-sm font-semibold">Phenotype distribution by population</h2>
            <p className="mt-1 text-xs text-muted">
              Metabolizer/function phenotype share per population, for a selected gene.
            </p>
          </div>
          <Link href="/phenotypes" className="shrink-0 text-xs text-accent hover:underline">
            View as table →
          </Link>
        </div>
        <DivergingPhenotypeBars phenotypes={phenotypes} />
      </section>
    </div>
  );
}
