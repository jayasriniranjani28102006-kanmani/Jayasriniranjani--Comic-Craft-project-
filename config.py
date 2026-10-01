from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    hf_token: str = ""
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"
    hf_provider: str = "auto"
    image_backend: str = "huggingface"
    panel_count: int = 5
    image_width: int = 768
    image_height: int = 768
    image_steps: int = 4
    image_timeout: int = 180

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panel_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def export_dir(self) -> Path:
        return self.static_dir / "exports"

    def ensure_dirs(self) -> None:
        self.panel_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
