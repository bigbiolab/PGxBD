"""
Tests for the PGxBD API.

Run with:
    pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------
def test_api_info():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "PGxBD: Bangladeshi Pharmacogenomic Frequency Database"
    assert data["version"] == "2.0.0"
    assert "statistics" in data
    assert data["statistics"]["pharmacogenes"] == 18
    assert data["statistics"]["allele_frequencies"] == 203
    assert data["statistics"]["phenotype_frequencies"] == 138


# ---------------------------------------------------------------------------
# Genes
# ---------------------------------------------------------------------------
def test_list_genes():
    resp = client.get("/genes")
    assert resp.status_code == 200
    genes = resp.json()
    assert len(genes) == 18
    gene_ids = {g["gene_id"] for g in genes}
    assert "CYP2D6" in gene_ids
    assert "CYP3A5" in gene_ids


def test_get_gene_detail():
    resp = client.get("/genes/CYP2D6")
    assert resp.status_code == 200
    data = resp.json()
    assert data["gene"]["gene_id"] == "CYP2D6"
    assert len(data["star_alleles"]) > 0
    assert len(data["beb_allele_frequencies"]) > 0
    assert len(data["drug_recommendations"]) > 0


def test_get_gene_not_found():
    resp = client.get("/genes/FAKEGENE")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Frequencies
# ---------------------------------------------------------------------------
def test_get_frequencies_all():
    resp = client.get("/frequencies")
    assert resp.status_code == 200
    freqs = resp.json()
    assert len(freqs) == 203


def test_get_frequencies_by_gene():
    resp = client.get("/frequencies?gene=CYP3A5")
    assert resp.status_code == 200
    freqs = resp.json()
    assert all(f["gene_id"] == "CYP3A5" for f in freqs)
    assert len(freqs) > 0


def test_get_frequencies_by_population():
    resp = client.get("/frequencies?population=BEB")
    assert resp.status_code == 200
    freqs = resp.json()
    assert all(f["population"] == "BEB" for f in freqs)
    # 29 variants for BEB
    assert len(freqs) == 29


def test_get_frequencies_by_rsid():
    resp = client.get("/frequencies?rsid=rs776746")
    assert resp.status_code == 200
    freqs = resp.json()
    assert all(f["variant_rsid"] == "rs776746" for f in freqs)
    # 7 populations
    assert len(freqs) == 7


def test_compare_populations():
    resp = client.get("/frequencies/compare?gene=CYP3A5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    # Each entry should have population breakdowns
    assert "populations" in data[0]
    assert "BEB" in data[0]["populations"]


# ---------------------------------------------------------------------------
# Phenotypes
# ---------------------------------------------------------------------------
def test_get_phenotypes_all():
    resp = client.get("/phenotypes")
    assert resp.status_code == 200
    phenos = resp.json()
    assert len(phenos) == 138


def test_get_phenotypes_by_gene():
    resp = client.get("/phenotypes?gene=CYP2C19")
    assert resp.status_code == 200
    phenos = resp.json()
    assert all(p["gene_id"] == "CYP2C19" for p in phenos)


def test_phenotype_sums_to_one():
    """For each gene/population, phenotype frequencies should sum to ~1.0."""
    resp = client.get("/phenotypes?population=BEB")
    assert resp.status_code == 200
    phenos = resp.json()
    from collections import defaultdict

    sums = defaultdict(float)
    for p in phenos:
        sums[p["gene_id"]] += p["frequency"]
    for gene, total in sums.items():
        assert abs(total - 1.0) < 0.01, f"{gene} phenotypes sum to {total}, not 1.0"


# ---------------------------------------------------------------------------
# Drugs
# ---------------------------------------------------------------------------
def test_get_drugs_all():
    resp = client.get("/drugs")
    assert resp.status_code == 200
    drugs = resp.json()
    assert len(drugs) == 2020


def test_get_drugs_by_gene():
    resp = client.get("/drugs?gene=CYP2D6")
    assert resp.status_code == 200
    drugs = resp.json()
    assert all(d["gene_id"] == "CYP2D6" for d in drugs)


def test_get_drugs_by_cpic_level():
    resp = client.get("/drugs?cpic_level=A")
    assert resp.status_code == 200
    drugs = resp.json()
    assert all(d["cpic_level"] == "A" for d in drugs)


# ---------------------------------------------------------------------------
# Variants
# ---------------------------------------------------------------------------
def test_list_variants():
    resp = client.get("/variants")
    assert resp.status_code == 200
    variants = resp.json()
    assert len(variants) == 29
    # Check that each variant has population data
    for v in variants:
        assert "rsid" in v
        assert "gene" in v
        assert "populations" in v
        assert "BEB" in v["populations"]


def test_variant_cyp3a5_correction():
    """CYP3A5*3 (rs776746) BEB frequency should be ~0.634 (corrected)."""
    resp = client.get("/variants")
    assert resp.status_code == 200
    variants = resp.json()
    cyp3a5 = [v for v in variants if v["rsid"] == "rs776746"][0]
    beb_af = cyp3a5["populations"]["BEB"]["allele_frequency"]
    assert 0.60 < beb_af < 0.67, f"CYP3A5*3 BEB AF={beb_af}, expected ~0.634"


def test_variant_g6pd_correction():
    """G6PD rs1050828 BEB frequency should be 0.0 (corrected)."""
    resp = client.get("/variants")
    assert resp.status_code == 200
    variants = resp.json()
    g6pd = [v for v in variants if v["rsid"] == "rs1050828"][0]
    beb_af = g6pd["populations"]["BEB"]["allele_frequency"]
    assert beb_af == 0.0, f"G6PD rs1050828 BEB AF={beb_af}, expected 0.0"
