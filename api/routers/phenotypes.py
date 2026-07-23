"""
Phenotypes router – query phenotype frequencies.
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List
import sqlite3

from ..database import get_db
from ..models import PhenotypeFrequency

router = APIRouter(prefix="/phenotypes", tags=["phenotypes"])


@router.get("", response_model=List[PhenotypeFrequency])
def get_phenotypes(
    gene: Optional[str] = Query(None, description="Filter by gene"),
    population: Optional[str] = Query(
        None, description="Filter by population (BEB, SAS_EXCL_BEB, SAS, EUR, EAS, AFR, AMR)"
    ),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Query phenotype frequencies with optional filters for gene and population."""
    query = "SELECT * FROM phenotype_frequencies WHERE 1=1"
    params: list = []

    if gene:
        query += " AND gene_id = ?"
        params.append(gene)
    if population:
        query += " AND population = ?"
        params.append(population)

    query += " ORDER BY gene_id, population, frequency DESC"
    cursor = conn.cursor()
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]
