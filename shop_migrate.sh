# Generate migration script
docker exec -it iepcourierproject-owner-app-1 flask --app source_owner/migrate.py db migrate -m "Added dummy"

# Apply changes to database
docker exec -it iepcourierproject-owner-app-1 flask --app source_owner/migrate.py db upgrade
