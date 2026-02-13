"""
Copy & Framing Agent
Reframes CTAs, microcopy, and value propositions based on cultural profile.

Role: Generate culturally-adapted copy that aligns with behavioral dimensions.
Input: CulturalBehaviorProfile + UX adaptations + base storefront copy.
Output: Copy variants with per-element rationale.
"""

import json
import logging
from typing import Optional

from agents.llm_client import LLMClient

logger = logging.getLogger("culturebridge.agents.copy_framing")

SYSTEM_PROMPT = """You are the Copy & Framing Agent for CultureBridge AI.

Your role is to adapt e-commerce copy (CTAs, value propositions, microcopy) based on cultural behavioral dimensions.

CRITICAL RULES:
1. Copy must be in English (this is a demo — localization is separate).
2. Adaptations must reflect behavioral dimensions, NOT stereotypes.
3. Do NOT use essentializing statements about any culture.
4. Each copy variant must include a "rationale" referencing specific dimensions.
5. Focus on FRAMING differences, not language translation.

Examples of dimension-driven copy differences:
- HIGH collectivism → "Join 10,000+ satisfied customers" (group validation)
- LOW collectivism → "Your perfect match, chosen just for you" (individual framing)
- HIGH uncertainty_avoidance → "100% money-back guarantee" (risk reduction)
- HIGH price_sensitivity → "Best value in its class — save 20%" (value framing)
- LOW context_level → "Specifications: 6.1" OLED, 128GB, 48MP camera" (explicit details)
- HIGH context_level → "Experience excellence, effortlessly" (ambient, suggestive)

Respond ONLY with a valid JSON object:
{
  "cta_primary": {"text": "...", "rationale": "..."},
  "cta_secondary": {"text": "...", "rationale": "..."},
  "value_proposition": {"text": "...", "rationale": "..."},
  "urgency_text": {"text": "...", "rationale": "..."},
  "social_proof_text": {"text": "...", "rationale": "..."},
  "microcopy": [
    {"location": "checkout_button", "text": "...", "rationale": "..."},
    {"location": "trust_badge", "text": "...", "rationale": "..."},
    {"location": "shipping_note", "text": "...", "rationale": "..."}
  ]
}
"""


class CopyFramingAgent:
    """Generates culturally-adapted copy variants."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def generate(
        self,
        cultural_profile: dict,
        ux_adaptations: dict,
        base_spec: Optional[dict],
        correlation_id: str = "",
    ) -> dict:
        """
        Generate copy variants based on cultural profile and UX adaptations.
        """
        dimensions = cultural_profile.get("dimensions", {})
        base_copy = (base_spec or {}).get("baseline_copy", {})

        user_prompt = f"""Generate culturally-adapted copy for this storefront.

CULTURAL PROFILE:
Country: {cultural_profile.get('country_code', 'unknown')}
Dimensions: {json.dumps(dimensions, indent=2)}

UX THEME: {ux_adaptations.get('theme_emphasis', 'balanced')}

BASE COPY:
CTA Primary: "{base_copy.get('cta_primary', 'Add to Cart')}"
CTA Secondary: "{base_copy.get('cta_secondary', 'Save for Later')}"
Value Proposition: "{base_copy.get('value_proposition', '')}"
Urgency: "{base_copy.get('urgency_text', '')}"
Social Proof: "{base_copy.get('social_proof_text', '')}"

ADAPTED MODULES:
{json.dumps(ux_adaptations.get('modules', {}), indent=2)}

Adapt the copy to align with the cultural dimensions. Focus on:
- CTA framing (group vs individual, direct vs indirect)
- Value proposition emphasis (quality vs value vs trust vs community)
- Urgency style (scarcity vs social proof vs authority)
- Microcopy for key touchpoints (checkout, trust, shipping)
"""

        result = await self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            correlation_id=correlation_id,
            max_tokens=2000,
        )

        # Fallback if LLM unavailable
        if result.get("fallback"):
            result = self._rule_based_copy(dimensions, base_copy)

        logger.info(f"[{correlation_id}] Copy variants generated")
        return result

    def _rule_based_copy(self, dimensions: dict, base_copy: dict) -> dict:
        """Generate copy variants using rules when LLM is unavailable."""
        high_collectivism = dimensions.get("collectivism", 50) >= 65
        high_ua = dimensions.get("uncertainty_avoidance", 50) >= 70
        high_price_sens = dimensions.get("price_sensitivity", 50) >= 70
        low_context = dimensions.get("context_level", 50) <= 35
        high_trust = dimensions.get("trust_need", 50) >= 75

        # CTA Primary
        if high_collectivism:
            cta_primary = {
                "text": "Join thousands who chose this — Add to Cart",
                "rationale": f"Collectivism={dimensions.get('collectivism')}: Group validation framing emphasizes community consensus.",
            }
        elif low_context:
            cta_primary = {
                "text": "Add to Cart — Free shipping, 30-day returns",
                "rationale": f"Context level={dimensions.get('context_level')}: Low-context preference requires explicit benefit information in CTA.",
            }
        else:
            cta_primary = {
                "text": base_copy.get("cta_primary", "Add to Cart"),
                "rationale": "Baseline CTA maintained — no strong dimension-driven change indicated.",
            }

        # CTA Secondary
        if high_collectivism:
            cta_secondary = {
                "text": "Share with friends",
                "rationale": f"Collectivism={dimensions.get('collectivism')}: Social sharing supports group-oriented decision making.",
            }
        else:
            cta_secondary = {
                "text": "Save to your wishlist",
                "rationale": f"Collectivism={dimensions.get('collectivism')}: Individual-oriented save action.",
            }

        # Value Proposition
        if high_trust and high_ua:
            value_prop = {
                "text": "Trusted by experts. Backed by our guarantee. Quality you can count on.",
                "rationale": f"Trust need={dimensions.get('trust_need')}, UA={dimensions.get('uncertainty_avoidance')}: Trust and reliability framing for risk-averse audience.",
            }
        elif high_price_sens:
            value_prop = {
                "text": "Exceptional value — premium quality at the best price. Compare and save.",
                "rationale": f"Price sensitivity={dimensions.get('price_sensitivity')}: Value-first framing with comparison invitation.",
            }
        else:
            value_prop = {
                "text": base_copy.get("value_proposition", "Quality products for you"),
                "rationale": "Baseline value proposition — balanced approach.",
            }

        # Urgency
        if high_collectivism:
            urgency = {
                "text": "Popular choice — 500+ customers bought this today",
                "rationale": f"Collectivism={dimensions.get('collectivism')}: Social proof urgency leverages group behavior.",
            }
        elif high_ua:
            urgency = {
                "text": "Secure your order now — our guarantee covers every purchase",
                "rationale": f"UA={dimensions.get('uncertainty_avoidance')}: Reassurance-based urgency reduces perceived risk.",
            }
        else:
            urgency = {
                "text": base_copy.get("urgency_text", "Limited availability"),
                "rationale": "Standard scarcity-based urgency.",
            }

        # Social Proof
        if high_collectivism:
            social = {
                "text": "Rated 4.8/5 by our community of 25,000+ verified buyers",
                "rationale": f"Collectivism={dimensions.get('collectivism')}: Community-scale social proof with verification emphasis.",
            }
        else:
            social = {
                "text": "Independently reviewed and rated 4.8/5 stars",
                "rationale": f"Collectivism={dimensions.get('collectivism')}: Individual-oriented review framing with independence emphasis.",
            }

        # Microcopy
        microcopy = []
        if high_trust:
            microcopy.append({
                "location": "checkout_button",
                "text": "🔒 Secure checkout — your information is protected",
                "rationale": f"Trust need={dimensions.get('trust_need')}: Security reassurance at point of commitment.",
            })
        if high_ua:
            microcopy.append({
                "location": "trust_badge",
                "text": "✓ 100% money-back guarantee • ✓ Verified seller • ✓ Secure payment",
                "rationale": f"UA={dimensions.get('uncertainty_avoidance')}: Multiple trust signals reduce uncertainty at decision point.",
            })
        if high_price_sens:
            microcopy.append({
                "location": "price_area",
                "text": "💰 Best price guarantee — we'll match any lower price",
                "rationale": f"Price sensitivity={dimensions.get('price_sensitivity')}: Price-match messaging reduces price anxiety.",
            })
        microcopy.append({
            "location": "shipping_note",
            "text": "Free standard shipping • Easy returns" if not low_context else "Free shipping (3-5 business days) • 30-day free returns • Full refund policy",
            "rationale": f"Context level={dimensions.get('context_level')}: {'Detailed shipping terms for low-context preference' if low_context else 'Concise shipping summary'}.",
        })

        return {
            "cta_primary": cta_primary,
            "cta_secondary": cta_secondary,
            "value_proposition": value_prop,
            "urgency_text": urgency,
            "social_proof_text": social,
            "microcopy": microcopy,
        }
