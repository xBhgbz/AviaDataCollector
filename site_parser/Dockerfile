FROM python:3.11.0-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY . .

ENV PYTHONPATH=/app/src