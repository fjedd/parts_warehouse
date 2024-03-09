ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-alpine3.19
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN apk update && apk add bash build-base
RUN pip install -U pip && pip install poetry
RUN poetry install

COPY . /app/
