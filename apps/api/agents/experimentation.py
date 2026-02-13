"""
Experimentation Agent
Generates predicted conversion lift estimates and A/B test plans.

Role: Calculate predicted lift using transparent heuristic model.
Input: Complete variant spec + audit results.
Output: Predicted lift with methodology, assumptions, and A/B test plan.
"""

import json
import logging
from typing import Optional

from agents.llm_client import LLMClient

logger = logging.getLogger("culturebridge.agents.experimentation")

SYSTEM_PROMPT = """You are the Experimentation Agent for CultureBridge AI.

Your role is to:
1. Calculate predicted conversion lift for culturally-adapted variants
2. Generate A/B test plans for validating adaptations
3. Provide transparent methodology and assumptions

CRITICAL RULES:
1. ALL predictions are SIMULATED/HEURISTIC — never claim measured results
2. Always disclose assumptions and methodology
3. Confidence levels must be honest and conservative
4. Use "predicted" and "estimated" language, never "proven" or "guaranteed"

PREDICTION METHODOLOGY:
- Each applicable cultural mapping rule contributes an estimated lift factor (2-8% relative)
- Factors compound multiplicatively
- Higher audit scores increase confidence
- More applicable rules = higher predicted lift
- Baseline conversion rates use industry averages (1.5-3%)

Respond ONLY with a valid JSON object:
{
  "metric": "conversion_rate",
  "baseline": 2.1,
  "predicted": 2.8,
  "lift_percentage": 33.3,
  "confidence_level": "low|medium|high",
  "method": "Description of prediction methodology",
  "assumptions": [
    "Assumption 1",
    "Assumption 2"
  ],
  "ab_test_plan": {
    "recommended_sample_size": 5000,
    "recommended_duration_days": 14,
    "success_metric": "conversion_rate",
    "segments": ["new_visitors", "returning_visitors"],
    "statistical_significance_target": 0.95
  },
  "rationale": "Detailed explanation of the prediction"
}
"""

# Lift factor estimates per rule type (relative improvement %)
RULE_LIFT_FACTORS = {
    "increase_trust_modules": 0.05,
    "increase_process_clarity": 0.03,
    "increase_explicit_info": 0.04,
    "increase_social_proof": 0.06,
    "reduce_checkout_steps": 0.08,
    "enhance_guarantees": 0.04,
    "value_framing": 0.05,
    "add_authority_signals": 0.03,
    "ambient_information": 0.02,
    "individual_framing": 0.03,
}

# Baseline conversion rates by category
BASELINE_RATES = {
    "electronics": 2.1,
    "fashion": 2.8,
    "food_beverage": 3.5,
    "home_garden": 1.8,
    "health_beauty": 3.0,
}


class ExperimentationAgent:
    """Generates predicted lift estimates and A/B test plans."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def predict(
        self,
        variant: dict,
        audit_result: dict,
        correlation_id: str = "",
    ) -> dict:
        """
        Generate predicted conversion lift for a variant.
        Uses a transparent heuristic model + optional LLM enrichment.
        """
        # Calculate heuristic lift
        heuristic = self._calculate_heuristic_lift(variant, audit_result)

        # Try LLM enrichment for richer explanation
        user_prompt = f"""Generate a predicted conversion lift analysis for this adapted variant.

VARIANT:
Region: {variant.get('region', 'unknown')}
Theme: {variant.get('theme_emphasis', 'unknown')}
Audit Score: {audit_result.get('audit_score', 0)}
Risk Flags: {len(audit_result.get('risk_flags', []))}

HEURISTIC CALCULATION:
Baseline: {heuristic['baseline']}%
Predicted: {heuristic['predicted']}%
Lift: {heuristic['lift_percentage']}%
Applied Factors: {json.dumps(heuristic.get('applied_factors', []), indent=2)}

CULTURAL DIMENSIONS:
{json.dumps(variant.get('cultural_profile', {}).get('dimensions', {}), indent=2)}

Provide:
1. Validation of the heuristic prediction
2. Confidence level assessment
3. Key assumptions
4. A/B test plan recommendation
"""

        llm_result = await self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            correlation_id=correlation_id,
            max_tokens=1500,
        )

        # Use LLM enrichment if available, otherwise use heuristic
        if not llm_result.get("fallback") and "confidence_level" in llm_result:
            result = {
                "metric": "conversion_rate",
                "baseline": heuristic["baseline"],
                "predicted": heuristic["predicted"],
                "lift_percentage": heuristic["lift_percentage"],
                "confidence_level": llm_result.get("confidence_level", heuristic["confidence_level"]),
                "method": llm_result.get("method", heuristic["method"]),
                "assumptions": llm_result.get("assumptions", heuristic["assumptions"]),
                "ab_test_plan": llm_result.get("ab_test_plan", heuristic["ab_test_plan"]),
                "rationale": llm_result.get("rationale", heuristic["rationale"]),
            }
        else:
            result = heuristic

        logger.info(
            f"[{correlation_id}] Predicted lift: {result['lift_percentage']:.1f}% "
            f"(confidence: {result['confidence_level']})"
        )

        return result

    def _calculate_heuristic_lift(self, variant: dict, audit_result: dict) -> dict:
        """
        Calculate predicted lift using transparent heuristic model.

        Methodology:
        1. Start with industry-average baseline conversion rate
        2. Apply multiplicative lift factors for each applicable adaptation
        3. Discount by audit score (lower audit = lower confidence)
        4. Return with full transparency on assumptions
        """
        # Determine baseline
        profile = variant.get("cultural_profile", {})
        # Try to extract product category from flow context
        baseline = 2.3  # default

        # Calculate compound lift from adaptations
        modules = variant.get("modules", {})
        applied_factors = []
        compound_factor = 1.0

        # Check which adaptations are active and apply lift factors
        if modules.get("reviews", {}).get("placement") == "above_fold":
            factor = RULE_LIFT_FACTORS.get("increase_social_proof", 0.04)
            compound_factor *= (1 + factor)
            applied_factors.append({"rule": "Social proof emphasis", "lift": f"+{factor*100:.1f}%"})

        if modules.get("guarantees", {}).get("prominence") == "high":
            factor = RULE_LIFT_FACTORS.get("enhance_guarantees", 0.04)
            compound_factor *= (1 + factor)
            applied_factors.append({"rule": "Enhanced guarantees", "lift": f"+{factor*100:.1f}%"})

        if modules.get("shipping_info", {}).get("placement") == "above_fold":
            factor = RULE_LIFT_FACTORS.get("increase_trust_modules", 0.03)
            compound_factor *= (1 + factor)
            applied_factors.append({"rule": "Trust modules above fold", "lift": f"+{factor*100:.1f}%"})

        if modules.get("payment_options", {}).get("show_installments"):
            factor = RULE_LIFT_FACTORS.get("value_framing", 0.05)
            compound_factor *= (1 + factor)
            applied_factors.append({"rule": "Value/installment framing", "lift": f"+{factor*100:.1f}%"})

        if modules.get("social_proof", {}).get("enabled"):
            factor = RULE_LIFT_FACTORS.get("increase_social_proof", 0.04)
            if not any("Social proof" in f["rule"] for f in applied_factors):
                compound_factor *= (1 + factor)
                applied_factors.append({"rule": "Social proof module", "lift": f"+{factor*100:.1f}%"})

        # Check for streamlined flow
        flow = variant.get("flow", [])
        for step in flow:
            if step.get("step_id") == "express_checkout":
                factor = RULE_LIFT_FACTORS.get("reduce_checkout_steps", 0.08)
                compound_factor *= (1 + factor)
                applied_factors.append({"rule": "Checkout step reduction", "lift": f"+{factor*100:.1f}%"})
                break

        # Apply audit score discount
        audit_score = audit_result.get("audit_score", 80)
        audit_multiplier = audit_score / 100
        compound_factor = 1 + (compound_factor - 1) * audit_multiplier

        predicted = round(baseline * compound_factor, 2)
        lift_pct = round((predicted - baseline) / baseline * 100, 1)

        # Determine confidence
        num_factors = len(applied_factors)
        if num_factors >= 4 and audit_score >= 80:
            confidence = "high"
        elif num_factors >= 2 and audit_score >= 60:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "metric": "conversion_rate",
            "baseline": baseline,
            "predicted": predicted,
            "lift_percentage": lift_pct,
            "confidence_level": confidence,
            "method": (
                "Transparent heuristic model: each applicable cultural adaptation rule "
                "contributes an estimated lift factor (2-8% relative improvement). "
                "Factors compound multiplicatively and are discounted by audit compliance score. "
                "Baseline uses industry-average conversion rates."
            ),
            "assumptions": [
                f"Baseline conversion rate assumed at {baseline}% (industry average for e-commerce)",
                f"{num_factors} cultural adaptation factors applied with estimated impact ranges",
                "Lift factors are based on published e-commerce conversion optimization research patterns",
                "Factors assume proper implementation of all adaptations",
                f"Audit score ({audit_score}/100) applied as confidence multiplier",
                "No actual A/B test data validates these predictions — they are simulated estimates",
                "Real lift depends on product, market entry strategy, competition, and execution quality",
            ],
            "applied_factors": applied_factors,
            "ab_test_plan": {
                "recommended_sample_size": 5000,
                "recommended_duration_days": 14,
                "success_metric": "conversion_rate",
                "segments": ["new_visitors", "returning_visitors"],
                "statistical_significance_target": 0.95,
            },
            "rationale": (
                f"Predicted {lift_pct}% conversion lift based on {num_factors} applicable cultural adaptation factors. "
                f"Audit compliance score of {audit_score}/100 applied as confidence multiplier. "
                f"Confidence level: {confidence}. "
                "This is a simulated prediction for demonstration purposes — "
                "real impact should be validated through controlled A/B testing."
            ),
        }
