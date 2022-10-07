FROM python:3.8-slim

COPY example_app/run.py /app/run.py
WORKDIR /app
