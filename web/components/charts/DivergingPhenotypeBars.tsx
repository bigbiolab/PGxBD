"use client";

import { useMemo, useState } from "react";
import MarkTooltip from "./MarkTooltip";
import Legend from "./Legend";
import { phenotypeColor, phenotypeOrder } from "@/lib/dataviz";
import { POPULATION_ORDER, type PhenotypeFrequency } from "@/lib/types";

const GENES = ["CYP2D6", "CYP2C19", "CYP2C9", "CYP3A5", "TPMT", "SLCO1B1", "VKORC1"];

export default function DivergingPhenotypeBars({
  phenotypes,
}: {
  phenotypes: PhenotypeFrequency[];
}) {
  const [gene, setGene] = useState("CYP2D6");

  const byPopulation = useMemo(() => {
    const map = new Map<string, PhenotypeFrequency[]>();
    for (const p of phenotypes) {
      if (p.gene_id !== gene) continue;
      const list = map.get(p.population) ?? [];
      list.push(p);
      map.set(p.population, list);
    }
    return map;
  }, [phenotypes, gene]);

  const order = phenotypeOrder(gene);
  const populations = POPULATION_ORDER.filter((pop) => byPopulation.has(pop));

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <label className="flex items-center gap-2 text-xs text-muted">
          Gene
          <select
            value={gene}
            onChange={(e) => setGene(e.target.value)}
            className="rounded-md border border-border bg-background px-2 py-1.5 text-sm text-foreground"
          >
            {GENES.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </label>
        <Legend
          items={order.map((phenotype) => ({
            label: phenotype,
            color: phenotypeColor(gene, phenotype),
          }))}
        />
      </div>

      <div className="flex flex-col gap-2 rounded-xl border border-border bg-surface p-4">
        {populations.map((pop) => {
          const rows = (byPopulation.get(pop) ?? [])
            .slice()
            .sort((a, b) => order.indexOf(a.phenotype) - order.indexOf(b.phenotype));
          return (
            <div key={pop} className="grid grid-cols-[7rem_1fr] items-center gap-3">
              <span className="text-xs font-medium">{pop}</span>
              <div className="flex h-5 gap-0.5 overflow-hidden rounded-full bg-surface-muted">
                {rows.map((r) => (
                  <MarkTooltip
                    key={r.phenotype}
                    className="h-full"
                    style={{ width: `${Math.max(0, r.frequency) * 100}%` }}
                    tooltip={
                      <>
                        <span className="font-semibold tabular-nums">
                          {(r.frequency * 100).toFixed(1)}%
                        </span>{" "}
                        <span className="text-muted">
                          {pop} · {r.phenotype}
                        </span>
                      </>
                    }
                  >
                    <div
                      className="h-full w-full"
                      style={{ background: phenotypeColor(gene, r.phenotype) }}
                    />
                  </MarkTooltip>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
