# Dockerfile

# pull the official docker image
FROM python:3.11.1-slim

# set work directory

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV BACKEND_APP_ADDRESS web:8000
ENV POSTS_STORAGE_ADDRESS 0.0.0.0:50051

# install dependencies
COPY . gateway
COPY ./requirements.txt gateway
RUN pip install -r gateway/requirements.txt

RUN python3 -m grpc_tools.protoc -I. --python_out=./gateway --pyi_out=./gateway --grpc_python_out=./gateway gateway/proto/posts.proto 

WORKDIR /gateway

# copy project