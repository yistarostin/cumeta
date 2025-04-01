from enum import Enum
from pydantic import BaseModel
import typing
import os


class LoginPayload(BaseModel):
    username: str
    password: str


class TokenPayload(BaseModel):
    username: str
    token: str


class UserBaseInfo(BaseModel):
    username: str
    email: str
    name: str
    surname: str
    token: typing.Optional[str]


class UserExtendedInfo(BaseModel):
    username: str
    about: typing.Optional[str]
    relationship_status: typing.Optional[str]
    education: typing.Optional[str]
    phone_number: typing.Optional[str]
    job: typing.Optional[str]
    birthdate: str
    token: typing.Optional[str]


backend_uri = os.environ.get("BACKEND_APP_ADDRESS", "web:8000")


class Addresses(Enum):
    _BACKEND_ROOT = f"http://{backend_uri}"

    CHECK_USER_ADDRESS = f"{_BACKEND_ROOT}/authorize"
    ADD_USER = f"{_BACKEND_ROOT}/create"

    GET_USER = f"{_BACKEND_ROOT}/get"
    GET_USER_INFO = f"{_BACKEND_ROOT}/get_info"

    EDIT_USER = f"{_BACKEND_ROOT}/edit"
    EDIT_USER_INFO = f"{_BACKEND_ROOT}/edit_info"
