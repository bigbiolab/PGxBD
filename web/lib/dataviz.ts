import type { Population } from "./types";

// Same 24 clinically-key variants used by scripts/07_generate_figures.py's
// fig1, so this mirrors a figure already validated against the live DB.
export const KEY_VARIANTS: { gene: string; starAllele: string }[] = [
  { gene: "CYP2C19", starAllele: "*2" },
  { gene: "CYP2C19", starAllele: "*3" },
  { gene: "CYP2C19", starAllele: "*17" },
  { gene: "CYP2C9", starAllele: "*2" },
  { gene: "CYP2C9", starAllele: "*3" },
  { gene: "CYP2D6", starAllele: "*4" },
  { gene: "CYP2D6", starAllele: "*10" },
  { gene: "CYP3A5", starAllele: "*3" },
  { gene: "CYP3A4", starAllele: "*1G" },
  { gene: "CYP3A4", starAllele: "*22" },
  { gene: "TPMT", starAllele: "*3A" },
  { gene: "TPMT", starAllele: "*3C" },
  { gene: "SLCO1B1", starAllele: "*5" },
  { gene: "SLCO1B1", starAllele: "*1B" },
  { gene: "VKORC1", starAllele: "-1639G>A" },
  { gene: "DPYD", starAllele: "*2A" },
  { gene: "DPYD", starAllele: "C29R" },
  { gene: "CYP2B6", starAllele: "*6" },
  { gene: "CYP4F2", starAllele: "*3" },
  { gene: "MTHFR", starAllele: "C677T" },
  { gene: "MTHFR", starAllele: "A1298C" },
  { gene: "F5", starAllele: "Leiden" },
  { gene: "G6PD", starAllele: "A-" },
  { gene: "G6PD", starAllele: "Mediterranean" },
];

// Capped at 4 series (the skill's mandatory-direct-label threshold) rather
// than all 7 populations, which would produce 24 x 7 = 168 bars.
export const BAR_POPULATIONS: Population[] = ["BEB", "SAS_EXCL_BEB", "EUR", "AFR"];

// Metabolizer phenotype is a true bidirectional ordered scale (Poor <-
// Normal -> Ultrarapid), so it gets a diverging ramp centered on the
// neutral "Normal" midpoint.
const METABOLIZER_ORDER = [
  "Poor Metabolizer",
  "Intermediate Metabolizer",
  "Normal Metabolizer",
  "Rapid Metabolizer",
  "Ultrarapid Metabolizer",
];
const METABOLIZER_COLOR: Record<string, string> = {
  "Poor Metabolizer": "var(--div-poor)",
  "Intermediate Metabolizer": "var(--div-intermediate)",
  "Normal Metabolizer": "var(--div-normal)",
  "Rapid Metabolizer": "var(--div-rapid)",
  "Ultrarapid Metabolizer": "var(--div-ultrarapid)",
};

// SLCO1B1 and VKORC1 are one-directional scales (no "faster than normal"
// pole), so they get a monotone single-hue ordinal ramp instead.
const ORDINAL_ORDERS: Record<string, string[]> = {
  SLCO1B1: ["Normal Function", "Decreased Function", "Low Function"],
  VKORC1: [
    "GG (normal sensitivity)",
    "GA (intermediate sensitivity)",
    "AA (high sensitivity)",
  ],
};
const ORDINAL_STEPS = ["var(--ord-1)", "var(--ord-2)", "var(--ord-3)"];

export function phenotypeOrder(gene: string): string[] {
  return ORDINAL_ORDERS[gene] ?? METABOLIZER_ORDER;
}

export function phenotypeColor(gene: string, phenotype: string): string {
  const ordinalOrder = ORDINAL_ORDERS[gene];
  if (ordinalOrder) {
    const idx = ordinalOrder.indexOf(phenotype);
    return idx >= 0 ? ORDINAL_STEPS[idx] : "var(--muted)";
  }
  return METABOLIZER_COLOR[phenotype] ?? "var(--muted)";
}

export function sequentialFill(value: number): string {
  const alpha = 0.1 + Math.min(1, Math.max(0, value)) * 0.8;
  return `color-mix(in srgb, var(--accent) ${Math.round(alpha * 100)}%, transparent)`;
}
