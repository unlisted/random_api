from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://test:test@postgres:5432/test"
    debug: bool = False
    remove_module: bool = False
    enable_token: bool = False





settings = Settings()