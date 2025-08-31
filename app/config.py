from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    MODEL_PATH: Path = Field(default=Path("app") / "models" / "model.joblib")

    MAX_UPLOAD_BYTES: int = Field(default=2_000_000)  # ~2MB

    APP_NAME: str = "Email Classifier API"
    APP_ENV: str = "local"

    HF_API_KEY: Optional[str] = None
    USE_HF_CLASSIFIER: bool = False
    HF_ZS_MODEL: str = "joeddav/xlm-roberta-large-xnli"

    USE_HF_REPLY: bool = False
    HF_REPLY_MODEL: str = "google/flan-t5-small"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
