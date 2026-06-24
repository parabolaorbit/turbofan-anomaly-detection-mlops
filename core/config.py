from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Anomaly Detection API"
    env: str = "local"
    api_key: str = "dev-secret-key"

    database_url: str = "sqlite:///./anomaly.db"

    model_path: str = "models/anomaly_api_model.pt"
    scaler_path: str = "models/scaler.pkl"

    threshold: float = 0.1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()