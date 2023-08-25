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

python load_data.py

if [ $? -eq 0 ]; then
  # If the exit code is 0, the script was successful
  echo "Python script executed successfully"
  echo -e "HTTP/1.1 200 OK\n\n done" > response.txt
else
  # If the exit code is non-zero, the script failed
  echo "Python script failed"
  echo -e "HTTP/1.1 500 Internal Server Error\n\n failed" > response.txt
fi

# Start a simple HTTP server with nc that always returns the response
while true; do
  cat response.txt | nc -l -p 8010
done
