#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: bash migrate.sh <container_name>"
  exit 1
fi

CONTAINER=${1}

# Generate migration script
docker exec -it $CONTAINER flask --app source/migrate.py db migrate -m "Added dummy"

# Apply changes to database
docker exec -it $CONTAINER flask --app source/migrate.py db upgrade
