#!/usr/bin/env bash
set -e

host="${POSTGRES_HOST:-db}"
port="${POSTGRES_PORT:-5432}"

until nc -z "$host" "$port"; do
  echo "Aguardando banco em $host:$port..."
  sleep 2
done

echo "Instalando dependências (garantia de gunicorn e libs)..."
poetry install --no-root --no-ansi

echo "Banco disponível, rodando migrações..."
poetry run python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
poetry run python manage.py collectstatic --noinput

echo "Iniciando servidor..."
exec poetry run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
