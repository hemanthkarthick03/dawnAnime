from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field, field_validator

class Settings(BaseSettings):
    # Database settings
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "root"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "test"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @field_validator('DATABASE_URL', mode='after')
    @classmethod
    def validate_database_url(cls, v):
        if not v.startswith('postgresql+asyncpg://'):
            raise ValueError('DATABASE_URL must start with postgresql+asyncpg://')
        return v

    # Security settings
    SECRET_KEY: str = "super-secret-jwt-key"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600  # 1 hour
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 604800  # 7 days

    # Minio settings

    # Redis settings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()