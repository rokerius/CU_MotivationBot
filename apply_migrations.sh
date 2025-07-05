#!/bin/bash

# Ждём, пока Postgres будет готов принимать соединения
until pg_isready -h postgres -p 5432 -U ${PG_USER}; do
  echo "Waiting for postgres..."
  sleep 2
done

# Применяем миграции (init.sql)
psql -h postgres -U ${PG_USER} -d ${PG_DATABASE} -f /docker-entrypoint-initdb.d/init.sql

# Запускаем бота
exec python bot.py
