from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv
from utils.exceptions import ConfigurationError


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_model: str
    max_upload_size_mb: int


def load_settings() -> Settings:
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
    load_dotenv(override=False)

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    max_upload_size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

    if max_upload_size_mb <= 0:
        raise ConfigurationError("MAX_UPLOAD_SIZE_MB must be a positive integer.")

    return Settings(
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
        max_upload_size_mb=max_upload_size_mb,
    )
