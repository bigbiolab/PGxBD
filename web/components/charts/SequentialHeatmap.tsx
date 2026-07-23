import MarkTooltip from "./MarkTooltip";
import { sequentialFill } from "@/lib/dataviz";
import { POPULATION_ORDER, POPULATION_N } from "@/lib/types";
import type { VariantComparison } from "@/lib/types";

export default function SequentialHeatmap({ variants }: { variants: VariantComparison[] }) {
  const sorted = [...variants].sort((a, b) =>
    a.gene === b.gene ? a.rsid.localeCompare(b.rsid) : a.gene.localeCompare(b.gene)
  );

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3 text-xs text-muted">
        <span>Allele frequency</span>
        <div className="flex items-center gap-1">
          <span>0</span>
          <div
            className="h-2.5 w-24 rounded-sm"
            style={{
              background: "linear-gradient(to right, color-mix(in srgb, var(--accent) 10%, transparent), var(--accent))",
            }}
          />
          <span>1</span>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[820px] border-separate border-spacing-1 p-1 text-xs">
          <thead>
            <tr>
              <th className="sticky left-0 z-10 bg-surface px-2 py-1 text-left font-medium text-muted">
                Variant
              </th>
              {POPULATION_ORDER.map((pop) => (
                <th key={pop} className="px-1 py-1 text-center font-medium text-muted">
                  {pop}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((v) => (
              <tr key={`${v.gene}-${v.rsid}`}>
                <td className="sticky left-0 z-10 bg-surface px-2 py-1 font-medium">
                  {v.gene} <span className="font-mono text-muted">{v.rsid}</span>
                </td>
                {POPULATION_ORDER.map((pop) => {
                  const cell = v.populations[pop];
                  const freq = cell?.allele_frequency;
                  return (
                    <td key={pop} className="p-0 text-center">
                      {freq === undefined ? (
                        <div className="flex h-8 items-center justify-center text-muted">—</div>
                      ) : (
                        <MarkTooltip
                          className="block h-8 w-full"
                          tooltip={
                            <>
                              <span className="font-semibold tabular-nums">{freq.toFixed(3)}</span>{" "}
                              <span className="text-muted">
                                {v.gene} {v.rsid} · {pop} (N={cell.sample_size ?? POPULATION_N[pop]})
                              </span>
                            </>
                          }
                        >
                          <div
                            className="flex h-8 w-full items-center justify-center rounded-md tabular-nums"
                            style={{ background: sequentialFill(freq) }}
                          >
                            {freq.toFixed(2)}
                          </div>
                        </MarkTooltip>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
