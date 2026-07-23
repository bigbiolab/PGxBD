import { POPULATION_COLOR_VAR } from "@/lib/colors";
import { POPULATION_N, type Population } from "@/lib/types";

export default function PopulationBadge({
  population,
  withN = false,
}: {
  population: Population | string;
  withN?: boolean;
}) {
  const pop = population as Population;
  const color = POPULATION_COLOR_VAR[pop] ?? "var(--muted)";
  const n = POPULATION_N[pop];

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface px-2 py-0.5 text-xs font-medium">
      <span className="pop-swatch" style={{ background: color }} />
      {population}
      {withN && n ? <span className="text-muted">N={n}</span> : null}
    </span>
  );
}
