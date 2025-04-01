from typing import Union
import typing
import grpc
import pytest
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import requests
from fastapi.responses import JSONResponse
import logging
import os
import sys
from fastapi import Depends, FastAPI, HTTPException, status, Request
from enum import Enum
from gateway.auth import Authorizer
from gateway.models import (
    Addresses,
    LoginPayload,
    PostCreatePayload,
    PostGetPayload,
    TokenPayload,
    UserBaseInfo,
    UserExtendedInfo,
    PostUpdatePayload,
    PostsGetPayload,
)

from gateway.proto import posts_pb2
from gateway.proto import posts_pb2_grpc

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

channel = grpc.insecure_channel(Addresses.POSTS_ROOT.value)
stub = posts_pb2_grpc.PostServiceStub(channel)


def _validate_request(payload):
    return True
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


@app.post("/posts/create")
async def posts_create(request: PostCreatePayload):
    logger.info("Create post request request: %s", request)
    _validate_request(request)

    grpc_request = posts_pb2.CreatePostRequest(
        title=request.title,
        description=request.description,
        creator_id=request.creator_id,
        is_private=request.is_private,
        tags=request.tags,
    )
    grpc_response = stub.CreatePost(grpc_request)
    logger.info(grpc_response)
    if grpc_response.post_id == 0:
        raise HTTPException(status_code=500, detail="Post creation failed")
    return {"post_id": grpc_response.post_id}


@app.post("/posts/get")
async def posts_get(request: PostGetPayload):
    logger.info("User get info request: %s", request)
    _validate_request(request)

    grpc_request = posts_pb2.GetPostRequest(post_id=request.post_id)
    grpc_response = stub.GetPost(grpc_request)
    post = grpc_response.post
    logger.info(grpc_response)
    if post.post_id == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return jsonable_encoder(
        {
            "post_id": post.post_id,
            "title": post.title,
            "description": post.description,
            "creator_id": post.creator_id,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
        }
    )


@app.post("/posts/update")
async def posts_update(request: PostUpdatePayload):
    logger.info("Post update info request: %s", request)
    _validate_request(request)

    grpc_request = posts_pb2.UpdatePostRequest(
        post_id=request.post_id,
        title=request.title,
        description=request.description,
        is_private=request.is_private,
        tags=request.tags,
    )
    grpc_response = stub.UpdatePost(grpc_request)
    post = grpc_response.post
    logger.info(grpc_response)
    if post.post_id == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return jsonable_encoder(
        {
            "post_id": post.post_id,
            "title": post.title,
            "description": post.description,
            "creator_id": post.creator_id,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
        }
    )


@app.post("/posts/get_many")
async def posts_get_many(request: PostsGetPayload):
    logger.info("User get info request: %s", request)

    try:
        grpc_request = posts_pb2.GetPostsRequest(
            page_size=request.page_size,
            page=request.page_number,
        )
        grpc_response = stub.GetPosts(grpc_request)
        posts = grpc_response.posts
        logger.info(grpc_response)

        if not posts:
            raise HTTPException(status_code=404, detail="Posts not found")
        posts = filter(
            lambda post: (not post.is_private) or (post.creator_id == request.username),
            posts,
        )
        return jsonable_encoder(
            [
                {
                    "post_id": post.post_id,
                    "title": post.title,
                    "description": post.description,
                    "creator_id": post.creator_id,
                    "created_at": post.created_at,
                    "updated_at": post.updated_at,
                    "is_private": post.is_private,
                }
                for post in posts
            ]
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=404, detail="Posts not found")
