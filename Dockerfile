FROM ghcr.io/astral-sh/uv:debian-slim@sha256:0a3f822c6e1f707e48b6169e2838b289996694f273340ea499bef40da5f978c5 AS build

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN uv export --no-group dev --frozen --no-emit-project > /app/requirements.txt

FROM python:3.10-slim@sha256:f680fc3f447366d9be2ae53dc7a6447fe9b33311af209225783932704f0cb4e7

ENV PIP_ROOT_USER_ACTION=ignore
WORKDIR /app

COPY --from=build /app/requirements.txt .

RUN pip install --only-binary=:all: --no-cache --no-deps -r requirements.txt

COPY . .
