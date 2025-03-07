import os

from pydantic import Field, BaseSettings


class Settings(BaseSettings):
    db_url: str = Field(..., env="DATABASE_URL")


settings = Settings()
