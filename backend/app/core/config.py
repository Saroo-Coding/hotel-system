from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "dev"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    TIME_ZONE: str

    LENGTH_OF_TEMP_PASSWORD: int = 8

    BASE_PASSWORD: str

    class Config:
        env_file = "backend/.env"

settings = Settings()
