### convert poetry.lock to requirements.txt ###
FROM python:3.11-slim AS poetry

WORKDIR /src
COPY . ./
COPY pyproject.toml poetry.lock ./

RUN pip install poetry &&\
  poetry export -f requirements.txt --output requirements.txt

### final image ###
FROM python:3.11-slim

WORKDIR /src

ENV PYTHONPATH=/src

COPY --from=poetry /src/requirements.txt ./requirements.txt

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT [ "python", "./app/main.py" ]
