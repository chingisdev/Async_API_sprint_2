#!/bin/bash

wait_for_service() {
  host="$1"
  port="$2"

  echo "Waiting for $host:$port..."

  while ! nc -z "$host" "$port"; do
    sleep 1
  done

  echo "$host:$port is available."
}

wait_for_service elasticsearch 9200
wait_for_service redis 6379

uvicorn main:app --host 0.0.0.0 --port 8000 --workers $UVICORN_WORKERS_NUM