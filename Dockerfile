# syntax=docker/dockerfile:1

FROM python:3.10-slim
WORKDIR /app
COPY pyproject.toml .
COPY poetry.lock .

RUN apt update && apt upgrade -y && apt install -y build-essential libldap2-dev libsasl2-dev libffi-dev
RUN python -m pip install --upgrade pip
RUN pip install poetry && poetry install
COPY . .

CMD ["poetry", "run", "python", "ldapsync.py"] 
