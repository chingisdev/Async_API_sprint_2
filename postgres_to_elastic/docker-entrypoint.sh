#!/bin/bash

# Function to wait for a service to be available
wait_for_service() {
  host="$1"
  port="$2"

  echo "Waiting for $host:$port..."

  while ! nc -z "$host" "$port"; do
    sleep 1
  done

  echo "$host:$port is available."
}

wait_for_service postgres 5432
wait_for_service elasticsearch 9200
wait_for_service redis 6379

# Wait for the signal file to be created after Sqlite to Postgres loaded
#while true; do
#  RESPONSE=$(curl -s http://sqlite-to-postgres:8010/status)
#  if [ "$RESPONSE" = "done" ]; then
#    break
#  fi
#  echo "Waiting for sqlite to postgres etl to complete..."
#  sleep 5
#done
# wait_for_service sqlite-to-postgres 8010


python main.py