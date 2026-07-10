"""
IBM Granite LLM Service via WatsonX AI
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class GraniteLLM:
    """Wrapper for IBM Granite via WatsonX AI."""

    def __init__(self):
        self._model = None
        self._initialized = False

    def _init_model(self):
        if self._initialized:
            return
        try:
            from ibm_watsonx_ai.foundation_models import Model
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
            from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes

            self._generate_params = {
                GenParams.MAX_NEW_TOKENS: 1024,
                GenParams.MIN_NEW_TOKENS: 10,
                GenParams.TEMPERATURE: 0.3,
                GenParams.TOP_P: 0.9,
                GenParams.REPETITION_PENALTY: 1.1,
                GenParams.STOP_SEQUENCES: ["<|endoftext|>", "Human:", "User:"],
            }

            self._model = Model(
                model_id=settings.GRANITE_MODEL_ID,
                params=self._generate_params,
                credentials={
                    "apikey": settings.WATSONX_API_KEY,
                    "url": settings.WATSONX_URL,
                },
                project_id=settings.WATSONX_PROJECT_ID,
            )
            self._initialized = True
            logger.info(f"✅ Granite LLM initialized: {settings.GRANITE_MODEL_ID}")
        except Exception as e:
            logger.error(f"LLM init failed: {e}")
            self._initialized = False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        self._init_model()
        if not self._initialized or self._model is None:
            return self._fallback_response()

        try:
            response = self._model.generate_text(prompt=prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return self._fallback_response()

    def _fallback_response(self) -> str:
        return (
            "I'm sorry, I'm currently unable to connect to the AI service. "
            "Please check your WatsonX credentials or try again later."
        )


# Singleton instance
_llm = GraniteLLM()


def generate_response(prompt: str) -> str:
    return _llm.generate(prompt)
