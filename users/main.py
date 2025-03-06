from fastapi import FastAPI, HTTPException
import logging
import datetime

from pydantic import BaseModel
from users.db import database, User, UserInfo


app = FastAPI(title="FastAPI, Docker, and Traefik")
logger = logging.getLogger(__name__)


@app.get("/")
async def read_root():
    return await User.objects.all()


@app.post("/users/create/")
async def create_user(user: User):
    now = datetime.datetime.now()
    user.created = now
    user.updated = now
    await user.save()
    return user


@app.post("/users/update/")
async def update_user(user: User):
    now_user = await User.objects.get(username=user.username)
    if user.password != now_user.password or user.username != now_user.username:
        raise HTTPException(
            status_code=404, detail="Cannot update users's username or password"
        )
    now = datetime.datetime.now()
    user.updated = now
    await user.update()
    return user


@app.post("/users/delete/")
async def delete_user(user: User):
    await user.delete()
    return user


@app.get("/users/get/{login}")
async def get_user(login: str):
    return await User.objects.get(username=login)


class LoginItem(BaseModel):
    username: str
    password: str


@app.get("/authorize")
async def authorize(login: LoginItem):
    user_found = User.objects.exists(username=login.username, password=login.password)
    if user_found:
        return {"status": "ok"}
    return {"status": "fail"}


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()

    logger.debug("Creating a dummy entry")
    await User.objects.get_or_create(id=1, username="yars", password="test")
    await UserInfo.objects.get_or_create(about="I am a test user", user_id=1)
    logger.debug("Created a dummy entry")


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
