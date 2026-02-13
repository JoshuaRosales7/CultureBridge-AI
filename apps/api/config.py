"""
Configuration management for CultureBridge AI API.
Loads settings from environment variables, with Azure Key Vault integration for production.
"""

import os
from functools import lru_cache
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-10-21"

    # Application Insights
    app_insights_connection_string: str = ""

    # API
    api_cors_origins: str = "http://localhost:3000"
    api_jwt_secret: str = "dev-secret-change-in-production"

    # Azure Key Vault (production)
    azure_keyvault_url: str = ""

    # Data paths
    cultural_priors_path: str = ""


@lru_cache()
def get_settings() -> Settings:
    """Load settings from environment variables (cached singleton)."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    settings = Settings(
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        azure_openai_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        app_insights_connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", ""),
        api_cors_origins=os.getenv("API_CORS_ORIGINS", "http://localhost:3000"),
        api_jwt_secret=os.getenv("API_JWT_SECRET", "dev-secret-change-in-production"),
        azure_keyvault_url=os.getenv("AZURE_KEYVAULT_URL", ""),
        cultural_priors_path=os.path.join(base_dir, "data", "cultural_priors.json"),
    )

    return settings
