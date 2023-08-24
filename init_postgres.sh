#!/bin/bash

#!/bin/bash

echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"
echo "Current pg_hba.conf:"
cat /etc/postgresql/pg_hba.conf

echo "host $POSTGRES_DB $POSTGRES_USER all md5" >> /etc/postgresql/pg_hba.conf

# Start PostgreSQL
exec docker-entrypoint.sh postgres
