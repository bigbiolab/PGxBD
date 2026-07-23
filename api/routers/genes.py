"""
Genes router – list and detail endpoints for pharmacogenes.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import sqlite3

from ..database import get_db
from ..models import Pharmacogene, StarAllele, AlleleFrequency, PhenotypeFrequency, DrugRecommendation

router = APIRouter(prefix="/genes", tags=["genes"])


@router.get("", response_model=List[Pharmacogene])
def list_genes(conn: sqlite3.Connection = Depends(get_db)):
    """List all pharmacogenes in the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pharmacogenes ORDER BY gene_id")
    return [dict(row) for row in cursor.fetchall()]


@router.get("/{gene_id}")
def get_gene(gene_id: str, conn: sqlite3.Connection = Depends(get_db)):
    """Get detailed information about a specific pharmacogene, including its
    star alleles, BEB allele frequencies, BEB phenotype frequencies, and
    drug recommendations."""
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pharmacogenes WHERE gene_id = ?", (gene_id,))
    gene = cursor.fetchone()
    if not gene:
        raise HTTPException(status_code=404, detail=f"Gene {gene_id} not found")

    cursor.execute(
        "SELECT * FROM star_alleles WHERE gene_id = ? ORDER BY allele_id",
        (gene_id,),
    )
    alleles = [dict(r) for r in cursor.fetchall()]

    cursor.execute(
        """SELECT * FROM allele_frequencies
           WHERE gene_id = ? AND population = 'BEB'
           ORDER BY variant_rsid""",
        (gene_id,),
    )
    beb_freqs = [dict(r) for r in cursor.fetchall()]

    cursor.execute(
        """SELECT * FROM phenotype_frequencies
           WHERE gene_id = ? AND population = 'BEB'
           ORDER BY frequency DESC""",
        (gene_id,),
    )
    beb_phenos = [dict(r) for r in cursor.fetchall()]

    cursor.execute(
        """SELECT DISTINCT drug_name, phenotype, recommendation,
                  guideline_source, evidence_level, cpic_level, fda_label
           FROM drug_recommendations
           WHERE gene_id = ?
           ORDER BY drug_name""",
        (gene_id,),
    )
    drugs = [dict(r) for r in cursor.fetchall()]

    return {
        "gene": dict(gene),
        "star_alleles": alleles,
        "beb_allele_frequencies": beb_freqs,
        "beb_phenotype_frequencies": beb_phenos,
        "drug_recommendations": drugs,
    }
