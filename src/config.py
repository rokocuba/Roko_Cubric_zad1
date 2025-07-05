"""
Konfiguracija aplikacije

Autor: Roko Čubrić (roko.cubric@fer.hr)
AI Akademija 2025 - Python Developer Test

Generated with AI assistance - GitHub Copilot
Razlog: Pydantic-based konfiguracija s environment varijablama za FastAPI aplikaciju
Prompt: "Kreiraj pydantic settings klasu za konfiguraciju FastAPI aplikacije s environment varijablama"
"""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Aplikacijske postavke koje se čitaju iz environment varijabli ili .env datoteke"""

    # API konfiguracija
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False

    # Vanjski servisi
    dummyjson_base_url: str = "https://dummyjson.com"

    # Cache
    redis_url: Optional[str] = None
    cache_ttl: int = 300  # 5 minuta

    # Logiranje
    log_level: str = "INFO"

    # Autentifikacija (opcional)
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # sekunde

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Globalna instanca settings
settings = Settings()
