from typing import Union
import typing
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import requests
import logging
import os
import sys
from fastapi import Depends, FastAPI, HTTPException, status, Request
from enum import Enum
from gateway.auth import Authorizer

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)
logger = logging.getLogger(__name__)

backend_uri = os.environ.get("BACKEND_APP_ADDRESS", "web:8000")
authorizer = Authorizer()


class Addresses(Enum):

    BACKEND_ROOT = f"http://{backend_uri}"

    CHECK_USER_ADDRESS = f"{BACKEND_ROOT}/authorize"
    ADD_USER = f"{BACKEND_ROOT}/create"

    GET_USER = f"{BACKEND_ROOT}/get"
    GET_USER_INFO = f"{BACKEND_ROOT}/get_info"

    EDIT_USER = f"{BACKEND_ROOT}/edit"
    EDIT_USER_INFO = f"{BACKEND_ROOT}/edit_info"


class GetPayload(BaseModel):
    username: str
    token: str


def _validate_request(payload):
    username, token = payload["username"], payload["token"]
    if not authorizer.check_token(username, token):
        raise HTTPException(status_code=401, detail="Unauthorized")


app = FastAPI()


def checkUser(username: str, password: str):
    response = requests.get(
        Addresses.CHECK_USER_ADDRESS.value,
        json={"username": username, "password": password},
        timeout=10,
    )
    return response.status_code == 200


@app.get("/")
async def read_root():
    backend_response = requests.get(Addresses.BACKEND_ROOT.value, timeout=10)
    logger.info("Backend response: %s", backend_response.json)
    return {"response": backend_response.json()}


@app.post("/users/create")
async def create_user(request: Request):
    payload = request.json()["user"]
    response = await requests.post(Addresses.ADD_USER.value, json=payload, timeout=10)
    return response.json()


@app.post("/users/edit")
async def edit_user(request: Request):
    payload = await request.json()
    _validate_request(payload)
    logger.info("User edit request: %s", payload)
    payload.pop("token")
    return await request.post(Addresses.EDIT_USER, json=payload, timeout=10)


@app.post("/users/edit_info")
async def edit_user_info(request: Request):
    payload = await request.json()
    logger.info("User edit info request: %s", payload)
    _validate_request(payload)
    payload.pop("token")
    return await request.post(Addresses.EDIT_USER_INFO, json=payload, timeout=10)


@app.post("/users/get")
async def get_user(request: GetPayload):
    payload = request.dict()
    logger.info("User get request: %s", payload)
    _validate_request(payload)
    payload.pop("token")
    response = requests.get(
        f"{Addresses.GET_USER.value}/{payload['username']}", timeout=10
    )
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
    return jsonable_encoder(response.json())


@app.post("/users/get_info")
async def get_user_info(request: GetPayload):
    payload = request.dict()
    logger.info("User get info request: %s", payload)
    _validate_request(payload)
    payload.pop("token")
    response = requests.get(
        f"{Addresses.GET_USER_INFO.value}/{payload['username']}", timeout=10
    )
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")

    return jsonable_encoder(response.json())


@app.post("/users/check_token")
async def check_token(request: GetPayload):
    json = await request.json()
    username, token = json["username"], json["token"]
    if authorizer.check_token(username, token):
        return {"status": "ok", "message": "authorized"}
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/users/authorize")
async def read_users_me(
    request: Request,
):
    json = await request.json()
    username, password = json["username"], json["password"]
    if checkUser(username, password):
        return {"status": "ok", "token": authorizer.make_token(username)}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
