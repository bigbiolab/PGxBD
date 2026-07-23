"""
Frequencies router – query and compare allele frequencies.
"""

import json
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
import sqlite3

from ..database import get_db
from ..models import AlleleFrequency

router = APIRouter(prefix="/frequencies", tags=["frequencies"])


@router.get("", response_model=List[AlleleFrequency])
def get_frequencies(
    gene: Optional[str] = Query(None, description="Filter by gene (e.g., CYP2D6)"),
    population: Optional[str] = Query(
        None, description="Filter by population (BEB, SAS_EXCL_BEB, SAS, EUR, EAS, AFR, AMR)"
    ),
    rsid: Optional[str] = Query(None, description="Filter by variant rsID (e.g., rs9923231)"),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Query allele frequencies with optional filters for gene, population, and rsID."""
    query = "SELECT * FROM allele_frequencies WHERE 1=1"
    params: list = []

    if gene:
        query += " AND gene_id = ?"
        params.append(gene)
    if population:
        query += " AND population = ?"
        params.append(population)
    if rsid:
        query += " AND variant_rsid = ?"
        params.append(rsid)

    query += " ORDER BY gene_id, population, variant_rsid"
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()

    results = []
    for row in rows:
        r = dict(row)
        if r.get("genotype_counts"):
            try:
                r["genotype_counts"] = json.loads(r["genotype_counts"])
            except (json.JSONDecodeError, TypeError):
                pass
        results.append(r)
    return results


@router.get("/compare")
def compare_populations(
    gene: Optional[str] = Query(None, description="Filter by gene"),
    rsid: Optional[str] = Query(None, description="Filter by variant rsID"),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Compare allele frequencies across populations for a gene or variant.
    Returns a list of variant-centric objects, each with a per-population
    breakdown of allele frequency, sample size, and genotype counts."""
    query = """
        SELECT gene_id, variant_rsid, population, allele_frequency,
               sample_size, confidence_interval, genotype_counts
        FROM allele_frequencies
        WHERE 1=1
    """
    params: list = []
    if gene:
        query += " AND gene_id = ?"
        params.append(gene)
    if rsid:
        query += " AND variant_rsid = ?"
        params.append(rsid)

    query += " ORDER BY gene_id, variant_rsid, population"
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()

    comparisons: dict = {}
    for row in rows:
        r = dict(row)
        key = f"{r['gene_id']}_{r['variant_rsid']}"
        if key not in comparisons:
            comparisons[key] = {
                "gene": r["gene_id"],
                "rsid": r["variant_rsid"],
                "populations": {},
            }
        gc = r.get("genotype_counts")
        if gc:
            try:
                gc = json.loads(gc)
            except (json.JSONDecodeError, TypeError):
                pass
        comparisons[key]["populations"][r["population"]] = {
            "allele_frequency": r["allele_frequency"],
            "sample_size": r["sample_size"],
            "confidence_interval": r["confidence_interval"],
            "genotype_counts": gc,
        }

    return list(comparisons.values())
