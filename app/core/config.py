import os
from pydantic_settings import BaseSettings
from passlib.context import CryptContext


class Settings(BaseSettings):
    DATABASE_URL: str 
    REDIS_URL: str
    
    SECRET_KEY: str 
    ALGORITHM: str 

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '..', '..', '.env')

settings = Settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")