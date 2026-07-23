import { POPULATION_COLOR_VAR } from "@/lib/colors";
import type { Population } from "@/lib/types";

export default function FrequencyBar({
  value,
  population,
  showValue = true,
}: {
  value: number;
  population?: Population;
  showValue?: boolean;
}) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  const color = population ? POPULATION_COLOR_VAR[population] : "var(--accent)";

  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-surface-muted">
        <div
          className="h-full rounded-full"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      {showValue && (
        <span className="tabular-nums text-xs text-muted">{value.toFixed(3)}</span>
      )}
    </div>
  );
}
