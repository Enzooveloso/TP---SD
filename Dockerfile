# syntax=docker/dockerfile:1.7
FROM python:3.12.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR=/root/.cache/pypoetry

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl tini libpq-dev \
    && pip install --no-cache-dir poetry \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-ansi --no-root


# COPY . /app

# RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app
# USER appuser

EXPOSE 8000

ENTRYPOINT ["/usr/bin/tini","--"]
# migrate + devserver (hot reload)
CMD ["bash", "-lc", "poetry run python manage.py migrate && poetry run python manage.py runserver 0.0.0.0:8000"]
