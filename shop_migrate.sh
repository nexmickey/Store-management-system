#!/bin/bash

CONTAINER=${1}

# Generate migration script
docker exec -it $CONTAINER flask --app source_owner/migrate.py db migrate -m "Added dummy"

# Apply changes to database
docker exec -it $CONTAINER flask --app source_owner/migrate.py db upgrade
