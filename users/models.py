from pydantic import BaseModel
import typing


class LoginItem(BaseModel):
    username: str
    password: str


class UserBaseInfo(BaseModel):
    username: str
    email: str
    name: str
    surname: str


class UserExtendedInfo(BaseModel):
    username: str
    about: typing.Optional[str]
    relationship_status: typing.Optional[str]
    education: typing.Optional[str]
    phone_number: typing.Optional[str]
    job: typing.Optional[str]
    birthdate: str
