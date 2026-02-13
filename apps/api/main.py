"""
CultureBridge AI — FastAPI Backend
Main application entry point with middleware, routes, and error handling.
"""

import uuid
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import get_settings
from models import AdaptRequest, AuditRequest, VariantResponse, AuditResponse, HealthResponse
from orchestrator import AgentOrchestrator
from variant_store import VariantStore

load_dotenv()

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s [%(correlation_id)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    defaults={"correlation_id": "no-correlation-id"},
)
logger = logging.getLogger("culturebridge.api")


# ---------- Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    settings = get_settings()
    app.state.orchestrator = AgentOrchestrator(settings)
    app.state.variant_store = VariantStore()
    logger.info("CultureBridge AI API started")
    yield
    logger.info("CultureBridge AI API shutting down")


# ---------- App ----------
app = FastAPI(
    title="CultureBridge AI API",
    description="Cultural behavior adaptation engine for e-commerce storefronts",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------- CORS ----------
cors_origins = os.getenv("API_CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Correlation ID Middleware ----------
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Inject a correlation ID into every request for distributed tracing."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    # Add to logging context
    logger_adapter = logging.LoggerAdapter(logger, {"correlation_id": correlation_id})
    request.state.logger = logger_adapter

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# ---------- Error Handlers ----------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.error(f"[{correlation_id}] Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# ---------- Routes ----------
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )


@app.post("/api/adapt", response_model=VariantResponse, tags=["Adaptation"])
async def adapt_storefront(request: Request, body: AdaptRequest):
    """
    Generate a culturally-adapted storefront variant.

    Triggers the multi-agent pipeline:
    1. Cultural Intelligence Agent → behavioral profile
    2. UX Adaptation Agent → flow + module adaptations
    3. Copy & Framing Agent → copy variants
    4. Compliance & Bias Auditor → risk flags + score
    5. Experimentation Agent → predicted lift
    """
    correlation_id = request.state.correlation_id
    request.state.logger.info(
        f"Adaptation request: country={body.country_code}, "
        f"category={body.product_category}, band={body.price_band}"
    )

    try:
        orchestrator: AgentOrchestrator = request.app.state.orchestrator
        variant_store: VariantStore = request.app.state.variant_store

        variant = await orchestrator.run_adaptation_pipeline(
            country_code=body.country_code,
            product_category=body.product_category,
            price_band=body.price_band,
            audience=body.audience,
            override_dimensions=body.override_dimensions,
            correlation_id=correlation_id,
        )

        # Store the variant
        variant_store.store(variant["variant_id"], variant)

        request.state.logger.info(
            f"Variant generated: id={variant['variant_id']}, "
            f"audit_score={variant['audit_score']}"
        )

        return VariantResponse(
            variant=variant,
            correlation_id=correlation_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as e:
        request.state.logger.error(f"Adaptation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Adaptation pipeline failed: {str(e)}")


@app.get("/api/variants/{variant_id}", response_model=VariantResponse, tags=["Variants"])
async def get_variant(request: Request, variant_id: str):
    """Retrieve a previously generated variant by ID."""
    correlation_id = request.state.correlation_id
    variant_store: VariantStore = request.app.state.variant_store

    variant = variant_store.get(variant_id)
    if variant is None:
        raise HTTPException(status_code=404, detail=f"Variant {variant_id} not found")

    return VariantResponse(
        variant=variant,
        correlation_id=correlation_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/api/audit", response_model=AuditResponse, tags=["Compliance"])
async def audit_variant(request: Request, body: AuditRequest):
    """
    Run a compliance and bias audit on a variant.
    Re-invokes the Compliance & Bias Auditor agent.
    """
    correlation_id = request.state.correlation_id
    variant_store: VariantStore = request.app.state.variant_store

    variant = variant_store.get(body.variant_id)
    if variant is None:
        raise HTTPException(status_code=404, detail=f"Variant {body.variant_id} not found")

    try:
        orchestrator: AgentOrchestrator = request.app.state.orchestrator
        audit_result = await orchestrator.run_audit(
            variant=variant,
            strict_mode=body.strict_mode,
            correlation_id=correlation_id,
        )

        return AuditResponse(
            variant_id=body.variant_id,
            audit=audit_result,
            correlation_id=correlation_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as e:
        request.state.logger.error(f"Audit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")
