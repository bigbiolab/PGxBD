import type { Population } from "./types";

export const POPULATION_COLOR_VAR: Record<Population, string> = {
  BEB: "var(--pop-beb)",
  SAS_EXCL_BEB: "var(--pop-sas-excl-beb)",
  SAS: "var(--pop-sas)",
  EUR: "var(--pop-eur)",
  EAS: "var(--pop-eas)",
  AFR: "var(--pop-afr)",
  AMR: "var(--pop-amr)",
};

export function functionColor(fn: string | null | undefined): string {
  const f = (fn ?? "").toLowerCase();
  if (f.includes("no function") || f.includes("poor")) return "var(--pop-amr)";
  if (f.includes("decreased") || f.includes("intermediate")) return "var(--pop-sas)";
  if (f.includes("increased") || f.includes("rapid") || f.includes("ultra")) return "var(--pop-eas)";
  if (f.includes("normal") || f.includes("uncertain")) return "var(--muted)";
  return "var(--muted)";
}

export function cpicLevelColor(level: string | null | undefined): string {
  switch ((level ?? "").toUpperCase()) {
    case "A":
      return "var(--pop-eas)";
    case "B":
      return "var(--pop-sas)";
    case "C":
    case "D":
      return "var(--pop-amr)";
    default:
      return "var(--muted)";
  }
}
