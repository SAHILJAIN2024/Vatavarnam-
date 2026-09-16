from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    data_raw_path: str = "../data/raw"
    data_processed_path: str = "../data/processed"

    cds_dataset: str = "reanalysis-era5-single-levels"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()