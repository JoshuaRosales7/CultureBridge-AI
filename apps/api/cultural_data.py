"""
Cultural data loader — loads and serves cultural priors, mapping rules, and product baselines.
"""

import json
import os
import logging
from typing import Optional

logger = logging.getLogger("culturebridge.data")


class CulturalDataLoader:
    """Loads cultural priors, dimension→UX mapping rules, and product baselines from JSON data."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self._data: Optional[dict] = None
        self._load()

    def _load(self):
        """Load the cultural priors data file."""
        if not os.path.exists(self.data_path):
            logger.warning(f"Cultural priors file not found: {self.data_path}")
            self._data = {"cultural_priors": {}, "product_baselines": {}, "dimension_ux_mapping": {"rules": []}}
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        logger.info(f"Loaded cultural priors from {self.data_path}")

    def get_cultural_prior(self, country_code: str) -> Optional[dict]:
        """Get the cultural prior for a country code."""
        priors = self._data.get("cultural_priors", {})
        prior = priors.get(country_code)
        if prior:
            return {
                "country_code": country_code,
                "country_name": prior.get("country_name", country_code),
                "dimensions": prior["dimensions"],
                "evidence": prior["evidence"],
                "notes": prior["notes"],
            }
        return None

    def get_cultural_prior_with_overrides(
        self, country_code: str, overrides: dict
    ) -> Optional[dict]:
        """Get cultural prior with manual dimension overrides applied."""
        prior = self.get_cultural_prior(country_code)
        if prior and overrides:
            for dim_key, dim_value in overrides.items():
                if dim_key in prior["dimensions"]:
                    prior["dimensions"][dim_key] = dim_value
            prior["notes"] += " [Manual overrides applied to some dimensions]"
        return prior

    def get_mapping_rules(self) -> list[dict]:
        """Get the dimension→UX mapping rules."""
        return self._data.get("dimension_ux_mapping", {}).get("rules", [])

    def get_applicable_rules(self, dimensions: dict) -> list[dict]:
        """Get mapping rules that apply given a set of dimension values."""
        all_rules = self.get_mapping_rules()
        applicable = []

        for rule in all_rules:
            dimension = rule["dimension"]
            condition = rule["condition"]

            if dimension not in dimensions:
                continue

            value = dimensions[dimension]

            # Parse condition (e.g., ">=70", "<=35")
            if condition.startswith(">="):
                threshold = float(condition[2:])
                if value >= threshold:
                    applicable.append(rule)
            elif condition.startswith("<="):
                threshold = float(condition[2:])
                if value <= threshold:
                    applicable.append(rule)
            elif condition.startswith(">"):
                threshold = float(condition[1:])
                if value > threshold:
                    applicable.append(rule)
            elif condition.startswith("<"):
                threshold = float(condition[1:])
                if value < threshold:
                    applicable.append(rule)

        return applicable

    def get_product_baseline(self, product_category: str) -> Optional[dict]:
        """Get the baseline storefront spec for a product category."""
        baselines = self._data.get("product_baselines", {})
        return baselines.get(product_category)

    def get_all_country_codes(self) -> list[str]:
        """Get all available country codes."""
        return list(self._data.get("cultural_priors", {}).keys())
