"""
Agent Orchestrator — Microsoft Agent Framework Integration
Coordinates the multi-agent pipeline for cultural adaptation.

Pipeline:
1. Cultural Intelligence Agent → CulturalBehaviorProfile
2. UX Adaptation Agent → Flow + module adaptations
3. Copy & Framing Agent → Copy variants
4. Compliance & Bias Auditor Agent → Audit score + risk flags
5. Experimentation Agent → Predicted lift
"""

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from config import Settings
from agents.cultural_intelligence import CulturalIntelligenceAgent
from agents.ux_adaptation import UXAdaptationAgent
from agents.copy_framing import CopyFramingAgent
from agents.compliance_auditor import ComplianceAuditorAgent
from agents.experimentation import ExperimentationAgent
from agents.llm_client import LLMClient
from cultural_data import CulturalDataLoader

logger = logging.getLogger("culturebridge.orchestrator")


class AgentOrchestrator:
    """
    Orchestrates the multi-agent cultural adaptation pipeline.
    Uses Microsoft Agent Framework patterns with structured tool calls.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm_client = LLMClient(settings)
        self.data_loader = CulturalDataLoader(settings.cultural_priors_path)

        # Initialize specialist agents
        self.cultural_intel = CulturalIntelligenceAgent(self.llm_client, self.data_loader)
        self.ux_adapter = UXAdaptationAgent(self.llm_client, self.data_loader)
        self.copy_framer = CopyFramingAgent(self.llm_client)
        self.compliance_auditor = ComplianceAuditorAgent(self.llm_client)
        self.experimentation = ExperimentationAgent(self.llm_client)

    async def run_adaptation_pipeline(
        self,
        country_code: str,
        product_category: str,
        price_band: str,
        audience: str,
        override_dimensions: Optional[dict] = None,
        correlation_id: str = "",
    ) -> dict:
        """
        Run the full multi-agent adaptation pipeline.

        Returns a complete VariantSpec dict.
        """
        log = logging.LoggerAdapter(logger, {"correlation_id": correlation_id})
        variant_id = f"var_{uuid.uuid4().hex[:12]}"
        overrides = {}
        if override_dimensions:
            overrides = {
                k: v
                for k, v in override_dimensions.model_dump().items()
                if v is not None
            }

        # Step 1: Cultural Intelligence Agent
        log.info("Step 1/5: Cultural Intelligence Agent")
        cultural_profile = await self.cultural_intel.analyze(
            country_code=country_code,
            product_category=product_category,
            override_dimensions=overrides,
            correlation_id=correlation_id,
        )
        log.info(f"Cultural profile generated for {country_code}")

        # Step 2: UX Adaptation Agent
        log.info("Step 2/5: UX Adaptation Agent")
        base_spec = self.data_loader.get_product_baseline(product_category)
        ux_adaptations = await self.ux_adapter.adapt(
            cultural_profile=cultural_profile,
            base_spec=base_spec,
            price_band=price_band,
            audience=audience,
            correlation_id=correlation_id,
        )
        log.info("UX adaptations generated")

        # Step 3: Copy & Framing Agent
        log.info("Step 3/5: Copy & Framing Agent")
        copy_variants = await self.copy_framer.generate(
            cultural_profile=cultural_profile,
            ux_adaptations=ux_adaptations,
            base_spec=base_spec,
            correlation_id=correlation_id,
        )
        log.info("Copy variants generated")

        # Assemble partial variant for audit
        partial_variant = {
            "variant_id": variant_id,
            "region": country_code,
            "theme_emphasis": ux_adaptations.get("theme_emphasis", "balanced"),
            "flow": ux_adaptations.get("flow", []),
            "modules": ux_adaptations.get("modules", {}),
            "copy": copy_variants,
            "cultural_profile": cultural_profile,
        }

        # Step 4: Compliance & Bias Auditor Agent
        log.info("Step 4/5: Compliance & Bias Auditor Agent")
        audit_result = await self.compliance_auditor.audit(
            variant=partial_variant,
            correlation_id=correlation_id,
        )
        log.info(f"Audit complete: score={audit_result.get('audit_score', 'N/A')}")

        # Step 5: Experimentation Agent
        log.info("Step 5/5: Experimentation Agent")
        lift_prediction = await self.experimentation.predict(
            variant=partial_variant,
            audit_result=audit_result,
            correlation_id=correlation_id,
        )
        log.info(f"Predicted lift: {lift_prediction.get('lift_percentage', 'N/A')}%")

        # Assemble final VariantSpec
        variant_spec = {
            "variant_id": variant_id,
            "region": country_code,
            "theme_emphasis": ux_adaptations.get("theme_emphasis", "balanced"),
            "flow": ux_adaptations.get("flow", []),
            "modules": ux_adaptations.get("modules", {}),
            "copy": copy_variants,
            "risk_flags": audit_result.get("risk_flags", []),
            "audit_score": audit_result.get("audit_score", 0),
            "predicted_lift": lift_prediction,
            "rationale": ux_adaptations.get("rationale", ""),
            "cultural_profile": cultural_profile,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        log.info(f"Variant {variant_id} complete for {country_code}")
        return variant_spec

    async def run_audit(
        self,
        variant: dict,
        strict_mode: bool = False,
        correlation_id: str = "",
    ) -> dict:
        """Re-run the compliance audit on an existing variant."""
        log = logging.LoggerAdapter(logger, {"correlation_id": correlation_id})
        log.info(f"Re-auditing variant {variant.get('variant_id', 'unknown')}")

        audit_result = await self.compliance_auditor.audit(
            variant=variant,
            strict_mode=strict_mode,
            correlation_id=correlation_id,
        )

        return audit_result
