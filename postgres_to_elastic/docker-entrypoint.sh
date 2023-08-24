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

# Load data from SQLite to Postgres
python sqlite_to_postgres/load_data.py
if [ $? -ne 0 ]; then
  echo "Failed to load data - exiting"
  exit 1
fi


python main.py