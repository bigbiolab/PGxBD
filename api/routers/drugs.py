"""
Drugs router – query drug recommendations.
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List
import sqlite3

from ..database import get_db
from ..models import DrugRecommendation

router = APIRouter(prefix="/drugs", tags=["drugs"])


@router.get("", response_model=List[DrugRecommendation])
def get_drugs(
    gene: Optional[str] = Query(None, description="Filter by gene"),
    drug_name: Optional[str] = Query(None, description="Filter by drug name (partial match)"),
    cpic_level: Optional[str] = Query(None, description="Filter by CPIC level (A, B, C, D)"),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Query drug recommendations with optional filters for gene, drug name,
    and CPIC evidence level."""
    query = "SELECT * FROM drug_recommendations WHERE 1=1"
    params: list = []

    if gene:
        query += " AND gene_id = ?"
        params.append(gene)
    if drug_name:
        query += " AND drug_name LIKE ?"
        params.append(f"%{drug_name}%")
    if cpic_level:
        query += " AND cpic_level = ?"
        params.append(cpic_level)

    query += " ORDER BY gene_id, drug_name"
    cursor = conn.cursor()
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]
