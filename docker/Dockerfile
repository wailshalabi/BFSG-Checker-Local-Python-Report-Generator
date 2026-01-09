# Playwright base image includes Chromium + all OS deps (avoids Debian testing/trixie issues)
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Vendor axe-core (no Node/NPM needed)
RUN mkdir -p /app/vendor/axe \
    && curl -fsSL https://unpkg.com/axe-core@4.10.2/axe.min.js -o /app/vendor/axe/axe.min.js

COPY app /app/app

EXPOSE 8000
