"""
UX Adaptation Agent
Adapts checkout flow, modules, and layout emphasis based on cultural profile.

Role: Map cultural dimensions → concrete UX changes using explicit rules.
Input: CulturalBehaviorProfile + StorefrontBaseSpec + price_band + audience.
Output: Adapted flow, modules, theme_emphasis with per-element rationale.
"""

import json
import logging
from typing import Optional

from agents.llm_client import LLMClient
from cultural_data import CulturalDataLoader

logger = logging.getLogger("culturebridge.agents.ux_adaptation")

SYSTEM_PROMPT = """You are the UX Adaptation Agent for CultureBridge AI.

Your role is to adapt an e-commerce storefront's UX (checkout flow, trust modules, layout emphasis) based on a cultural behavioral profile.

CRITICAL RULES:
1. Every adaptation MUST reference a specific behavioral dimension and its score.
2. Use the dimension→UX mapping rules provided to justify changes.
3. Do NOT make changes based on stereotypes — only dimension-driven effects.
4. Each change must include a "rationale" linking to specific dimension scores.
5. Changes should be functional (flow, modules, emphasis), NOT visual stereotypes.

You will receive:
- Cultural behavior profile with dimension scores
- Base storefront specification
- Applicable mapping rules
- Price band and audience context

Respond ONLY with a valid JSON object:
{
  "theme_emphasis": "functional emphasis description (e.g., 'trust-first', 'efficiency-driven')",
  "rationale": "Overall rationale for the adaptation approach",
  "flow": [
    {
      "step_id": "...",
      "name": "...",
      "description": "...",
      "adaptations": [
        {"change": "...", "dimension_driver": "...", "rationale": "..."}
      ],
      "required_fields": ["..."],
      "validations": ["..."]
    }
  ],
  "modules": {
    "reviews": {"enabled": true, "placement": "...", "style": "...", "adaptation_rationale": "..."},
    "guarantees": {"enabled": true, "types": ["..."], "prominence": "...", "adaptation_rationale": "..."},
    "shipping_info": {"enabled": true, "placement": "...", "detail_level": "...", "adaptation_rationale": "..."},
    "returns": {"enabled": true, "prominence": "...", "adaptation_rationale": "..."},
    "payment_options": {"enabled": true, "show_installments": false, "show_local_methods": false, "emphasized_methods": ["..."], "adaptation_rationale": "..."},
    "social_proof": {"enabled": true, "type": "...", "placement": "...", "adaptation_rationale": "..."}
  }
}
"""


class UXAdaptationAgent:
    """Adapts storefront UX based on cultural behavioral dimensions."""

    def __init__(self, llm_client: LLMClient, data_loader: CulturalDataLoader):
        self.llm = llm_client
        self.data = data_loader

    async def adapt(
        self,
        cultural_profile: dict,
        base_spec: Optional[dict],
        price_band: str,
        audience: str,
        correlation_id: str = "",
    ) -> dict:
        """
        Generate UX adaptations based on cultural profile and base spec.

        1. Determine applicable dimension→UX rules
        2. Use LLM to synthesize rules into coherent UX adaptations
        3. Return structured flow + modules with rationale
        """
        dimensions = cultural_profile.get("dimensions", {})
        applicable_rules = self.data.get_applicable_rules(dimensions)

        if not base_spec:
            base_spec = self._default_base_spec()

        user_prompt = f"""Adapt this storefront's UX for the target cultural profile.

CULTURAL PROFILE:
Country: {cultural_profile.get('country_code', 'unknown')}
Dimensions: {json.dumps(dimensions, indent=2)}

APPLICABLE MAPPING RULES (based on dimension thresholds):
{json.dumps(applicable_rules, indent=2)}

BASE STOREFRONT SPECIFICATION:
Product Category: {base_spec.get('product_category', 'general')}
Price Band: {price_band}
Audience: {audience}
Baseline Flow: {json.dumps(base_spec.get('baseline_flow', []), indent=2)}
Baseline Modules: {json.dumps(base_spec.get('baseline_modules', {}), indent=2)}

Apply the applicable mapping rules to adapt the flow and modules. 
Each adaptation must reference the specific rule and dimension score that drives it.
If rules conflict, explain the trade-off in your rationale.
"""

        result = await self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            correlation_id=correlation_id,
            max_tokens=4000,
        )

        # If LLM is unavailable, generate rule-based adaptations
        if result.get("fallback"):
            result = self._rule_based_adaptation(
                dimensions, applicable_rules, base_spec, price_band
            )

        logger.info(
            f"[{correlation_id}] UX adaptations generated: "
            f"{len(result.get('flow', []))} flow steps, "
            f"{len(applicable_rules)} rules applied"
        )

        return result

    def _rule_based_adaptation(
        self, dimensions: dict, rules: list, base_spec: dict, price_band: str
    ) -> dict:
        """
        Generate adaptations using only the mapping rules (no LLM).
        Used as fallback when Azure OpenAI is not available.
        """
        flow = []
        base_flow = base_spec.get("baseline_flow", [])

        # Determine if we need to streamline checkout
        low_friction = dimensions.get("friction_tolerance", 50) <= 40

        if low_friction:
            # Combine shipping + payment steps
            for step in base_flow:
                if step["step_id"] == "shipping":
                    combined = {
                        "step_id": "express_checkout",
                        "name": "Express Checkout",
                        "description": "Combined shipping and payment in a single streamlined step",
                        "adaptations": [
                            {
                                "change": "Combined shipping and payment steps",
                                "dimension_driver": f"friction_tolerance={dimensions.get('friction_tolerance', 50)}",
                                "rationale": "Low friction tolerance requires streamlined flow to prevent cart abandonment",
                            }
                        ],
                        "required_fields": ["full_name", "address", "payment_method"],
                        "validations": ["address_format"],
                    }
                    flow.append(combined)
                elif step["step_id"] != "payment":
                    flow.append({**step, "adaptations": []})
        else:
            flow = [{**step, "adaptations": []} for step in base_flow]

        # Build modules based on rules
        base_modules = base_spec.get("baseline_modules", {})
        modules = {
            "reviews": {
                "enabled": True,
                "placement": "above_fold" if dimensions.get("collectivism", 50) >= 65 else "below_fold",
                "style": "community" if dimensions.get("collectivism", 50) >= 65 else "stars",
                "adaptation_rationale": f"Collectivism={dimensions.get('collectivism', 50)}: {'Strong social proof emphasis' if dimensions.get('collectivism', 50) >= 65 else 'Standard review display'}",
            },
            "guarantees": {
                "enabled": True,
                "types": (
                    ["money-back guarantee", "authenticity guarantee", "secure payment", "official warranty"]
                    if dimensions.get("trust_need", 50) >= 75
                    else ["30-day returns", "manufacturer warranty"]
                ),
                "prominence": "high" if dimensions.get("trust_need", 50) >= 75 else "medium",
                "adaptation_rationale": f"Trust need={dimensions.get('trust_need', 50)}: {'Enhanced guarantee prominence' if dimensions.get('trust_need', 50) >= 75 else 'Standard guarantees'}",
            },
            "shipping_info": {
                "enabled": True,
                "placement": "above_fold" if dimensions.get("uncertainty_avoidance", 50) >= 70 else "product_detail",
                "detail_level": "detailed" if dimensions.get("context_level", 50) <= 35 else "standard",
                "adaptation_rationale": f"UA={dimensions.get('uncertainty_avoidance', 50)}, CL={dimensions.get('context_level', 50)}: {'Detailed upfront shipping info' if dimensions.get('uncertainty_avoidance', 50) >= 70 else 'Standard shipping display'}",
            },
            "returns": {
                "enabled": True,
                "prominence": "high" if dimensions.get("uncertainty_avoidance", 50) >= 70 else "medium",
                "adaptation_rationale": f"UA={dimensions.get('uncertainty_avoidance', 50)}: {'High prominence returns policy' if dimensions.get('uncertainty_avoidance', 50) >= 70 else 'Standard returns'}",
            },
            "payment_options": {
                "enabled": True,
                "show_installments": dimensions.get("price_sensitivity", 50) >= 70,
                "show_local_methods": True,
                "emphasized_methods": (
                    ["installments", "BNPL", "mobile_payment"]
                    if dimensions.get("price_sensitivity", 50) >= 70
                    else ["credit_card", "debit_card"]
                ),
                "adaptation_rationale": f"Price sensitivity={dimensions.get('price_sensitivity', 50)}: {'Installment and flexible payment emphasis' if dimensions.get('price_sensitivity', 50) >= 70 else 'Standard payment options'}",
            },
            "social_proof": {
                "enabled": dimensions.get("collectivism", 50) >= 65,
                "type": "community" if dimensions.get("collectivism", 50) >= 65 else "individual",
                "placement": "above_fold" if dimensions.get("collectivism", 50) >= 65 else "sidebar",
                "adaptation_rationale": f"Collectivism={dimensions.get('collectivism', 50)}: {'Community-driven social proof' if dimensions.get('collectivism', 50) >= 65 else 'Individual testimonials'}",
            },
        }

        # Determine theme emphasis
        themes = []
        if dimensions.get("trust_need", 50) >= 75:
            themes.append("trust-first")
        if dimensions.get("friction_tolerance", 50) <= 40:
            themes.append("efficiency-driven")
        if dimensions.get("collectivism", 50) >= 65:
            themes.append("community-validated")
        if dimensions.get("context_level", 50) <= 35:
            themes.append("information-rich")
        if dimensions.get("price_sensitivity", 50) >= 70:
            themes.append("value-oriented")

        theme = ", ".join(themes) if themes else "balanced"

        return {
            "theme_emphasis": theme,
            "rationale": f"Adaptation driven by {len(rules)} applicable mapping rules for {len(themes)} identified behavioral patterns. Generated using rule-based fallback.",
            "flow": flow,
            "modules": modules,
        }

    def _default_base_spec(self) -> dict:
        """Default base spec when none is provided."""
        return {
            "product_category": "general",
            "baseline_flow": [
                {"step_id": "browse", "name": "Browse", "description": "Product browsing"},
                {"step_id": "detail", "name": "Product Detail", "description": "Product detail page"},
                {"step_id": "cart", "name": "Cart", "description": "Shopping cart"},
                {"step_id": "checkout", "name": "Checkout", "description": "Checkout process"},
                {"step_id": "confirm", "name": "Confirmation", "description": "Order confirmation"},
            ],
            "baseline_modules": {},
        }
