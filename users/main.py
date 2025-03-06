import typing
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
import datetime
import sys
import ormar
from pydantic import BaseModel
from users.db import database, User, UserInfo

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)
logger = logging.getLogger(__name__)


app = FastAPI(title="FastAPI, Docker, and Traefik")


class LoginItem(BaseModel):
    username: str
    password: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    email: str
    name: str
    surname: str


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


@app.get("/")
async def read_root():
    return await User.objects.all()


@app.post("/create/")
async def create_user(user: UserCreateRequest):
    user_item = await User.objects.create(
        username=user.username,
        password=user.password,
        email=user.email,
        name=user.name,
        surname=user.surname,
        created=datetime.datetime.now(),
        updated=datetime.datetime.now(),
    )
    return user_item


@app.post("/update/")
async def update_user(user: UserBaseInfo):
    try:
        result = await User.objects.filter(username=user.username).update(
            email=user.email,
            name=user.name,
            surname=user.surname,
            updated=datetime.datetime.now(),
        )
        return {"status": ("Updated" if result > 0 else "Such user does not exist")}
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/get/{username}")
async def get_user(username: str):
    try:
        return await User.objects.fields(
            ["username", "email", "name", "surname", "created", "updated"]
        ).get(username=username)
    except ormar.exceptions.NoMatch:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/get_info/{username}")
async def get_info_user(username: str):
    try:
        user_object = await User.objects.get(username=username)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        return await UserInfo.objects.get(user_id=user_object.id)
    except UserInfo.DoesNotExist:
        raise HTTPException(
            status_code=404, detail="UserInfo not found for username=" + username
        )


@app.post("/authorize")
async def authorize(login: LoginItem):
    user_found = await User.objects.filter(
        username=login.username, password=login.password
    ).exists()
    if user_found:
        return JSONResponse(content={"status": "Authorized"}, status_code=200)
    return JSONResponse(content={"message": "Resource Not Found"}, status_code=404)


@app.post("/edit")
async def edit(user: UserBaseInfo):
    try:
        user_object = await User.objects.get(username=user.username)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    new_user_info = UserBaseInfo(
        username=user_object.username,
        email=user_object.email,
        name=user_object.name,
        surname=user_object.surname,
    )
    result = await User.objects.update_or_create(
        username=user_object.username,
        defaults=new_user_info.dict(),
        updated=datetime.datetime.now(),
    )
    return result


@app.post("/edit_info")
async def edit_info(user: UserExtendedInfo):
    logger.debug("User edit request: %s", user)
    try:
        user_object = await User.objects.get(username=user.username)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    new_user_info = UserInfo(
        user_id=user_object.id,
        about=user.about,
        relationship_status=user.relationship_status,
        education=user.education,
        phone_number=user.phone_number,
        job=user.job,
        birthdate=user.birthdate,
    )
    result = await UserInfo.objects.update_or_create(
        user_id=user_object.id, defaults=new_user_info.dict()
    )
    logger.debug("Updated user info: %s", result)
    return result


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()

    logger.debug("Creating a dummy entry")
    await User.objects.get_or_create(
        username="yars",
        password="test",
        email="test@gmail.com",
        name="Yaroslav",
        surname="Sobol",
    )
    await UserInfo.objects.get_or_create(about="I am a test user", user_id=1)
    logger.debug("Created a dummy entry")


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
