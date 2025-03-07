import typing
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
import datetime
import sys
import ormar
from pydantic import BaseModel
from users.db import database, User, UserInfo
from users.utils import PasswordHasher
from users.models import UserBaseInfo, UserExtendedInfo, LoginItem

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)
logger = logging.getLogger(__name__)


app = FastAPI(title="FastAPI, Docker, and Traefik")


@app.get("/")
async def read_root():
    return await User.objects.all()


@app.post("/create/")
async def create_user(user: LoginItem):
    if await User.objects.filter(username=user.username).exists():
        raise HTTPException(status_code=400, detail="Username already exists")
    user_item = await User.objects.get_or_create(
        username=user.username,
        password=PasswordHasher.hash_password(user.password),
        created=datetime.datetime.now(),
        updated=datetime.datetime.now(),
    )
    return user_item


@app.get("/get/{username}")
async def get_user(username: str):
    try:
        return await User.objects.get(username=username)
    except ormar.exceptions.NoMatch:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/get_info/{username}")
async def get_info_user(username: str):
    if not await User.objects.filter(username=username).exists():
        raise HTTPException(status_code=404, detail="User not found")

    user = await User.objects.get(username=username)
    try:
        return await UserInfo.objects.get(user_id=user.id)
    except ormar.exceptions.NoMatch:
        raise HTTPException(status_code=404, detail="User info not found")


@app.post("/authorize")
async def authorize(login: LoginItem):
    user_found = await User.objects.filter(
        username=login.username, password=PasswordHasher.hash_password(login.password)
    ).exists()
    if user_found:
        return JSONResponse(content={"status": "Authorized"}, status_code=200)
    return JSONResponse(content={"message": "Resource Not Found"}, status_code=404)


@app.post("/edit")
async def edit(user: UserBaseInfo):
    if not User.objects.filter(username=user.username).exists():
        raise HTTPException(status_code=404, detail="User not found")
    await User.objects.filter(username=user.username).update(
        username=user.username,
        email=user.email,
        name=user.name,
        surname=user.surname,
        updated=datetime.datetime.now(),
    )
    return JSONResponse(
        content={"status": "Updated user base info for user:" + user.username},
        status_code=200,
    )


@app.post("/edit_info")
async def edit_info(user: UserExtendedInfo):
    logger.debug("User info edit request: %s", user)
    try:
        user_object = await User.objects.get(username=user.username)
    except ormar.exceptions.NoMatch:
        raise HTTPException(status_code=404, detail="User not found")

    await UserInfo.objects.get_or_create(
        user_id=user_object.id,
        about=user.about,
        relationship_status=user.relationship_status,
        education=user.education,
        phone_number=user.phone_number,
        job=user.job,
        birthdate=user.birthdate,
    )
    return JSONResponse(
        content={"status": "Updated user info for user: " + user.username},
        status_code=200,
    )


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()

    logger.debug("Creating a dummy entry")
    await User.objects.get_or_create(
        username="yars",
        password=PasswordHasher.hash_password("test"),
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
