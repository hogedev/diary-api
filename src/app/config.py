from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///data/diary.db"
    photos_dir: str = "data/photos"
    thumb_max_dimension: int = 800

    model_config = {"env_file": ".env"}


settings = Settings()
