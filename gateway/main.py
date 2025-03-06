from typing import Union
import typing
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
    """
    Addresses is an enumeration that contains various endpoint URLs for backend services.

    Attributes:
        BACKEND_ROOT (str): The root URL of the backend service.
        CHECK_USER_ADDRESS (str): The URL to check user authorization.
        ADD_USER (str): The URL to add a new user.
        UPDATE_USER (str): The URL to update an existing user.
        DELETE_USER (str): The URL to delete a user.
        GET_USER (str): The URL to retrieve user information.
    """

    BACKEND_ROOT = f"http://{backend_uri}"
    CHECK_USER_ADDRESS = f"{BACKEND_ROOT}/authorize"
    ADD_USER = f"{BACKEND_ROOT}/create"
    UPDATE_USER = f"{backend_uri}/update"
    DELETE_USER = f"{backend_uri}/delete"
    GET_USER = f"{backend_uri}/get"


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


@app.get("/users/create")
async def create_user(request: Request):
    user_payload = request.json()["user"]
    response = await requests.post(
        Addresses.ADD_USER.value, json=user_payload, timeout=10
    )
    return response.json()


@app.get("/users/update")
async def update_user(request: Request):
    payload = await request.json()
    logger.info("User update request: %s", payload)
    _validate_request(payload)
    return await request.post(Addresses.UPDATE_USER, json=payload, timeout=10)


@app.get("/users/delete")
async def delete_user(request: Request):
    payload = await request.json()
    logger.info("User delete request: %s", payload)
    _validate_request(payload)
    response = await requests.post(
        Addresses.DELETE_USER.value, json=payload, timeout=10
    )
    return response


@app.get("/users/get")
async def get_user_info(request: Request):
    payload = await request.json()
    logger.info("User get info request: %s", payload)
    _validate_request(payload)
    response = await requests.post(
        f"{Addresses.GET_USER.value}/{payload['username']}", timeout=10
    )
    return response


@app.get("/users/check_token")
async def check_token(request: Request):
    json = await request.json()
    username, token = json["username"], json["token"]
    if authorizer.check_token(username, token):
        return {"status": "ok", "message": "authorized"}
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/users/authorize")
async def read_users_me(
    request: Request,
):
    json = await request.json()
    username, password = json["username"], json["password"]
    if checkUser(username, password):
        return {"status": "ok", "token": authorizer.make_token(username)}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
