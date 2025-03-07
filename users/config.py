import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = Field(os.environ.get("DATABASE_URL"), env="DATABASE_URL")


settings = Settings()
