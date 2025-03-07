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
from gateway.models import (
    Addresses,
    LoginPayload,
    TokenPayload,
    UserBaseInfo,
    UserExtendedInfo,
)

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)
logger = logging.getLogger(__name__)

authorizer = Authorizer()

app = FastAPI()


def _validate_request(payload):
    username, token = payload.username, payload.token
    if not authorizer.check_token(username, token):
        raise HTTPException(status_code=401, detail="Unauthorized")


def validateUserCredentials(username: str, password: str):
    response = requests.post(
        Addresses.CHECK_USER_ADDRESS.value,
        json={"username": username, "password": password},
        timeout=10,
    )
    return response.status_code == 200


@app.get("/")
async def read_root():
    backend_response = requests.get(Addresses._BACKEND_ROOT.value, timeout=10)
    logger.info("Backend response: %s", backend_response.json)
    return {"response": backend_response.json()}


@app.post("/users/create")
async def create_user(request: LoginPayload):
    response = requests.post(
        Addresses.ADD_USER.value, json=jsonable_encoder(request), timeout=10
    )
    return response.json()


@app.post("/users/edit")
async def edit_user(request: UserBaseInfo):
    if request.token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    logger.info("User edit request: %s", request)
    _validate_request(request)
    payload = jsonable_encoder(request)
    payload.pop("token")

    response = requests.post(Addresses.EDIT_USER.value, json=payload, timeout=10).json()
    logger.info(response)
    return jsonable_encoder(response)


@app.post("/users/edit_info")
async def edit_user_info(request: UserExtendedInfo):
    if request.token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    logger.info("User edit request: %s", request)
    _validate_request(request)

    payload = jsonable_encoder(request)
    payload.pop("token")
    response = requests.post(
        Addresses.EDIT_USER_INFO.value, json=payload, timeout=10
    ).json()
    logger.info(response)
    return jsonable_encoder(response)


@app.post("/users/get")
async def get_user(request: TokenPayload):
    logger.info("User get request: %s", request)
    _validate_request(request)
    response = requests.get(
        f"{Addresses.GET_USER.value}/{request.username}", timeout=10
    )
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")

    response = response.json()
    response.pop("password")
    return jsonable_encoder(response)


@app.post("/users/get_info")
async def get_user_info(request: TokenPayload):
    logger.info("User get info request: %s", request)
    _validate_request(request)

    response = requests.get(
        f"{Addresses.GET_USER_INFO.value}/{request.username}", timeout=10
    )
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User info not found")

    return jsonable_encoder(response.json())


@app.post("/users/check_token")
async def check_token(request: TokenPayload):
    username, token = request.username, request.token
    if authorizer.check_token(username, token):
        return {"status": "ok", "message": "authorized"}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/users/authorize")
async def read_users_me(
    request: LoginPayload,
):
    username, password = request.username, request.password
    if validateUserCredentials(username, password):
        return {"status": "ok", "token": authorizer.make_token(username)}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
