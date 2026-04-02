from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "tax-synth"
    tax_year: int = 2024

    project_root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = Field(default=Path("data"))
    templates_dir: Path = Field(default=Path("templates"))

    input_dir: Path = Field(default=Path("data/input"))
    output_dir: Path = Field(default=Path("data/output"))
    temp_dir: Path = Field(default=Path("data/temp"))

    random_seed: int = 42
    default_locale: str = "en_US"

    def resolved_path(self, path_value: Path) -> Path:
        if path_value.is_absolute():
            return path_value
        return self.project_root / path_value


settings = Settings()