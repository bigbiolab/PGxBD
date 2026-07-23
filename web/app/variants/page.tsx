import { getVariants } from "@/lib/api";
import { POPULATION_ORDER, type Population } from "@/lib/types";
import { POPULATION_COLOR_VAR } from "@/lib/colors";

export const metadata = { title: "Variants — PGxBD" };

function heatCell(freq: number | undefined, color: string) {
  if (freq === undefined) {
    return <span className="text-muted">—</span>;
  }
  const alpha = 0.12 + Math.min(1, freq) * 0.68;
  return (
    <div
      className="rounded-md px-2 py-1 text-center tabular-nums"
      style={{ backgroundColor: colorMix(color, alpha) }}
    >
      {freq.toFixed(3)}
    </div>
  );
}

function colorMix(cssVar: string, alpha: number) {
  return `color-mix(in srgb, ${cssVar} ${Math.round(alpha * 100)}%, transparent)`;
}

export default async function VariantsPage() {
  const variants = await getVariants();
  const sorted = [...variants].sort((a, b) =>
    a.gene === b.gene ? a.rsid.localeCompare(b.rsid) : a.gene.localeCompare(b.gene)
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Variants Across Populations</h1>
        <p className="mt-1 text-sm text-muted">
          {sorted.length} key PGx variants, allele frequency by population.
        </p>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[820px] text-sm">
          <thead className="bg-surface-muted text-left text-xs text-muted">
            <tr>
              <th className="sticky left-0 bg-surface-muted px-3 py-2 font-medium">Gene</th>
              <th className="px-3 py-2 font-medium">rsID</th>
              {POPULATION_ORDER.map((pop) => (
                <th key={pop} className="px-2 py-2 text-center font-medium">
                  {pop}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {sorted.map((v) => (
              <tr key={`${v.gene}-${v.rsid}`} className="bg-surface">
                <td className="sticky left-0 bg-surface px-3 py-2 font-medium">{v.gene}</td>
                <td className="px-3 py-2 font-mono text-xs">{v.rsid}</td>
                {POPULATION_ORDER.map((pop) => (
                  <td key={pop} className="px-2 py-1.5">
                    {heatCell(
                      v.populations[pop]?.allele_frequency,
                      POPULATION_COLOR_VAR[pop as Population]
                    )}
                  </td>
                ))}
              </tr>
            ))}
            {sorted.length === 0 && (
              <tr>
                <td colSpan={2 + POPULATION_ORDER.length} className="px-3 py-6 text-center text-muted">
                  No variant data available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
