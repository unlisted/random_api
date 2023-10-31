from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = False
    remove_module: bool = False




settings = Settings()