from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///data/diary.db"
    minio_endpoint: str = "192.168.10.207:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "diary"
    minio_secure: bool = False
    thumb_max_dimension: int = 800

    model_config = {"env_file": ".env"}


settings = Settings()
