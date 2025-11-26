#!/bin/bash
set -e

# Wait for Postgres to become available (TCP check)
echo "Waiting for Postgres at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
host="${POSTGRES_HOST:-db}"
port="${POSTGRES_PORT:-5432}"

until bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; do
  sleep 1
done

echo "Postgres is reachable, starting server..."

# Start uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
