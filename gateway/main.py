from typing import Union
import typing
import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import logging
import os
from fastapi import Depends, FastAPI, HTTPException, status, Request


logger = logging.getLogger(__name__)

backend_uri = os.environ.get("BACKEND_APP_ADDRESS", "web:8000")
BACKEND_ADDRESS = f"http://{backend_uri}"

CHECK_USER_ADDRESS = f"{BACKEND_ADDRESS}/authorize"


app = FastAPI()


def checkUser(username: str, password: str):
    response = requests.get(
        CHECK_USER_ADDRESS,
        json={"username": username, "password": password},
    )
    if response.status_code == 200:
        return True
    return False


@app.get("/")
def read_root():
    backend_response = requests.get(BACKEND_ADDRESS)
    logger.info(f"Backend response: {backend_response.json()}")
    return {"response": backend_response.json()}


@app.get("/authorize")
async def read_users_me(
    request: Request,
):
    json = await request.json()
    username, password = json["username"], json["password"]
    if checkUser(username, password):
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
