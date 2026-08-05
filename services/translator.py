from typing import Any

from google.genai import Client
from google.genai.types import HttpOptions

from config.config import Settings
from utils.exceptions import TranslationError, ConfigurationError


class TranslatorService:
    def __init__(self, settings: Settings):
        if not settings.gemini_api_key:
            raise ConfigurationError("GEMINI_API_KEY is required.")
        self.client = Client(
            api_key=settings.gemini_api_key,
            http_options=HttpOptions(timeout=20),
        )
        self.model = settings.gemini_model

    def translate(self, text: str, language: str) -> str:
        try:
            response = self.client.interactions.create(
                model=self.model,
                input={
                    "content": [
                        {
                            "type": "text",
                            "text": f"Translate the following text to {language}: {text}",
                        }
                    ]
                },
            )
            if response.output and response.output[0].content:
                return response.output[0].content[0].text
            raise TranslationError("Received empty translation response.")
        except Exception as exc:
            raise TranslationError(str(exc)) from exc
