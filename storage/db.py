import databases
import ormar
import sqlalchemy

from config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Post(ormar.Model):
    class Meta(BaseMeta):
        tablename = "posts"

    id: int = ormar.Integer(primary_key=True)
    user_owner: str = ormar.String(max_length=128)
    title: str = ormar.String(max_length=128, nullable=False)
    description: str = ormar.String(max_length=128, nullable=True)
    is_private: bool = ormar.Boolean(nullable=True)
    tags: str = ormar.String(max_length=256, nullable=True)
    created: sqlalchemy.DateTime = ormar.DateTime(nullable=True)
    updated: sqlalchemy.DateTime = ormar.DateTime(nullable=True)


engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)
