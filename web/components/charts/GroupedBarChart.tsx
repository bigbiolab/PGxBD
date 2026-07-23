import MarkTooltip from "./MarkTooltip";
import Legend from "./Legend";
import { KEY_VARIANTS, BAR_POPULATIONS } from "@/lib/dataviz";
import { POPULATION_COLOR_VAR } from "@/lib/colors";
import type { AlleleFrequency } from "@/lib/types";

export default function GroupedBarChart({ frequencies }: { frequencies: AlleleFrequency[] }) {
  const byKey = new Map<string, AlleleFrequency>();
  for (const f of frequencies) {
    byKey.set(`${f.gene_id}|${f.star_allele}|${f.population}`, f);
  }

  const rows = KEY_VARIANTS.map(({ gene, starAllele }) => ({
    gene,
    starAllele,
    bars: BAR_POPULATIONS.map((pop) => ({
      population: pop,
      row: byKey.get(`${gene}|${starAllele}|${pop}`),
    })),
  })).filter((row) => row.bars.some((b) => b.row));

  return (
    <div className="flex flex-col gap-4">
      <Legend
        items={BAR_POPULATIONS.map((pop) => ({ label: pop, color: POPULATION_COLOR_VAR[pop] }))}
      />
      <div className="flex flex-col divide-y divide-border rounded-xl border border-border bg-surface">
        {rows.map(({ gene, starAllele, bars }) => (
          <div key={`${gene}-${starAllele}`} className="grid grid-cols-[9rem_1fr] items-center gap-3 px-3 py-2">
            <span className="truncate text-xs font-medium" title={`${gene} ${starAllele}`}>
              {gene} <span className="text-muted">{starAllele}</span>
            </span>
            <div className="flex flex-col gap-0.5">
              {bars.map(({ population, row }) => (
                <div key={population} className="flex h-3 items-center gap-1.5">
                  <div className="relative h-2.5 flex-1 overflow-hidden rounded-full bg-surface-muted">
                    {row && (
                      <div
                        className="absolute inset-y-0 left-0"
                        style={{ width: `${Math.max(2, Math.min(1, row.allele_frequency) * 100)}%` }}
                      >
                        <MarkTooltip
                          className="h-full w-full"
                          tooltip={
                            <>
                              <span className="font-semibold tabular-nums">
                                {row.allele_frequency.toFixed(3)}
                              </span>{" "}
                              <span className="text-muted">
                                {gene} {starAllele} · {population} (N={row.sample_size})
                              </span>
                            </>
                          }
                        >
                          <div
                            className="h-full w-full rounded-full"
                            style={{ background: POPULATION_COLOR_VAR[population] }}
                          />
                        </MarkTooltip>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
