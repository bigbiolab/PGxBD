"""
PGxBD API – FastAPI application entry point.

Run with:
    uvicorn api.main:app --reload --port 8000

API docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

from .database import get_db
from .routers import genes, frequencies, phenotypes, drugs, variants

app = FastAPI(
    title="PGxBD: Bangladeshi Pharmacogenomic Frequency Database",
    description=(
        "Pharmacogenomic allele frequency database for the Bangladeshi "
        "population (BEB, N=86), built from 1000 Genomes Project phase 3 "
        "data with corrected allele orientation and full HWE phenotype "
        "computation."
    ),
    version="2.0.0",
)

# CORS – allow web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(genes.router)
app.include_router(frequencies.router)
app.include_router(phenotypes.router)
app.include_router(drugs.router)
app.include_router(variants.router)


@app.get("/", tags=["info"])
def api_info(conn: sqlite3.Connection = Depends(get_db)):
    """API information and database statistics."""
    cursor = conn.cursor()
    stats = {}
    for table in [
        "pharmacogenes",
        "star_alleles",
        "studies",
        "allele_frequencies",
        "drug_recommendations",
        "phenotype_frequencies",
    ]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]

    return {
        "name": "PGxBD: Bangladeshi Pharmacogenomic Frequency Database",
        "version": "2.0.0",
        "description": (
            "Pharmacogenomic allele frequency database for the Bangladeshi "
            "population, built from 1000 Genomes Project phase 3 data."
        ),
        "statistics": stats,
        "endpoints": [
            "/genes",
            "/genes/{gene_id}",
            "/frequencies",
            "/frequencies/compare",
            "/phenotypes",
            "/drugs",
            "/variants",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
