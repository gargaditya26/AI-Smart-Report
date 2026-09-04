from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "smartreports"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    # Application
    SECRET_KEY: str = "your-secret-key-change-in-production"
    SESSION_TTL: int = 3600  # 1 hour
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Storage
    STORAGE_TYPE: str = "local"  # local, s3, azure
    UPLOAD_DIR: str = "/tmp/smartreports/uploads"
    PDF_OUTPUT_DIR: str = "/tmp/smartreports/pdfs"

    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_BUCKET_NAME: Optional[str] = None

    # Azure
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_CONTAINER_NAME: Optional[str] = None

    # OCR
    TESSERACT_CMD: str = "/usr/bin/tesseract"

    # PDF Generation
    PDF_GENERATION_TIMEOUT: int = 60

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def origins_list(self) -> list:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
