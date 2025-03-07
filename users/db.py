import databases
import ormar
import sqlalchemy

from users.config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=128, unique=True)
    password: str = ormar.String(max_length=128, nullable=False)
    email: str = ormar.String(max_length=128, nullable=True)
    name: str = ormar.String(max_length=128, nullable=True)
    surname: str = ormar.String(max_length=128, nullable=True)
    created: sqlalchemy.DateTime = ormar.DateTime(nullable=True)
    updated: sqlalchemy.DateTime = ormar.DateTime(nullable=True)


class UserInfo(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users_info"

    id: int = ormar.Integer(primary_key=True)

    user_id: int = ormar.ForeignKey(User)
    about: str = ormar.String(max_length=1024, nullable=True)
    relationship_status = ormar.String(max_length=128, nullable=True)
    education = ormar.String(max_length=128, nullable=True)
    phone_number = ormar.String(max_length=128, nullable=True)
    job = ormar.String(max_length=128, nullable=True)
    birthdate: str = ormar.String(max_length=128, nullable=True)


engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)
