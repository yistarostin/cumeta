# Dockerfile

# pull the official docker image
FROM python:3.11.1-slim

# set work directory
WORKDIR /gateway

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV BACKEND_APP_ADDRESS web:8000

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
