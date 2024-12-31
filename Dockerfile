# syntax=docker/dockerfile:1@sha256:865e5dd094beca432e8c0a1d5e1c465db5f998dca4e439981029b3b81fb39ed5

### convert poetry.lock to requirements.txt ###
FROM python:3.10-slim@sha256:bdc6c5b8f725df8b009b32da65cbf46bfd24d1c86dce2e6169452c193ad660b4 AS poetry

WORKDIR /app

ENV PIP_ROOT_USER_ACTION=ignore

COPY requirements-poetry.txt ./
RUN pip install -r requirements-poetry.txt

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt

### final image ###
FROM python:3.10-slim@sha256:bdc6c5b8f725df8b009b32da65cbf46bfd24d1c86dce2e6169452c193ad660b4

WORKDIR /app

ENV PYTHONPATH=/app

COPY --from=poetry /app/requirements.txt ./requirements.txt

ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install -U pip && \
    pip install -r requirements.txt

WORKDIR /app

COPY . .
