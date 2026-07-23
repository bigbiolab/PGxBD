#!/usr/bin/env python3
"""
07_generate_figures.py
======================
Generate publication-quality PNG figures from the corrected PGxBD data.

Figures:
  1. Frequency comparison bar chart (BEB vs EUR vs AFR for key variants)
  2. Allele frequency heatmap (all variants × all populations)
  3. BEB vs EUR scatter plot (allele frequency correlation)
  4. Phenotype frequencies grouped bar chart (BEB vs SAS_EXCL_BEB vs EUR)
  5. Top frequency differences (BEB vs EUR, ranked)

All figures saved to figures/ as PNG.
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rc_params = matplotlib.rcParams
import seaborn as sns

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FREQ_FILE = PROJECT_ROOT / "data" / "processed" / "allele_frequencies" / "corrected_frequencies.csv"
PHENO_FILE = PROJECT_ROOT / "data" / "processed" / "phenotypes" / "phenotype_frequencies.csv"
FIG_DIR = PROJECT_ROOT / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Phylo color palette
PHYLO_COLORS = {
    "BEB": "#FF9400",
    "SAS_EXCL_BEB": "#FD9BED",
    "SAS": "#E9ED4C",
    "EUR": "#0279EE",
    "EAS": "#75A025",
    "AFR": "#000000",
    "AMR": "#FAF9F3",
}

# Font settings
rc_params["font.family"] = ["Liberation Sans", "Arimo", "DejaVu Sans"]
rc_params["svg.fonttype"] = "none"
rc_params["figure.dpi"] = 150
rc_params["savefig.dpi"] = 300
rc_params["savefig.bbox"] = "tight"

# Population display order
POP_ORDER = ["BEB", "SAS_EXCL_BEB", "SAS", "EUR", "EAS", "AFR", "AMR"]
POP_LABELS = {
    "BEB": "BEB\n(N=86)",
    "SAS_EXCL_BEB": "SAS excl. BEB\n(N=403)",
    "SAS": "SAS\n(N=489)",
    "EUR": "EUR\n(N=503)",
    "EAS": "EAS\n(N=504)",
    "AFR": "AFR\n(N=661)",
    "AMR": "AMR\n(N=347)",
}


def load_data():
    freq = pd.read_csv(FREQ_FILE)
    pheno = pd.read_csv(PHENO_FILE)
    return freq, pheno


def variant_label(row):
    """Create a readable label like 'CYP2D6 *4'."""
    gene = row["gene"]
    allele = row["star_allele"]
    return f"{gene} {allele}"


# ---------------------------------------------------------------------------
# Figure 1: Frequency comparison bar chart
# ---------------------------------------------------------------------------
def fig1_frequency_comparison_bar(freq):
    """Grouped bar chart comparing BEB, EUR, and AFR for key variants."""
    # Select key clinically important variants
    key_variants = [
        ("CYP2C19", "*2"), ("CYP2C19", "*3"), ("CYP2C19", "*17"),
        ("CYP2C9", "*2"), ("CYP2C9", "*3"),
        ("CYP2D6", "*4"), ("CYP2D6", "*10"),
        ("CYP3A5", "*3"),
        ("CYP3A4", "*1G"), ("CYP3A4", "*22"),
        ("TPMT", "*3A"), ("TPMT", "*3C"),
        ("SLCO1B1", "*5"), ("SLCO1B1", "*1B"),
        ("VKORC1", "-1639G>A"),
        ("DPYD", "*2A"), ("DPYD", "C29R"),
        ("CYP2B6", "*6"),
        ("CYP4F2", "*3"),
        ("MTHFR", "C677T"), ("MTHFR", "A1298C"),
        ("F5", "Leiden"),
        ("G6PD", "A-"), ("G6PD", "Mediterranean"),
    ]

    key_pops = ["BEB", "EUR", "AFR"]
    rows = []
    for gene, allele in key_variants:
        mask = (freq["gene"] == gene) & (freq["star_allele"] == allele)
        for pop in key_pops:
            r = freq[mask & (freq["population"] == pop)]
            if len(r) > 0:
                rows.append({
                    "label": f"{gene} {allele}",
                    "population": pop,
                    "frequency": r["pgx_allele_frequency"].values[0],
                })

    df = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(16, 8))
    labels = df["label"].unique()
    x = np.arange(len(labels))
    width = 0.25

    for i, pop in enumerate(key_pops):
        vals = [df[(df["label"] == l) & (df["population"] == pop)]["frequency"].values
                for l in labels]
        vals = [v[0] if len(v) > 0 else 0 for v in vals]
        ax.bar(x + i * width, vals, width, label=POP_LABELS[pop],
               color=PHYLO_COLORS[pop], edgecolor="white", linewidth=0.5)

    ax.set_xticks(x + width)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Allele Frequency", fontsize=11)
    ax.set_title("Pharmacogenomic Allele Frequencies: BEB vs EUR vs AFR", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(0, 1.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = FIG_DIR / "pgxbd_frequency_comparison_bar.png"
    plt.savefig(out)
    plt.close()
    print(f"  -> {out.name}")


# ---------------------------------------------------------------------------
# Figure 2: Allele frequency heatmap
# ---------------------------------------------------------------------------
def fig2_frequency_heatmap(freq):
    """Heatmap of all variant frequencies across all populations."""
    # Create variant labels
    freq = freq.copy()
    freq["variant_label"] = freq.apply(
        lambda r: f"{r['gene']} {r['star_allele']}", axis=1
    )

    # Pivot: rows=variants, cols=populations
    pivot = freq.pivot_table(
        index="variant_label", columns="population",
        values="pgx_allele_frequency", aggfunc="first"
    )
    # Reorder columns
    pivot = pivot[[p for p in POP_ORDER if p in pivot.columns]]
    # Sort by gene then allele
    pivot = pivot.sort_index()

    fig, ax = plt.subplots(figsize=(10, 14))
    sns.heatmap(
        pivot, annot=True, fmt=".3f", cmap="YlOrRd",
        linewidths=0.5, ax=ax, cbar_kws={"label": "Allele Frequency"},
        vmin=0, vmax=1,
    )
    ax.set_title("PGx Allele Frequencies Across Populations", fontsize=13, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticklabels([POP_LABELS.get(c, c) for c in pivot.columns],
                       rotation=0, fontsize=9)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)

    plt.tight_layout()
    out = FIG_DIR / "pgxbd_frequency_heatmap.png"
    plt.savefig(out)
    plt.close()
    print(f"  -> {out.name}")


# ---------------------------------------------------------------------------
# Figure 3: BEB vs EUR scatter
# ---------------------------------------------------------------------------
def fig3_beb_vs_eur_scatter(freq):
    """Scatter plot of BEB vs EUR allele frequencies with diagonal reference."""
    pivot = freq.pivot_table(
        index=["gene", "star_allele", "rsid"],
        columns="population", values="pgx_allele_frequency", aggfunc="first"
    ).reset_index()

    if "BEB" not in pivot.columns or "EUR" not in pivot.columns:
        print("  [skip] BEB or EUR column missing")
        return

    fig, ax = plt.subplots(figsize=(8, 8))

    # Color points by gene
    genes = pivot["gene"].unique()
    palette = sns.color_palette("husl", n_colors=len(genes))
    gene_colors = dict(zip(genes, palette))

    for gene in genes:
        subset = pivot[pivot["gene"] == gene]
        ax.scatter(
            subset["EUR"], subset["BEB"],
            label=gene, color=gene_colors[gene],
            s=60, alpha=0.8, edgecolors="white", linewidth=0.5,
        )

    # Diagonal reference line
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, linewidth=1)

    # Annotate notable outliers
    for _, row in pivot.iterrows():
        diff = abs(row["BEB"] - row["EUR"])
        if diff > 0.25:
            label = f"{row['gene']} {row['star_allele']}"
            ax.annotate(
                label, (row["EUR"], row["BEB"]),
                fontsize=7, ha="left", va="bottom",
                xytext=(4, 4), textcoords="offset points",
            )

    ax.set_xlabel("EUR Allele Frequency", fontsize=11)
    ax.set_ylabel("BEB Allele Frequency", fontsize=11)
    ax.set_title("BEB vs EUR Allele Frequencies", fontsize=13, fontweight="bold")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper left", fontsize=7, ncol=2, framealpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_aspect("equal")
    ax.grid(alpha=0.2)

    # Correlation
    corr = pivot["BEB"].corr(pivot["EUR"])
    ax.text(0.05, 0.95, f"Pearson r = {corr:.3f}", transform=ax.transAxes,
            fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    out = FIG_DIR / "pgxbd_beb_vs_eur_scatter.png"
    plt.savefig(out)
    plt.close()
    print(f"  -> {out.name}")


# ---------------------------------------------------------------------------
# Figure 4: Phenotype frequencies
# ---------------------------------------------------------------------------
def fig4_phenotype_frequencies(pheno):
    """Grouped bar chart of phenotype frequencies for BEB, SAS_EXCL_BEB, EUR."""
    key_pops = ["BEB", "SAS_EXCL_BEB", "EUR"]
    genes = pheno["gene_id"].unique()

    n_genes = len(genes)
    fig, axes = plt.subplots(n_genes, 1, figsize=(12, 3 * n_genes), squeeze=False)

    for idx, gene in enumerate(sorted(genes)):
        ax = axes[idx, 0]
        gene_data = pheno[pheno["gene_id"] == gene]

        phenotypes = gene_data["phenotype"].unique()
        x = np.arange(len(phenotypes))
        width = 0.25

        for i, pop in enumerate(key_pops):
            vals = []
            for p in phenotypes:
                r = gene_data[(gene_data["phenotype"] == p) & (gene_data["population"] == pop)]
                vals.append(r["frequency"].values[0] if len(r) > 0 else 0)
            ax.bar(x + i * width, vals, width,
                   label=POP_LABELS[pop], color=PHYLO_COLORS[pop],
                   edgecolor="white", linewidth=0.5)

        ax.set_xticks(x + width)
        ax.set_xticklabels(phenotypes, rotation=20, ha="right", fontsize=8)
        ax.set_ylabel("Frequency", fontsize=9)
        ax.set_title(gene, fontsize=11, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", alpha=0.3)
        if idx == 0:
            ax.legend(loc="upper right", fontsize=8)

    fig.suptitle("Phenotype Frequencies: BEB vs SAS (excl. BEB) vs EUR",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = FIG_DIR / "pgxbd_phenotype_frequencies.png"
    plt.savefig(out)
    plt.close()
    print(f"  -> {out.name}")


# ---------------------------------------------------------------------------
# Figure 5: Top frequency differences (BEB vs EUR)
# ---------------------------------------------------------------------------
def fig5_top_differences(freq):
    """Horizontal bar chart of largest BEB vs EUR frequency differences."""
    pivot = freq.pivot_table(
        index=["gene", "star_allele"],
        columns="population", values="pgx_allele_frequency", aggfunc="first"
    ).reset_index()

    if "BEB" not in pivot.columns or "EUR" not in pivot.columns:
        print("  [skip] BEB or EUR column missing")
        return

    pivot["diff"] = pivot["BEB"] - pivot["EUR"]
    pivot["label"] = pivot["gene"] + " " + pivot["star_allele"]
    pivot = pivot.sort_values("diff")

    # Take top 10 and bottom 10
    top_diff = pd.concat([pivot.head(10), pivot.tail(10)])

    fig, ax = plt.subplots(figsize=(10, 10))
    colors = ["#0279EE" if d < 0 else "#FF9400" for d in top_diff["diff"]]
    ax.barh(top_diff["label"], top_diff["diff"], color=colors,
            edgecolor="white", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("BEB - EUR Allele Frequency Difference", fontsize=11)
    ax.set_title("Top Allele Frequency Differences: BEB vs EUR", fontsize=13, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.3)

    # Add value labels
    for i, (label, diff) in enumerate(zip(top_diff["label"], top_diff["diff"])):
        ha = "left" if diff > 0 else "right"
        offset = 0.01 if diff > 0 else -0.01
        ax.text(diff + offset, i, f"{diff:+.3f}", va="center", ha=ha, fontsize=8)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#FF9400", label="Higher in BEB"),
        Patch(facecolor="#0279EE", label="Higher in EUR"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

    plt.tight_layout()
    out = FIG_DIR / "pgxbd_top_differences.png"
    plt.savefig(out)
    plt.close()
    print(f"  -> {out.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=== 07_generate_figures.py ===")
    print("Loading data...")
    freq, pheno = load_data()
    print(f"  Frequencies: {freq.shape[0]} rows, {freq['gene'].nunique()} genes, "
          f"{freq['population'].nunique()} populations")
    print(f"  Phenotypes: {pheno.shape[0]} rows, {pheno['gene_id'].nunique()} genes")

    print("\nGenerating figures...")
    fig1_frequency_comparison_bar(freq)
    fig2_frequency_heatmap(freq)
    fig3_beb_vs_eur_scatter(freq)
    fig4_phenotype_frequencies(pheno)
    fig5_top_differences(freq)

    print(f"\nAll figures saved to {FIG_DIR}/")


if __name__ == "__main__":
    main()
