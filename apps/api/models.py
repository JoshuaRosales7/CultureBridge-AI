"""
Pydantic models for API request/response validation.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------- Request Models ----------


class OverrideDimensions(BaseModel):
    """Optional dimension overrides for manual tuning."""

    uncertainty_avoidance: Optional[float] = Field(None, ge=0, le=100)
    collectivism: Optional[float] = Field(None, ge=0, le=100)
    authority_distance: Optional[float] = Field(None, ge=0, le=100)
    context_level: Optional[float] = Field(None, ge=0, le=100)
    price_sensitivity: Optional[float] = Field(None, ge=0, le=100)
    trust_need: Optional[float] = Field(None, ge=0, le=100)
    friction_tolerance: Optional[float] = Field(None, ge=0, le=100)


class AdaptRequest(BaseModel):
    """POST /api/adapt request body."""

    country_code: str = Field(..., pattern="^(JP|GT|DE)$", description="Target region")
    product_category: str = Field(
        ...,
        pattern="^(electronics|fashion|food_beverage|home_garden|health_beauty)$",
    )
    price_band: str = Field(..., pattern="^(budget|mid|premium|luxury)$")
    audience: str = Field(
        ...,
        pattern="^(general_consumer|tech_enthusiast|young_adult|professional|family)$",
    )
    override_dimensions: Optional[OverrideDimensions] = None


class AuditRequest(BaseModel):
    """POST /api/audit request body."""

    variant_id: str = Field(..., pattern="^var_[a-zA-Z0-9]{8,}$")
    strict_mode: bool = False


# ---------- Response Models ----------


class VariantResponse(BaseModel):
    """Response wrapper for variant data."""

    variant: dict = Field(..., description="The complete VariantSpec")
    correlation_id: str
    timestamp: str


class AuditResponse(BaseModel):
    """Response wrapper for audit results."""

    variant_id: str
    audit: dict = Field(..., description="Audit results including score and risk flags")
    correlation_id: str
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    version: str
