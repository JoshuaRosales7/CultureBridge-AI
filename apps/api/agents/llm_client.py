"""
LLM Client — Azure OpenAI integration.
Handles API calls to Azure OpenAI with retry logic and structured output parsing.
"""

import json
import logging
from typing import Optional

from openai import AsyncAzureOpenAI
from config import Settings

logger = logging.getLogger("culturebridge.llm")


class LLMClient:
    """Client for Azure OpenAI API calls with structured JSON output support."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Optional[AsyncAzureOpenAI] = None

        if settings.azure_openai_endpoint and settings.azure_openai_api_key:
            self.client = AsyncAzureOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )
            logger.info("Azure OpenAI client initialized")
        else:
            logger.warning("Azure OpenAI credentials not configured — using fallback mode")

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        correlation_id: str = "",
        max_tokens: int = 4000,
        temperature: float = 0.3,
    ) -> dict:
        """
        Generate a structured JSON response from Azure OpenAI.

        If Azure OpenAI is not configured, returns a fallback response.
        """
        if not self.client:
            logger.warning(f"[{correlation_id}] LLM not available, using fallback")
            return self._fallback_response(system_prompt)

        try:
            response = await self.client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                logger.info(f"[{correlation_id}] LLM response received ({len(content)} chars)")
                return result
            else:
                logger.warning(f"[{correlation_id}] Empty LLM response")
                return {"error": "Empty response from LLM", "rationale": "Fallback due to empty response"}

        except json.JSONDecodeError as e:
            logger.error(f"[{correlation_id}] Failed to parse LLM JSON response: {e}")
            return {"error": str(e), "rationale": "Failed to parse LLM response as JSON"}

        except Exception as e:
            logger.error(f"[{correlation_id}] LLM call failed: {e}")
            return {"error": str(e), "rationale": f"LLM call failed: {str(e)}"}

    def _fallback_response(self, system_prompt: str) -> dict:
        """Generate a fallback response when LLM is not available."""
        return {
            "rationale": "Generated using fallback mode (Azure OpenAI not configured). Configure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY for full functionality.",
            "fallback": True,
        }
