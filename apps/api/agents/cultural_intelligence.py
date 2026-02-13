"""
Cultural Intelligence Agent
Analyzes behavioral dimensions for a target region and product category.

Role: Load cultural priors, apply overrides, enrich with LLM reasoning.
Input: Country code, product category, optional dimension overrides.
Output: CulturalBehaviorProfile (machine-readable JSON with rationale).
"""

import json
import logging
from typing import Optional

from agents.llm_client import LLMClient
from cultural_data import CulturalDataLoader

logger = logging.getLogger("culturebridge.agents.cultural_intel")

SYSTEM_PROMPT = """You are the Cultural Intelligence Agent for CultureBridge AI.

Your role is to analyze cultural behavioral dimensions for a target region in the context of e-commerce purchase behavior.

CRITICAL RULES:
1. You MUST ground all analysis in behavioral dimensions, NOT stereotypes.
2. You MUST NOT use essentializing language ("People in X always...").
3. You MUST provide evidence-based rationale for dimension values.
4. You MUST acknowledge limitations and individual variance.
5. Dimensions are population-level tendencies, not prescriptive characteristics.

You will receive base cultural priors (from established frameworks) and must:
- Validate and contextualize the dimension values for the specific product category
- Provide a rationale explaining how each dimension affects e-commerce behavior
- Note any caveats or limitations

Respond ONLY with a valid JSON object matching this structure:
{
  "country_code": "XX",
  "dimensions": {
    "uncertainty_avoidance": 0-100,
    "collectivism": 0-100,
    "authority_distance": 0-100,
    "context_level": 0-100,
    "price_sensitivity": 0-100,
    "trust_need": 0-100,
    "friction_tolerance": 0-100
  },
  "evidence": [
    {"source": "...", "description": "..."}
  ],
  "notes": "...",
  "rationale": "Overall explanation of how this profile affects e-commerce behavior for this product category",
  "dimension_rationales": {
    "uncertainty_avoidance": "Why this value for this region+category...",
    ...
  }
}
"""


class CulturalIntelligenceAgent:
    """Analyzes cultural behavioral dimensions for a target region."""

    def __init__(self, llm_client: LLMClient, data_loader: CulturalDataLoader):
        self.llm = llm_client
        self.data = data_loader

    async def analyze(
        self,
        country_code: str,
        product_category: str,
        override_dimensions: Optional[dict] = None,
        correlation_id: str = "",
    ) -> dict:
        """
        Analyze cultural profile for a region.

        1. Load base priors from data
        2. Apply any dimension overrides
        3. Enrich with LLM reasoning for the specific product category
        """
        # Load base priors
        base_prior = self.data.get_cultural_prior_with_overrides(
            country_code, override_dimensions or {}
        )

        if not base_prior:
            logger.warning(f"[{correlation_id}] No cultural prior found for {country_code}")
            return self._default_profile(country_code)

        # Build enrichment prompt
        user_prompt = f"""Analyze the cultural behavioral profile for e-commerce in this context:

Country: {base_prior.get('country_name', country_code)} ({country_code})
Product Category: {product_category}

Base cultural priors (from established frameworks):
{json.dumps(base_prior['dimensions'], indent=2)}

Evidence sources:
{json.dumps(base_prior['evidence'], indent=2)}

Notes: {base_prior['notes']}

{"Dimension overrides applied: " + json.dumps(override_dimensions) if override_dimensions else "No overrides applied."}

Please validate these dimensions for the {product_category} category context and provide:
1. Adjusted dimension values if the product category significantly shifts any dimension
2. Rationale for each dimension explaining its e-commerce behavioral impact
3. Evidence sources supporting your analysis
4. Caveats and limitations
"""

        # Call LLM for enrichment
        result = await self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            correlation_id=correlation_id,
        )

        # If LLM returned valid enriched profile, use it; otherwise use base priors
        if "dimensions" in result and not result.get("fallback"):
            # Merge LLM enrichment with base data
            profile = {
                "country_code": country_code,
                "dimensions": result.get("dimensions", base_prior["dimensions"]),
                "evidence": result.get("evidence", base_prior["evidence"]),
                "notes": result.get("notes", base_prior["notes"]),
                "rationale": result.get("rationale", ""),
                "dimension_rationales": result.get("dimension_rationales", {}),
            }
        else:
            # Use base priors as-is (fallback)
            profile = {
                "country_code": country_code,
                "dimensions": base_prior["dimensions"],
                "evidence": base_prior["evidence"],
                "notes": base_prior["notes"],
                "rationale": f"Base cultural priors for {country_code} in {product_category} context. LLM enrichment not available.",
                "dimension_rationales": {},
            }

        logger.info(f"[{correlation_id}] Cultural profile complete for {country_code}")
        return profile

    def _default_profile(self, country_code: str) -> dict:
        """Default profile when no data is available."""
        return {
            "country_code": country_code,
            "dimensions": {
                "uncertainty_avoidance": 50,
                "collectivism": 50,
                "authority_distance": 50,
                "context_level": 50,
                "price_sensitivity": 50,
                "trust_need": 50,
                "friction_tolerance": 50,
            },
            "evidence": [
                {
                    "source": "Default baseline",
                    "description": "No specific cultural data available; using neutral midpoint values.",
                }
            ],
            "notes": f"No cultural priors available for {country_code}. Using default neutral values.",
            "rationale": "Default neutral profile applied due to missing cultural data.",
            "dimension_rationales": {},
        }
