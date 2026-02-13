"""
Compliance & Bias Auditor Agent
Checks generated variants for stereotyping, essentializing, and unjustified adaptations.

Role: Audit variant outputs for bias, require dimension-based justification, flag risks.
Input: Complete or partial VariantSpec.
Output: audit_score (0-100), risk_flags[], recommended_changes[].
"""

import json
import logging
from typing import Optional

from agents.llm_client import LLMClient

logger = logging.getLogger("culturebridge.agents.compliance_auditor")

SYSTEM_PROMPT = """You are the Compliance & Bias Auditor Agent for CultureBridge AI.

Your role is to audit culturally-adapted storefront variants for:
1. ESSENTIALIZING STATEMENTS: Copy that claims "People in X always..." or implies cultural determinism
2. STEREOTYPE-BASED JUSTIFICATIONS: Changes justified by stereotypes rather than behavioral dimensions
3. RISKY ADAPTATIONS: Changes that could be perceived as discriminatory or offensive
4. MISSING JUSTIFICATION: Any adaptation without a clear dimension-based rationale
5. PROPORTIONALITY: Extreme adaptations not justified by dimension scores

SCORING GUIDE:
- 90-100: Excellent — all adaptations well-justified, no flags
- 70-89: Good — minor concerns, easily addressed
- 50-69: Needs improvement — significant flags requiring attention
- 0-49: High risk — major bias concerns, should not deploy without revision

Respond ONLY with a valid JSON object:
{
  "audit_score": 0-100,
  "summary": "Overall assessment summary",
  "risk_flags": [
    {
      "flag_id": "FLAG_001",
      "severity": "low|medium|high|critical",
      "description": "What the issue is",
      "recommendation": "How to fix it",
      "affected_element": "Which part of the variant is affected"
    }
  ],
  "recommended_changes": [
    {
      "element": "Which element to change",
      "current": "Current value",
      "suggested": "Suggested replacement",
      "reason": "Why this change is recommended"
    }
  ],
  "positive_notes": ["What was done well"],
  "rationale": "Detailed explanation of the audit findings"
}
"""


class ComplianceAuditorAgent:
    """Audits variant specs for bias, stereotyping, and compliance issues."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def audit(
        self,
        variant: dict,
        strict_mode: bool = False,
        correlation_id: str = "",
    ) -> dict:
        """
        Audit a variant for bias and compliance issues.
        """
        user_prompt = f"""Audit this culturally-adapted storefront variant for bias and compliance.

VARIANT SPECIFICATION:
Region: {variant.get('region', 'unknown')}
Theme: {variant.get('theme_emphasis', 'unknown')}

FLOW ADAPTATIONS:
{json.dumps(variant.get('flow', []), indent=2)}

MODULE ADAPTATIONS:
{json.dumps(variant.get('modules', {}), indent=2)}

COPY VARIANTS:
{json.dumps(variant.get('copy', {}), indent=2)}

CULTURAL PROFILE USED:
{json.dumps(variant.get('cultural_profile', {}), indent=2)}

{"STRICT MODE ENABLED: Apply higher standards for bias detection." if strict_mode else "Standard audit mode."}

Check for:
1. Any essentializing language in copy or rationale
2. Stereotype-based justifications (not dimension-based)
3. Adaptations that could be discriminatory or offensive
4. Missing dimension-based justifications
5. Proportionality of adaptations to dimension scores
"""

        result = await self.llm.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            correlation_id=correlation_id,
            max_tokens=2000,
        )

        # Fallback if LLM unavailable
        if result.get("fallback"):
            result = self._rule_based_audit(variant, strict_mode)

        logger.info(
            f"[{correlation_id}] Audit complete: score={result.get('audit_score', 'N/A')}, "
            f"flags={len(result.get('risk_flags', []))}"
        )

        return result

    def _rule_based_audit(self, variant: dict, strict_mode: bool = False) -> dict:
        """Rule-based audit when LLM is unavailable."""
        risk_flags = []
        positive_notes = []
        score = 100
        flag_counter = 0

        # Check copy for essentializing language
        copy_data = variant.get("copy", {})
        essentializing_patterns = [
            "always", "never", "all people in", "everyone in",
            "they always", "they never", "people in", "typical of",
        ]

        for key, value in copy_data.items():
            if isinstance(value, dict):
                text = value.get("text", "")
                rationale = value.get("rationale", "")
                for pattern in essentializing_patterns:
                    if pattern.lower() in text.lower() or pattern.lower() in rationale.lower():
                        flag_counter += 1
                        risk_flags.append({
                            "flag_id": f"FLAG_{flag_counter:03d}",
                            "severity": "medium" if not strict_mode else "high",
                            "description": f"Potentially essentializing language detected in {key}: contains '{pattern}'",
                            "recommendation": f"Rephrase to avoid generalizing statements. Use dimension-specific language instead.",
                            "affected_element": f"copy.{key}",
                        })
                        score -= 10

        # Check for dimension-based justification in modules
        modules = variant.get("modules", {})
        for mod_name, mod_data in modules.items():
            if isinstance(mod_data, dict):
                rationale = mod_data.get("adaptation_rationale", "")
                if rationale and not any(dim in rationale.lower() for dim in [
                    "uncertainty", "collectivism", "authority", "context",
                    "price", "trust", "friction", "ua=", "cl=",
                ]):
                    flag_counter += 1
                    risk_flags.append({
                        "flag_id": f"FLAG_{flag_counter:03d}",
                        "severity": "low",
                        "description": f"Module '{mod_name}' rationale may not reference specific behavioral dimensions",
                        "recommendation": "Ensure rationale explicitly references dimension scores and mapping rules.",
                        "affected_element": f"modules.{mod_name}",
                    })
                    score -= 5

        # Check flow adaptations have rationale
        flow = variant.get("flow", [])
        for step in flow:
            adaptations = step.get("adaptations", [])
            for adaptation in adaptations:
                if not adaptation.get("dimension_driver"):
                    flag_counter += 1
                    risk_flags.append({
                        "flag_id": f"FLAG_{flag_counter:03d}",
                        "severity": "medium",
                        "description": f"Flow step '{step.get('name', 'unknown')}' adaptation lacks dimension driver",
                        "recommendation": "Add specific dimension and score that drives this adaptation.",
                        "affected_element": f"flow.{step.get('step_id', 'unknown')}",
                    })
                    score -= 8

        # Positive notes
        if len(risk_flags) == 0:
            positive_notes.append("All adaptations include dimension-based justification")
        if variant.get("cultural_profile", {}).get("evidence"):
            positive_notes.append("Cultural profile includes evidence sources")
        if variant.get("cultural_profile", {}).get("notes"):
            positive_notes.append("Cultural profile acknowledges limitations in notes")

        # Apply strict mode penalty
        if strict_mode:
            score = max(0, score - 10)

        score = max(0, min(100, score))

        return {
            "audit_score": score,
            "summary": f"Rule-based audit complete. Score: {score}/100 with {len(risk_flags)} flags identified.",
            "risk_flags": risk_flags,
            "recommended_changes": [],
            "positive_notes": positive_notes,
            "rationale": "Audit performed using rule-based checks (LLM not available). Checks include: essentializing language detection, dimension justification verification, and flow adaptation coverage.",
        }
