from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://glucose_user:glucose_pass@localhost:5432/glucose_db"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "glucose_db"
    db_user: str = "glucose_user"
    db_password: str = "glucose_pass"
    
    # Redis Configuration
    redis_url: str = "redis://:redis_pass@localhost:6379"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "redis_pass"
    
    # Application Configuration
    port: int = 8080
    host: str = "0.0.0.0"
    debug: bool = True
    
    # Security
    jwt_secret: str = "your-super-secret-jwt-key-change-this-in-production"
    api_key_secret: str = "dev-api-key-12345"
    
    # Medical Device Specific
    max_glucose_reading_rate: int = 30  # seconds
    glucose_min_value: int = 40
    glucose_max_value: int = 400
    
    class Config:
        env_file = "config.env"
        case_sensitive = False

settings = Settings() 