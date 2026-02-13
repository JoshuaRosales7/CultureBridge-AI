"""
Unit tests for CultureBridge AI
Tests cover: mapping rules, schema validation, cultural data loading,
agent outputs, and predicted lift calculation.
"""

import json
import os
import sys
import pytest

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "api"))

from cultural_data import CulturalDataLoader


# ---------- Fixtures ----------

@pytest.fixture
def data_loader():
    """Create a CulturalDataLoader with the real cultural priors data."""
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "cultural_priors.json"
    )
    return CulturalDataLoader(data_path)


@pytest.fixture
def japan_dimensions():
    """Japan's cultural dimensions."""
    return {
        "uncertainty_avoidance": 82,
        "collectivism": 78,
        "authority_distance": 54,
        "context_level": 85,
        "price_sensitivity": 45,
        "trust_need": 88,
        "friction_tolerance": 72,
    }


@pytest.fixture
def guatemala_dimensions():
    """Guatemala's cultural dimensions."""
    return {
        "uncertainty_avoidance": 55,
        "collectivism": 72,
        "authority_distance": 68,
        "context_level": 70,
        "price_sensitivity": 82,
        "trust_need": 75,
        "friction_tolerance": 35,
    }


@pytest.fixture
def germany_dimensions():
    """Germany's cultural dimensions."""
    return {
        "uncertainty_avoidance": 75,
        "collectivism": 25,
        "authority_distance": 30,
        "context_level": 20,
        "price_sensitivity": 55,
        "trust_need": 70,
        "friction_tolerance": 65,
    }


# ---------- Test 1: Cultural Prior Loading ----------

class TestCulturalDataLoading:
    """Test that cultural priors load correctly."""

    def test_load_japan_prior(self, data_loader):
        """Japan's cultural prior should load with all required dimensions."""
        prior = data_loader.get_cultural_prior("JP")
        assert prior is not None
        assert prior["country_code"] == "JP"
        assert "dimensions" in prior
        assert all(
            dim in prior["dimensions"]
            for dim in [
                "uncertainty_avoidance", "collectivism", "authority_distance",
                "context_level", "price_sensitivity", "trust_need", "friction_tolerance",
            ]
        )

    def test_load_guatemala_prior(self, data_loader):
        """Guatemala's cultural prior should load correctly."""
        prior = data_loader.get_cultural_prior("GT")
        assert prior is not None
        assert prior["country_code"] == "GT"
        assert prior["dimensions"]["price_sensitivity"] == 82

    def test_load_germany_prior(self, data_loader):
        """Germany's cultural prior should load correctly."""
        prior = data_loader.get_cultural_prior("DE")
        assert prior is not None
        assert prior["dimensions"]["context_level"] == 20  # Low-context

    def test_unknown_country_returns_none(self, data_loader):
        """Unknown country codes should return None."""
        prior = data_loader.get_cultural_prior("XX")
        assert prior is None

    def test_dimension_overrides(self, data_loader):
        """Manual dimension overrides should be applied correctly."""
        prior = data_loader.get_cultural_prior_with_overrides(
            "JP", {"uncertainty_avoidance": 50, "collectivism": 30}
        )
        assert prior is not None
        assert prior["dimensions"]["uncertainty_avoidance"] == 50
        assert prior["dimensions"]["collectivism"] == 30
        # Other dimensions should remain unchanged
        assert prior["dimensions"]["trust_need"] == 88


# ---------- Test 2: Mapping Rule Application ----------

class TestMappingRules:
    """Test that dimension→UX mapping rules apply correctly."""

    def test_japan_triggers_high_trust_rules(self, data_loader, japan_dimensions):
        """Japan (UA=82, trust=88) should trigger trust-related rules."""
        rules = data_loader.get_applicable_rules(japan_dimensions)
        rule_ids = [r["rule_id"] for r in rules]

        assert "UA_HIGH_TRUST" in rule_ids, "Japan should trigger UA_HIGH_TRUST"
        assert "UA_HIGH_CLARITY" in rule_ids, "Japan should trigger UA_HIGH_CLARITY"
        assert "TRUST_HIGH_GUARANTEES" in rule_ids, "Japan should trigger TRUST_HIGH_GUARANTEES"

    def test_japan_triggers_social_proof(self, data_loader, japan_dimensions):
        """Japan (collectivism=78) should trigger social proof rule."""
        rules = data_loader.get_applicable_rules(japan_dimensions)
        rule_ids = [r["rule_id"] for r in rules]

        assert "COL_HIGH_SOCIAL" in rule_ids, "Japan should trigger COL_HIGH_SOCIAL"

    def test_japan_triggers_high_context(self, data_loader, japan_dimensions):
        """Japan (context=85) should trigger high-context rule."""
        rules = data_loader.get_applicable_rules(japan_dimensions)
        rule_ids = [r["rule_id"] for r in rules]

        assert "CTX_HIGH_IMPLICIT" in rule_ids, "Japan should trigger CTX_HIGH_IMPLICIT"

    def test_guatemala_triggers_streamline(self, data_loader, guatemala_dimensions):
        """Guatemala (friction=35) should trigger checkout streamlining."""
        rules = data_loader.get_applicable_rules(guatemala_dimensions)
        rule_ids = [r["rule_id"] for r in rules]

        assert "FRIC_LOW_STREAMLINE" in rule_ids, "Guatemala should trigger FRIC_LOW_STREAMLINE"

    def test_guatemala_triggers_value_framing(self, data_loader, guatemala_dimensions):
        """Guatemala (price_sensitivity=82) should trigger value framing."""
        rules = data_loader.get_applicable_rules(guatemala_dimensions)
        rule_ids = [r["rule_id"] for r in rules]

        assert "PRICE_HIGH_VALUE" in rule_ids, "Guatemala should trigger PRICE_HIGH_VALUE"

    def test_germany_triggers_explicit_info(self, data_loader, germany_dimensions):
        """Germany (context=20) should trigger explicit information rule."""
        rules = data_loader.get_applicable_rules(germany_dimensions)
        rule_ids = [r["rule_id"] for r in rules]

        assert "CTX_LOW_EXPLICIT" in rule_ids, "Germany should trigger CTX_LOW_EXPLICIT"

    def test_germany_triggers_individual_framing(self, data_loader, germany_dimensions):
        """Germany (collectivism=25) should trigger individual framing."""
        rules = data_loader.get_applicable_rules(germany_dimensions)
        rule_ids = [r["rule_id"] for r in rules]

        assert "COL_LOW_INDIVIDUAL" in rule_ids, "Germany should trigger COL_LOW_INDIVIDUAL"

    def test_germany_does_not_trigger_social_proof(self, data_loader, germany_dimensions):
        """Germany (collectivism=25) should NOT trigger social proof rule."""
        rules = data_loader.get_applicable_rules(germany_dimensions)
        rule_ids = [r["rule_id"] for r in rules]

        assert "COL_HIGH_SOCIAL" not in rule_ids, "Germany should NOT trigger COL_HIGH_SOCIAL"


# ---------- Test 3: Schema Validation ----------

class TestSchemaValidation:
    """Test that JSON schemas validate correctly."""

    def test_cultural_profile_schema(self):
        """CulturalBehaviorProfile schema should load and parse."""
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "packages", "shared", "schemas",
            "cultural-behavior-profile.schema.json"
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        assert schema["title"] == "CulturalBehaviorProfile"
        assert "dimensions" in schema["properties"]
        assert len(schema["properties"]["dimensions"]["required"]) == 7

    def test_variant_spec_schema(self):
        """VariantSpec schema should load and contain all required fields."""
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "packages", "shared", "schemas",
            "variant-spec.schema.json"
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        assert schema["title"] == "VariantSpec"
        required = schema["required"]
        assert "variant_id" in required
        assert "region" in required
        assert "predicted_lift" in required
        assert "audit_score" in required
        assert "risk_flags" in required

    def test_adapt_request_schema(self):
        """AdaptRequest schema should validate country codes."""
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "packages", "shared", "schemas",
            "adapt-request.schema.json"
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        assert "JP" in schema["properties"]["country_code"]["enum"]
        assert "GT" in schema["properties"]["country_code"]["enum"]
        assert "DE" in schema["properties"]["country_code"]["enum"]


# ---------- Test 4: Product Baseline Loading ----------

class TestProductBaselines:
    """Test product baseline data loading."""

    def test_electronics_baseline_exists(self, data_loader):
        """Electronics baseline should exist with required fields."""
        baseline = data_loader.get_product_baseline("electronics")
        assert baseline is not None
        assert baseline["product_category"] == "electronics"
        assert len(baseline["baseline_flow"]) >= 4

    def test_fashion_baseline_exists(self, data_loader):
        """Fashion baseline should exist."""
        baseline = data_loader.get_product_baseline("fashion")
        assert baseline is not None
        assert baseline["product_category"] == "fashion"

    def test_unknown_category_returns_none(self, data_loader):
        """Unknown product categories should return None."""
        baseline = data_loader.get_product_baseline("nonexistent")
        assert baseline is None


# ---------- Test 5: Predicted Lift Calculation ----------

class TestPredictedLift:
    """Test the heuristic predicted lift calculation."""

    def test_lift_calculation_basic(self):
        """Basic lift calculation should produce positive lift."""
        from agents.experimentation import ExperimentationAgent, RULE_LIFT_FACTORS

        # Verify lift factors are defined and reasonable
        for rule, factor in RULE_LIFT_FACTORS.items():
            assert 0 < factor <= 0.15, f"Lift factor for {rule} should be between 0 and 15%"

    def test_baseline_rates_defined(self):
        """Baseline conversion rates should be defined for all categories."""
        from agents.experimentation import BASELINE_RATES

        assert "electronics" in BASELINE_RATES
        assert "fashion" in BASELINE_RATES
        for category, rate in BASELINE_RATES.items():
            assert 0.5 <= rate <= 10, f"Baseline rate for {category} should be reasonable"


# ---------- Test 6: Rule Count Per Region ----------

class TestRuleCoverage:
    """Ensure each region has meaningful rule coverage."""

    def test_japan_has_multiple_rules(self, data_loader, japan_dimensions):
        """Japan should trigger at least 4 mapping rules."""
        rules = data_loader.get_applicable_rules(japan_dimensions)
        assert len(rules) >= 4, f"Japan should trigger 4+ rules, got {len(rules)}"

    def test_guatemala_has_multiple_rules(self, data_loader, guatemala_dimensions):
        """Guatemala should trigger at least 4 mapping rules."""
        rules = data_loader.get_applicable_rules(guatemala_dimensions)
        assert len(rules) >= 4, f"Guatemala should trigger 4+ rules, got {len(rules)}"

    def test_germany_has_multiple_rules(self, data_loader, germany_dimensions):
        """Germany should trigger at least 3 mapping rules."""
        rules = data_loader.get_applicable_rules(germany_dimensions)
        assert len(rules) >= 3, f"Germany should trigger 3+ rules, got {len(rules)}"

    def test_different_regions_trigger_different_rules(
        self, data_loader, japan_dimensions, germany_dimensions
    ):
        """Japan and Germany should trigger different rule sets."""
        jp_rules = set(r["rule_id"] for r in data_loader.get_applicable_rules(japan_dimensions))
        de_rules = set(r["rule_id"] for r in data_loader.get_applicable_rules(germany_dimensions))

        # They should have some overlap (e.g., UA rules) but not be identical
        assert jp_rules != de_rules, "Japan and Germany should trigger different rules"
        # Japan should have social proof, Germany should have individual framing
        assert "COL_HIGH_SOCIAL" in jp_rules
        assert "COL_LOW_INDIVIDUAL" in de_rules
