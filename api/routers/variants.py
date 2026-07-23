"""
Variants router – list all key PGx variants with cross-population frequencies.
"""

import json
from fastapi import APIRouter, Depends
import sqlite3

from ..database import get_db

router = APIRouter(prefix="/variants", tags=["variants"])


@router.get("")
def list_variants(conn: sqlite3.Connection = Depends(get_db)):
    """List all key pharmacogenomic variants with their frequencies across
    all populations. Returns a variant-centric list, each entry containing
    a per-population breakdown."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT DISTINCT af.gene_id, af.variant_rsid, af.population,
               af.allele_frequency, af.sample_size, af.genotype_counts,
               af.confidence_interval, af.notes
        FROM allele_frequencies af
        WHERE af.variant_rsid IS NOT NULL
        ORDER BY af.gene_id, af.variant_rsid, af.population
        """
    )
    rows = cursor.fetchall()

    variants: dict = {}
    for row in rows:
        r = dict(row)
        key = r["variant_rsid"]
        if key not in variants:
            variants[key] = {
                "rsid": r["variant_rsid"],
                "gene": r["gene_id"],
                "populations": {},
            }
        gc = r.get("genotype_counts")
        if gc:
            try:
                gc = json.loads(gc)
            except (json.JSONDecodeError, TypeError):
                pass
        variants[key]["populations"][r["population"]] = {
            "allele_frequency": r["allele_frequency"],
            "sample_size": r["sample_size"],
            "confidence_interval": r["confidence_interval"],
            "genotype_counts": gc,
        }

    return list(variants.values())
