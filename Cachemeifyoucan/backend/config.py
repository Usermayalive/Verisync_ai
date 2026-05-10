import os
import warnings
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    GOOGLE_API_KEY: str = "your-gemini-key-here"
    GOOGLE_API_KEY_1: str = ""
    GOOGLE_API_KEY_2: str = ""
    GOOGLE_API_KEY_3: str = ""
    GOOGLE_API_KEY_4: str = ""
    GOOGLE_API_KEY_5: str = ""
    GOOGLE_API_KEY_6: str = ""
    GOOGLE_API_KEY_7: str = ""
    GOOGLE_API_KEY_8: str = ""
    GOOGLE_API_KEY_9: str = ""
    GOOGLE_API_KEY_10: str = ""
    GOOGLE_API_KEY_11: str = ""
    GOOGLE_API_KEY_12: str = ""
    GOOGLE_API_KEY_13: str = ""
    GOOGLE_API_KEY_14: str = ""
    GOOGLE_API_KEY_15: str = ""
    DATABASE_URL: str
    DEEPSEEK_API_KEY: str = ""
    USE_DEEPSEEK: bool = False
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    API_SECRET_KEY: str = "change-this-in-prod"
    DEFAULT_MODEL: str = "gemini-3-flash-preview"
    JUDGE_MODEL: str = "gemini-3-flash-preview"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    CONFIDENCE_THRESHOLD: float = 0.5
    SIMILARITY_THRESHOLD: float = 0.95
    DRIFT_DAYS_THRESHOLD: int = 30
    RETRIEVAL_K: int = 10
    RETRIEVAL_ALPHA: float = 0.5
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    @property
    def valid_google_api_keys(self) -> list[str]:
        keys = []
        if self.GOOGLE_API_KEY and "your-gemini-key" not in self.GOOGLE_API_KEY.lower():
            keys.append(self.GOOGLE_API_KEY)
            
        for i in range(1, 16):
            val = getattr(self, f"GOOGLE_API_KEY_{i}", "")
            if val and "your-gemini-key" not in val.lower():
                keys.append(val)
                
        return list(dict.fromkeys(keys))

    @model_validator(mode="after")
    def validate_secrets(self) -> "Settings":
        placeholder_keys = {"your-gemini-key-here", "change-this-in-prod", ""}
        if self.GOOGLE_API_KEY in placeholder_keys:
            warnings.warn(
                "\n\n⚠️  [CONFIG] GOOGLE_API_KEY is still a placeholder!\n"
                "   Update 'backend/.env' with a real Gemini API key.\n"
                "   Get one at: https://makersuite.google.com/app/apikey\n",
                stacklevel=2,
            )
        if self.API_SECRET_KEY == "change-this-in-prod":
            warnings.warn(
                "\n\n⚠️  [CONFIG] API_SECRET_KEY is using the default placeholder value!\n"
                "   Set a real secret in 'backend/.env' before deploying.\n",
                stacklevel=2,
            )
        return self


settings = Settings()
