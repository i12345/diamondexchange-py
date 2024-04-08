from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
