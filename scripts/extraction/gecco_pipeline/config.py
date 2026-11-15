from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import List, Optional


class Settings(BaseSettings):
    """Pipeline configuration loaded from environment variables and .env file."""

    # API Configuration
    GOOGLE_API_KEY: str = Field(description="Google AI API key for Gemini (single key fallback)")
    GOOGLE_API_KEYS: Optional[str] = Field(
        default=None,
        description="Comma-separated list of Google AI API keys for rotation",
    )
    MODEL_NAME: str = Field(default="gemini-3.5-flash")

    # Paths
    PDF_BASE_DIR: Path = Field(default=Path("data/pdfs"))
    OUTPUT_DIR: Path = Field(default=Path("data/outputs"))
    REPORTS_DIR: Path = Field(default=Path("data/reports"))

    # Processing
    MAX_RETRIES: int = Field(default=3)
    RETRY_BASE_DELAY: float = Field(default=2.0, description="Base delay in seconds for exponential backoff")
    BATCH_SIZE: int = Field(default=5, description="Number of papers per batch before cooldown")
    RATE_LIMIT_RPM: int = Field(default=10, description="Max requests per minute (conservative for free tier)")
    TEMPERATURE: float = Field(default=0.1, description="LLM temperature for extraction")

    # Bulk processing
    BATCH_COOLDOWN_SECONDS: int = Field(default=65, description="Seconds to pause between batches")
    REQUESTS_PER_KEY_BEFORE_ROTATE: int = Field(default=14, description="Rotate API key after this many requests")

    @property
    def api_keys(self) -> List[str]:
        """Return list of all available API keys for rotation."""
        if self.GOOGLE_API_KEYS:
            keys = [k.strip() for k in self.GOOGLE_API_KEYS.split(",") if k.strip()]
            if keys:
                return keys
        return [self.GOOGLE_API_KEY]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_settings() -> Settings:
    """Create and return a Settings instance."""
    return Settings()
