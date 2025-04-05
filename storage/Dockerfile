# Dockerfile

# pull the official docker image
FROM python:3.11.1-slim

# set work directory
WORKDIR /storage

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY . .
COPY requirements.txt .
COPY proto  .
RUN pip install -r requirements.txt

RUN python3 -m grpc_tools.protoc -I. --python_out=./ --pyi_out=./ --grpc_python_out=./ proto/posts.proto   

# copy project
