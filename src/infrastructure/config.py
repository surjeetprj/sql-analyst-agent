from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class FrontendSettings(AppConfig):
    API_BASE_URL: str = "http://127.0.0.1:8000"
    API_USERNAME: str
    API_PASSWORD: str

class BackendSettings(AppConfig):
    PROJECT_NAME: str = "Enterprise SQL Agent"
    CUBE_API_URL: str = ""
    GROQ_API_KEY: str

    # API Security
    JWT_SECRET_KEY: str = "fallback_secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_USERNAME: str
    API_PASSWORD: str

    # LangSmith Observability
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str | None = None
    LANGCHAIN_PROJECT: str = "sql-analyst-agent-prod"

    # Database components
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # 1. Neon provides `postgresql://`, but SQLAlchemy needs `postgresql+asyncpg://`
        url = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        
        # 2. asyncpg requires `ssl=require` instead of `sslmode=require`
        url = url.replace("sslmode=require", "ssl=require")
        return url

@lru_cache()
def get_frontend_settings() -> FrontendSettings:
    return FrontendSettings()

@lru_cache()
def get_backend_settings() -> BackendSettings:
    return BackendSettings()