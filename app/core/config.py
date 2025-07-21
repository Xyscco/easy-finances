from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Informações da API
    PROJECT_NAME: str = "Financial Management API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:syncode123@localhost:5432/financial_db"
    
    # Security
    SECRET_KEY: str = "sua-chave-secreta-super-segura-aqui-mude-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:4200",  # Angular dev server
        # "http://localhost:3000",  # React dev server
        # "http://localhost:8080",  # Vue dev server
        "http://127.0.0.1:4200",
        # "http://127.0.0.1:3000",
        # "http://127.0.0.1:8080"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()