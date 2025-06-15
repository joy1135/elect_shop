from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_NAME: str = "deafult"
    SECRET_KEY: str 

    model_config=SettingsConfigDict(env_file=".env")

settings = Settings()