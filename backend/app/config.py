from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    api_cors_origins: str = "http://localhost:3000"
    redis_url: str = "redis://localhost:6379/0"
    queue_backend: str = "celery"
    pipeline_execution_mode: str = "simulated"
    github_token: str | None = None
    github_webhook_secret: str | None = None
    github_api_url: str = "https://api.github.com"
    aws_deploy_mode: str = "dry-run"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    langchain_project: str = "workflow-orchestrator"
    aws_region: str = "us-west-2"
    sqs_queue_url: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
