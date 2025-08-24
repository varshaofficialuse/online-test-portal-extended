# app/core/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# load .env file
load_dotenv()

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_NAME: str = os.getenv("DB_NAME", "online_test_portal")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY","")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    ALGORITHM: str=os.getenv("ALGORITHM",'SHA256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int =os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES",10080)
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY","")


    @property
    def DATABASE_URL(self):
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()
