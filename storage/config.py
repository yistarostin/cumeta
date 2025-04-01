import os

from pydantic import Field, BaseSettings


class Settings(BaseSettings):
    db_url = Field(
        default=os.getenv("DATABASE_URL", "postgresql:///test.db"),
        env="DATABASE_URL",
    )


settings = Settings()
