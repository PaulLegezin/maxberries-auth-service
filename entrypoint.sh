#!/bin/bash
set -e

echo "Ожидание базы данных ($POSTGRES_HOST:$POSTGRES_PORT)..."

until (echo > /dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT) >/dev/null 2>&1; do
  echo "База данных недоступна, ждем..."
  sleep 1
done

echo "База данных готова!"

echo "Выполнение миграций..."
alembic upgrade head

echo "Запуск приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000