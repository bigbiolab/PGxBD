"""
Pydantic response models for the PGxBD API.

These models document the shape of API responses in the OpenAPI schema.
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Gene models
# ---------------------------------------------------------------------------
class Pharmacogene(BaseModel):
    gene_id: str
    gene_name: str
    chromosome: str
    grch37_start: Optional[int] = None
    grch37_end: Optional[int] = None
    grch38_start: Optional[int] = None
    grch38_end: Optional[int] = None
    function_category: Optional[str] = None
    cpic_level: Optional[str] = None
    pharmgkb_id: Optional[str] = None
    pharmvar_url: Optional[str] = None


class StarAllele(BaseModel):
    allele_id: str
    gene_id: str
    function: Optional[str] = None
    activity_score: Optional[float] = None
    defining_variants: Optional[str] = None
    pharmvar_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Frequency models
# ---------------------------------------------------------------------------
class AlleleFrequency(BaseModel):
    id: int
    gene_id: str
    allele_id: Optional[str] = None
    variant_rsid: str
    population: str
    study_id: Optional[str] = None
    allele_frequency: float
    genotype_counts: Optional[Union[str, Dict[str, Any]]] = None
    sample_size: int
    confidence_interval: Optional[str] = None
    methodology: Optional[str] = None
    notes: Optional[str] = None


class PhenotypeFrequency(BaseModel):
    id: int
    gene_id: str
    phenotype: str
    population: str
    frequency: float
    study_id: Optional[str] = None
    calculation_method: Optional[str] = None


# ---------------------------------------------------------------------------
# Drug recommendation model
# ---------------------------------------------------------------------------
class DrugRecommendation(BaseModel):
    id: int
    gene_id: str
    phenotype: str
    drug_name: str
    recommendation: Optional[str] = None
    guideline_source: Optional[str] = None
    guideline_url: Optional[str] = None
    evidence_level: Optional[str] = None
    cpic_level: Optional[str] = None
    fda_label: Optional[str] = None


# ---------------------------------------------------------------------------
# Aggregated / comparison models
# ---------------------------------------------------------------------------
class PopulationFrequency(BaseModel):
    allele_frequency: float
    sample_size: int
    confidence_interval: Optional[str] = None
    genotype_counts: Optional[Dict[str, Any]] = None


class VariantComparison(BaseModel):
    rsid: str
    gene: str
    populations: Dict[str, PopulationFrequency]


class GeneDetail(BaseModel):
    gene: Pharmacogene
    star_alleles: List[StarAllele]
    beb_allele_frequencies: List[AlleleFrequency]
    beb_phenotype_frequencies: List[PhenotypeFrequency]
    drug_recommendations: List[DrugRecommendation]


class APIInfo(BaseModel):
    name: str
    version: str
    description: str
    statistics: Dict[str, int]
    endpoints: List[str]
